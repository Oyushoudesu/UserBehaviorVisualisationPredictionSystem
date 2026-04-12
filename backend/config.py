# backend/config.py
import os

# 数据库连接 —— 把 your_password 改成你 MySQL 的真实密码
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://root:123456@localhost:3306/ecommerce_behavior"
)

# JWT配置
JWT_SECRET_KEY = os.getenv(
    "JWT_SECRET_KEY",
    "ecommerce-analysis-secret-key-change-in-production"
)