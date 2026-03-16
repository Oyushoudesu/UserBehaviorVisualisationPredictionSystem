"""
可视化数据API
文件: backend/app/api/visualization.py
提供前端需要的可视化数据
"""

from fastapi import APIRouter, HTTPException
import pandas as pd
from datetime import datetime

router = APIRouter()

# 全局缓存数据
GLOBAL_DATA = {
    "raw_data": None,   # 原始数据
    "features_m4": None,# 预处理特征数据，按月份存储
    "features_m5": None,
    "features_m6": None
}
def init_app_data():
    '''在FastAPI应用启动时加载数据到全局缓存'''
    try:
        # 加载并清洗原始数据
        df = pd.read_csv('data/raw/transactions.csv')
        df.columns = df.columns.str.lower()
        df['date'] = pd.to_datetime(df['date'],format='%Y%m%d',errors='coerce')
        df['date_received'] = pd.to_datetime(df['date_received'],format='%Y%m%d', errors='coerce')
        df['month'] = df['date'].dt.month
        GLOBAL_DATA['raw_data'] = df

        # 加载预处理特征数据
        GLOBAL_DATA['features_m4'] = pd.read_csv('data/features/user_features_month4.csv')
        GLOBAL_DATA['features_m5'] = pd.read_csv('data/features/user_features_month5.csv')
        GLOBAL_DATA['features_m6'] = pd.read_csv('data/features/user_features_month6.csv')
    except Exception as e:
        print(f"数据加载失败: {str(e)}")

# 初始化
init_app_data()

# ============================================================================
# 接口1: 总览数据
# ============================================================================

@router.get("/overview")
def get_overview():
    """
    获取总览数据
    返回：总用户数、总商户数、总购买行为数、总发券量、转化率 (CVR) 以及券核销率。
    """
    # 优化数据访问，直接引用全局内存中的DataFrame
    df = GLOBAL_DATA.get("raw_data")
    if df is None:
        raise HTTPException(status_code=500, detail="数据未加载或加载失败")
    
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

# ============================================================================
# 接口2: 每日趋势
# ============================================================================

@router.get("/daily-trend")
def get_daily_trend(start_date: str = None, end_date: str = None):
    """
    获取时间序列上的每日行为趋势数据（适合绘制折线图）。
    参数可以接收可选的起止日期进行数据截断，默认返回所有日期。
    
    参数：
    - start_date: 起始日期 (可选)
    - end_date: 结束日期 (可选)
    
    返回：每日购买/领券数据
    """
    df = GLOBAL_DATA.get("raw_data")
    if df is None:
        raise HTTPException(status_code=500, detail="数据未加载或加载失败")
    
    # 筛选日期范围
    # 若前端传了日期范围参数，则对 DataFrame 进行时间切片过滤
    if start_date:
        df = df[df['date'] >= pd.to_datetime(start_date)]
    if end_date:
        df = df[df['date'] <= pd.to_datetime(end_date)]
    
    # 按日期统计购买
    # df['date'].dt.date 提取出 YYYY-MM-DD 格式的日期进行 groupby
    daily_purchases = df[df['date'].notna()].groupby(
        df['date'].dt.date
    ).size().reset_index()
    # 重命名列名以便合并
    daily_purchases.columns = ['date', 'purchases']
    
    # 按天分组统计领券量
    daily_coupons = df[df['date_received'].notna()].groupby(
        df['date_received'].dt.date
    ).size().reset_index()
    daily_coupons.columns = ['date', 'coupons']
    
    # 合并
    # 使用外连接 (outer join) 合并购买和领券数据
    # 因为某些日期可能只有领券没有购买，或只有购买没有领券
    daily_data = pd.merge(
        daily_purchases, 
        daily_coupons, 
        on='date', 
        how='outer'
    ).fillna(0) # 将因为 outer join 产生的 NaN 填充为 0
    
    # 转换为列表
    # 为了能被 JSON 序列化，需要将日期对象转回字符串类型
    daily_data['date'] = daily_data['date'].astype(str)
    
    # 将 Pandas 的 Series 转换为原生 Python List 返回
    return {
        "dates": daily_data['date'].tolist(),
        "purchases": daily_data['purchases'].astype(int).tolist(),
        "coupons": daily_data['coupons'].astype(int).tolist()
    }

# ============================================================================
# 接口3: 按月统计
# ============================================================================

@router.get("/monthly-stats")
def get_monthly_stats():
    """
    获取按月统计数据
    获取按月聚合的统计数据（适合绘制柱状图或多维对比图）。
    硬编码了 1 到 6 月的数据遍历
    返回：每月购买/领券/CVR数据
    """
    df = load_data()
    
    monthly_data = []
    
    for month in range(1, 7):
        # 筛选出指定月份的数据
        month_df = df[df['month'] == month]
        # 统计该月有效购买和发券行为
        purchases = month_df['date'].notna().sum()
        coupons = month_df['date_received'].notna().sum()
        
        # 计算该月的 CVR
        if 'action' in month_df.columns:
            clicks = (month_df['action'] == 0).sum()
            cvr = (purchases / clicks * 100) if clicks > 0 else 0
        else:
            cvr = 0
        
        # 组装当前月的数据字典
        monthly_data.append({
            "month": month,
            "purchases": int(purchases),
            "coupons": int(coupons),
            "cvr": round(cvr, 2)
        })
    
    return {"data": monthly_data}

# ============================================================================
# 接口4: 用户分层（RFM）
# ============================================================================

@router.get("/user-segmentation")
def get_user_segmentation():
    """
    获取用户分层数据（RFM）
    获取基于 RFM 模型的用户分层数据（适合绘制饼图或漏斗图）。
    注意：此接口读取的是预先提取好的特征文件，而不是原始宽表。
    返回：不同层级用户数量
    """
    # 加载特征数据
    try:
        features = pd.read_csv('data/features/user_features_month4.csv')
    except:
        raise HTTPException(status_code=404, detail="特征数据未找到")
    
    # RFM分层
    # 基于 Recency(最近一次消费间隔) 和 Frequency(消费频率) 进行分群
    # 这里的阈值 (30天, 10次, 90天) 是业务经验值，在模型调优时可动态调整
    segments = {
        "高价值用户": ((features['recency'] <= 30) & (features['frequency'] >= 10)).sum(),
        "重要挽留用户": ((features['recency'] > 30) & (features['frequency'] >= 10)).sum(),
        "新用户": ((features['is_new_user'] == 1)).sum(),
        "流失用户": ((features['recency'] > 90)).sum()
    }
    # 转换为适合 Echarts 等前端图表库的 Key-Value 数组格式
    return {
        "segments": [
            {"name": k, "value": int(v)} 
            for k, v in segments.items()
        ]
    }

# ============================================================================
# 接口5: 转化漏斗
# ============================================================================

@router.get("/conversion-funnel")
def get_conversion_funnel():
    """
    获取转化漏斗数据
    
    返回：点击 → 领券 → 购买 各阶段人数
    """
    df = load_data()
    
    # 1. 漏斗顶层：覆盖的总独立用户数
    total_users = df['user_id'].nunique()
    # 2. 第二层：产生过点击行为的用户数
    if 'action' in df.columns:
        clicked_users = df[df['action'] == 0]['user_id'].nunique()
    else:
        # 兼容处理：如果没有 action 字段，默认全量用户都有“浏览/点击”动作
        clicked_users = total_users
    # 3. 第三层：成功领取到优惠券的用户数
    coupon_users = df[df['date_received'].notna()]['user_id'].nunique()
    # 4. 漏斗底层：最终产生购买行为的用户数
    purchased_users = df[df['date'].notna()]['user_id'].nunique()
    
    return {
        "funnel": [
            {"stage": "总用户", "count": int(total_users)},
            {"stage": "点击用户", "count": int(clicked_users)},
            {"stage": "领券用户", "count": int(coupon_users)},
            {"stage": "购买用户", "count": int(purchased_users)}
        ]
    }

# ============================================================================
# 接口6: 用户统计指标（UserAnalysis 页顶部卡片）
# ============================================================================
@router.get("/user-stats")
def get_user_stats(month: int = 4):
    try:
        features = pd.read_csv(f'data/features/user_features_month{month}.csv')
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"特征数据未找到: {str(e)}")

    total_users = len(features)
    high_value = int(((features['recency'] <= 30) & (features['frequency'] >= 10)).sum())
    avg_recency = float(features['recency'].mean()) if 'recency' in features.columns else 0
    churn_risk = int((features['recency'] > 90).sum()) if 'recency' in features.columns else 0

    return {
        "total_users": total_users,
        "high_value_users": high_value,
        "avg_recency": round(avg_recency, 1),
        "churn_risk_users": churn_risk
    }


# ============================================================================
# 接口7: RFM 散点图数据
# ============================================================================

@router.get("/user-rfm")
def get_user_rfm(month: int = 4, sample_n: int = 2000):
    try:
        features = pd.read_csv(f'data/features/user_features_month{month}.csv')
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"特征数据未找到: {str(e)}")

    required_cols = ['user_id', 'recency', 'frequency']
    for col in required_cols:
        if col not in features.columns:
            raise HTTPException(status_code=500, detail=f"特征文件缺少字段: {col}")

    if 'purchase_count' not in features.columns:
        features['purchase_count'] = features['frequency']

    if len(features) > sample_n:
        features = features.sample(n=sample_n, random_state=42)

    def classify(row):
        if row['recency'] <= 30 and row['frequency'] >= 10:
            return '高价值用户'
        elif row['recency'] > 30 and row['frequency'] >= 10:
            return '重要挽留用户'
        elif row.get('is_new_user', 0) == 1:
            return '新用户'
        elif row['recency'] > 90:
            return '流失用户'
        else:
            return '其他'

    features['segment'] = features.apply(classify, axis=1)
    points = features[['user_id', 'recency', 'frequency', 'purchase_count', 'segment']].copy()
    points['user_id'] = points['user_id'].astype(str)

    return {"points": points.to_dict(orient='records')}


# ============================================================================
# 接口8: 用户画像雷达图数据
# ============================================================================

@router.get("/user-profile")
def get_user_profile(month: int = 4):
    try:
        features = pd.read_csv(f'data/features/user_features_month{month}.csv')
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"特征数据未找到: {str(e)}")

    dim_map = {
        'purchase_freq':  'frequency',
        'active_days':    'active_days',
        'coupon_rate':    'coupon_receive_rate',
        'cvr':            'cvr',
        'merchant_div':   'merchant_count',
        'recency_score':  'recency',
    }
    available = {k: v for k, v in dim_map.items() if v in features.columns}

    high_mask = (features['recency'] <= 30) & (features['frequency'] >= 10) \
        if 'recency' in features.columns and 'frequency' in features.columns \
        else pd.Series([False] * len(features))
    normal_mask = ~high_mask

    def normalize_col(series, invert=False):
        min_v, max_v = series.min(), series.max()
        if max_v == min_v:
            return pd.Series([50.0] * len(series), index=series.index)
        norm = (series - min_v) / (max_v - min_v) * 100
        return (100 - norm) if invert else norm

    result = {'high_value': [], 'normal': []}
    dim_order = ['purchase_freq', 'active_days', 'coupon_rate', 'cvr', 'merchant_div', 'recency_score']

    for dim in dim_order:
        if dim not in available:
            result['high_value'].append(50)
            result['normal'].append(50)
            continue
        col = available[dim]
        invert = (dim == 'recency_score')
        full_norm = normalize_col(features[col], invert=invert)
        hv = round(float(full_norm[high_mask].mean()), 1) if high_mask.any() else 50.0
        nm = round(float(full_norm[normal_mask].mean()), 1) if normal_mask.any() else 50.0
        result['high_value'].append(hv)
        result['normal'].append(nm)

    return result


# ============================================================================
# 接口9: 行为时段热力图
# ============================================================================

@router.get("/behavior-heatmap")
def get_behavior_heatmap(month: int = 4):
    """
    获取行为时段热力图数据（小时 × 星期）
    
    依赖原始数据中的时间字段；若无小时字段则用模拟分布返回。
    返回格式：matrix = [[hour, weekday, count], ...]，max_value
    """
    try:
        df = load_data()
        # 只取对应月份的购买记录
        month_df = df[(df['month'] == month) & df['date'].notna()].copy()

        if len(month_df) == 0:
            raise ValueError("无数据")

        # 原始数据若有小时字段
        if 'hour' in month_df.columns:
            month_df['hour'] = month_df['hour'].astype(int)
        else:
            # 无小时字段：用行为量按正态分布模拟（峰值10时、20时）
            import numpy as np
            np.random.seed(42)
            n = len(month_df)
            hours = np.random.choice(
                range(24),
                size=n,
                p=[0.01,0.01,0.01,0.01,0.01,0.02,0.03,0.05,0.07,0.08,
                   0.07,0.06,0.05,0.05,0.05,0.05,0.06,0.07,0.08,0.07,
                   0.06,0.05,0.03,0.02]
            )
            month_df['hour'] = hours

        month_df['weekday'] = month_df['date'].dt.weekday  # 0=周一

        agg = month_df.groupby(['hour', 'weekday']).size().reset_index(name='count')
        matrix = agg[['hour', 'weekday', 'count']].values.tolist()
        max_value = int(agg['count'].max())

        return {"matrix": matrix, "max_value": max_value}

    except Exception as e:
        # 若数据加载失败，返回空矩阵
        raise HTTPException(status_code=500, detail=f"热力图数据生成失败: {str(e)}")

# ============================================================================
# 接口10: 行为路径桑基图
# ============================================================================

@router.get("/behavior-sankey")
def get_behavior_sankey(month: int = 4, period: str = "all"):
    """
    获取用户行为路径桑基图数据
    节点：点击用户 / 领券用户 / 仅购买用户 / 券+购买 / 未转化
    """
    df = load_data()

    # 月份筛选
    if period == "regular":
        df = df[df['month'] <= 4]
    elif period == "promotion":
        df = df[df['month'] >= 5]
    else:
        df = df[df['month'] == month]

    if 'action' in df.columns:
        clicked = set(df[df['action'] == 0]['user_id'])
    else:
        clicked = set(df['user_id'])

    coupon_users   = set(df[df['date_received'].notna()]['user_id'])
    purchase_users = set(df[df['date'].notna()]['user_id'])
    # 用券购买
    coupon_purchase = set(df[(df['date'].notna()) & (df['coupon_id'].notna())]['user_id'])

    click_to_coupon    = len(clicked & coupon_users)
    click_no_coupon    = len(clicked - coupon_users)
    coupon_to_purchase = len(coupon_users & coupon_purchase)
    coupon_no_purchase = len(coupon_users - coupon_purchase)
    direct_purchase    = len(purchase_users - coupon_users)
    no_purchase        = len(clicked - purchase_users)

    nodes = [
        {"name": "点击用户"},
        {"name": "领券用户"},
        {"name": "未领券用户"},
        {"name": "券+购买"},
        {"name": "券未购买"},
        {"name": "直接购买"},
        {"name": "未购买"}
    ]

    links = [
        {"source": "点击用户", "target": "领券用户",  "value": max(click_to_coupon, 1)},
        {"source": "点击用户", "target": "未领券用户", "value": max(click_no_coupon, 1)},
        {"source": "领券用户", "target": "券+购买",   "value": max(coupon_to_purchase, 1)},
        {"source": "领券用户", "target": "券未购买",  "value": max(coupon_no_purchase, 1)},
        {"source": "未领券用户", "target": "直接购买", "value": max(direct_purchase, 1)},
        {"source": "未领券用户", "target": "未购买",   "value": max(no_purchase, 1)}
    ]

    return {"nodes": nodes, "links": links}


# ============================================================================
# 接口11: 不同用户群体转化率对比
# ============================================================================

@router.get("/group-conversion")
def get_group_conversion(month: int = 4):
    """
    获取不同用户群体的转化率对比（高价值/重要挽留/新用户/流失用户/其他）
    """
    try:
        features = pd.read_csv(f'data/features/user_features_month{month}.csv')
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"特征数据未找到: {str(e)}")

    def classify(row):
        if row.get('recency', 999) <= 30 and row.get('frequency', 0) >= 10:
            return '高价值用户'
        elif row.get('recency', 999) > 30 and row.get('frequency', 0) >= 10:
            return '重要挽留用户'
        elif row.get('is_new_user', 0) == 1:
            return '新用户'
        elif row.get('recency', 0) > 90:
            return '流失用户'
        else:
            return '普通用户'

    features['segment'] = features.apply(classify, axis=1)

    groups = ['高价值用户', '重要挽留用户', '普通用户', '新用户', '流失用户']
    result = {'groups': groups, 'ctr': [], 'coupon_rate': [], 'redemption_rate': [], 'cvr': []}

    for g in groups:
        gdf = features[features['segment'] == g]
        if len(gdf) == 0:
            result['ctr'].append(0)
            result['coupon_rate'].append(0)
            result['redemption_rate'].append(0)
            result['cvr'].append(0)
            continue

        def safe_mean(col):
            if col in gdf.columns:
                return round(float(gdf[col].mean() * 100), 2)
            return 0

        result['ctr'].append(safe_mean('ctr'))
        result['coupon_rate'].append(safe_mean('coupon_receive_rate'))
        result['redemption_rate'].append(safe_mean('coupon_use_rate'))
        result['cvr'].append(safe_mean('cvr'))

    return result


# ============================================================================
# 接口12: 平销期 vs 促销期对比摘要
# ============================================================================

@router.get("/comparison-summary")
def get_comparison_summary():
    """
    获取平销期(1-4月) vs 促销期(5-6月)核心指标对比
    """
    df = load_data()

    def period_stats(pdf):
        total_days = pdf['date'].dt.date.nunique() if pdf['date'].notna().any() else 1
        purchases = int(pdf['date'].notna().sum())
        coupons = int(pdf['date_received'].notna().sum())
        active_users = int(pdf['user_id'].nunique())

        if 'action' in pdf.columns:
            clicks = int((pdf['action'] == 0).sum())
            cvr = round(purchases / clicks * 100, 2) if clicks > 0 else 0
        else:
            cvr = 0

        coupon_rate = round(coupons / (purchases + coupons) * 100, 2) if (purchases + coupons) > 0 else 0
        daily_purchases = round(purchases / max(total_days, 1), 0)

        return {
            "cvr": cvr,
            "coupon_rate": coupon_rate,
            "daily_purchases": int(daily_purchases),
            "active_users": active_users
        }

    regular_df   = df[df['month'] <= 4]
    promotion_df = df[df['month'] >= 5]

    regular   = period_stats(regular_df)
    promotion = period_stats(promotion_df)

    # 变化量
    changes = {
        k: round(promotion[k] - regular[k], 2)
        for k in regular
    }

    # 雷达图归一化数据（0-100）
    def to_radar(stats, ref):
        result = []
        for k in ['cvr', 'daily_purchases', 'coupon_rate', 'active_users', 'cvr', 'coupon_rate']:
            max_v = max(stats.get(k, 0), ref.get(k, 1), 1)
            result.append(round(stats.get(k, 0) / max_v * 100, 1))
        return result

    return {
        "regular": regular,
        "promotion": promotion,
        "changes": changes,
        "radar": {
            "regular":   to_radar(regular, promotion),
            "promotion": to_radar(promotion, promotion)
        }
    }
