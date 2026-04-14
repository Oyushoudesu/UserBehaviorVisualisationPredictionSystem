"""
预测API
文件: backend/app/api/prediction.py

提供滑动窗口模型预测功能
支持两种预测模式：
  - ensemble: 加权集成（0.67 * XGBoost + 0.33 * LightGBM）
  - stacking: Stacking元学习（XGB+LGB → LogisticRegression）
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
import pandas as pd
import pickle
import numpy as np
import os
from app.services.data_cache import GLOBAL_DF_CACHE

router = APIRouter()

# 项目根目录（prediction.py 位于 backend/app/api/，向上三级）
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

# ============================================================================
# 请求/响应模型
# ============================================================================
class PredictionRequest(BaseModel):
    """预测请求"""
    user_ids: List[str]
    pred_mode: str = "ensemble"  # "ensemble"（加权集成）或 "stacking"（元学习）

class PredictionResponse(BaseModel):
    """预测响应"""
    user_id: str
    probability: float
    prediction: int
    risk_level: str

# ============================================================================
# 加载模型和元数据（启动时加载）
# ============================================================================
sliding_models = {}
model_meta = {}

def load_models():
    """加载滑动窗口训练好的模型及元数据"""
    try:
        with open(os.path.join(PROJECT_ROOT, 'ml_models/xgb_sliding.pkl'), 'rb') as f:
            sliding_models["xgb"] = pickle.load(f)
        with open(os.path.join(PROJECT_ROOT, 'ml_models/lgb_sliding.pkl'), 'rb') as f:
            sliding_models["lgb"] = pickle.load(f)
        with open(os.path.join(PROJECT_ROOT, 'ml_models/stacking_sliding.pkl'), 'rb') as f:
            sliding_models["stacking"] = pickle.load(f)
        with open(os.path.join(PROJECT_ROOT, 'ml_models/model_metadata_v2.pkl'), 'rb') as f:
            meta = pickle.load(f)
            model_meta["feature_cols"]      = meta["feature_cols"]
            model_meta["best_weight_xgb"]   = meta["best_weight_xgb"]     # 0.67
            model_meta["optimal_threshold"] = meta["optimal_threshold"]   # 0.4724
            model_meta["test_auc_ensemble"] = meta["test_auc_ensemble"]
            model_meta["test_auc_stacking"] = meta["test_auc_stacking"]
            model_meta["test_f1_youden"]    = meta["test_f1_youden"]
        print("滑动窗口模型加载成功")
    except Exception as e:
        print(f"模型加载失败: {e}")

load_models()

# ============================================================================
# 内部工具函数
# ============================================================================
def _get_pred_df():
    """从缓存获取预测数据（test_618.csv）"""
    df = GLOBAL_DF_CACHE.get("prediction_data")
    if df is None:
        raise HTTPException(status_code=503, detail="预测数据未加载，请检查 test_618.csv 是否存在")
    return df

def _predict_proba(X: pd.DataFrame, pred_mode: str) -> np.ndarray:
    """根据预测模式返回复购概率"""
    if pred_mode == "stacking":
        return sliding_models["stacking"].predict_proba(X)[:, 1]
    # 默认 ensemble 加权集成
    w = model_meta["best_weight_xgb"]
    prob_xgb = sliding_models["xgb"].predict_proba(X)[:, 1]
    prob_lgb = sliding_models["lgb"].predict_proba(X)[:, 1]
    return w * prob_xgb + (1 - w) * prob_lgb

def _risk_level(prob: float) -> str:
    if prob >= 0.7:
        return "高"
    elif prob >= 0.4:
        return "中"
    return "低"

# ============================================================================
# 接口1: 用户复购预测
# ============================================================================

@router.post("/repurchase", response_model=List[PredictionResponse])
def predict_repurchase(request: PredictionRequest):
    """
    用户复购预测

    参数：
    - user_ids: 用户ID列表
    - pred_mode: 预测模式（"ensemble" 加权集成 / "stacking" Stacking元学习）

    返回：每个用户的复购概率和预测结果
    """
    if request.pred_mode not in ("ensemble", "stacking"):
        raise HTTPException(status_code=400, detail="pred_mode 必须是 'ensemble' 或 'stacking'")

    if not sliding_models:
        raise HTTPException(status_code=503, detail="模型未加载，请稍后重试")

    features_df = _get_pred_df()
    features_df = features_df.copy()
    features_df["user_id"] = features_df["user_id"].astype(str)
    user_features = features_df[features_df["user_id"].isin(request.user_ids)]

    if len(user_features) == 0:
        raise HTTPException(status_code=404, detail="未找到指定用户的特征数据")

    feature_cols = model_meta["feature_cols"]
    X = user_features[feature_cols]
    threshold = model_meta["optimal_threshold"]

    prob_arr = _predict_proba(X, request.pred_mode)

    results = []
    for i, user_id in enumerate(user_features["user_id"]):
        prob = float(prob_arr[i])
        results.append(PredictionResponse(
            user_id=str(user_id),
            probability=round(prob, 4),
            prediction=int(prob >= threshold),
            risk_level=_risk_level(prob)
        ))
    return results

# ============================================================================
# 接口2: 批量预测统计（在全量预测数据上评估）
# ============================================================================

@router.get("/batch-stats")
def get_batch_prediction_stats(pred_mode: str = "ensemble"):
    """
    获取批量预测统计（在 test_618.csv 上运行并对比真实标签）

    参数：
    - pred_mode: 预测模式（"ensemble" / "stacking"）

    返回：AUC、精确率、召回率、F1 及分布统计
    """
    if pred_mode not in ("ensemble", "stacking"):
        raise HTTPException(status_code=400, detail="pred_mode 必须是 'ensemble' 或 'stacking'")

    features_df = _get_pred_df()

    if "label" not in features_df.columns:
        raise HTTPException(status_code=500, detail="预测数据中缺少真实 label 列，无法计算评估指标")

    feature_cols = model_meta["feature_cols"]
    X = features_df[feature_cols]
    y_true = features_df["label"]
    threshold = model_meta["optimal_threshold"]

    prob = _predict_proba(X, pred_mode)
    pred = (prob >= threshold).astype(int)

    from sklearn.metrics import roc_auc_score, precision_score, recall_score, f1_score

    return {
        "total_users":        len(features_df),
        "predicted_positive": int(pred.sum()),
        "predicted_negative": int((pred == 0).sum()),
        "auc":       round(float(roc_auc_score(y_true, prob)), 4),
        "precision": round(float(precision_score(y_true, pred, zero_division=0)), 4),
        "recall":    round(float(recall_score(y_true, pred, zero_division=0)), 4),
        "f1_score":  round(float(f1_score(y_true, pred, zero_division=0)), 4),
        "threshold": round(threshold, 4),
        "pred_mode": pred_mode
    }

# ============================================================================
# 接口3: 特征重要性（XGBoost）
# ============================================================================

@router.get("/feature-importance")
def get_feature_importance(pred_mode: str = "ensemble", top_n: int = 20):
    """
    获取特征重要性（始终基于 XGBoost 模型）

    参数：
    - pred_mode: 预测模式（仅用于响应标注，特征重要性固定取 XGB）
    - top_n: 返回 Top N 个特征

    返回：特征重要性排序
    """
    if not sliding_models:
        raise HTTPException(status_code=503, detail="模型未加载")

    xgb_model = sliding_models["xgb"]
    feature_cols = model_meta["feature_cols"]
    importance   = xgb_model.feature_importances_

    importance_df = (
        pd.DataFrame({"feature": feature_cols, "importance": importance})
        .sort_values("importance", ascending=False)
        .head(top_n)
    )

    return {
        "features":   importance_df["feature"].tolist(),
        "importance": importance_df["importance"].tolist()
    }
