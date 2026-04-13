<!-- Prediction.vue
智能预测页面：单用户预测、批量预测、预测结果表格、特征重要性
Vue3 Composition API + Element Plus + ECharts + Axios
-->
<template>
  <div class="prediction">
    <h1>智能预测</h1>

    <el-tabs v-model="activeTab" type="border-card">

      <!-- ================================================================
           Tab1: 单用户预测
      ================================================================ -->
      <el-tab-pane label="单用户预测" name="single">
        <el-row :gutter="30">
          <!-- 左侧：输入区 -->
          <el-col :span="10">
            <el-card shadow="never" class="input-card">
              <template #header><span>预测参数</span></template>

              <div class="form-item">
                <div class="form-label">预测类型</div>
                <el-radio-group v-model="singleForm.task">
                  <el-radio label="repurchase">用户复购预测</el-radio>
                  <el-radio label="coupon">优惠券核销预测</el-radio>
                </el-radio-group>
              </div>

              <div class="form-item">
                <div class="form-label">模型场景</div>
                <el-select v-model="singleForm.model_type" style="width: 100%">
                  <el-option label="平销期模型（1-4月）" value="regular" />
                  <el-option label="促销期模型（含618）" value="promotion" />
                </el-select>
              </div>

              <div class="form-item">
                <div class="form-label">用户 ID</div>
                <el-input
                  v-model="singleForm.user_id"
                  placeholder="输入用户ID，如：13740231"
                  clearable
                />
                <div class="form-hint">可从特征文件中选取真实用户ID</div>
              </div>

              <el-button
                type="primary"
                :loading="singleLoading"
                @click="runSinglePredict"
                style="width: 100%; margin-top: 12px"
              >
                开始预测
              </el-button>
            </el-card>
          </el-col>

          <!-- 右侧：结果区 -->
          <el-col :span="14">
            <el-card shadow="never" class="result-card">
              <template #header><span>预测结果</span></template>

              <div v-if="!singleResult" class="empty-result">
                <el-empty description="输入用户ID后点击预测" />
              </div>

              <div v-else class="result-content">
                <!-- 概率仪表盘 -->
                <div id="gauge-chart" style="height: 260px"></div>

                <!-- 结论标签 -->
                <div class="result-conclusion">
                  <el-tag
                    :type="singleResult.prediction === 1 ? 'danger' : 'success'"
                    size="large"
                    effect="dark"
                  >
                    {{ singleResult.prediction === 1 ? '预测：会复购 ✓' : '预测：不会复购 ✗' }}
                  </el-tag>
                  <el-tag :type="riskTagType(singleResult.risk_level)" size="large">
                    风险等级：{{ singleResult.risk_level }}
                  </el-tag>
                </div>

                <!-- 详细数据 -->
                <el-descriptions :column="2" border size="small" class="result-detail">
                  <el-descriptions-item label="用户ID">{{ singleResult.user_id }}</el-descriptions-item>
                  <el-descriptions-item label="复购概率">
                    <span style="font-weight: bold; color: #F56C6C">
                      {{ (singleResult.probability * 100).toFixed(2) }}%
                    </span>
                  </el-descriptions-item>
                  <el-descriptions-item label="预测结论">
                    {{ singleResult.prediction === 1 ? '会复购' : '不会复购' }}
                  </el-descriptions-item>
                  <el-descriptions-item label="风险等级">{{ singleResult.risk_level }}</el-descriptions-item>
                </el-descriptions>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </el-tab-pane>

      <!-- ================================================================
           Tab2: 批量预测
      ================================================================ -->
      <el-tab-pane label="批量预测" name="batch">
        <el-row :gutter="30">
          <el-col :span="10">
            <el-card shadow="never" class="input-card">
              <template #header><span>批量预测参数</span></template>

              <div class="form-item">
                <div class="form-label">模型场景</div>
                <el-select v-model="batchForm.model_type" style="width: 100%">
                  <el-option label="平销期模型（1-4月）" value="regular" />
                  <el-option label="促销期模型（含618）" value="promotion" />
                </el-select>
              </div>

              <div class="form-item">
                <div class="form-label">用户 ID 列表（每行一个）</div>
                <el-input
                  v-model="batchForm.user_ids_text"
                  type="textarea"
                  :rows="8"
                  placeholder="13740231&#10;14336199&#10;10539231"
                />
              </div>

              <el-button
                type="primary"
                :loading="batchLoading"
                @click="runBatchPredict"
                style="width: 100%; margin-top: 12px"
              >
                批量预测
              </el-button>
            </el-card>
          </el-col>

          <el-col :span="14">
            <el-card shadow="never">
              <template #header>
                <div class="card-header">
                  <span>批量预测结果</span>
                  <el-button
                    v-if="batchResults.length > 0"
                    size="small"
                    @click="exportBatch"
                  >导出CSV</el-button>
                </div>
              </template>

              <el-empty v-if="batchResults.length === 0" description="暂无预测结果" />

              <el-table v-else :data="batchResults" stripe style="width: 100%">
                <el-table-column prop="user_id" label="用户ID" width="120" />
                <el-table-column label="复购概率" width="120">
                  <template #default="{ row }">
                    <el-progress
                      :percentage="parseFloat((row.probability * 100).toFixed(1))"
                      :color="row.probability >= 0.5 ? '#F56C6C' : '#67C23A'"
                    />
                  </template>
                </el-table-column>
                <el-table-column label="预测结论" width="100">
                  <template #default="{ row }">
                    <el-tag :type="row.prediction === 1 ? 'danger' : 'success'" size="small">
                      {{ row.prediction === 1 ? '会复购' : '不复购' }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column label="风险等级">
                  <template #default="{ row }">
                    <el-tag :type="riskTagType(row.risk_level)" size="small">
                      {{ row.risk_level }}
                    </el-tag>
                  </template>
                </el-table-column>
              </el-table>
            </el-card>
          </el-col>
        </el-row>
      </el-tab-pane>

      <!-- ================================================================
           Tab3: 模型性能 + 特征重要性
      ================================================================ -->
      <el-tab-pane label="模型性能" name="performance">
        <el-row :gutter="20" style="margin-bottom: 20px">
          <el-col :span="24">
            <el-radio-group v-model="perfModelType" @change="loadPerformance">
              <el-radio-button label="regular">平销期模型</el-radio-button>
              <el-radio-button label="promotion">促销期模型</el-radio-button>
            </el-radio-group>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <!-- 模型指标卡 -->
          <el-col :span="10">
            <el-card shadow="hover">
              <template #header><span>模型评估指标</span></template>
              <div v-loading="perfLoading">
                <el-row :gutter="12" v-if="perfStats.auc">
                  <el-col :span="12" v-for="item in perfItems" :key="item.key">
                    <div class="perf-item">
                      <div class="perf-value">{{ perfStats[item.key] }}</div>
                      <div class="perf-label">{{ item.label }}</div>
                      <el-progress
                        :percentage="parseFloat((perfStats[item.key] * 100).toFixed(1))"
                        :color="perfStats[item.key] >= 0.8 ? '#67C23A' : '#E6A23C'"
                        :show-text="false"
                        style="margin-top: 6px"
                      />
                    </div>
                  </el-col>
                </el-row>
                <el-empty v-else description="暂无指标数据" />
              </div>
            </el-card>
          </el-col>

          <!-- 特征重要性 -->
          <el-col :span="14">
            <el-card shadow="hover">
              <template #header><span>Top 20 特征重要性（XGBoost）</span></template>
              <div v-loading="featureLoading" id="feature-chart" style="height: 460px"></div>
            </el-card>
          </el-col>
        </el-row>
      </el-tab-pane>

    </el-tabs>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import * as echarts from 'echarts'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const API_BASE = 'http://localhost:8000/api/v1'

// ---- Tab 状态 ----
const activeTab = ref('single')

// ---- 单用户预测 ----
const singleForm = ref({ task: 'repurchase', model_type: 'regular', user_id: '' })
const singleLoading = ref(false)
const singleResult = ref(null)

const riskTagType = level => ({ '高': 'danger', '中': 'warning', '低': 'success' }[level] || 'info')

const runSinglePredict = async () => {
  if (!singleForm.value.user_id.trim()) {
    return
  }
  singleLoading.value = true
  singleResult.value = null
  try {
    const res = await axios.post(`${API_BASE}/prediction/repurchase`, {
      user_ids: [singleForm.value.user_id.trim()],
      model_type: singleForm.value.model_type
    })
    singleResult.value = res.data[0]
    renderGauge(res.data[0].probability)
  } catch (e) {
    const msg = e.response?.data?.detail || '预测失败，请检查用户ID是否存在'
    ElMessage.error(msg)
    console.error('单用户预测失败:', e)
  }
  finally {
    singleLoading.value = false
  }
}

const renderGauge = (prob) => {
  setTimeout(() => {
    const chart = echarts.init(document.getElementById('gauge-chart'))
    chart.setOption({
      series: [{
        type: 'gauge',
        startAngle: 200, endAngle: -20,
        min: 0, max: 1,
        splitNumber: 5,
        axisLine: {
          lineStyle: {
            width: 20,
            color: [[0.4, '#67C23A'], [0.7, '#E6A23C'], [1, '#F56C6C']]
          }
        },
        pointer: { itemStyle: { color: 'auto' } },
        axisTick: { distance: -25, length: 8, lineStyle: { color: '#fff', width: 2 } },
        splitLine: { distance: -35, length: 20, lineStyle: { color: '#fff', width: 4 } },
        axisLabel: { color: 'inherit', distance: 40, fontSize: 12 },
        detail: {
          valueAnimation: true,
          formatter: val => `${(val * 100).toFixed(1)}%\n复购概率`,
          color: 'inherit',
          fontSize: 18,
          offsetCenter: [0, '60%']
        },
        data: [{ value: prob }]
      }]
    })
  }, 100)
}

// ---- 批量预测 ----
const batchForm = ref({ model_type: 'regular', user_ids_text: '' })
const batchLoading = ref(false)
const batchResults = ref([])

const runBatchPredict = async () => {
  const ids = batchForm.value.user_ids_text
    .split('\n')
    .map(s => s.trim())
    .filter(Boolean)
  if (ids.length === 0) return

  batchLoading.value = true
  batchResults.value = []
  try {
    const res = await axios.post(`${API_BASE}/prediction/repurchase`, {
      user_ids: ids,
      model_type: batchForm.value.model_type
    })
    batchResults.value = res.data
  } catch (e) {
    const msg = e.response?.data?.detail || '批量预测失败，请检查用户ID'
    ElMessage.error(msg)
    console.error('批量预测失败:', e)
  } finally {
    batchLoading.value = false
  }
}

const exportBatch = () => {
  const rows = [['user_id', 'probability', 'prediction', 'risk_level']]
  batchResults.value.forEach(r => {
    rows.push([r.user_id, r.probability, r.prediction, r.risk_level])
  })
  const csv = rows.map(r => r.join(',')).join('\n')
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'prediction_results.csv'
  a.click()
}

// ---- 模型性能 ----
const perfModelType = ref('regular')
const perfLoading = ref(false)
const featureLoading = ref(false)
const perfStats = ref({})

const perfItems = [
  { key: 'auc', label: 'AUC' },
  { key: 'precision', label: '精确率' },
  { key: 'recall', label: '召回率' },
  { key: 'f1_score', label: 'F1-Score' }
]

const loadPerformance = async () => {
  perfLoading.value = true
  featureLoading.value = true
  try {
    // 模型指标
    const statsRes = await axios.get(`${API_BASE}/prediction/batch-stats`, {
      params: { model_type: perfModelType.value }
    })
    perfStats.value = statsRes.data
  } catch (e) {
    console.error('加载模型指标失败:', e)
  } finally {
    perfLoading.value = false
  }

  try {
    // 特征重要性
    const featRes = await axios.get(`${API_BASE}/prediction/feature-importance`, {
      params: { model_type: perfModelType.value, top_n: 20 }
    })
    renderFeatureChart(featRes.data)
  } catch (e) {
    console.error('加载特征重要性失败:', e)
  } finally {
    featureLoading.value = false
  }
}

const renderFeatureChart = (data) => {
  const chart = echarts.init(document.getElementById('feature-chart'))
  // 倒序，让最重要的在顶部
  const features = [...data.features].reverse()
  const importance = [...data.importance].reverse()

  chart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { left: '3%', right: '8%', bottom: '3%', containLabel: true },
    xAxis: { type: 'value', name: '重要性得分' },
    yAxis: { type: 'category', data: features, axisLabel: { fontSize: 11 } },
    color: ['#409EFF'],
    series: [{
      type: 'bar',
      data: importance,
      barMaxWidth: 20,
      itemStyle: {
        color: params => {
          const ratio = params.dataIndex / features.length
          return ratio > 0.7 ? '#409EFF' : ratio > 0.4 ? '#67C23A' : '#E6A23C'
        }
      },
      label: { show: true, position: 'right', formatter: val => val.toFixed(4), fontSize: 11 }
    }]
  })
}

onMounted(() => {
  loadPerformance()
})
</script>

<style scoped>
.prediction { padding: 20px; }
h1 { margin-bottom: 20px; color: #303133; }

.input-card, .result-card { height: 100%; }

.form-item { margin-bottom: 20px; }
.form-label { font-size: 13px; color: #606266; margin-bottom: 8px; font-weight: 500; }
.form-hint { font-size: 12px; color: #C0C4CC; margin-top: 4px; }

.empty-result {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 300px;
}

.result-content { padding: 10px 0; }

.result-conclusion {
  display: flex;
  gap: 12px;
  justify-content: center;
  margin: 12px 0;
}

.result-detail { margin-top: 16px; }

.perf-item {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 12px;
  text-align: center;
}
.perf-value { font-size: 28px; font-weight: bold; color: #303133; }
.perf-label { font-size: 13px; color: #909399; margin-top: 4px; }

.card-header { display: flex; align-items: center; justify-content: space-between; }
</style>
