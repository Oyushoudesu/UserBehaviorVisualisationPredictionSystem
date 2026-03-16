"""
预测API
文件: backend/app/api/prediction.py

提供模型预测功能
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
import pandas as pd
import pickle
import numpy as np

router = APIRouter()

# ============================================================================
# 请求/响应模型
# ============================================================================

class PredictionRequest(BaseModel):
    """预测请求"""
    user_ids: List[str]
    model_type: str = "regular"  # "regular" or "promotion"

class PredictionResponse(BaseModel):
    """预测响应"""
    user_id: str
    probability: float
    prediction: int
    risk_level: str

# ============================================================================
# 加载模型（启动时加载）
# ============================================================================

models = {
    "regular": {},
    "promotion": {}
}

def load_models():
    """加载训练好的模型"""
    try:
        # 加载平销期模型
        with open('ml_models/regular_period/xgb_model.pkl', 'rb') as f:
            models["regular"]["xgb"] = pickle.load(f)
        with open('ml_models/regular_period/lgb_model.pkl', 'rb') as f:
            models["regular"]["lgb"] = pickle.load(f)
        
        # 加载促销期模型
        with open('ml_models/promotion_period/xgb_model.pkl', 'rb') as f:
            models["promotion"]["xgb"] = pickle.load(f)
        with open('ml_models/promotion_period/lgb_model.pkl', 'rb') as f:
            models["promotion"]["lgb"] = pickle.load(f)
        
        print("模型加载成功")
    except Exception as e:
        print(f"模型加载失败: {e}")

# 应用启动时加载模型
load_models()

# ============================================================================
# 接口1: 用户复购预测
# ============================================================================

@router.post("/repurchase", response_model=List[PredictionResponse])
def predict_repurchase(request: PredictionRequest):
    """
    用户复购预测
    
    参数：
    - user_ids: 用户ID列表
    - model_type: 模型类型 ("regular" 平销期 / "promotion" 促销期)
    
    返回：每个用户的复购概率和预测结果
    """
    # 验证模型类型
    if request.model_type not in ["regular", "promotion"]:
        raise HTTPException(
            status_code=400, 
            detail="model_type必须是'regular'或'promotion'"
        )
    
    # 检查模型是否加载
    if not models[request.model_type]:
        raise HTTPException(
            status_code=503, 
            detail="模型未加载，请稍后重试"
        )
    
    # 加载特征数据
    try:
        # 根据模型类型选择特征数据
        if request.model_type == "regular":
            features_df = pd.read_csv('data/features/user_features_month4.csv')
        else:
            features_df = pd.read_csv('data/features/user_features_month6.csv')
    except Exception as e:
        raise HTTPException(
            status_code=404, 
            detail=f"特征数据加载失败: {str(e)}"
        )
    # 筛选指定用户
    features_df['user_id'] = features_df['user_id'].astype(str)
    user_features = features_df[features_df['user_id'].isin(request.user_ids)]
    if len(user_features) == 0:
        raise HTTPException(
            status_code=404, 
            detail="未找到指定用户的特征数据"
        )
    
    # 准备特征
    feature_cols = [col for col in user_features.columns 
                   if col not in ['user_id', 'label']]
    X = user_features[feature_cols]
    
    # 模型预测
    xgb_model = models[request.model_type]["xgb"]
    lgb_model = models[request.model_type]["lgb"]
    
    # 融合预测
    prob_xgb = xgb_model.predict_proba(X)[:, 1]
    prob_lgb = lgb_model.predict_proba(X)[:, 1]
    prob_ensemble = (prob_xgb + prob_lgb) / 2
    
    # 生成预测结果
    results = []
    for i, user_id in enumerate(user_features['user_id']):
        prob = float(prob_ensemble[i])
        pred = 1 if prob >= 0.5 else 0
        
        # 风险等级
        if prob >= 0.7:
            risk_level = "高"
        elif prob >= 0.4:
            risk_level = "中"
        else:
            risk_level = "低"
        
        results.append(PredictionResponse(
            user_id=str(user_id),
            probability=round(prob, 4),
            prediction=pred,
            risk_level=risk_level
        ))
    
    return results

# ============================================================================
# 接口2: 批量预测统计
# ============================================================================

@router.get("/batch-stats")
def get_batch_prediction_stats(model_type: str = "regular"):
    """
    获取批量预测统计
    
    参数：
    - model_type: 模型类型
    
    返回：预测结果的统计分布
    """
    # 加载特征数据
    # 优化数据访问，直接引用全局内存中的DataFrame
    try:
        if model_type == "regular":
            features_df = GLOBAL_DATA.get("features_m5")
        else:
            features_df = GLOBAL_DATA.get("features_m6")
        if features_df is None:
            raise HTTPException(status_code=500, detail="特征数据未加载或加载失败")
    except:
        raise HTTPException(status_code=404, detail="特征数据未找到")
    
    # 准备特征
    feature_cols = [col for col in features_df.columns 
                   if col not in ['user_id', 'label']]
    X = features_df[feature_cols]
    y_true = features_df['label']
    
    # 预测
    xgb_model = models[model_type]["xgb"]
    lgb_model = models[model_type]["lgb"]
    
    prob_xgb = xgb_model.predict_proba(X)[:, 1]
    prob_lgb = lgb_model.predict_proba(X)[:, 1]
    prob = (prob_xgb + prob_lgb) / 2
    
    # 统计
    pred = (prob >= 0.5).astype(int)
    
    from sklearn.metrics import roc_auc_score, precision_score, recall_score, f1_score
    
    return {
        "total_users": len(features_df),
        "predicted_positive": int(pred.sum()),
        "predicted_negative": int((pred == 0).sum()),
        "auc": round(float(roc_auc_score(y_true, prob)), 4),
        "precision": round(float(precision_score(y_true, pred)), 4),
        "recall": round(float(recall_score(y_true, pred)), 4),
        "f1_score": round(float(f1_score(y_true, pred)), 4)
    }

# ============================================================================
# 接口3: 特征重要性
# ============================================================================

@router.get("/feature-importance")
def get_feature_importance(model_type: str = "regular", top_n: int = 20):
    """
    获取特征重要性
    
    参数：
    - model_type: 模型类型
    - top_n: 返回Top N个特征
    
    返回：特征重要性排序
    """
    if model_type not in models or not models[model_type]:
        raise HTTPException(status_code=503, detail="模型未加载")
    
    # 获取XGBoost模型的特征重要性
    xgb_model = models[model_type]["xgb"]
    
    # 获取特征名
    try:
        features_df = GLOBAL_DATA.get("features_m4")
        if features_df is None:
            raise HTTPException(status_code=500, detail="特征数据未加载或加载失败")
        feature_cols = [col for col in features_df.columns 
                       if col not in ['user_id', 'label']]
    except:
        raise HTTPException(status_code=404, detail="特征数据未找到")
    
    # 特征重要性
    importance = xgb_model.feature_importances_
    
    # 创建DataFrame并排序
    importance_df = pd.DataFrame({
        'feature': feature_cols,
        'importance': importance
    }).sort_values('importance', ascending=False).head(top_n)
    
    return {
        "features": importance_df['feature'].tolist(),
        "importance": importance_df['importance'].tolist()
    }
