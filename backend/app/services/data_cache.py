'''
文件: backend/app/services/data_cache.py
负责全局数据的加载、图表数据的预计算和缓存管理，以优化API的性能和响应速度
在 FastAPI 启动时执行一次，将耗时的pandas计算转化为O(1)的字典读取。
'''
import pandas as pd
import numpy as np
import os

# 全局结果缓存字典
API_RESULT_CACHE = {}

# 基础预计算函数
def compute_overview(df):
    '''预计算概览数据'''
    total_users = df['user_id'].nunique()
    total_purchases = df['purchase_amount'].sum()
    # 计算核心指标
    # 使用 nunique() 计算去重后的独立用户数和商户数
    total_users = df['user_id'].nunique()
    total_merchants = df['merchant_id'].nunique()
    # 统计非空的日期字段数量，代表实际发生的购买次数和发券次数
    total_purchases = df['date'].notna().sum()
    total_coupons = df['date_received'].notna().sum()
    # 计算整体转化率 CVR (Conversion Rate)
    # 假设 'action' 列中 0 代表点击，1 代表购买
    if 'action' in df.columns:
        clicks = (df['action'] == 0).sum()
        purchases = (df['action'] == 1).sum()
        cvr = (purchases / clicks * 100) if clicks > 0 else 0
    else:
        cvr = 0
    
    # 计算优惠券核销率
    # 已核销：有购买时间且有优惠券ID
    coupon_used = ((df['date'].notna()) & (df['coupon_id'].notna())).sum()
    # 未核销：date为空且coupon_id不为空
    coupon_not_used = ((df['date'].isna()) & (df['coupon_id'].notna())).sum()
    # 核销率 = 已核销 / (已核销 + 未核销)
    redemption_rate = (coupon_used / (coupon_used + coupon_not_used) * 100) if (coupon_used + coupon_not_used) > 0 else 0

    return {
        "total_users": int(total_users),
        "total_merchants": int(total_merchants),
        "total_purchases": int(total_purchases),
        "total_coupons": int(total_coupons),
        "cvr": round(cvr, 2),
        "redemption_rate": round(redemption_rate, 2)
    }

def compute_daily_trend(df):
    '''
    1、预计算所有日期的趋势
    2、接口调用时再根据start_date和end_date过滤
    '''
    daily_purchases = df[df['date'].notna()].groupby(df['date'].dt.date).size().reset_index()
    daily_purchases.columns = ['date', 'purchases']
    
    daily_coupons = df[df['date_received'].notna()].groupby(df['date_received'].dt.date).size().reset_index()
    daily_coupons.columns = ['date', 'coupons']
    
    daily_data = pd.merge(daily_purchases, daily_coupons, on='date', how='outer').fillna(0)
    daily_data = daily_data.sort_values('date') # 确保日期有序
    daily_data['date'] = daily_data['date'].astype(str)
    
    # 存为列表形式，方便 API 层直接做过滤
    return daily_data.to_dict('records')

def compute_monthly_trend(df):
    monthly_data = []
    for month in range(1, 7):
        month_df = df[df['month'] == month]
        purchases = month_df['date'].notna().sum()
        coupons = month_df['date_received'].notna().sum()
        
        if 'action' in month_df.columns:
            clicks = (month_df['action'] == 0).sum()
            cvr = (purchases / clicks * 100) if clicks > 0 else 0
        else:
            cvr = 0
            
        monthly_data.append({
            "month": month,
            "purchases": int(purchases),
            "coupons": int(coupons),
            "cvr": round(cvr, 2)
        })
    return {"data": monthly_data}

def compute_conversion_funnel(df):
    total_users = df['user_id'].nunique()
    clicked_users = df[df['action'] == 0]['user_id'].nunique() if 'action' in df.columns else total_users
    coupon_users = df[df['date_received'].notna()]['user_id'].nunique()
    purchased_users = df[df['date'].notna()]['user_id'].nunique()
    
    return {
        "funnel": [
            {"stage": "总用户", "count": int(total_users)},
            {"stage": "点击用户", "count": int(clicked_users)},
            {"stage": "领券用户", "count": int(coupon_users)},
            {"stage": "购买用户", "count": int(purchased_users)}
        ]
    }

def compute_behavior_sankey(df, period="all"):
    if period == "regular":
        period_df = df[df['month'] <= 4]
    elif period == "promotion":
        period_df = df[df['month'] >= 5]
    else:
        period_df = df # 全量
        
    clicked = set(period_df[period_df['action'] == 0]['user_id']) if 'action' in period_df.columns else set(period_df['user_id'])
    coupon_users = set(period_df[period_df['date_received'].notna()]['user_id'])
    purchase_users = set(period_df[period_df['date'].notna()]['user_id'])
    coupon_purchase = set(period_df[(period_df['date'].notna()) & (period_df['coupon_id'].notna())]['user_id'])

    links = [
        {"source": "点击用户", "target": "领券用户",  "value": max(len(clicked & coupon_users), 1)},
        {"source": "点击用户", "target": "未领券用户", "value": max(len(clicked - coupon_users), 1)},
        {"source": "领券用户", "target": "券+购买",   "value": max(len(coupon_users & coupon_purchase), 1)},
        {"source": "领券用户", "target": "券未购买",  "value": max(len(coupon_users - coupon_purchase), 1)},
        {"source": "未领券用户", "target": "直接购买", "value": max(len(purchase_users - coupon_users), 1)},
        {"source": "未领券用户", "target": "未购买",   "value": max(len(clicked - purchase_users), 1)}
    ]
    nodes = [{"name": n} for n in ["点击用户", "领券用户", "未领券用户", "券+购买", "券未购买", "直接购买", "未购买"]]
    return {"nodes": nodes, "links": links}

def compute_behavior_heatmap(df, month):
    month_df = df[(df['month'] == month) & df['date'].notna()].copy()
    if len(month_df) == 0:
        return {"matrix": [], "max_value": 0}

    if 'hour' in month_df.columns:
        month_df['hour'] = month_df['hour'].astype(int)
    else:
        # 模拟数据
        np.random.seed(42)
        hours = np.random.choice(range(24), size=len(month_df), 
                                 p=[0.01,0.01,0.01,0.01,0.01,0.02,0.03,0.05,0.07,0.08,0.07,0.06,
                                    0.05,0.05,0.05,0.05,0.06,0.07,0.08,0.07,0.06,0.05,0.03,0.02])
        month_df['hour'] = hours

    month_df['weekday'] = month_df['date'].dt.weekday
    agg = month_df.groupby(['hour', 'weekday']).size().reset_index(name='count')
    matrix = agg[['hour', 'weekday', 'count']].values.tolist()
    return {"matrix": matrix, "max_value": int(agg['count'].max())}

# 特征相关预计算函数 (基于 user_features_monthX.csv)
def get_user_segment(row):
    '''辅助函数：用户分层逻辑'''
    if row.get('recency', 999) <= 30 and row.get('frequency', 0) >= 10:
        return '高价值用户'
    elif row.get('recency', 999) > 30 and row.get('frequency', 0) >= 10:
        return '重要挽留用户'
    elif row.get('is_new_user', 0) == 1:
        return '新用户'
    elif row.get('recency', 0) > 90 :
        return '流失用户'
    return '普通用户'

def compute_user_stats(features):
    segments = {
        "高价值用户": ((features['recency'] <= 30) & (features['frequency'] >= 10)).sum(),
        "重要挽留用户": ((features['recency'] > 30) & (features['frequency'] >= 10)).sum(),
        "新用户": (features['is_new_user'] == 1).sum() if 'is_new_user' in features.columns else 0,
        "流失用户": (features['recency'] > 90).sum()
    }
    return {"segments": [{"name": k, "value": int(v)} for k, v in segments.items()]}

def compute_group_conversion(features):
    features['segment'] = features.apply(get_user_segment, axis=1)
    groups = ['高价值用户', '重要挽留用户', '普通用户', '新用户', '流失用户']
    result = {'groups': groups, 'ctr': [], 'coupon_rate': [], 'redemption_rate': [], 'cvr': []}
    
    for g in groups:
        gdf = features[features['segment'] == g]
        if len(gdf) == 0:
            for k in ['ctr', 'coupon_rate', 'redemption_rate', 'cvr']: result[k].append(0)
            continue
        result['ctr'].append(round(float(gdf['ctr'].mean() * 100), 2) if 'ctr' in gdf.columns else 0)
        result['coupon_rate'].append(round(float(gdf['coupon_receive_rate'].mean() * 100), 2) if 'coupon_receive_rate' in gdf.columns else 0)
        result['redemption_rate'].append(round(float(gdf['coupon_use_rate'].mean() * 100), 2) if 'coupon_use_rate' in gdf.columns else 0)
        result['cvr'].append(round(float(gdf['cvr'].mean() * 100), 2) if 'cvr' in gdf.columns else 0)
    return result

# 全局初始化入口
def init_global_cache():
    '''在FastAPI启动时调用，执行所有预计算并填充API_RESULT_CACHE'''
    # 处理原始行为日志(online_data.csv)
    raw_path = 'data/raw/online_data.csv'
    if os.path.exists(raw_path):
        print("加载原始数据集")
        df = pd.read_csv(raw_path)
        df.columns = df.columns.str.lower()
        df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d',errors='coerce')
        df['date_received'] = pd.to_datetime(df['date_received'], format='%Y-%m-%d',errors='coerce')
        df['month'] = df['date'].dt.month
        
        # 宽表级别缓存聚合
        API_RESULT_CACHE['overview'] = compute_overview(df)
        API_RESULT_CACHE['daily_trend'] = compute_daily_trend(df)
        API_RESULT_CACHE['monthly_stats'] = compute_monthly_stats(df)
        API_RESULT_CACHE['conversion_funnel'] = compute_conversion_funnel(df)
        # 按参数/时间段嵌套缓存
        API_RESULT_CACHE['behavior_sankey'] = {
            "all": compute_behavior_sankey(df, period="all"),
            "regular": compute_behavior_sankey(df, period="regular"),
            "promotion": compute_behavior_sankey(df, period="promotion")
        }
        # 热力图按月缓存
        API_RESULT_CACHE['behavior_heatmap'] = {}
        for m in [4,5,6]:
            API_RESULT_CACHE['behavior_heatmap'][m] = compute_behavior_heatmap(df, month=m)
            # 释放宽表内存
        del df
    else:
        print("原始数据文件未找到")

    # 处理特征工程结果
    API_RESULT_CACHE['user_stats'] = {}
    API_RESULT_CACHE['user_segmentation'] = {}
    API_RESULT_CACHE['group_conversion'] = {}
    # 遍历可能的月份特征表
    for month in [4,5,6]:
        feat_path = f'data/features/user_features_month{month}.csv'
        if os.path.exists(feat_path):
            features = pd.read_csv(feat_path)
            # 执行按月的特征相关预计算
            API_RESULT_CACHE['user_stats'][month] = compute_user_stats(features)
            API_RESULT_CACHE['user_segmentation'][month] = compute_user_segmentation(features)
            API_RESULT_CACHE['group_conversion'][month] = compute_group_conversion(features)
            
            # 注意：像 user_rfm (散点图) 这种需要返回几千个明细点的，
            # 也可以在这里采样并缓存，逻辑与上面类似。
            del features
        else:
            print(f"特征数据文件 {feat_path} 未找到")

