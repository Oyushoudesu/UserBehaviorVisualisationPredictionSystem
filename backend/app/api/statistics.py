"""
统计分析API
文件: backend/app/api/statistics.py

提供用户/商户统计数据
"""

from fastapi import APIRouter, HTTPException
import pandas as pd

router = APIRouter()

# ============================================================================
# 接口1: 用户统计信息
# ============================================================================

@router.get("/user/{user_id}")
def get_user_stats(user_id: str):
    """
    获取单个用户的统计信息
    
    参数：
    - user_id: 用户ID
    
    返回：用户详细统计数据
    """
    try:
        # 加载用户特征数据
        # 优化数据访问，直接引用全局内存中的DataFrame
        features = GLOBAL_DATA.get("features_m4")
        if features is None:
            raise HTTPException(status_code=500, detail="特征数据未加载或加载失败")
        
        # 查找用户
        user_data = features[features['user_id'] == user_id]
        
        if len(user_data) == 0:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        user_info = user_data.iloc[0].to_dict()
        
        # 删除user_id字段
        user_info.pop('user_id', None)
        
        return {
            "user_id": user_id,
            "stats": user_info
        }
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="特征数据未找到")

# ============================================================================
# 接口2: Top用户排行
# ============================================================================

@router.get("/top-users")
def get_top_users(metric: str = "total_purchases", top_n: int = 10):
    """
    获取Top用户排行榜
    
    参数：
    - metric: 排序指标（total_purchases, total_coupons等）
    - top_n: 返回Top N
    
    返回：Top用户列表
    """
    try:
        features = GLOBAL_DATA.get("features_m4")
        if features is None:
            raise HTTPException(status_code=500, detail="特征数据未加载或加载失败")
        
        # 检查指标是否存在
        if metric not in features.columns:
            raise HTTPException(
                status_code=400, 
                detail=f"指标'{metric}'不存在"
            )
        
        # 排序
        top_users = features.nlargest(top_n, metric)[
            ['user_id', metric, 'total_purchases', 'merchant_count']
        ]
        
        return {
            "metric": metric,
            "top_users": top_users.to_dict('records')
        }
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="特征数据未找到")

# ============================================================================
# 接口3: 商户统计
# ============================================================================

@router.get("/merchant-ranking")
def get_merchant_ranking(top_n: int = 20):
    """
    获取商户排行榜
    
    参数：
    - top_n: 返回Top N商户
    
    返回：商户销量排行
    """
    try:
        # 加载原始数据
        df = GLOBAL_DATA.get("raw_data")
        if df is None:
            raise HTTPException(status_code=500, detail="数据未加载或加载失败")
        df = df.copy()
        df.columns = df.columns.str.lower()
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        
        # 统计每个商户的销量
        merchant_sales = df[df['date'].notna()].groupby('merchant_id').agg({
            'user_id': ['count', 'nunique']
        }).reset_index()
        
        merchant_sales.columns = ['merchant_id', 'sales', 'unique_users']
        
        # 排序
        top_merchants = merchant_sales.nlargest(top_n, 'sales')
        
        return {
            "merchants": top_merchants.to_dict('records')
        }
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="数据文件未找到")

# ============================================================================
# 接口4: 复购率统计
# ============================================================================

@router.get("/repurchase-rate")
def get_repurchase_rate():
    """
    获取各月复购率统计
    
    返回：4/5/6月的复购率
    """
    try:
        df = GLOBAL_DATA.get("raw_data")
        if df is None:
            raise HTTPException(status_code=500, detail="数据未加载或加载失败")
        df = df.copy()
        df.columns = df.columns.str.lower()
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df['month'] = df['date'].dt.month
        
        # 1-3月活跃用户
        train_users = df[
            (df['month'].isin([1, 2, 3])) & (df['date'].notna())
        ]['user_id'].unique()
        
        # 各月复购率
        repurchase_rates = []
        for month in [4, 5, 6]:
            month_buyers = df[
                (df['month'] == month) & (df['date'].notna())
            ]['user_id'].unique()
            
            repurchase_users = set(train_users) & set(month_buyers)
            rate = len(repurchase_users) / len(train_users) * 100
            
            repurchase_rates.append({
                "month": month,
                "rate": round(rate, 2),
                "repurchase_users": len(repurchase_users),
                "total_users": len(train_users)
            })
        
        return {"data": repurchase_rates}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="数据文件未找到")
