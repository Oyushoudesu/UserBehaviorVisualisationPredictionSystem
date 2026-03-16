<!-- UserAnalysis.vue
用户分析页面，展示RFM散点图、用户生命周期饼图、用户画像雷达图、行为时段热力图
风格与Dashboard.vue保持一致：Vue3 Composition API + Element Plus + ECharts + Axios
-->
<template>
  <div class="user-analysis">
    <h1>用户分析</h1>

    <!-- 筛选栏 -->
    <el-card shadow="never" class="filter-card">
      <el-row :gutter="20" align="middle">
        <el-col :span="6">
          <span class="filter-label">数据周期：</span>
          <el-select v-model="selectedMonth" @change="loadAll" style="width: 140px">
            <el-option label="第1月（1月）" :value="1" />
            <el-option label="第2月（2月）" :value="2" />
            <el-option label="第3月（3月）" :value="3" />
            <el-option label="第4月（4月）" :value="4" />
            <el-option label="第5月（5月）" :value="5" />
            <el-option label="第6月（6月）" :value="6" />
          </el-select>
        </el-col>
        <el-col :span="18">
          <el-tag type="info" size="small">
            基于 user_features_month{{ selectedMonth }}.csv 特征数据
          </el-tag>
        </el-col>
      </el-row>
    </el-card>

    <!-- 核心指标 -->
    <el-row :gutter="20" class="metrics-row">
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="metric-card">
            <el-icon :size="40" color="#409EFF"><User /></el-icon>
            <div class="metric-content">
              <div class="metric-value">{{ stats.total_users?.toLocaleString() || '-' }}</div>
              <div class="metric-label">分析用户数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="metric-card">
            <el-icon :size="40" color="#67C23A"><Star /></el-icon>
            <div class="metric-content">
              <div class="metric-value">{{ stats.high_value_users?.toLocaleString() || '-' }}</div>
              <div class="metric-label">高价值用户</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="metric-card">
            <el-icon :size="40" color="#E6A23C"><Clock /></el-icon>
            <div class="metric-content">
              <div class="metric-value">{{ stats.avg_recency?.toFixed(0) || '-' }} 天</div>
              <div class="metric-label">平均最近购买间隔</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="metric-card">
            <el-icon :size="40" color="#F56C6C"><Warning /></el-icon>
            <div class="metric-content">
              <div class="metric-value">{{ stats.churn_risk_users?.toLocaleString() || '-' }}</div>
              <div class="metric-label">流失风险用户</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表第一行：RFM散点图 + 用户生命周期饼图 -->
    <el-row :gutter="20" class="charts-row">
      <el-col :span="14">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>RFM 用户分层散点图</span>
              <el-tooltip content="X轴：购买频率，Y轴：最近购买距今天数（越小越近），气泡大小：购买总量" placement="top">
                <el-icon color="#909399"><QuestionFilled /></el-icon>
              </el-tooltip>
            </div>
          </template>
          <div v-loading="loading.rfm" id="rfm-chart" style="height: 420px"></div>
        </el-card>
      </el-col>

      <el-col :span="10">
        <el-card shadow="hover">
          <template #header>
            <span>用户生命周期分布</span>
          </template>
          <div v-loading="loading.lifecycle" id="lifecycle-chart" style="height: 420px"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表第二行：用户画像雷达图 + 行为时段热力图 -->
    <el-row :gutter="20" class="charts-row">
      <el-col :span="10">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>用户画像雷达图</span>
              <el-radio-group v-model="radarSegment" size="small" @change="renderRadar">
                <el-radio-button label="高价值用户" />
                <el-radio-button label="普通用户" />
              </el-radio-group>
            </div>
          </template>
          <div v-loading="loading.radar" id="radar-chart" style="height: 420px"></div>
        </el-card>
      </el-col>

      <el-col :span="14">
        <el-card shadow="hover">
          <template #header>
            <span>行为时段热力图（小时 × 星期）</span>
          </template>
          <div v-loading="loading.heatmap" id="heatmap-chart" style="height: 420px"></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { User, Star, Clock, Warning, QuestionFilled } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import axios from 'axios'

const API_BASE = 'http://localhost:8000/api/v1'

// 状态
const selectedMonth = ref(4)
const radarSegment = ref('高价值用户')
const stats = ref({})
const radarData = ref(null)

const loading = ref({
  rfm: false,
  lifecycle: false,
  radar: false,
  heatmap: false
})

// ECharts 实例缓存（用于 resize）
let charts = {}

// ============================================================================
// 加载核心指标
// ============================================================================
const loadStats = async () => {
  try {
    const res = await axios.get(`${API_BASE}/visualization/user-stats`, {
      params: { month: selectedMonth.value }
    })
    stats.value = res.data
  } catch (error) {
    console.error('加载用户统计失败:', error)
  }
}

// ============================================================================
// RFM 散点图
// ============================================================================
const loadRFM = async () => {
  loading.value.rfm = true
  try {
    const res = await axios.get(`${API_BASE}/visualization/user-rfm`, {
      params: { month: selectedMonth.value }
    })
    const data = res.data

    const chart = echarts.init(document.getElementById('rfm-chart'))
    charts.rfm = chart

    // 按用户分层分组，每组一个 series
    const seriesMap = {}
    data.points.forEach(p => {
      if (!seriesMap[p.segment]) seriesMap[p.segment] = []
      seriesMap[p.segment].push([p.frequency, p.recency, p.purchase_count, p.user_id])
    })

    const colorMap = {
      '高价值用户': '#409EFF',
      '重要挽留用户': '#E6A23C',
      '新用户': '#67C23A',
      '流失用户': '#F56C6C',
      '其他': '#909399'
    }

    const series = Object.entries(seriesMap).map(([name, points]) => ({
      name,
      type: 'scatter',
      data: points,
      symbolSize: val => Math.max(5, Math.min(30, val[2] / 20)),
      itemStyle: { color: colorMap[name] || '#909399', opacity: 0.7 }
    }))

    chart.setOption({
      tooltip: {
        formatter: params => {
          const [freq, rec, cnt, uid] = params.data
          return `用户ID: ${uid}<br/>购买频率: ${freq}<br/>距今: ${rec}天<br/>购买总量: ${cnt}`
        }
      },
      legend: { data: Object.keys(seriesMap), bottom: 0 },
      xAxis: { name: '购买频率', nameLocation: 'center', nameGap: 30, splitLine: { show: false } },
      yAxis: {
        name: '距今天数',
        nameLocation: 'center',
        nameGap: 40,
        inverse: true,
        splitLine: { lineStyle: { type: 'dashed' } }
      },
      series
    })
  } catch (error) {
    console.error('加载RFM数据失败:', error)
  } finally {
    loading.value.rfm = false
  }
}

// ============================================================================
// 用户生命周期饼图
// ============================================================================
const loadLifecycle = async () => {
  loading.value.lifecycle = true
  try {
    const res = await axios.get(`${API_BASE}/visualization/user-segmentation`, {
      params: { month: selectedMonth.value }
    })
    const data = res.data.segments

    const chart = echarts.init(document.getElementById('lifecycle-chart'))
    charts.lifecycle = chart

    chart.setOption({
      tooltip: {
        trigger: 'item',
        formatter: '{b}: {c} ({d}%)'
      },
      legend: {
        orient: 'vertical',
        left: 'left',
        top: 'center'
      },
      color: ['#409EFF', '#67C23A', '#E6A23C', '#F56C6C'],
      series: [
        {
          type: 'pie',
          radius: ['40%', '65%'],
          center: ['60%', '50%'],
          data,
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          },
          label: {
            formatter: '{b}\n{d}%'
          }
        }
      ]
    })
  } catch (error) {
    console.error('加载用户生命周期失败:', error)
  } finally {
    loading.value.lifecycle = false
  }
}

// ============================================================================
// 用户画像雷达图
// ============================================================================
const loadRadar = async () => {
  loading.value.radar = true
  try {
    const res = await axios.get(`${API_BASE}/visualization/user-profile`, {
      params: { month: selectedMonth.value }
    })
    radarData.value = res.data
    renderRadar()
  } catch (error) {
    console.error('加载用户画像失败:', error)
  } finally {
    loading.value.radar = false
  }
}

const renderRadar = () => {
  if (!radarData.value) return
  const data = radarData.value

  const chart = charts.radar || echarts.init(document.getElementById('radar-chart'))
  charts.radar = chart

  const indicators = [
    { name: '购买频率', max: 100 },
    { name: '活跃天数', max: 100 },
    { name: '领券率', max: 100 },
    { name: '转化率', max: 100 },
    { name: '商户多样性', max: 100 },
    { name: '用户新鲜度', max: 100 }
  ]

  const segmentKey = radarSegment.value === '高价值用户' ? 'high_value' : 'normal'
  const values = data[segmentKey] || [0, 0, 0, 0, 0, 0]

  chart.setOption({
    tooltip: { trigger: 'item' },
    legend: { data: [radarSegment.value], bottom: 0 },
    radar: {
      indicator: indicators,
      splitNumber: 4,
      axisName: { color: '#606266', fontSize: 12 }
    },
    series: [
      {
        type: 'radar',
        data: [
          {
            name: radarSegment.value,
            value: values,
            areaStyle: { opacity: 0.25 },
            itemStyle: { color: radarSegment.value === '高价值用户' ? '#409EFF' : '#67C23A' }
          }
        ]
      }
    ]
  })
}

// ============================================================================
// 行为时段热力图
// ============================================================================
const loadHeatmap = async () => {
  loading.value.heatmap = true
  try {
    const res = await axios.get(`${API_BASE}/visualization/behavior-heatmap`, {
      params: { month: selectedMonth.value }
    })
    const data = res.data

    const chart = echarts.init(document.getElementById('heatmap-chart'))
    charts.heatmap = chart

    const hours = Array.from({ length: 24 }, (_, i) => `${i}时`)
    const days = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']

    chart.setOption({
      tooltip: {
        position: 'top',
        formatter: params => {
          return `${days[params.data[1]]} ${hours[params.data[0]]}<br/>行为次数: ${params.data[2]}`
        }
      },
      grid: { top: '10%', left: '10%', right: '5%', bottom: '15%' },
      xAxis: {
        type: 'category',
        data: hours,
        axisLabel: { fontSize: 11 },
        splitArea: { show: true }
      },
      yAxis: {
        type: 'category',
        data: days,
        splitArea: { show: true }
      },
      visualMap: {
        min: 0,
        max: data.max_value || 100,
        calculable: true,
        orient: 'horizontal',
        left: 'center',
        bottom: '0%',
        inRange: { color: ['#EBF5FF', '#409EFF', '#003580'] }
      },
      series: [
        {
          type: 'heatmap',
          data: data.matrix,
          label: { show: false },
          emphasis: {
            itemStyle: { shadowBlur: 10, shadowColor: 'rgba(0, 0, 0, 0.5)' }
          }
        }
      ]
    })
  } catch (error) {
    console.error('加载热力图失败:', error)
  } finally {
    loading.value.heatmap = false
  }
}

// ============================================================================
// 统一加载
// ============================================================================
const loadAll = () => {
  loadStats()
  loadRFM()
  loadLifecycle()
  loadRadar()
  loadHeatmap()
}

onMounted(() => {
  loadAll()
})
</script>

<style scoped>
.user-analysis {
  padding: 20px;
}

h1 {
  margin-bottom: 20px;
  color: #303133;
}

.filter-card {
  margin-bottom: 20px;
  background: #f8f9fa;
}

.filter-label {
  font-size: 14px;
  color: #606266;
  margin-right: 8px;
}

.metrics-row {
  margin-bottom: 20px;
}

.metric-card {
  display: flex;
  align-items: center;
  gap: 20px;
}

.metric-content {
  flex: 1;
}

.metric-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 5px;
}

.metric-label {
  font-size: 14px;
  color: #909399;
}

.charts-row {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
</style>
