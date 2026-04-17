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
                <el-input v-model="singleForm.user_id" placeholder="输入用户ID，如：13740231" size="large" clearable />
                <div class="field-hint">可从 test_618.csv 中选取真实用户ID</div>
              </div>
              <button class="pred-btn" :class="{ loading: singleLoading }" :disabled="singleLoading" @click="runSinglePredict">
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
                <!-- 顶部: 仪表盘 + 结论 -->
                <div class="result-top">
                  <div id="gauge-chart" style="width:200px;height:200px;flex-shrink:0"></div>
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
                <!-- 底部: 用户特征百分位 -->
                <div class="profile-section">
                  <div class="profile-title">该用户 Top 10 特征百分位排名</div>
                  <div v-loading="profileLoading" style="height:220px">
                    <div id="profile-chart" style="height:100%;width:100%"></div>
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
                <el-input v-model="batchForm.user_ids_text" type="textarea" :rows="9" placeholder="13740231&#10;14336199&#10;10539231" />
              </div>
              <button class="pred-btn" :class="{ loading: batchLoading }" :disabled="batchLoading" @click="runBatchPredict">
                {{ batchLoading ? '预测中…' : '批量预测' }}
              </button>
            </div>
          </el-col>

          <el-col :span="15">
            <div class="panel" style="min-height:400px">
              <div class="panel-title">
                <el-icon color="#3b82f6"><Grid /></el-icon>预测结果
                <el-button v-if="batchResults.length > 0" size="small" style="margin-left:auto" @click="exportBatch">导出 CSV</el-button>
              </div>
              <el-empty v-if="batchResults.length === 0" description="暂无预测结果" style="margin-top:40px" />
              <el-table v-else :data="batchResults" stripe style="width:100%" max-height="320">
                <el-table-column prop="user_id" label="用户ID" width="130" />
                <el-table-column label="复购概率" min-width="160">
                  <template #default="{ row }">
                    <div style="display:flex;align-items:center;gap:8px">
                      <el-progress :percentage="parseFloat((row.probability * 100).toFixed(1))"
                        :color="row.probability >= 0.5 ? '#ef4444' : '#22c55e'"
                        style="flex:1" :show-text="false" />
                      <span style="font-size:12px;font-weight:600;width:44px;text-align:right">{{ (row.probability * 100).toFixed(1) }}%</span>
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

        <!-- 批量分析图表（有结果后显示） -->
        <el-row v-if="batchResults.length > 0" :gutter="24" style="margin-top:16px">
          <el-col :span="14">
            <div class="panel">
              <div class="panel-title">
                <el-icon color="#3b82f6"><DataLine /></el-icon>复购概率分布
              </div>
              <div id="batch-hist-chart" style="height:260px"></div>
            </div>
          </el-col>
          <el-col :span="10">
            <div class="panel">
              <div class="panel-title">
                <el-icon color="#3b82f6"><PieChart /></el-icon>风险等级分布
              </div>
              <div id="batch-pie-chart" style="height:260px"></div>
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

        <!-- 第一行: 指标卡 + 特征重要性 -->
        <el-row :gutter="20" style="margin-bottom:16px">
          <el-col :span="10">
            <div class="panel" style="min-height:440px">
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
                      <el-progress :percentage="parseFloat((perfStats[item.key] * 100).toFixed(1))"
                        :stroke-width="4" :show-text="false"
                        :color="perfStats[item.key] >= 0.8 ? '#22c55e' : '#f59e0b'"
                        style="margin-top:8px" />
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
                    <div class="extra-item">
                      <span class="extra-label">判断阈值</span>
                      <span class="extra-val" style="color:#f59e0b">{{ perfStats.threshold }}</span>
                    </div>
                  </div>
                </template>
                <el-empty v-else description="暂无指标数据" style="margin-top:40px" />
              </div>
            </div>
          </el-col>

          <el-col :span="14">
            <div class="panel" style="min-height:440px">
              <div class="panel-title">
                <el-icon color="#3b82f6"><DataLine /></el-icon>Top 20 特征重要性（XGBoost）
              </div>
              <div v-loading="featureLoading" style="height:390px">
                <div id="feature-chart" style="height:100%;width:100%"></div>
              </div>
            </div>
          </el-col>
        </el-row>

        <!-- 第二行: ROC曲线 + 混淆矩阵 -->
        <el-row :gutter="20">
          <el-col :span="13">
            <div class="panel">
              <div class="panel-title">
                <el-icon color="#3b82f6"><TrendCharts /></el-icon>ROC 曲线
                <span class="panel-sub" v-if="rocData">AUC = {{ rocData.auc }}</span>
              </div>
              <div v-loading="rocLoading" style="height:300px">
                <div id="roc-chart" style="height:100%;width:100%"></div>
              </div>
            </div>
          </el-col>
          <el-col :span="11">
            <div class="panel">
              <div class="panel-title">
                <el-icon color="#3b82f6"><Grid /></el-icon>混淆矩阵
                <span class="panel-sub" v-if="cmData">准确率 {{ (cmData.accuracy * 100).toFixed(1) }}%</span>
              </div>
              <div v-loading="cmLoading" style="height:300px;display:flex;align-items:center;justify-content:center">
                <div v-if="cmData" class="cm-grid">
                  <div class="cm-header-row">
                    <div class="cm-corner"></div>
                    <div class="cm-head">预测负例</div>
                    <div class="cm-head">预测正例</div>
                  </div>
                  <div class="cm-data-row">
                    <div class="cm-side">实际负例</div>
                    <div class="cm-cell cm-tn">
                      <div class="cm-val">{{ cmData.tn.toLocaleString() }}</div>
                      <div class="cm-label">TN（真负例）</div>
                      <div class="cm-pct">{{ ((cmData.tn / cmData.total) * 100).toFixed(1) }}%</div>
                    </div>
                    <div class="cm-cell cm-fp">
                      <div class="cm-val">{{ cmData.fp.toLocaleString() }}</div>
                      <div class="cm-label">FP（假正例）</div>
                      <div class="cm-pct">{{ ((cmData.fp / cmData.total) * 100).toFixed(1) }}%</div>
                    </div>
                  </div>
                  <div class="cm-data-row">
                    <div class="cm-side">实际正例</div>
                    <div class="cm-cell cm-fn">
                      <div class="cm-val">{{ cmData.fn.toLocaleString() }}</div>
                      <div class="cm-label">FN（假负例）</div>
                      <div class="cm-pct">{{ ((cmData.fn / cmData.total) * 100).toFixed(1) }}%</div>
                    </div>
                    <div class="cm-cell cm-tp">
                      <div class="cm-val">{{ cmData.tp.toLocaleString() }}</div>
                      <div class="cm-label">TP（真正例）</div>
                      <div class="cm-pct">{{ ((cmData.tp / cmData.total) * 100).toFixed(1) }}%</div>
                    </div>
                  </div>
                </div>
                <el-empty v-else description="暂无数据" />
              </div>
            </div>
          </el-col>
        </el-row>
      </el-tab-pane>

    </el-tabs>
  </div>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue'
import * as echarts from 'echarts'
import { ElMessage } from 'element-plus'
import {
  User, Setting, DataAnalysis, List, Grid,
  TrendCharts, Odometer, DataLine, Aim, Search, Timer, PieChart
} from '@element-plus/icons-vue'
import { useTheme } from '@/composables/useTheme'
import axiosInstance from '@/api/axiosInstance'

const { isDark } = useTheme()

const ecInit = (id) => {
  const el = document.getElementById(id)
  if (!el) return null
  echarts.getInstanceByDom(el)?.dispose()
  return echarts.init(el, isDark.value ? 'dark' : null)
}

watch(isDark, () => {
  if (singleResult.value) { renderGauge(singleResult.value.probability); renderProfile() }
  if (perfLoaded.value)   { renderFeatureChart(cachedFeatureData.value); renderROC() }
  if (batchResults.value.length) renderBatchCharts()
})

const cachedFeatureData = ref(null)
const activeTab = ref('single')

// ── 单用户预测 ──
const singleForm    = ref({ pred_mode: 'ensemble', user_id: '' })
const singleLoading = ref(false)
const singleResult  = ref(null)
const profileLoading = ref(false)
const profileData    = ref(null)

const riskTagType = level => ({ '高': 'danger', '中': 'warning', '低': 'success' }[level] || 'info')
const probColor   = prob  => prob >= 0.7 ? '#ef4444' : prob >= 0.4 ? '#f59e0b' : '#22c55e'

const runSinglePredict = async () => {
  if (!singleForm.value.user_id.trim()) return
  singleLoading.value = true
  singleResult.value  = null
  profileData.value   = null
  try {
    const res = await axiosInstance.post('/prediction/repurchase', {
      user_ids: [singleForm.value.user_id.trim()],
      pred_mode: singleForm.value.pred_mode
    })
    singleResult.value = res.data[0]
    await nextTick()
    renderGauge(res.data[0].probability)
    loadUserProfile(singleForm.value.user_id.trim())
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '预测失败，请检查用户ID是否存在')
  } finally {
    singleLoading.value = false
  }
}

const loadUserProfile = async (userId) => {
  profileLoading.value = true
  try {
    const res = await axiosInstance.get(`/prediction/user-profile/${userId}`)
    profileData.value = res.data
    await nextTick()
    renderProfile()
  } catch (e) { console.error(e) } finally { profileLoading.value = false }
}

const renderProfile = () => {
  const data = profileData.value
  if (!data) return
  const chart = ecInit('profile-chart')
  if (!chart) return
  const features = data.features.map(d => d.feature).reverse()
  const percentiles = data.features.map(d => d.percentile).reverse()
  chart.setOption({
    tooltip: {
      trigger: 'axis', axisPointer: { type: 'shadow' },
      formatter: params => {
        const idx = data.features.length - 1 - params[0].dataIndex
        const d = data.features[idx]
        return `${d.feature}<br/>百分位: <b>${d.percentile}%</b><br/>值: ${d.value}<br/>均值: ${d.mean}`
      }
    },
    grid: { left: '2%', right: '8%', top: '4%', bottom: '4%', containLabel: true },
    xAxis: { type: 'value', max: 100, axisLabel: { formatter: '{value}%', color: '#94a3b8', fontSize: 10 }, splitLine: { lineStyle: { type: 'dashed', color: '#f1f5f9' } } },
    yAxis: { type: 'category', data: features, axisLabel: { fontSize: 10, color: '#475569' } },
    series: [{
      type: 'bar', data: percentiles, barMaxWidth: 14,
      itemStyle: {
        borderRadius: [0, 4, 4, 0],
        color: params => {
          const v = params.value
          if (v >= 75) return new echarts.graphic.LinearGradient(1,0,0,0,[{offset:0,color:'#3b82f6'},{offset:1,color:'#06b6d4'}])
          if (v >= 50) return new echarts.graphic.LinearGradient(1,0,0,0,[{offset:0,color:'#10b981'},{offset:1,color:'#34d399'}])
          return new echarts.graphic.LinearGradient(1,0,0,0,[{offset:0,color:'#f59e0b'},{offset:1,color:'#fbbf24'}])
        }
      },
      label: { show: true, position: 'right', formatter: '{c}%', fontSize: 10, color: '#64748b' },
      markLine: { silent: true, data: [{ xAxis: 50 }], lineStyle: { color: '#94a3b8', type: 'dashed' }, label: { formatter: '中位线' } }
    }]
  })
}

const renderGauge = (prob) => {
  setTimeout(() => {
    const el = document.getElementById('gauge-chart')
    if (!el) return
    echarts.getInstanceByDom(el)?.dispose()
    echarts.init(el, isDark.value ? 'dark' : null).setOption({
      series: [{
        type: 'gauge', startAngle: 200, endAngle: -20, min: 0, max: 1, splitNumber: 5,
        axisLine: { lineStyle: { width: 18, color: [[0.4, '#22c55e'], [0.7, '#f59e0b'], [1, '#ef4444']] } },
        pointer: { itemStyle: { color: 'auto' } },
        axisTick:  { distance: -22, length: 7,  lineStyle: { color: '#fff', width: 2 } },
        splitLine: { distance: -30, length: 16, lineStyle: { color: '#fff', width: 3 } },
        axisLabel: { color: 'inherit', distance: 36, fontSize: 11 },
        detail: { valueAnimation: true, formatter: val => `${(val * 100).toFixed(1)}%\n复购概率`, color: 'inherit', fontSize: 15, offsetCenter: [0, '65%'] },
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
    const res = await axiosInstance.post('/prediction/repurchase', {
      user_ids: ids, pred_mode: batchForm.value.pred_mode
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
  const blob = new Blob(['\uFEFF' + csv], { type: 'text/csv;charset=utf-8;' })
  const a    = Object.assign(document.createElement('a'), { href: URL.createObjectURL(blob), download: 'prediction_results.csv' })
  a.click()
}

const renderBatchCharts = () => {
  const results = batchResults.value
  if (!results.length) return
  setTimeout(() => {
    // 直方图
    const bins = Array(10).fill(0)
    results.forEach(r => { const idx = Math.min(Math.floor(r.probability * 10), 9); bins[idx]++ })
    const histChart = ecInit('batch-hist-chart')
    if (histChart) {
      const labels = ['0-10%','10-20%','20-30%','30-40%','40-50%','50-60%','60-70%','70-80%','80-90%','90-100%']
      histChart.setOption({
        tooltip: { trigger: 'axis', formatter: '{b}: <b>{c}</b> 人' },
        grid: { left: '3%', right: '4%', bottom: '12%', top: '8%', containLabel: true },
        xAxis: { type: 'category', data: labels, axisLabel: { rotate: 30, color: '#334155', fontSize: 11 } },
        yAxis: { type: 'value', name: '用户数', splitLine: { lineStyle: { type: 'dashed', color: '#f1f5f9' } } },
        series: [{
          type: 'bar', data: bins.map((v, i) => ({
            value: v,
            itemStyle: { color: i < 4 ? '#22c55e' : i < 7 ? '#f59e0b' : '#ef4444', borderRadius: [4,4,0,0] }
          })),
          label: { show: true, position: 'top', formatter: '{c}', fontSize: 11, color: '#64748b' }
        }]
      })
    }
    // 饼图
    const riskCount = { '低': 0, '中': 0, '高': 0 }
    results.forEach(r => { if (riskCount[r.risk_level] !== undefined) riskCount[r.risk_level]++ })
    const pieChart = ecInit('batch-pie-chart')
    if (pieChart) {
      pieChart.setOption({
        tooltip: { trigger: 'item', formatter: '{b}: {c} 人 ({d}%)' },
        legend: { orient: 'vertical', left: 'left', top: 'center', textStyle: { fontSize: 12 } },
        color: ['#22c55e', '#f59e0b', '#ef4444'],
        series: [{
          type: 'pie', radius: ['40%', '68%'], center: ['60%', '50%'],
          data: [
            { name: '低风险', value: riskCount['低'] },
            { name: '中风险', value: riskCount['中'] },
            { name: '高风险', value: riskCount['高'] }
          ],
          itemStyle: { borderRadius: 6, borderColor: '#fff', borderWidth: 3 },
          label: { formatter: '{b}\n{d}%', fontSize: 12 },
          emphasis: { itemStyle: { shadowBlur: 10, shadowColor: 'rgba(0,0,0,0.15)' } }
        }]
      })
    }
  }, 200)
}

watch(batchResults, () => nextTick(() => renderBatchCharts()), { deep: true })

// ── 模型性能 ──
const perfModelType  = ref('ensemble')
const perfLoading    = ref(false)
const featureLoading = ref(false)
const rocLoading     = ref(false)
const cmLoading      = ref(false)
const perfStats      = ref({})
const perfLoaded     = ref(false)
const rocData        = ref(null)
const cmData         = ref(null)

// rocData 到达后等 loading 遮罩动画结束再渲染
watch(rocData, (val) => { if (val) setTimeout(() => renderROC(), 300) })

const perfItems = [
  { key: 'auc',       label: 'AUC',      cls: 'mb-blue',   icon: TrendCharts },
  { key: 'precision', label: '精确率',   cls: 'mb-green',  icon: Aim         },
  { key: 'recall',    label: '召回率',   cls: 'mb-orange', icon: Search      },
  { key: 'f1_score',  label: 'F1-Score', cls: 'mb-purple', icon: Timer       },
]

const handleTabChange = (tabName) => {
  if (tabName === 'performance' && !perfLoaded.value) loadPerformance()
}

const onModelChange = () => { perfLoaded.value = false; loadPerformance() }

const loadPerformance = async () => {
  perfLoading.value = featureLoading.value = rocLoading.value = cmLoading.value = true
  perfLoaded.value = true

  axiosInstance.get('/prediction/batch-stats', { params: { pred_mode: perfModelType.value } })
    .then(res => { perfStats.value = res.data })
    .catch(e => ElMessage.error(e.response?.data?.detail || '模型指标加载失败'))
    .finally(() => { perfLoading.value = false })

  axiosInstance.get('/prediction/feature-importance', { params: { pred_mode: perfModelType.value, top_n: 20 } })
    .then(res => { renderFeatureChart(res.data) })
    .catch(e => console.error(e))
    .finally(() => { featureLoading.value = false })

  axiosInstance.get('/prediction/roc-curve', { params: { pred_mode: perfModelType.value } })
    .then(res => { rocData.value = res.data })
    .catch(e => ElMessage.error(e.response?.data?.detail || 'ROC 曲线加载失败'))
    .finally(() => { rocLoading.value = false })

  axiosInstance.get('/prediction/confusion-matrix', { params: { pred_mode: perfModelType.value } })
    .then(res => { cmData.value = res.data })
    .catch(e => console.error(e))
    .finally(() => { cmLoading.value = false })
}

const renderFeatureChart = (data) => {
  if (!data) return
  cachedFeatureData.value = data
  setTimeout(() => {
    const chart = ecInit('feature-chart')
    if (!chart) return
    const features = [...data.features].reverse()
    const importance = [...data.importance].reverse()
    chart.setOption({
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
      grid:    { left: '2%', right: '10%', top: '2%', bottom: '2%', containLabel: true },
      xAxis:   { type: 'value', splitLine: { lineStyle: { color: '#f1f5f9' } } },
      yAxis:   { type: 'category', data: features, axisLabel: { fontSize: 11, color: '#64748b' } },
      series: [{
        type: 'bar', data: importance, barMaxWidth: 16,
        itemStyle: {
          borderRadius: [0, 4, 4, 0],
          color: params => {
            const t = params.dataIndex / features.length
            if (t > 0.75) return new echarts.graphic.LinearGradient(0,0,1,0,[{offset:0,color:'#3b82f6'},{offset:1,color:'#06b6d4'}])
            if (t > 0.45) return new echarts.graphic.LinearGradient(0,0,1,0,[{offset:0,color:'#22c55e'},{offset:1,color:'#16a34a'}])
            return new echarts.graphic.LinearGradient(0,0,1,0,[{offset:0,color:'#f59e0b'},{offset:1,color:'#ea580c'}])
          }
        },
        label: { show: true, position: 'right', formatter: params => params.value.toFixed(4), fontSize: 10, color: '#64748b' }
      }]
    })
  }, 200)
}

const renderROC = () => {
  const data = rocData.value
  if (!data) return
  const chart = ecInit('roc-chart')
  if (!chart) return
  const points = data.fpr.map((x, i) => [x, data.tpr[i]])
  chart.setOption({
    tooltip: { trigger: 'axis', formatter: params => `FPR: ${params[0].data[0]}<br/>TPR: ${params[0].data[1]}` },
    grid: { left: '8%', right: '4%', bottom: '12%', top: '8%', containLabel: true },
    xAxis: { type: 'value', name: 'FPR（假正例率）', min: 0, max: 1, nameLocation: 'center', nameGap: 28, axisLabel: { color: '#94a3b8', fontSize: 11 }, splitLine: { lineStyle: { type: 'dashed', color: '#f1f5f9' } } },
    yAxis: { type: 'value', name: 'TPR（真正例率）', min: 0, max: 1, nameLocation: 'center', nameGap: 38, axisLabel: { color: '#94a3b8', fontSize: 11 }, splitLine: { lineStyle: { type: 'dashed', color: '#f1f5f9' } } },
    series: [
      {
        type: 'line', data: points, smooth: false, symbol: 'none',
        lineStyle: { color: '#3b82f6', width: 2.5 },
        areaStyle: { color: new echarts.graphic.LinearGradient(0,0,0,1,[{offset:0,color:'rgba(59,130,246,0.25)'},{offset:1,color:'rgba(59,130,246,0.02)'}]) },
        name: `ROC (AUC=${data.auc})`
      },
      {
        type: 'line', data: [[0,0],[1,1]], symbol: 'none',
        lineStyle: { color: '#94a3b8', type: 'dashed', width: 1.5 },
        name: '随机猜测基线'
      }
    ],
    legend: { bottom: 0, itemHeight: 10, textStyle: { fontSize: 11 } }
  })
}

const renderCM = () => {} // 混淆矩阵用纯模板渲染，无需 ECharts
</script>

<style scoped>
.prediction { padding: 16px 20px; background: var(--bg-page); min-height: 100%; }

.pred-tabs :deep(.el-tabs__header) { background: var(--bg-card); border-radius: 10px 10px 0 0; border-bottom: 1px solid #e2e8f0; margin-bottom: 0; padding: 0 8px; }
.pred-tabs :deep(.el-tabs__item) { font-size: 13.5px; height: 48px; padding: 0 20px; color: #64748b; border: none !important; background: transparent !important; }
.pred-tabs :deep(.el-tabs__item.is-active) { color: #3b82f6; font-weight: 600; }
.pred-tabs :deep(.el-tabs__nav-wrap::after) { display: none; }
.pred-tabs :deep(.el-tabs__content) { background: transparent; padding: 0; }
.tab-label { display: flex; align-items: center; gap: 6px; }

.panel { background: var(--bg-card); border-radius: 10px; border: 1px solid var(--border); padding: 20px; }
.result-panel { min-height: 360px; }
.panel-title { display: flex; align-items: center; gap: 8px; font-size: 14px; font-weight: 600; color: var(--text-primary); padding-bottom: 14px; margin-bottom: 16px; border-bottom: 1px solid var(--border); }
.panel-sub { margin-left: auto; font-size: 12px; font-weight: 500; color: #3b82f6; background: rgba(59,130,246,0.08); padding: 2px 10px; border-radius: 8px; }

.field { margin-bottom: 18px; }
.field-label { font-size: 11px; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.6px; margin-bottom: 6px; }
.field-hint { font-size: 12px; color: #cbd5e1; margin-top: 5px; }

.pred-btn { width: 100%; height: 44px; margin-top: 6px; border: none; border-radius: 8px; background: linear-gradient(135deg, #3b82f6, #06b6d4); color: #fff; font-size: 15px; font-weight: 600; letter-spacing: 3px; cursor: pointer; transition: all 0.2s; box-shadow: 0 4px 14px rgba(59,130,246,0.35); }
.pred-btn:hover:not(:disabled) { transform: translateY(-1px); box-shadow: 0 6px 18px rgba(59,130,246,0.45); }
.pred-btn.loading, .pred-btn:disabled { opacity: 0.65; cursor: not-allowed; }

.empty-state { display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 280px; gap: 10px; }
.empty-icon { font-size: 52px; }
.empty-text { font-size: 15px; font-weight: 500; color: #475569; }
.empty-sub  { font-size: 12px; color: #94a3b8; }

.result-body { padding: 4px 0; }
.result-top  { display: flex; align-items: center; gap: 24px; margin-bottom: 16px; }
.result-info { flex: 1; }
.verdict     { font-size: 20px; font-weight: 700; margin-bottom: 12px; }
.verdict-yes { color: #ef4444; }
.verdict-no  { color: #22c55e; }
.prob-row    { display: flex; align-items: baseline; gap: 10px; margin-bottom: 20px; }
.prob-label  { font-size: 13px; color: #94a3b8; }
.prob-val    { font-size: 32px; font-weight: 700; }
.meta-row    { display: flex; gap: 28px; }
.meta-label  { font-size: 11px; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px; }
.meta-val    { font-size: 14px; font-weight: 600; color: var(--text-primary); }

.profile-section { border-top: 1px solid var(--border); padding-top: 14px; margin-top: 4px; }
.profile-title { font-size: 12px; font-weight: 600; color: #64748b; margin-bottom: 8px; }

.perf-switch { margin-bottom: 20px; }

.metric-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 16px; }
.metric-box        { border-radius: 10px; padding: 16px; }
.metric-box-icon   { width: 34px; height: 34px; border-radius: 8px; display: flex; align-items: center; justify-content: center; margin-bottom: 10px; }
.metric-box-val    { font-size: 26px; font-weight: 700; color: var(--text-primary); }
.metric-box-label  { font-size: 12px; color: var(--text-secondary); margin-top: 2px; }
.mb-blue   { background: rgba(59,130,246,0.08); } .mb-blue   .metric-box-icon { background: linear-gradient(135deg, #3b82f6, #06b6d4); box-shadow: 0 3px 8px rgba(59,130,246,0.3); }
.mb-green  { background: rgba(16,185,129,0.08); } .mb-green  .metric-box-icon { background: linear-gradient(135deg, #22c55e, #16a34a); box-shadow: 0 3px 8px rgba(34,197,94,0.3); }
.mb-orange { background: rgba(245,158,11,0.08); } .mb-orange .metric-box-icon { background: linear-gradient(135deg, #f59e0b, #ea580c); box-shadow: 0 3px 8px rgba(245,158,11,0.3); }
.mb-purple { background: rgba(139,92,246,0.08); } .mb-purple .metric-box-icon { background: linear-gradient(135deg, #8b5cf6, #6d28d9); box-shadow: 0 3px 8px rgba(139,92,246,0.3); }

.extra-stats { display: flex; flex-direction: column; gap: 10px; background: var(--bg-page); border-radius: 8px; padding: 14px; }
.extra-item  { display: flex; justify-content: space-between; align-items: center; }
.extra-label { font-size: 13px; color: var(--text-secondary); }
.extra-val   { font-size: 14px; font-weight: 700; color: var(--text-primary); }

/* 混淆矩阵 */
.cm-grid { display: flex; flex-direction: column; gap: 6px; }
.cm-header-row { display: flex; gap: 6px; padding-left: 72px; }
.cm-head { flex: 1; text-align: center; font-size: 12px; font-weight: 600; color: #64748b; padding: 6px 0; }
.cm-data-row { display: flex; align-items: center; gap: 6px; }
.cm-side { width: 66px; font-size: 12px; font-weight: 600; color: #64748b; text-align: right; padding-right: 6px; flex-shrink: 0; }
.cm-cell { flex: 1; border-radius: 10px; padding: 16px 10px; text-align: center; }
.cm-val   { font-size: 22px; font-weight: 800; }
.cm-label { font-size: 11px; margin: 3px 0; }
.cm-pct   { font-size: 12px; font-weight: 600; opacity: 0.7; }
.cm-tn { background: rgba(34,197,94,0.12);  color: #16a34a; }
.cm-fp { background: rgba(245,158,11,0.12); color: #b45309; }
.cm-fn { background: rgba(239,68,68,0.12);  color: #dc2626; }
.cm-tp { background: rgba(59,130,246,0.12); color: #1d4ed8; }
</style>
