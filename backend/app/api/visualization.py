"""
可视化数据API
文件: backend/app/api/visualization.py
提供前端需要的可视化数据
"""

from fastapi import APIRouter, HTTPException
import pandas as pd
from datetime import datetime
from app.services.data_cache import GLOBAL_DF_CACHE, API_RESULT_CACHE
router = APIRouter()
DATA_FILE = 'data/raw/online_data.csv'
# ============================================================================
# 接口1: 总览数据
# ============================================================================
@router.get("/overview")
def get_overview():
    """
    获取总览数据
    返回：总用户数、总商户数、总购买行为数、总发券量、转化率 (CVR) 以及券核销率。
    """
    result = API_RESULT_CACHE.get('overview')
    if not result: raise HTTPException(status_code=503, detail="数据准备中")
    return result

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
    all_data = API_RESULT_CACHE.get('daily_trend',[])
    # 过滤
    filtered = all_data
    if start_date or end_date:
        filtered = [
            r for r in all_data
            if (not start_date or r['date'] >= start_date) and (not end_date or r['date'] <= end_date)
        ]
    return {
        "dates": [r['date'] for r in filtered],
        "purchases": [int(r['purchases']) for r in filtered],
        "coupons": [int(r['coupons']) for r in filtered]
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
    result = API_RESULT_CACHE.get('monthly_stats')
    if not result: raise HTTPException(status_code=503, detail="数据准备中")
    return result

# ============================================================================
# 接口4: 用户分层（RFM）
# ============================================================================
@router.get("/user-segmentation")
def get_user_segmentation(month: int = 4):
    """
    获取用户分层数据（RFM）
    获取基于 RFM 模型的用户分层数据（适合绘制饼图或漏斗图）。
    注意：此接口读取的是预先提取好的特征文件，而不是原始宽表。
    返回：不同层级用户数量
    """
    # RFM分层
    # 基于 Recency(最近一次消费间隔) 和 Frequency(消费频率) 进行分群
    # 这里的阈值 (30天, 10次, 90天) 是业务经验值，在模型调优时可动态调整
    '''
    # TODO
    测试可视化计算结果
    '''
    result = API_RESULT_CACHE.get('user_segmentation',{}).get(month)
    if not result: 
        raise HTTPException(status_code=404, detail="该月数据不存在或未准备好")
    return result

# ============================================================================
# 接口5: 转化漏斗
# ============================================================================
@router.get("/conversion-funnel")
def get_conversion_funnel(month: int = None, period: str = "all"):
    """
    获取转化漏斗数据
    返回：点击 → 领券 → 购买 各阶段人数
    month ∈ {4,5,6} 时按月切片，否则按 period (all/regular/promotion)
    """
    if month in (4, 5, 6):
        result = API_RESULT_CACHE.get('conversion_funnel_by_month', {}).get(month)
    else:
        result = API_RESULT_CACHE.get('conversion_funnel_by_period', {}).get(period) \
                 or API_RESULT_CACHE.get('conversion_funnel')
    if not result:
        raise HTTPException(status_code=503, detail="数据准备中")
    return result

# ============================================================================
# 接口6: 用户统计指标（UserAnalysis 页顶部卡片）
# ============================================================================
@router.get("/user-stats")
def get_user_stats(month: int = 4):
    """
    获取用户统计指标数据
    返回：总用户数、活跃用户数、平均购买频次、平均领券率等关键统计指标。
    """
    result = API_RESULT_CACHE.get('user_stats',{}).get(month)
    if not result: 
        raise HTTPException(status_code=404, detail=f"{month}月数据不存在或未准备好")
    return result

# ============================================================================
# 接口7: RFM 散点图数据
# ============================================================================
@router.get("/user-rfm")
def get_user_rfm(month: int = 4, sample_n: int = 2000):
    """
    获取用户 RFM 散点图数据
    返回：用户的 Recency、Frequency、Monetary 数据（适合绘制散点图）。
    注意：此接口读取的是预先提取好的特征文件，而不是原始宽表。
    参数：
    - month: 月份 (1-6)
    - sample_n: 采样数量(默认2000,避免前端渲染过慢)
    """
    # 优先从全局缓存获取 DataFrame，不再读硬盘
    features = GLOBAL_DF_CACHE.get("features", {}).get(month)
    if features is None:
        raise HTTPException(status_code=404, detail=f"内存中未找到 {month} 月特征数据"
        )
    required_cols = ['user_id', 'recency', 'frequency']
    for col in required_cols:
        if col not in features.columns:
            raise HTTPException(status_code=500, detail=f"特征文件缺少字段: {col}")

    if 'purchase_count' not in features.columns:
        features['purchase_count'] = features['frequency']
    # 在内存中直接采样，速度极快
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
# 接口8: 用户画像雷达图数据(动态读取内存 DataFrame)
# ============================================================================
@router.get("/user-profile")
def get_user_profile(month: int = 4):
    """
    获取用户画像雷达图数据
    返回：用户画像维度的平均值（适合绘制雷达图）
    """
    features = GLOBAL_DF_CACHE.get("features", {}).get(month)
    if features is None:
        raise HTTPException(status_code=404, detail=f"内存中未找到 {month} 月特征数据")
    dim_map = {
        'purchase_freq':  'frequency',
        'active_days':    'lifetime',          # 特征文件实际列名
        'coupon_rate':    'coupon_use_rate',   # 实际列名（无 coupon_receive_rate）
        'cvr':            'purchase_rate',     # 实际列名（无 cvr）
        'merchant_div':   'merchant_count',
        'recency_score':  'recency',
    }
    available = {k: v for k, v in dim_map.items() if v in features.columns}

    high_mask = (features['recency'] <= 30) & (features['frequency'] >= 10) \
        if 'recency' in features.columns and 'frequency' in features.columns \
        else pd.Series([False] * len(features))
    normal_mask = ~high_mask

    def normalize_col(series, invert=False):
        # 使用百分位排名归一化（rank-based），避免极值压缩分布
        s = series.astype(float)
        if s.nunique() <= 1:
            return pd.Series([50.0] * len(s), index=s.index)
        norm = s.rank(method='average', pct=True) * 100
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
    result = API_RESULT_CACHE.get('behavior_heatmap', {}).get(month)
    if not result:
        # 如果缓存没命中（比如请求了不支持的月份），返回空矩阵防止前端报错
        return {"matrix": [], "max_value": 0}
    return result

# ============================================================================
# 接口10: 行为路径桑基图
# ============================================================================
@router.get("/behavior-sankey")
def get_behavior_sankey(month: int = 4, period: str = "all"):
    """
    获取用户行为路径桑基图数据
    节点：点击用户 / 领券用户 / 仅购买用户 / 券+购买 / 未转化
    """
    # month 参数优先：4/5/6 走按月缓存；否则按 period (all/regular/promotion)
    if month in (4, 5, 6):
        result = API_RESULT_CACHE.get('behavior_sankey_by_month', {}).get(month)
    else:
        result = API_RESULT_CACHE.get('behavior_sankey', {}).get(period)
    if not result:
        raise HTTPException(status_code=404, detail="该时段的桑基图数据未就绪")
    return result


# ============================================================================
# 接口11: 不同用户群体转化率对比
# ============================================================================

@router.get("/group-conversion")
def get_group_conversion(month: int = 4):
    """
    获取不同用户群体的转化率对比（高价值/重要挽留/新用户/流失用户/其他）
    """
    result = API_RESULT_CACHE.get('group_conversion', {}).get(month)
    if not result:
        raise HTTPException(status_code=404, detail=f"未找到 {month} 月的分群转化率数据")
    return result


# ============================================================================
# 接口12: 平销期 vs 促销期对比摘要
# ============================================================================

@router.get("/comparison-summary")
def get_comparison_summary():
    """
    获取平销期(1-4月) vs 促销期(5-6月)核心指标对比
    """
    # 因为这个接口较少被高频刷新，且逻辑复杂，暂留兜底读取逻辑。
    # 如果你后续在 data_cache.py 中也把它存进去了，这里就会优先走缓存。
    cached_result = API_RESULT_CACHE.get('comparison_summary')
    if cached_result:
        return cached_result
        
    try:
        df = pd.read_csv(DATA_FILE)
        df.columns = df.columns.str.lower()
        df['date'] = pd.to_datetime(df['date'],format='%Y%m%d',errors='coerce')
        df['date_received'] = pd.to_datetime(df['date_received'],format='%Y%m%d', errors='coerce')
        df['month'] = df['date'].dt.month
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"数据加载失败: {str(e)}")

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

        # 核销率：使用优惠券购买数 / 领券数
        coupon_used = int(((pdf['date'].notna()) & (pdf['coupon_id'].notna())).sum())
        redemption_rate = round(coupon_used / coupons * 100, 2) if coupons > 0 else 0

        # 复购率：购买 ≥2 次的用户占活跃用户比例
        buyers = pdf[pdf['date'].notna()]
        if len(buyers) > 0 and active_users > 0:
            user_purchase_counts = buyers.groupby('user_id').size()
            repeat_users = int((user_purchase_counts >= 2).sum())
            repurchase_rate = round(repeat_users / active_users * 100, 2)
        else:
            repurchase_rate = 0

        return {
            "cvr": cvr,
            "coupon_rate": coupon_rate,
            "daily_purchases": int(daily_purchases),
            "active_users": active_users,
            "redemption_rate": redemption_rate,
            "repurchase_rate": repurchase_rate,
        }

    regular_df   = df[df['month'] <= 4]
    promotion_df = df[df['month'] >= 5]

    regular   = period_stats(regular_df)
    promotion = period_stats(promotion_df)

    changes = {k: round(promotion[k] - regular[k], 2) for k in regular}

    # 雷达图维度顺序（与前端 indicator 对齐）：转化率 / 购买量 / 领券率 / 活跃用户 / 复购率 / 核销率
    radar_keys = ['cvr', 'daily_purchases', 'coupon_rate', 'active_users', 'repurchase_rate', 'redemption_rate']

    # 每一维以"两期最大值 * 1.25"为上限，使较大方落在 80 附近，两条折线都有可读空间
    caps = {}
    for k in radar_keys:
        cap = max(regular.get(k, 0), promotion.get(k, 0)) * 1.25
        caps[k] = cap if cap > 0 else 1

    def to_radar(stats):
        return [round(stats.get(k, 0) / caps[k] * 100, 1) for k in radar_keys]

    return {
        "regular": regular,
        "promotion": promotion,
        "changes": changes,
        "radar": {
            "regular":   to_radar(regular),
            "promotion": to_radar(promotion)
        }
    }

# ============================================================================
# 接口17: 分时段CVR
# ============================================================================
@router.get("/hourly-cvr")
def get_hourly_cvr():
    """获取每小时点击/购买/CVR数据"""
    result = API_RESULT_CACHE.get('hourly_cvr')
    if result is None:
        raise HTTPException(status_code=503, detail="数据准备中")
    return {"data": result}

# ============================================================================
# 接口18: 月度用户留存率
# ============================================================================
@router.get("/monthly-retention")
def get_monthly_retention():
    """获取4→5月、5→6月的用户留存/流失/新增数据"""
    result = API_RESULT_CACHE.get('monthly_retention')
    if not result:
        raise HTTPException(status_code=503, detail="数据准备中")
    return {"data": result}

# ============================================================================
# 接口16: 用户特征分布（活跃天数 / 商户多样性）
# ============================================================================
@router.get("/user-feature-dist")
def get_user_feature_dist(month: int = 4):
    """获取活跃天数 & 商户多样性的分布直方图数据"""
    result = API_RESULT_CACHE.get('user_feature_dist', {}).get(month)
    if not result:
        raise HTTPException(status_code=404, detail=f"{month}月分布数据未就绪")
    return result

# ============================================================================
# 接口14: 周内购买分布
# ============================================================================
@router.get("/weekday-distribution")
def get_weekday_distribution():
    """获取周一到周日的购买量分布"""
    result = API_RESULT_CACHE.get('weekday_distribution')
    if not result:
        raise HTTPException(status_code=503, detail="数据准备中")
    return {"data": result}

# ============================================================================
# 接口15: 总览大屏商户TOP10排名
# ============================================================================
@router.get("/merchant-ranking")
def get_merchant_ranking():
    """获取购买量TOP10商户（预计算缓存版）"""
    result = API_RESULT_CACHE.get('merchant_ranking')
    if not result:
        raise HTTPException(status_code=503, detail="数据准备中")
    return result

# ============================================================================
# 接口13：用户生命周期分布
# ============================================================================
@router.get("/lifecycle")
def get_lifecycle(month: int = 4):
    """获取用户生命周期分布数据"""
    # 结合 RFM 模型映射生命周期
    result = API_RESULT_CACHE.get('user_segmentation', {}).get(month)
    if not result:
        return [{"name": "暂无数据", "value": 0}]
    
    segments = {item['name']: item['value'] for item in result['segments']}
    
    return [
        {"name": "引入期 (新用户)", "value": segments.get("新用户", 0)},
        {"name": "成长期 (普通用户)", "value": segments.get("普通用户", 1500)}, # 设定一个基准值
        {"name": "成熟期 (高价值用户)", "value": segments.get("高价值用户", 0)},
        {"name": "休眠期 (重要挽留)", "value": segments.get("重要挽留用户", 0)},
        {"name": "流失期 (流失用户)", "value": segments.get("流失用户", 0)}
    ]