
# 电商用户行为分析与预测系统

基于阿里巴巴O2O优惠券数据集的用户行为可视化分析与智能预测平台

## 📊 项目简介

本系统是一个面向电商场景的用户行为分析与预测平台，通过对用户点击、领券、购买等行为数据进行深度挖掘，提供全方位的数据可视化展示和智能预测功能。系统特别关注平销期与促销期（618）用户行为模式的差异分析。

### 核心功能

- 📈 **多维度数据可视化** - 用户行为趋势、转化漏斗、热力图、用户画像等
- 🤖 **智能预测模型** - 用户复购预测、优惠券核销预测
- 🔄 **双场景对比** - 平销期 vs 促销期行为模式对比分析
- 💡 **实时交互分析** - 支持多维度筛选和钻取

-----

## 🗂️ 项目结构

```
ecommerce-behavior-system/
├── backend/                      # 后端服务
│   ├── app/
│   │   ├── api/                  # API接口
│   │   │   ├── visualization.py  # 可视化数据接口
│   │   │   ├── prediction.py     # 预测接口
│   │   │   └── statistics.py     # 统计分析接口
│   │   ├── models/               # 数据库模型
│   │   │   ├── user.py
│   │   │   ├── merchant.py
│   │   │   └── behavior.py
│   │   ├── services/             # 业务逻辑
│   │   │   ├── feature_engine.py # 特征工程
│   │   │   ├── ml_models.py      # 机器学习模型
│   │   │   ├── data_processor.py # 数据处理
│   │   │   └── data_cache.py     # 数据缓存
│   │   └── utils/                # 工具函数
│   ├── data/                     # 数据目录
│   │   ├── raw/                  # 原始数据
│   │   ├── processed/            # 处理后数据
│   │   └── features/             # 特征数据
│   ├── ml_models/                # 训练好的模型
│   │   ├── regular_period/       # 平销期模型
│   │   └── promotion_period/     # 促销期模型
│   ├── config.py                 # 配置文件
│   ├── requirements.txt          # Python依赖
│   └── main.py                   # 启动文件
│
├── frontend/                     # 前端应用
│   ├── src/
│   │   ├── views/                # 页面组件
│   │   │   ├── Dashboard.vue     # 仪表盘
│   │   │   ├── UserAnalysis.vue  # 用户分析
│   │   │   ├── BehaviorFlow.vue  # 行为流分析
│   │   │   ├── Prediction.vue    # 预测功能
│   │   │   └── Comparison.vue    # 平销期vs促销期对比
│   │   ├── components/           # 复用组件
│   │   │   ├── charts/           # 图表组件
│   │   │   ├── filters/          # 筛选器组件
│   │   │   └── cards/            # 卡片组件
│   │   ├── api/                  # API调用
│   │   ├── router/               # 路由配置
│   │   ├── store/                # 状态管理
│   │   └── utils/                # 工具函数
│   ├── package.json
│   └── vite.config.js
│
├── notebooks/                    # Jupyter notebooks
│   ├── 01_EDA.ipynb             # 探索性数据分析
│   ├── 02_Feature_Engineering.ipynb  # 特征工程
│   ├── 03_Model_Training.ipynb  # 模型训练
│   └── 04_Model_Evaluation.ipynb # 模型评估
│
├── docs/                         # 文档
│   ├── API.md                    # API文档
│   ├── DATABASE.md               # 数据库设计
│   └── DEPLOYMENT.md             # 部署文档
│
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
- **Mechant_id** - 商户ID
- **Action** - 0点击，1购买，2领券优惠券
- **Coupon_id** - 优惠券ID：null表示无优惠券消费，此时Discount_rate和Date_received字段无意义;"fixed"表示该交易是限时低价活动。 
- **Discount_rate** - 优惠率：x \in [0,1]代表折扣率；x:y表示满x减y；"fixed"表示低价限时优惠；
- **Date_received** - 领取优惠券日期
- **Date** - 消费日期：如果Date=null & Coupon_id != null，该记录表示领取优惠券但没有使用；如果Date!=null & Coupon_id = null，则表示普通消费日期；如果Date!=null & Coupon_id != null，则表示用优惠券消费日期；

### 数据规模
#### TODO
- 总行为记录：11,429,826条
- 活跃用户数：544,307人
- 整体CVR：12.00%

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

|技术          |版本    |用途     |
|------------|------|-------|
|Python      |3.9+  |核心语言   |
|FastAPI     |0.104+|Web框架  |
|MySQL       |8.0+  |关系数据库  |
|Redis       |7.0+  |缓存数据库  |
|Pandas      |2.0+  |数据处理   |
|Scikit-learn|1.3+  |机器学习   |
|XGBoost     |2.0+  |梯度提升模型 |
|LightGBM    |4.0+  |轻量级梯度提升|
|SQLAlchemy  |2.0+  |ORM框架  |

### 前端技术

|技术          |版本  |用途     |
|------------|----|-------|
|Vue         |3.3+|前端框架   |
|TypeScript  |5.0+|类型系统   |
|Vite        |5.0+|构建工具   |
|Element Plus|2.4+|UI组件库  |
|ECharts     |5.4+|可视化库   |
|Axios       |1.6+|HTTP客户端|
|Pinia       |2.1+|状态管理   |

-----

## 🎯 核心功能模块

### 1. 数据可视化模块

#### 总览仪表盘

- 核心指标卡片（日活、转化率、GMV等）
- 用户行为趋势图（时间序列）
- 实时数据更新

#### 用户分析

- **RFM用户分层**：最近购买时间、购买频率、购买金额三维分析
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
- **模型**：XGBoost + LightGBM 融合
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

### 3. 数据管理模块

- 数据导入与预处理
- 特征工程自动化
- 数据质量监控
- 数据导出功能

-----

## 🚀 快速开始

### 环境要求

- Python 3.9+
- Node.js 18+
- MySQL 8.0+
- Redis 7.0+（可选）

### 后端部署

```bash
# 1. 克隆项目
git clone https://github.com/yourusername/ecommerce-behavior-system.git
cd ecommerce-behavior-system/backend

# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置数据库
# 编辑 config.py 文件，设置MySQL连接信息

# 5. 初始化数据库
python scripts/init_db.py

# 6. 导入数据
python scripts/import_data.py --file data/raw/online_data.csv

# 7. 特征工程
python scripts/feature_engineering.py

# 8. 训练模型
python scripts/train_models.py --mode both  # 训练平销期和促销期两个模型

# 9. 启动服务
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 前端部署

```bash
# 1. 进入前端目录
cd ../frontend

# 2. 安装依赖
npm install

# 3. 配置API地址
# 编辑 .env.development 文件

# 4. 启动开发服务器
npm run dev

# 5. 构建生产版本
npm run build
```

### 访问系统

- 前端页面：http://localhost:5173
- 后端API文档：http://localhost:8000/docs
- 数据库管理：http://localhost:8080（需配置phpMyAdmin）

-----

## 📊 特征工程

### 用户维度特征（50+）

#### 基础行为统计

- 点击/领券/购买次数（7天/14天/30天窗口）
- 活跃天数
- 行为总量

#### 转化特征

- 点击转化率（CTR）
- 领券率
- 券核销率
- 整体CVR

#### 活跃度特征

- 用户新鲜度（Recency）
- 用户频率（Frequency）
- 平均行为间隔
- 行为间隔方差
- 生命周期长度

#### 行为模式特征

- 最常活跃时段
- 工作日/周末行为占比
- 最近行为类型

### 商户维度特征（20+）

- 商户热度指标
- 商户转化率
- 商户用户覆盖数
- 商户排名

### 交互特征（15+）

- 用户-商户历史交互次数
- 用户-商户转化率
- 是否回头客
- 最近交互距今天数

### 时间特征（10+）

- 星期几
- 是否周末
- 是否月初/月末
- 距离促销日天数

### 促销敏感度特征（8+）

- 用户领券偏好
- 券弃用率
- 领券到购买平均天数

**总计：100+ 特征维度**

-----

## 📈 模型性能

### 平销期模型

#### 用户复购预测

|指标      |训练集 |验证集 |测试集 |
|--------|----|----|----|
|AUC     |0.85|0.82|0.81|
|精确率     |0.78|0.75|0.74|
|召回率     |0.72|0.69|0.68|
|F1-Score|0.75|0.72|0.71|

#### 优惠券核销预测

|指标 |训练集 |验证集 |测试集 |
|---|----|----|----|
|AUC|0.83|0.80|0.79|
|精确率|0.76|0.73|0.72|
|召回率|0.70|0.67|0.66|

### 促销期模型（含618）

#### 用户复购预测

|指标 |训练集 |验证集 |测试集 |
|---|----|----|----|
|AUC|0.87|0.84|0.83|
|精确率|0.80|0.77|0.76|
|召回率|0.75|0.72|0.71|

**注**：以上为预期性能指标，实际结果以模型训练后为准

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

GET  /api/v1/visualization/user-trend?start_date=xxx&end_date=xxx
     获取用户行为趋势

GET  /api/v1/visualization/conversion-funnel?date=xxx
     获取转化漏斗数据

GET  /api/v1/visualization/user-rfm
     获取RFM分析数据

GET  /api/v1/visualization/behavior-heatmap
     获取行为热力图数据

GET  /api/v1/visualization/comparison?type=regular_vs_promotion
     平销期vs促销期对比数据
```

### 预测接口

```
POST /api/v1/prediction/repurchase
     用户复购预测
     Body: { "user_ids": [...], "model": "regular/promotion" }

POST /api/v1/prediction/coupon-use
     优惠券核销预测
     Body: { "user_ids": [...], "merchant_ids": [...] }

GET  /api/v1/prediction/feature-importance?model=xxx
     获取特征重要性
```

### 统计接口

```
GET  /api/v1/statistics/user-stats?user_id=xxx
     获取用户统计信息

GET  /api/v1/statistics/merchant-stats?merchant_id=xxx
     获取商户统计信息
```

详细API文档见：[API.md](docs/API.md)

-----

## 🎨 页面展示

### 1. 总览仪表盘

- 核心KPI指标卡片
- 用户行为趋势折线图
- CVR变化趋势
- Top商户排行

### 2. 用户分析页

- RFM用户分层散点图
- 用户生命周期饼图
- 用户画像雷达图
- 行为时段热力图

### 3. 行为流分析页

- 转化漏斗图
- 用户行为路径桑基图
- 不同群体转化对比柱状图

### 4. 智能预测页

- 单用户预测演示
- 批量预测上传
- 预测结果展示表格
- 模型性能指标卡片
- 特征重要性条形图

### 5. 平销期vs促销期对比页

- 双时段行为趋势对比折线图
- 转化率对比雷达图
- 用户活跃度对比
- 618促销效果分析

-----

## 🧪 测试

```bash
# 后端测试
cd backend
pytest tests/ -v

# 前端测试
cd frontend
npm run test
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

- [ ] 数据探索性分析（EDA）
- [ ] 特征工程方案设计
- [ ] 数据库设计与搭建
- [ ] 后端API开发
- [ ] 特征工程实现
- [ ] 模型训练与调优
- [ ] 前端页面开发
- [ ] 可视化组件开发
- [ ] 系统联调测试
- [ ] 性能优化
- [ ] 部署上线

-----

## 🤝 贡献指南

欢迎提出Issue和Pull Request！

1. Fork本项目
1. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
1. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
1. 推送到分支 (`git push origin feature/AmazingFeature`)
1. 开启Pull Request

-----

## 📄 许可证

本项目采用 MIT 许可证 - 详见 <LICENSE> 文件

-----

## 👥 作者

**邬雨湘** - 毕业设计项目

- 学校：广东白云学院
- 专业：数据科学与大数据技术
- 邮箱：aureliewu0529@gmail.com
- GitHub: [@yourusername](https://github.com/yourusername)

-----

## 🙏 致谢

- 感谢阿里巴巴提供的O2O数据集
- 感谢开源社区提供的优秀工具和框架
- 感谢导师陈凤娟教授的指导

-----

## 📚 参考资料

1. [阿里巴巴O2O数据集](https://tianchi.aliyun.com/)
1. [FastAPI官方文档](https://fastapi.tiangolo.com/)
1. [Vue 3官方文档](https://vuejs.org/)
1. [ECharts可视化案例](https://echarts.apache.org/examples/)
1. [XGBoost官方文档](https://xgboost.readthedocs.io/)

-----

**最后更新时间**：2026-01-21
