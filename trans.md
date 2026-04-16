| 字段名 | 数据类型 | 允许空 | 默认值 | 约束/索引 | 字段说明 |
| --- | --- | --- | --- | --- | --- |
| id | BIGINT | 否 | AUTO_INCREMENT | 主键 | 记录主键,自增 |
| user_id | VARCHAR(32) | 否 | — | INDEX | 用户 ID |
| merchant_id | VARCHAR(32) | 否 | — | INDEX | 商户 ID |
| action_type | TINYINT | 否 | — | INDEX | 行为类型:0=点击 1=购买 2=领券 |
| coupon_id | VARCHAR(32) | 是 | NULL | — | 优惠券 ID,无券消费为 NULL |
| discount_rate | VARCHAR(20) | 是 | NULL | — | 优惠率,支持小数、满减 (x:y)、固定金额 (fixed) 三种格式 |
| date_received | DATE | 是 | NULL | — | 领券日期 |
| action_date | DATE | 是 | NULL | INDEX | 行为发生日期 |
| created_at | DATETIME | 是 | CURRENT_TIMESTAMP | — | 入库时间 |



| 字段分组 | 字段名 | 数据类型 | 默认值 | 字段说明 |
| --- | --- | --- | --- | --- |
| 主键/标识 | id | BIGINT | AUTO_INCREMENT | 记录主键 |
| 主键/标识 | user_id | VARCHAR(32) | — | 用户 ID (与行为表关联) |
| 主键/标识 | feature_date | DATE | — | 特征计算截止日期 |
| 短窗口行为统计 | click_count_7d | INT | 0 | 近 7 天点击次数 |
| 短窗口行为统计 | purchase_count_7d | INT | 0 | 近 7 天购买次数 |
| 短窗口行为统计 | coupon_count_7d | INT | 0 | 近 7 天领券次数 |
| 长窗口行为统计 | click_count_30d | INT | 0 | 近 30 天点击次数 |
| 长窗口行为统计 | purchase_count_30d | INT | 0 | 近 30 天购买次数 |
| 长窗口行为统计 | coupon_count_30d | INT | 0 | 近 30 天领券次数 |
| 转化特征 | cvr | DECIMAL(7,4) | 0.0000 | 整体转化率 (购买/点击) |
| 转化特征 | coupon_use_rate | DECIMAL(7,4) | 0.0000 | 优惠券核销率 |
| RFM 特征 | recency | INT | 0 | 最近一次行为距特征日天数 |
| RFM 特征 | frequency | INT | 0 | 历史行为总频次 |
| 活跃度特征 | active_days | INT | 0 | 活跃天数 |
| 活跃度特征 | avg_action_interval | DECIMAL(7,2) | 0.00 | 平均行为间隔(天) |
| 活跃度特征 | lifecycle_days | INT | 0 | 用户生命周期长度(天) |
| 行为模式特征 | weekend_ratio | DECIMAL(5,4) | 0.0000 | 周末行为占比 |
| 行为模式特征 | peak_hour | TINYINT | 0 | 最活跃小时 (0-23) |
| 促销敏感度特征 | coupon_preference | DECIMAL(5,4) | 0.0000 | 历史领券偏好 |
| 促销敏感度特征 | avg_days_to_use | DECIMAL(7,2) | 0.00 | 领券到购买平均天数 |
| 预测标签 | label | TINYINT | NULL | 1=目标月复购 / 0=未复购 |



| 字段名 | 数据类型 | 默认值 | 字段说明 |
| --- | --- | --- | --- |
| id | BIGINT | AUTO_INCREMENT | 主键 |
| merchant_id | VARCHAR(32) | — | 商户 ID |
| feature_date | DATE | — | 特征计算截止日期 |
| total_clicks | INT | 0 | 总点击数 |
| total_purchases | INT | 0 | 总购买数 |
| total_coupons | INT | 0 | 总发券数 |
| cvr | DECIMAL(7,4) | 0.0000 | 商户转化率 |
| user_coverage | INT | 0 | 覆盖用户数 (去重) |
| repurchase_rate | DECIMAL(7,4) | 0.0000 | 回头客比例 |
| merchant_rank | INT | NULL | 按购买量的全局排名 |



| 字段名 | 数据类型 | 默认值 | 字段说明 |
| --- | --- | --- | --- |
| id | BIGINT | AUTO_INCREMENT | 主键 |
| user_id | VARCHAR(32) | — | 目标用户 ID |
| prediction_type | VARCHAR(20) | — | 预测任务类型:repurchase(复购)/coupon_use(券核销) |
| prediction_date | DATE | — | 预测执行日期 |
| probability | DECIMAL(6,4) | — | 模型输出的正类概率 ∈ [0,1] |
| predicted_label | TINYINT | NULL | 基于最优阈值的离散标签 |
| actual_result | TINYINT | NULL | 实际结果,可事后回填 |
| model_version | VARCHAR(20) | 'v1.0' | 所用模型版本号 |
| period_type | VARCHAR(20) | — | 场景:regular(常规期)/promotion(促销期如 618) |
| created_at | DATETIME | CURRENT_TIMESTAMP | 记录入库时间 |


| 字段名 | 数据类型 | 默认值 | 字段说明 |
| --- | --- | --- | --- |
| id | INT | AUTO_INCREMENT | 主键 |
| username | VARCHAR(50) | — | 登录用户名 (UNIQUE) |
| nickname | VARCHAR(50) | NULL | 显示昵称 |
| password | VARCHAR(255) | — | bcrypt 加密后的密码哈希 |
| role | VARCHAR(20) | 'user' | 角色:admin / user / viewer |
| is_active | TINYINT | 1 | 启用状态:1=启用 0=禁用 |
| created_at | DATETIME | CURRENT_TIMESTAMP | 创建时间 |
| last_login | DATETIME | NULL | 最近登录时间 |

<br>
<br>
<br>

| 字段名 | 数据类型 | 默认值 | 字段说明 |
| --- | --- | --- | --- |
| id | INT | AUTO_INCREMENT | 主键 |
| user_id | INT | — | 对应 sys_user.id |
| username | VARCHAR(50) | — | 用户名 |
| ip_address | VARCHAR(50) | NULL | 客户端 IP (兼容 IPv6) |
| success | TINYINT | 1 | bcrypt 加密后的密码哈希 |
| role | VARCHAR(20) | 'user' | 角色:admin / user / viewer |
| is_active | TINYINT | 1 | 1=成功 0=失败 |
| created_at | DATETIME | CURRENT_TIMESTAMP | 登录时间 |

<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>


| 所属表 | 索引名 | 索引列 | 服务的典型查询 |
| --- | --- | --- | --- |
| user_behavior | idx_user_id | user_id | 特征工程按用户聚合行为 |
| user_behavior | idx_merchant_id | merchant_id | 商户特征计算按商户聚合 |
| user_behavior | idx_action_date | action_date | 滑动时间窗口筛选 |
| user_behavior | idx_action_type | action_type | 按行为类型计算转化率 |
| user_features | idx_feature_date | feature_date | 按月份批量加载训练样本 |
| user_features | idx_label | label | 正负样本分层抽样 |
| merchant_features | idx_feature_date | feature_date | 按月份加载商户特征 |
| merchant_features | idx_cvr | cvr | 商户质量排序展示 |
| prediction_results | idx_user_id | user_id | 查询某用户的预测历史 |
| prediction_results | idx_prediction_type | prediction_type | 按任务类型汇总结果 |
| prediction_results | idx_period_type | period_type | 常规期/促销期分开统计 |
| prediction_results | idx_prediction_date | prediction_date | 按日期拉取预测批次 |
| login_log | idx_user_id | user_id | 审计某账号的登录历史 |

//
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>




| 特征组 | 字段名 | 数据类型 | 默认值 | 字段说明 |
| --- | --- | --- | --- | --- |
| 主键/标识 | id | BIGINT | AUTO_INCREMENT | 记录主键 |
| 主键/标识 | user_id | VARCHAR(32) | — | 用户 ID |
| 主键/标识 | feature_date | DATE | — | 特征截止日期 |
| 主键/标识 | window_type | VARCHAR(20) | — | 窗口标识:w1/w2/test_618 |
| 用户基础特征 | total_purchases | INT | 0 | 总购买次数 |
| 用户基础特征 | total_clicks | INT | 0 | 总点击次数 |
| 用户基础特征 | total_coupon_rcvd | INT | 0 | 总领券数 |
| 用户基础特征 | coupon_purchases | INT | 0 | 使用优惠券的购买次数 |
| 用户基础特征 | no_coupon_purchases | INT | 0 | 未使用优惠券的购买次数 |
| 用户基础特征 | coupons_not_used | INT | 0 | 领券未使用次数 |
| 用户基础特征 | merchant_count | INT | 0 | 交互过的商户数 |
| 用户基础特征 | coupon_types_count | INT | 0 | 领过的优惠券种类数 |
| 用户基础特征 | coupon_use_rate | DECIMAL(7,4) | 0.0000 | 券核销率 |
| 用户基础特征 | coupon_abandon_rate | DECIMAL(7,4) | 0.0000 | 券弃用率 |
| 用户基础特征 | coupon_purchase_ratio | DECIMAL(7,4) | 0.0000 | 有券购买占比 |
| 用户基础特征 | click_to_buy_rate | DECIMAL(7,4) | 0.0000 | 点击转化率 |
| 用户基础特征 | avg_purchase_per_merchant | DECIMAL(7,2) | 0.00 | 人均商户购买次数 |
| 用户-商户交互 | um_total_pairs | INT | 0 | 用户-商户交互对总数 |
| 用户-商户交互 | um_max_clicks | INT | 0 | 单商户最大点击数 |
| 用户-商户交互 | um_avg_clicks | DECIMAL(7,2) | 0.00 | 商户平均点击数 |
| 用户-商户交互 | um_total_clicks | INT | 0 | 交互对总点击数 |
| 用户-商户交互 | um_max_purchases | INT | 0 | 单商户最大购买数 |
| 用户-商户交互 | um_avg_purchases | DECIMAL(7,2) | 0.00 | 商户平均购买数 |
| 用户-商户交互 | um_total_um_purch | INT | 0 | 交互对总购买数 |
| 用户-商户交互 | um_purchase_pairs | INT | 0 | 有购买的交互对数 |
| 用户-商户交互 | um_purchase_penetration | DECIMAL(7,4) | 0.0000 | 商户购买渗透率 |
| 时间窗口特征 | purchases_7d | INT | 0 | 近 7 天购买数 |
| 时间窗口特征 | clicks_7d | INT | 0 | 近 7 天点击数 |
| 时间窗口特征 | coupons_7d | INT | 0 | 近 7 天领券数 |
| 时间窗口特征 | purchases_14d | INT | 0 | 近 14 天购买数 |
| 时间窗口特征 | clicks_14d | INT | 0 | 近 14 天点击数 |
| 时间窗口特征 | coupons_14d | INT | 0 | 近 14 天领券数 |
| 时间窗口特征 | purchases_30d | INT | 0 | 近 30 天购买数 |
| 时间窗口特征 | clicks_30d | INT | 0 | 近 30 天点击数 |
| 时间窗口特征 | coupons_30d | INT | 0 | 近 30 天领券数 |
| RFM 特征 | recency | INT | 0 | 最近一次购买距特征日天数 |
| RFM 特征 | lifetime | INT | 0 | 用户生命周期长度 |
| RFM 特征 | rfm_frequency | INT | 0 | 历史购买总次数 |
| RFM 特征 | purchase_frequency_daily | DECIMAL(7,4) | 0.0000 | 日均购买频次 |
| 优惠券特征 | avg_discount | DECIMAL(7,4) | 0.0000 | 平均折扣率(实付比例) |
| 优惠券特征 | median_discount | DECIMAL(7,4) | 0.0000 | 折扣率中位数 |
| 优惠券特征 | std_discount | DECIMAL(7,4) | 0.0000 | 折扣率标准差 |
| 优惠券特征 | min_discount | DECIMAL(7,4) | 0.0000 | 最小折扣率 |
| 优惠券特征 | max_discount | DECIMAL(7,4) | 0.0000 | 最大折扣率 |
| 优惠券特征 | avg_days_to_use | DECIMAL(7,2) | 0.00 | 平均核销时长(天) |
| 优惠券特征 | max_days_to_use | INT | 0 | 最大核销时长(天) |
| 时间偏好特征 | weekday_purchases | INT | 0 | 工作日购买数 |
| 时间偏好特征 | weekend_purchases | INT | 0 | 周末购买数 |
| 时间偏好特征 | weekend_purchase_ratio | DECIMAL(7,4) | 0.0000 | 周末购买占比 |
| 预测标签 | label | TINYINT | NULL | 1=下期购买 / 0=未购买 |