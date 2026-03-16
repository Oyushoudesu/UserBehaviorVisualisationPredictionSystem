<!-- BehaviorFlow.vue
行为流分析页面：转化漏斗、行为路径桑基图、不同用户群体转化对比
Vue3 Composition API + Element Plus + ECharts + Axios
-->
<template>
  <div class="behavior-flow">
    <h1>行为流分析</h1>

    <!-- 筛选栏 -->
    <el-card shadow="never" class="filter-card">
      <el-row :gutter="20" align="middle">
        <el-col :span="6">
          <span class="filter-label">数据月份：</span>
          <el-select v-model="selectedMonth" @change="loadAll" style="width: 140px">
            <el-option v-for="m in 6" :key="m" :label="`第${m}月`" :value="m" />
          </el-select>
        </el-col>
        <el-col :span="6">
          <span class="filter-label">场景：</span>
          <el-radio-group v-model="selectedPeriod" @change="loadAll">
            <el-radio-button label="all">全部</el-radio-button>
            <el-radio-button label="regular">平销期</el-radio-button>
            <el-radio-button label="promotion">促销期</el-radio-button>
          </el-radio-group>
        </el-col>
      </el-row>
    </el-card>

    <!-- 核心转化指标 -->
    <el-row :gutter="20" class="metrics-row">
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="metric-card">
            <el-icon :size="40" color="#409EFF"><Pointer /></el-icon>
            <div class="metric-content">
              <div class="metric-value">{{ funnelStats.click_users?.toLocaleString() || '-' }}</div>
              <div class="metric-label">点击用户数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="metric-card">
            <el-icon :size="40" color="#67C23A"><Ticket /></el-icon>
            <div class="metric-content">
              <div class="metric-value">{{ funnelStats.coupon_users?.toLocaleString() || '-' }}</div>
              <div class="metric-label">领券用户数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="metric-card">
            <el-icon :size="40" color="#E6A23C"><ShoppingCart /></el-icon>
            <div class="metric-content">
              <div class="metric-value">{{ funnelStats.purchase_users?.toLocaleString() || '-' }}</div>
              <div class="metric-label">购买用户数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="metric-card">
            <el-icon :size="40" color="#F56C6C"><TrendCharts /></el-icon>
            <div class="metric-content">
              <div class="metric-value">{{ funnelStats.overall_cvr?.toFixed(2) || '-' }}%</div>
              <div class="metric-label">整体转化率</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表第一行：漏斗 + 桑基图 -->
    <el-row :gutter="20" class="charts-row">
      <el-col :span="10">
        <el-card shadow="hover">
          <template #header><span>用户转化漏斗</span></template>
          <div v-loading="loading.funnel" id="funnel-chart" style="height: 420px"></div>
        </el-card>
      </el-col>
      <el-col :span="14">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>用户行为路径桑基图</span>
              <el-tooltip content="展示用户从点击→领券→购买的流向分布" placement="top">
                <el-icon color="#909399"><QuestionFilled /></el-icon>
              </el-tooltip>
            </div>
          </template>
          <div v-loading="loading.sankey" id="sankey-chart" style="height: 420px"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表第二行：不同群体转化对比 + 月度转化趋势 -->
    <el-row :gutter="20" class="charts-row">
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header><span>不同用户群体转化率对比</span></template>
          <div v-loading="loading.group" id="group-chart" style="height: 380px"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header><span>月度转化率趋势</span></template>
          <div v-loading="loading.trend" id="cvr-trend-chart" style="height: 380px"></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Pointer, Ticket, ShoppingCart, TrendCharts, QuestionFilled } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import axios from 'axios'

const API_BASE = 'http://localhost:8000/api/v1'

const selectedMonth = ref(4)
const selectedPeriod = ref('all')
const funnelStats = ref({})
const loading = ref({ funnel: false, sankey: false, group: false, trend: false })

// ============================================================================
// 转化漏斗
// ============================================================================
const loadFunnel = async () => {
  loading.value.funnel = true
  try {
    const res = await axios.get(`${API_BASE}/visualization/conversion-funnel`, {
      params: { month: selectedMonth.value, period: selectedPeriod.value }
    })
    const data = res.data.funnel
    // 顶部指标
    funnelStats.value = {
      click_users: data.find(d => d.stage === '点击用户')?.count,
      coupon_users: data.find(d => d.stage === '领券用户')?.count,
      purchase_users: data.find(d => d.stage === '购买用户')?.count,
      overall_cvr: res.data.cvr
    }

    const chart = echarts.init(document.getElementById('funnel-chart'))
    const maxVal = data[0]?.count || 1
    chart.setOption({
      tooltip: { trigger: 'item', formatter: '{b}: {c} 人' },
      color: ['#409EFF', '#67C23A', '#E6A23C', '#F56C6C'],
      series: [{
        type: 'funnel',
        left: '10%', width: '80%',
        min: 0, max: maxVal,
        minSize: '20%', maxSize: '100%',
        sort: 'descending',
        gap: 4,
        data: data.map(item => ({ name: item.stage, value: item.count })),
        label: { show: true, position: 'inside', formatter: '{b}\n{c}人' },
        itemStyle: { borderWidth: 0 }
      }]
    })
  } catch (e) {
    console.error('加载漏斗失败:', e)
  } finally {
    loading.value.funnel = false
  }
}

// ============================================================================
// 桑基图
// ============================================================================
const loadSankey = async () => {
  loading.value.sankey = true
  try {
    const res = await axios.get(`${API_BASE}/visualization/behavior-sankey`, {
      params: { month: selectedMonth.value, period: selectedPeriod.value }
    })
    const { nodes, links } = res.data

    const chart = echarts.init(document.getElementById('sankey-chart'))
    chart.setOption({
      tooltip: {
        trigger: 'item',
        triggerOn: 'mousemove',
        formatter: params => {
          if (params.dataType === 'edge') {
            return `${params.data.source} → ${params.data.target}<br/>用户数: ${params.data.value}`
          }
          return params.name
        }
      },
      series: [{
        type: 'sankey',
        layout: 'none',
        emphasis: { focus: 'adjacency' },
        data: nodes,
        links,
        lineStyle: { color: 'gradient', curveness: 0.5, opacity: 0.5 },
        label: { color: '#303133', fontSize: 13 },
        nodeWidth: 20,
        nodeGap: 12,
        itemStyle: { borderWidth: 0 }
      }]
    })
  } catch (e) {
    console.error('加载桑基图失败:', e)
  } finally {
    loading.value.sankey = false
  }
}

// ============================================================================
// 用户群体转化率对比（分组柱状图）
// ============================================================================
const loadGroupConversion = async () => {
  loading.value.group = true
  try {
    const res = await axios.get(`${API_BASE}/visualization/group-conversion`, {
      params: { month: selectedMonth.value }
    })
    const data = res.data

    const chart = echarts.init(document.getElementById('group-chart'))
    chart.setOption({
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
      legend: { data: ['CTR', '领券率', '核销率', 'CVR'], bottom: 0 },
      grid: { left: '3%', right: '4%', bottom: '12%', containLabel: true },
      xAxis: {
        type: 'category',
        data: data.groups,
        axisLabel: { fontSize: 12 }
      },
      yAxis: { type: 'value', name: '转化率(%)', max: 100 },
      color: ['#409EFF', '#67C23A', '#E6A23C', '#F56C6C'],
      series: [
        { name: 'CTR', type: 'bar', data: data.ctr, barMaxWidth: 30 },
        { name: '领券率', type: 'bar', data: data.coupon_rate, barMaxWidth: 30 },
        { name: '核销率', type: 'bar', data: data.redemption_rate, barMaxWidth: 30 },
        { name: 'CVR', type: 'bar', data: data.cvr, barMaxWidth: 30 }
      ]
    })
  } catch (e) {
    console.error('加载群体转化失败:', e)
  } finally {
    loading.value.group = false
  }
}

// ============================================================================
// 月度 CVR 趋势折线图
// ============================================================================
const loadCvrTrend = async () => {
  loading.value.trend = true
  try {
    const res = await axios.get(`${API_BASE}/visualization/monthly-stats`)
    const data = res.data.data

    const chart = echarts.init(document.getElementById('cvr-trend-chart'))
    chart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['CVR(%)', '领券率(%)'], bottom: 0 },
      grid: { left: '3%', right: '4%', bottom: '12%', containLabel: true },
      xAxis: { type: 'category', data: data.map(d => `${d.month}月`) },
      yAxis: { type: 'value', name: '转化率(%)', min: 0 },
      color: ['#F56C6C', '#E6A23C'],
      series: [
        {
          name: 'CVR(%)', type: 'line', smooth: true,
          data: data.map(d => d.cvr),
          areaStyle: { opacity: 0.1 },
          symbol: 'circle', symbolSize: 8
        },
        {
          name: '领券率(%)', type: 'line', smooth: true,
          data: data.map(d => d.coupons && d.purchases
            ? parseFloat(((d.coupons / (d.purchases + d.coupons)) * 100).toFixed(2))
            : 0),
          areaStyle: { opacity: 0.1 },
          symbol: 'circle', symbolSize: 8
        }
      ]
    })
  } catch (e) {
    console.error('加载CVR趋势失败:', e)
  } finally {
    loading.value.trend = false
  }
}

const loadAll = () => {
  loadFunnel()
  loadSankey()
  loadGroupConversion()
  loadCvrTrend()
}

onMounted(() => loadAll())
</script>

<style scoped>
.behavior-flow { padding: 20px; }
h1 { margin-bottom: 20px; color: #303133; }
.filter-card { margin-bottom: 20px; background: #f8f9fa; }
.filter-label { font-size: 14px; color: #606266; margin-right: 8px; }
.metrics-row { margin-bottom: 20px; }
.metric-card { display: flex; align-items: center; gap: 20px; }
.metric-content { flex: 1; }
.metric-value { font-size: 28px; font-weight: bold; color: #303133; margin-bottom: 5px; }
.metric-label { font-size: 14px; color: #909399; }
.charts-row { margin-bottom: 20px; }
.card-header { display: flex; align-items: center; justify-content: space-between; }
</style>
