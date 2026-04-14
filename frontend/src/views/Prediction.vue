<template>
  <div class="prediction">

    <el-tabs v-model="activeTab" type="card" class="pred-tabs" @tab-change="handleTabChange">

      <!-- ════════════════ Tab1: 单用户预测 ════════════════ -->
      <el-tab-pane name="single">
        <template #label>
          <span class="tab-label"><el-icon><User /></el-icon>单用户预测</span>
        </template>

        <el-row :gutter="24">
          <!-- 左：参数 -->
          <el-col :span="9">
            <div class="panel">
              <div class="panel-title">
                <el-icon color="#3b82f6"><Setting /></el-icon>预测参数
              </div>

              <div class="field">
                <div class="field-label">预测模式</div>
                <el-select v-model="singleForm.pred_mode" style="width:100%">
                  <el-option label="加权集成（0.67×XGB + 0.33×LGB）" value="ensemble" />
                  <el-option label="Stacking 元学习（XGB+LGB→LR）"   value="stacking" />
                </el-select>
              </div>

              <div class="field">
                <div class="field-label">用户 ID</div>
                <el-input
                  v-model="singleForm.user_id"
                  placeholder="输入用户ID，如：13740231"
                  size="large"
                  clearable
                />
                <div class="field-hint">可从 test_618.csv 中选取真实用户ID</div>
              </div>

              <button
                class="pred-btn"
                :class="{ loading: singleLoading }"
                :disabled="singleLoading"
                @click="runSinglePredict"
              >
                {{ singleLoading ? '预测中…' : '开始预测' }}
              </button>
            </div>
          </el-col>

          <!-- 右：结果 -->
          <el-col :span="15">
            <div class="panel result-panel">
              <div class="panel-title">
                <el-icon color="#3b82f6"><DataAnalysis /></el-icon>预测结果
              </div>

              <div v-if="!singleResult" class="empty-state">
                <div class="empty-icon">🤖</div>
                <div class="empty-text">输入用户 ID 后点击预测</div>
                <div class="empty-sub">支持加权集成与 Stacking 元学习两种预测模式</div>
              </div>

              <div v-else class="result-body">
                <div class="result-top">
                  <div id="gauge-chart" style="width:220px;height:220px;flex-shrink:0"></div>

                  <div class="result-info">
                    <div class="verdict" :class="singleResult.prediction === 1 ? 'verdict-yes' : 'verdict-no'">
                      {{ singleResult.prediction === 1 ? '预测：会复购' : '预测：不会复购' }}
                    </div>
                    <div class="prob-row">
                      <span class="prob-label">复购概率</span>
                      <span class="prob-val" :style="{ color: probColor(singleResult.probability) }">
                        {{ (singleResult.probability * 100).toFixed(2) }}%
                      </span>
                    </div>
                    <div class="meta-row">
                      <div class="meta-item">
                        <div class="meta-label">用户 ID</div>
                        <div class="meta-val">{{ singleResult.user_id }}</div>
                      </div>
                      <div class="meta-item">
                        <div class="meta-label">风险等级</div>
                        <div class="meta-val">
                          <el-tag :type="riskTagType(singleResult.risk_level)" effect="dark" size="small">
                            {{ singleResult.risk_level }}风险
                          </el-tag>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </el-col>
        </el-row>
      </el-tab-pane>

      <!-- ════════════════ Tab2: 批量预测 ════════════════ -->
      <el-tab-pane name="batch">
        <template #label>
          <span class="tab-label"><el-icon><List /></el-icon>批量预测</span>
        </template>

        <el-row :gutter="24">
          <el-col :span="9">
            <div class="panel">
              <div class="panel-title">
                <el-icon color="#3b82f6"><Setting /></el-icon>批量参数
              </div>

              <div class="field">
                <div class="field-label">预测模式</div>
                <el-select v-model="batchForm.pred_mode" style="width:100%">
                  <el-option label="加权集成（0.67×XGB + 0.33×LGB）" value="ensemble" />
                  <el-option label="Stacking 元学习（XGB+LGB→LR）"   value="stacking" />
                </el-select>
              </div>

              <div class="field">
                <div class="field-label">用户 ID 列表（每行一个）</div>
                <el-input
                  v-model="batchForm.user_ids_text"
                  type="textarea"
                  :rows="9"
                  placeholder="13740231&#10;14336199&#10;10539231"
                />
              </div>

              <button
                class="pred-btn"
                :class="{ loading: batchLoading }"
                :disabled="batchLoading"
                @click="runBatchPredict"
              >
                {{ batchLoading ? '预测中…' : '批量预测' }}
              </button>
            </div>
          </el-col>

          <el-col :span="15">
            <div class="panel" style="min-height:400px">
              <div class="panel-title">
                <el-icon color="#3b82f6"><Grid /></el-icon>预测结果
                <el-button
                  v-if="batchResults.length > 0"
                  size="small" style="margin-left:auto"
                  @click="exportBatch"
                >导出 CSV</el-button>
              </div>

              <el-empty v-if="batchResults.length === 0" description="暂无预测结果" style="margin-top:40px" />

              <el-table v-else :data="batchResults" stripe style="width:100%">
                <el-table-column prop="user_id" label="用户ID" width="130" />
                <el-table-column label="复购概率" min-width="160">
                  <template #default="{ row }">
                    <div style="display:flex;align-items:center;gap:8px">
                      <el-progress
                        :percentage="parseFloat((row.probability * 100).toFixed(1))"
                        :color="row.probability >= 0.5 ? '#ef4444' : '#22c55e'"
                        style="flex:1" :show-text="false"
                      />
                      <span style="font-size:12px;font-weight:600;width:44px;text-align:right">
                        {{ (row.probability * 100).toFixed(1) }}%
                      </span>
                    </div>
                  </template>
                </el-table-column>
                <el-table-column label="预测结论" width="110" align="center">
                  <template #default="{ row }">
                    <el-tag :type="row.prediction === 1 ? 'danger' : 'success'" size="small" effect="dark">
                      {{ row.prediction === 1 ? '会复购' : '不复购' }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column label="风险等级" width="100" align="center">
                  <template #default="{ row }">
                    <el-tag :type="riskTagType(row.risk_level)" size="small">{{ row.risk_level }}</el-tag>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </el-col>
        </el-row>
      </el-tab-pane>

      <!-- ════════════════ Tab3: 模型性能 ════════════════ -->
      <el-tab-pane name="performance">
        <template #label>
          <span class="tab-label"><el-icon><TrendCharts /></el-icon>模型性能</span>
        </template>

        <div class="perf-switch">
          <el-radio-group v-model="perfModelType" @change="onModelChange">
            <el-radio-button label="ensemble">加权集成模型</el-radio-button>
            <el-radio-button label="stacking">Stacking 元学习</el-radio-button>
          </el-radio-group>
        </div>

        <el-row :gutter="20">
          <!-- 指标卡 -->
          <el-col :span="10">
            <div class="panel" style="min-height:480px">
              <div class="panel-title">
                <el-icon color="#3b82f6"><Odometer /></el-icon>模型评估指标
              </div>
              <div v-loading="perfLoading" style="min-height:320px">
                <template v-if="perfStats.auc">
                  <div class="metric-grid">
                    <div v-for="item in perfItems" :key="item.key" class="metric-box" :class="item.cls">
                      <div class="metric-box-icon">
                        <el-icon :size="18" color="#fff"><component :is="item.icon" /></el-icon>
                      </div>
                      <div class="metric-box-val">{{ perfStats[item.key] }}</div>
                      <div class="metric-box-label">{{ item.label }}</div>
                      <el-progress
                        :percentage="parseFloat((perfStats[item.key] * 100).toFixed(1))"
                        :stroke-width="4" :show-text="false"
                        :color="perfStats[item.key] >= 0.8 ? '#22c55e' : '#f59e0b'"
                        style="margin-top:8px"
                      />
                    </div>
                  </div>

                  <div class="extra-stats">
                    <div class="extra-item">
                      <span class="extra-label">预测总用户数</span>
                      <span class="extra-val">{{ perfStats.total_users?.toLocaleString() }}</span>
                    </div>
                    <div class="extra-item">
                      <span class="extra-label">预测复购</span>
                      <span class="extra-val" style="color:#ef4444">{{ perfStats.predicted_positive?.toLocaleString() }}</span>
                    </div>
                    <div class="extra-item">
                      <span class="extra-label">预测不复购</span>
                      <span class="extra-val" style="color:#22c55e">{{ perfStats.predicted_negative?.toLocaleString() }}</span>
                    </div>
                  </div>
                </template>
                <el-empty v-else description="暂无指标数据" style="margin-top:40px" />
              </div>
            </div>
          </el-col>

          <!-- 特征重要性 -->
          <el-col :span="14">
            <div class="panel" style="min-height:480px">
              <div class="panel-title">
                <el-icon color="#3b82f6"><DataLine /></el-icon>Top 20 特征重要性（XGBoost）
              </div>
              <!-- loading 套在外层，feature-chart 独立，防止 ECharts 拿到 0 宽度 -->
              <div v-loading="featureLoading" style="height:420px">
                <div id="feature-chart" style="height:100%;width:100%"></div>
              </div>
            </div>
          </el-col>
        </el-row>
      </el-tab-pane>

    </el-tabs>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import * as echarts from 'echarts'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import {
  User, Setting, DataAnalysis, List, Grid,
  TrendCharts, Odometer, DataLine, Aim, Search, Timer
} from '@element-plus/icons-vue'

const API_BASE = 'http://localhost:8000/api/v1'

// ── Tab ──
const activeTab = ref('single')

// ── 单用户预测 ──
const singleForm   = ref({ pred_mode: 'ensemble', user_id: '' })
const singleLoading = ref(false)
const singleResult  = ref(null)

const riskTagType = level => ({ '高': 'danger', '中': 'warning', '低': 'success' }[level] || 'info')
const probColor   = prob  => prob >= 0.7 ? '#ef4444' : prob >= 0.4 ? '#f59e0b' : '#22c55e'

const runSinglePredict = async () => {
  if (!singleForm.value.user_id.trim()) return
  singleLoading.value = true
  singleResult.value  = null
  try {
    const res = await axios.post(`${API_BASE}/prediction/repurchase`, {
      user_ids:  [singleForm.value.user_id.trim()],
      pred_mode: singleForm.value.pred_mode
    })
    singleResult.value = res.data[0]
    renderGauge(res.data[0].probability)
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '预测失败，请检查用户ID是否存在')
  } finally {
    singleLoading.value = false
  }
}

const renderGauge = (prob) => {
  setTimeout(() => {
    const el = document.getElementById('gauge-chart')
    if (!el) return
    const inst = echarts.getInstanceByDom(el)
    if (inst) inst.dispose()
    echarts.init(el).setOption({
      series: [{
        type: 'gauge',
        startAngle: 200, endAngle: -20, min: 0, max: 1, splitNumber: 5,
        axisLine: {
          lineStyle: {
            width: 18,
            color: [[0.4, '#22c55e'], [0.7, '#f59e0b'], [1, '#ef4444']]
          }
        },
        pointer: { itemStyle: { color: 'auto' } },
        axisTick:  { distance: -22, length: 7,  lineStyle: { color: '#fff', width: 2 } },
        splitLine: { distance: -30, length: 16, lineStyle: { color: '#fff', width: 3 } },
        axisLabel: { color: 'inherit', distance: 36, fontSize: 11 },
        detail: {
          valueAnimation: true,
          formatter: val => `${(val * 100).toFixed(1)}%\n复购概率`,
          color: 'inherit', fontSize: 16,
          offsetCenter: [0, '65%']
        },
        data: [{ value: prob }]
      }]
    })
  }, 100)
}

// ── 批量预测 ──
const batchForm    = ref({ pred_mode: 'ensemble', user_ids_text: '' })
const batchLoading = ref(false)
const batchResults = ref([])

const runBatchPredict = async () => {
  const ids = batchForm.value.user_ids_text.split('\n').map(s => s.trim()).filter(Boolean)
  if (!ids.length) return
  batchLoading.value = true
  batchResults.value = []
  try {
    const res = await axios.post(`${API_BASE}/prediction/repurchase`, {
      user_ids:  ids,
      pred_mode: batchForm.value.pred_mode
    })
    batchResults.value = res.data
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '批量预测失败，请检查用户ID')
  } finally {
    batchLoading.value = false
  }
}

const exportBatch = () => {
  const rows = [['user_id', 'probability', 'prediction', 'risk_level']]
  batchResults.value.forEach(r => rows.push([r.user_id, r.probability, r.prediction, r.risk_level]))
  const csv  = rows.map(r => r.join(',')).join('\n')
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
  const a    = Object.assign(document.createElement('a'), {
    href: URL.createObjectURL(blob), download: 'prediction_results.csv'
  })
  a.click()
}

// ── 模型性能 ──
const perfModelType  = ref('ensemble')
const perfLoading    = ref(false)
const featureLoading = ref(false)
const perfStats      = ref({})
const perfLoaded     = ref(false)

const perfItems = [
  { key: 'auc',       label: 'AUC',      cls: 'mb-blue',   icon: TrendCharts },
  { key: 'precision', label: '精确率',   cls: 'mb-green',  icon: Aim         },
  { key: 'recall',    label: '召回率',   cls: 'mb-orange', icon: Search      },
  { key: 'f1_score',  label: 'F1-Score', cls: 'mb-purple', icon: Timer       },
]

const handleTabChange = (tabName) => {
  if (tabName === 'performance' && !perfLoaded.value) loadPerformance()
}

const onModelChange = () => {
  perfLoaded.value = false
  loadPerformance()
}

const loadPerformance = async () => {
  perfLoading.value    = true
  featureLoading.value = true
  perfLoaded.value     = true
  try {
    const res = await axios.get(`${API_BASE}/prediction/batch-stats`, {
      params: { pred_mode: perfModelType.value }
    })
    perfStats.value = res.data
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '模型指标加载失败')
  } finally {
    perfLoading.value = false
  }

  try {
    const res = await axios.get(`${API_BASE}/prediction/feature-importance`, {
      params: { pred_mode: perfModelType.value, top_n: 20 }
    })
    renderFeatureChart(res.data)
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '特征重要性加载失败')
  } finally {
    featureLoading.value = false
  }
}

const renderFeatureChart = (data) => {
  // 延迟等 Tab 动画结束、loading 遮罩消失，再初始化 ECharts
  setTimeout(() => {
    const el = document.getElementById('feature-chart')
    if (!el) return
    const inst = echarts.getInstanceByDom(el)
    if (inst) inst.dispose()

    const chart    = echarts.init(el)
    const features = [...data.features].reverse()
    const importance = [...data.importance].reverse()

    chart.setOption({
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
      grid:    { left: '2%', right: '10%', top: '2%', bottom: '2%', containLabel: true },
      xAxis:   { type: 'value', name: '重要性得分', nameTextStyle: { color: '#94a3b8' },
                 axisLine: { lineStyle: { color: '#e2e8f0' } },
                 splitLine: { lineStyle: { color: '#f1f5f9' } } },
      yAxis:   { type: 'category', data: features,
                 axisLabel: { fontSize: 11, color: '#64748b' },
                 axisLine:  { lineStyle: { color: '#e2e8f0' } } },
      series: [{
        type: 'bar', data: importance, barMaxWidth: 18,
        itemStyle: {
          borderRadius: [0, 4, 4, 0],
          color: params => {
            const t = params.dataIndex / features.length
            if (t > 0.75) return new echarts.graphic.LinearGradient(0,0,1,0,
              [{ offset:0, color:'#3b82f6' },{ offset:1, color:'#06b6d4' }])
            if (t > 0.45) return new echarts.graphic.LinearGradient(0,0,1,0,
              [{ offset:0, color:'#22c55e' },{ offset:1, color:'#16a34a' }])
            return new echarts.graphic.LinearGradient(0,0,1,0,
              [{ offset:0, color:'#f59e0b' },{ offset:1, color:'#ea580c' }])
          }
        },
        label: {
          show: true, position: 'right',
          formatter: params => params.value.toFixed(4),
          fontSize: 10, color: '#64748b'
        }
      }]
    })
  }, 200)
}
</script>

<style scoped>
.prediction { padding: 20px; }

/* ── Tabs ── */
.pred-tabs :deep(.el-tabs__header) {
  background: #fff;
  border-radius: 10px 10px 0 0;
  border-bottom: 1px solid #e2e8f0;
  margin-bottom: 0;
  padding: 0 8px;
}
.pred-tabs :deep(.el-tabs__item) {
  font-size: 13.5px;
  height: 48px;
  padding: 0 20px;
  color: #64748b;
  border: none !important;
  background: transparent !important;
}
.pred-tabs :deep(.el-tabs__item.is-active) { color: #3b82f6; font-weight: 600; }
.pred-tabs :deep(.el-tabs__nav-wrap::after) { display: none; }
.pred-tabs :deep(.el-tabs__content) { background: transparent; padding: 0; }
.tab-label { display: flex; align-items: center; gap: 6px; }

/* ── Panel ── */
.panel {
  background: #fff;
  border-radius: 10px;
  border: 1px solid #e2e8f0;
  padding: 20px;
}
.result-panel { min-height: 360px; }

.panel-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
  padding-bottom: 14px;
  margin-bottom: 16px;
  border-bottom: 1px solid #f1f5f9;
}

/* ── Fields ── */
.field { margin-bottom: 18px; }
.field-label {
  font-size: 11px;
  font-weight: 700;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.6px;
  margin-bottom: 6px;
}
.field-hint { font-size: 12px; color: #cbd5e1; margin-top: 5px; }

/* ── Predict button ── */
.pred-btn {
  width: 100%;
  height: 44px;
  margin-top: 6px;
  border: none;
  border-radius: 8px;
  background: linear-gradient(135deg, #3b82f6, #06b6d4);
  color: #fff;
  font-size: 15px;
  font-weight: 600;
  letter-spacing: 3px;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 4px 14px rgba(59,130,246,0.35);
}
.pred-btn:hover:not(:disabled) { transform: translateY(-1px); box-shadow: 0 6px 18px rgba(59,130,246,0.45); }
.pred-btn:active:not(:disabled) { transform: translateY(0); }
.pred-btn.loading, .pred-btn:disabled { opacity: 0.65; cursor: not-allowed; }

/* ── Empty state ── */
.empty-state {
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  min-height: 280px; gap: 10px;
}
.empty-icon { font-size: 52px; }
.empty-text { font-size: 15px; font-weight: 500; color: #475569; }
.empty-sub  { font-size: 12px; color: #94a3b8; }

/* ── Single result ── */
.result-body { padding: 4px 0; }
.result-top  { display: flex; align-items: center; gap: 28px; }
.result-info { flex: 1; }

.verdict     { font-size: 20px; font-weight: 700; margin-bottom: 12px; }
.verdict-yes { color: #ef4444; }
.verdict-no  { color: #22c55e; }

.prob-row    { display: flex; align-items: baseline; gap: 10px; margin-bottom: 20px; }
.prob-label  { font-size: 13px; color: #94a3b8; }
.prob-val    { font-size: 32px; font-weight: 700; }

.meta-row    { display: flex; gap: 28px; }
.meta-label  { font-size: 11px; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px; }
.meta-val    { font-size: 14px; font-weight: 600; color: #1e293b; }

/* ── Perf switch ── */
.perf-switch { margin-bottom: 20px; }

/* ── Metric grid ── */
.metric-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-bottom: 16px;
}
.metric-box        { border-radius: 10px; padding: 16px; }
.metric-box-icon   { width: 34px; height: 34px; border-radius: 8px; display: flex; align-items: center; justify-content: center; margin-bottom: 10px; }
.metric-box-val    { font-size: 26px; font-weight: 700; color: #1e293b; }
.metric-box-label  { font-size: 12px; color: #64748b; margin-top: 2px; }

.mb-blue   { background: #eff6ff; }
.mb-blue   .metric-box-icon { background: linear-gradient(135deg, #3b82f6, #06b6d4); box-shadow: 0 3px 8px rgba(59,130,246,0.3); }
.mb-green  { background: #f0fdf4; }
.mb-green  .metric-box-icon { background: linear-gradient(135deg, #22c55e, #16a34a); box-shadow: 0 3px 8px rgba(34,197,94,0.3); }
.mb-orange { background: #fffbeb; }
.mb-orange .metric-box-icon { background: linear-gradient(135deg, #f59e0b, #ea580c); box-shadow: 0 3px 8px rgba(245,158,11,0.3); }
.mb-purple { background: #faf5ff; }
.mb-purple .metric-box-icon { background: linear-gradient(135deg, #8b5cf6, #6d28d9); box-shadow: 0 3px 8px rgba(139,92,246,0.3); }

/* ── Extra stats ── */
.extra-stats {
  display: flex; flex-direction: column; gap: 10px;
  background: #f8fafc; border-radius: 8px; padding: 14px;
}
.extra-item  { display: flex; justify-content: space-between; align-items: center; }
.extra-label { font-size: 13px; color: #64748b; }
.extra-val   { font-size: 14px; font-weight: 700; color: #1e293b; }
</style>
