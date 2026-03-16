"""
后端主程序
文件: main.py
启动命令: uvicorn main:app --app-dir backend --reload --host 127.0.0.1 --port 8000
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# 创建FastAPI应用
app = FastAPI(
    title="电商用户行为分析与预测系统",
    description="基于O2O数据集的用户复购预测API",
    version="1.0.0"
)

# 配置CORS（允许前端跨域访问）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # 前端地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# 健康检查接口
# ============================================================================

@app.get("/")
def read_root():
    """根路径 - 健康检查"""
    return {
        "status": "ok",
        "message": "电商用户行为分析系统API",
        "version": "1.0.0"
    }

@app.get("/health")
def health_check():
    """健康检查接口"""
    return {"status": "healthy"}

# ============================================================================
# 导入路由模块
# ============================================================================

from app.api import visualization, prediction, statistics

# 注册路由
app.include_router(
    visualization.router,
    prefix="/api/v1/visualization",
    tags=["可视化"]
)

app.include_router(
    prediction.router,
    prefix="/api/v1/prediction",
    tags=["预测"]
)

app.include_router(
    statistics.router,
    prefix="/api/v1/statistics",
    tags=["统计"]
)

# ============================================================================
# 启动配置
# ============================================================================

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True  # 开发模式：代码修改自动重启
    )
