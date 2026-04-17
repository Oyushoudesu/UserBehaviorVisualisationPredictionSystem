
# 电商用户行为分析与预测系统

基于阿里巴巴O2O优惠券数据集的用户行为可视化分析与智能预测平台

## 📊 项目简介

本系统是一个面向电商场景的用户行为分析与预测平台，通过对用户点击、领券、购买等行为数据进行深度挖掘，提供全方位的数据可视化展示和智能预测功能。系统特别关注平销期与促销期（618）用户行为模式的差异分析。

### 核心功能

- 📈 **多维度数据可视化** - 用户行为趋势、转化漏斗、热力图、用户画像等
- 🤖 **智能预测模型** - 用户复购预测、优惠券核销预测（XGBoost + LightGBM 融合/Stacking集成）
- 🔄 **双场景对比** - 平销期 vs 促销期行为模式对比分析
- 🔐 **用户认证** - JWT登录注册、个人信息管理
- 💡 **实时交互分析** - 支持多维度筛选和钻取

-----

## 🗂️ 项目结构

```
UserBehaviorVisualisationPredictionSystem/
├── backend/                      # 后端服务（FastAPI）
│   ├── app/
│   │   ├── api/                  # API路由
│   │   │   ├── visualization.py  # 可视化数据接口
│   │   │   ├── prediction.py     # 预测接口
│   │   │   ├── statistics.py     # 统计分析接口
│   │   │   └── auth.py           # 认证接口
│   │   └── services/             # 业务逻辑
│   │       ├── data_cache.py     # 数据缓存（启动时预加载）
│   │       └── ...
│   ├── config.py                 # 数据库/JWT配置
│   ├── main.py                   # FastAPI入口
│   └── requirements.txt          # Python依赖
│
├── frontend/                     # 前端应用（Vue 3 + Vite）
│   ├── src/
│   │   ├── views/                # 页面组件
│   │   │   ├── Dashboard.vue     # 仪表盘总览
│   │   │   ├── UserAnalysis.vue  # 用户分析
│   │   │   ├── BehaviorFlow.vue  # 行为流分析
│   │   │   ├── Prediction.vue    # 智能预测
│   │   │   ├── Comparison.vue    # 平销期vs促销期对比
│   │   │   ├── Login.vue         # 登录
│   │   │   ├── Register.vue      # 注册
│   │   │   └── Profile.vue       # 个人信息
│   │   ├── components/           # 复用组件
│   │   ├── api/                  # Axios封装（含JWT拦截器）
│   │   ├── router/               # 路由配置（含路由守卫）
│   │   ├── store/                # Pinia状态管理
│   │   └── composables/          # Vue组合式函数
│   ├── package.json
│   └── vite.config.js
│
├── data/
│   ├── raw/                      # 原始数据（online_data.csv，约461MB）
│   └── features/                 # 预处理特征文件（月度滑窗CSV）
│
├── ml_models/                    # 训练好的模型
│   ├── xgb_sliding.pkl           # XGBoost模型
│   ├── lgb_sliding.pkl           # LightGBM模型
│   ├── stacking_sliding.pkl      # Stacking集成模型
│   ├── model_metadata_v2.pkl     # 模型元数据（特征列、权重、阈值）
│   ├── regular_period/           # 平销期专用模型
│   └── promotion_period/         # 促销期专用模型（含618）
│
├── notebook/                     # Jupyter notebooks（EDA、特征工程、模型训练）
├── docs/                         # 文档
└── README.md
```

-----

## 📅 数据集说明

### 数据来源

阿里巴巴O2O优惠券使用预测数据集（Online部分）

### 数据时间跨度

2016-01-01 至 2016-06-30（共6个月）

### 数据集原始字段解析

- **User_id** - 用户ID
- **Merchant_id** - 商户ID
- **Action** - 0点击，1购买，2领取优惠券
- **Coupon_id** - 优惠券ID：null表示无优惠券消费；"fixed"表示限时低价活动
- **Discount_rate** - 优惠率：x∈[0,1]代表折扣率；x:y表示满x减y；"fixed"表示低价限时优惠
- **Date_received** - 领取优惠券日期
- **Date** - 消费日期：Date=null & Coupon_id≠null 表示领券未使用；Date≠null & Coupon_id=null 表示普通消费；Date≠null & Coupon_id≠null 表示用券消费

### 数据规模

- 总行为记录：11,429,826 条
- 活跃用户数：544,307 人
- 整体CVR：14.00%

### 时间划分策略

#### 模型1：平销期模型

```
训练集：2016-01-01 ~ 2016-03-31（3个月）
验证集：2016-04-01 ~ 2016-04-30（1个月）
测试集：2016-05-01 ~ 2016-05-31（1个月）
```

#### 模型2：促销期模型（含618）

```
训练集：2016-01-01 ~ 2016-05-31（5个月）
验证集：2016-05-15 ~ 2016-05-31（半个月）
测试集：2016-06-01 ~ 2016-06-30（1个月，含618）
```

-----

## 🛠️ 技术栈

### 后端技术

|技术|版本|用途|
|---|---|---|
|Python|3.9+|核心语言|
|FastAPI|0.104+|Web框架|
|MySQL|8.0+|关系数据库|
|Redis|7.0+|缓存数据库（可选）|
|Pandas|2.0+|数据处理|
|Scikit-learn|1.3+|机器学习|
|XGBoost|2.0+|梯度提升模型|
|LightGBM|4.0+|轻量级梯度提升|
|SQLAlchemy|2.0+|ORM框架|
|python-jose|3.3+|JWT认证|

### 前端技术

|技术|版本|用途|
|---|---|---|
|Vue|3.5.25|前端框架|
|Vite|7.3.1|构建工具|
|Element Plus|2.13.3|UI组件库|
|ECharts|6.0.0|可视化库|
|Axios|1.13.6|HTTP客户端|
|Pinia|3.0.4|状态管理|
|Vue Router|5.0.3|路由管理|

-----

## 🎯 核心功能模块

### 1. 数据可视化模块

#### 总览仪表盘

- 核心指标卡片（总用户数、总商户数、总购买量、总领券量、CVR、核销率）
- 用户行为日趋势图（时间序列）
- Top商户排行

#### 用户分析

- **RFM用户分层**：最近购买时间、购买频率三维散点图分析
- **用户生命周期分析**：新用户、活跃用户、沉睡用户、流失用户分布
- **用户画像雷达图**：多维度用户特征展示
- **用户行为时段热力图**：24小时×7天行为分布

#### 行为流分析

- **转化漏斗**：点击 → 领券 → 购买
- **行为路径桑基图**：用户行为流向可视化
- **不同用户群体转化对比**

#### 商户分析

- 商户热度排行榜
- 商户转化率对比
- 商户用户覆盖分析

#### 平销期 vs 促销期对比

- 用户行为模式差异
- 转化率变化趋势
- 用户活跃度对比
- 618促销效果分析

### 2. 智能预测模块

#### 预测任务1：用户复购预测

- **目标**：预测用户在未来30天内是否会再次购买
- **应用场景**：精准营销、用户召回
- **模型**：XGBoost + LightGBM 加权融合（0.67:0.33）或 Stacking集成（元学习器：逻辑回归）
- **评估指标**：AUC、精确率、召回率、F1-Score

#### 预测任务2：优惠券核销预测

- **目标**：预测用户领券后是否会使用
- **应用场景**：优惠券发放策略优化
- **模型**：LightGBM
- **评估指标**：AUC、核销率预测准确度

#### 预测功能

- 单用户预测演示
- 批量预测
- 预测结果可视化
- 特征重要性分析

### 3. 用户认证模块

- JWT Token登录/注册
- 路由守卫（未登录自动跳转）
- 个人信息查看与修改
- 安全退出

### 4. 数据管理模块

- 启动时自动加载原始数据与特征文件（内存缓存）
- 特征工程自动化
- 数据质量监控

-----

## 🚀 快速开始

### 环境要求

- Python 3.9+
- Node.js 18+
- MySQL 8.0+
- Redis 7.0+（可选）

### 后端部署

```bash
# 1. 进入后端目录
cd backend

# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置数据库
# 编辑 config.py 文件，设置MySQL连接信息和JWT密钥

# 5. 启动服务
python main.py
```

### 前端部署

```bash
# 1. 进入前端目录
cd frontend

# 2. 安装依赖
npm install

# 3. 启动开发服务器
npm run dev

# 4. 构建生产版本
npm run build
```

### 访问系统

- 前端页面：http://localhost:5173
- 后端API文档：http://localhost:8000/docs

-----

## 📊 特征工程

### 用户维度特征（50+）

#### 基础行为统计

- 点击/领券/购买次数（7天/14天/30天滑动窗口）
- 活跃天数、行为总量

#### 转化特征

- 点击转化率（CTR）、领券率、券核销率、整体CVR

#### 活跃度特征

- 用户新鲜度（Recency）、用户频率（Frequency）
- 平均行为间隔、行为间隔方差、生命周期长度

#### 行为模式特征

- 最常活跃时段、工作日/周末行为占比、最近行为类型

### 商户维度特征（20+）

- 商户热度指标、商户转化率、商户用户覆盖数、商户排名

### 交互特征（15+）

- 用户-商户历史交互次数、用户-商户转化率、是否回头客、最近交互距今天数

### 时间特征（10+）

- 星期几、是否周末、是否月初/月末、距离促销日天数

### 促销敏感度特征（8+）

- 用户领券偏好、券弃用率、领券到购买平均天数

**总计：100+ 特征维度**

-----

## 📈 模型性能

### 平销期模型

#### 用户复购预测

|指标|训练集|验证集|测试集|
|---|---|---|---|
|AUC|0.85|0.82|0.81|
|精确率|0.78|0.75|0.74|
|召回率|0.72|0.69|0.68|
|F1-Score|0.75|0.72|0.71|

#### 优惠券核销预测

|指标|训练集|验证集|测试集|
|---|---|---|---|
|AUC|0.83|0.80|0.79|
|精确率|0.76|0.73|0.72|
|召回率|0.70|0.67|0.66|

### 促销期模型（含618）

#### 用户复购预测

|指标|训练集|验证集|测试集|
|---|---|---|---|
|AUC|0.87|0.84|0.83|
|精确率|0.80|0.77|0.76|
|召回率|0.75|0.72|0.71|

-----

## 🗄️ 数据库设计

### 核心表结构

#### user_behavior（用户行为表）

```sql
- id: BIGINT (主键)
- user_id: VARCHAR(32) (用户ID)
- merchant_id: VARCHAR(32) (商户ID)
- action_type: TINYINT (0:点击, 1:购买, 2:领券)
- action_time: DATETIME (行为时间)
- date: DATE (日期，用于分区)
```

#### user_features（用户特征表）

```sql
- user_id: VARCHAR(32) (主键)
- feature_date: DATE (特征计算日期)
- click_count_7d: INT
- purchase_count_7d: INT
- cvr: DECIMAL(5,4)
- ... (其他50+特征字段)
```

#### merchant_features（商户特征表）

```sql
- merchant_id: VARCHAR(32) (主键)
- feature_date: DATE
- total_clicks: INT
- total_purchases: INT
- cvr: DECIMAL(5,4)
- ... (其他20+特征字段)
```

#### prediction_results（预测结果表）

```sql
- id: BIGINT (主键)
- user_id: VARCHAR(32)
- prediction_type: VARCHAR(20) (repurchase/coupon_use)
- prediction_date: DATE
- probability: DECIMAL(5,4)
- actual_result: TINYINT (实际结果)
- model_version: VARCHAR(20)
```

-----

## 📡 API接口

### 可视化接口

```
GET  /api/v1/visualization/overview
     获取总览数据

GET  /api/v1/visualization/daily-trend?start_date=xxx&end_date=xxx
     获取用户行为日趋势

GET  /api/v1/visualization/conversion-funnel
     获取转化漏斗数据

GET  /api/v1/visualization/user-segmentation
     获取RFM用户分层数据

GET  /api/v1/visualization/behavior-heatmap
     获取行为热力图数据

GET  /api/v1/visualization/comparison
     平销期vs促销期对比数据
```

### 预测接口

```
POST /api/v1/prediction/repurchase
     用户复购预测
     Body: { "user_ids": [...], "model": "ensemble/stacking" }

POST /api/v1/prediction/coupon-use
     优惠券核销预测
     Body: { "user_ids": [...], "merchant_ids": [...] }

GET  /api/v1/prediction/feature-importance?model=xxx
     获取特征重要性
```

### 认证接口

```
POST /api/v1/auth/login      用户登录，返回JWT Token
POST /api/v1/auth/register   用户注册
GET  /api/v1/auth/me         获取当前用户信息
PUT  /api/v1/auth/profile    修改个人信息
```

### 统计接口

```
GET  /api/v1/statistics/user-stats?user_id=xxx
     获取用户统计信息

GET  /api/v1/statistics/merchant-stats?merchant_id=xxx
     获取商户统计信息
```

-----

## 🎨 页面展示

### 1. 总览仪表盘（/dashboard）

- 核心KPI指标卡片（6项）
- 用户行为日趋势折线图
- Top商户排行

### 2. 用户分析页（/user-analysis）

- RFM用户分层散点图
- 用户生命周期饼图
- 用户画像雷达图
- 行为时段热力图

### 3. 行为流分析页（/behavior-flow）

- 转化漏斗图
- 用户行为路径桑基图
- 不同群体转化对比柱状图

### 4. 智能预测页（/prediction）

- 单用户预测演示
- 批量预测上传
- 预测结果展示表格
- 模型性能指标卡片
- 特征重要性条形图

### 5. 平销期vs促销期对比页（/comparison）

- 双时段行为趋势对比折线图
- 转化率对比雷达图
- 用户活跃度对比
- 618促销效果分析

-----

## 🧪 测试

```bash
# 后端接口测试
cd backend
python test_api.py

# 前端构建检查
cd frontend
npm run build
```

-----

## 📦 部署

### Docker部署（推荐）

```bash
# 构建镜像
docker-compose build

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f
```

### 传统部署

见文档：[DEPLOYMENT.md](docs/DEPLOYMENT.md)

-----

## 📝 开发进度

- [x] 数据探索性分析（EDA）
- [x] 特征工程方案设计与实现（100+特征）
- [x] 数据库设计与搭建
- [x] 后端API开发（可视化、预测、统计、认证）
- [x] 机器学习模型训练（XGBoost、LightGBM、Stacking）
- [x] 前端页面开发（8个视图）
- [x] 可视化组件开发（ECharts）
- [x] 用户认证与权限控制
- [x] 系统联调测试
- [x] 前端UI优化

-----

## 📄 许可证

本项目采用 MIT 许可证 - 详见 LICENSE 文件

-----

## 👥 作者

**Aurelie** - 毕业设计项目

- 邮箱：aureliewu0529@gmail.com
- GitHub: [oyushoudesu](https://github.com/oyushoudesu)

-----

## 🙏 致谢

- 感谢阿里巴巴提供的O2O数据集
- 感谢开源社区提供的优秀工具和框架
- 感谢导师陈凤娟教授的指导

-----

## 📚 参考资料

1. [阿里巴巴O2O数据集 - 天池](https://tianchi.aliyun.com/)
2. [FastAPI官方文档](https://fastapi.tiangolo.com/)
3. [Vue 3官方文档](https://vuejs.org/)
4. [ECharts可视化案例](https://echarts.apache.org/examples/)
5. [XGBoost官方文档](https://xgboost.readthedocs.io/)
6. [LightGBM官方文档](https://lightgbm.readthedocs.io/)

-----

**最后更新时间**：2026-04-17
