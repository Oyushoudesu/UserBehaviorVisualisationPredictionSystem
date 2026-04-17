<template>
  <div class="page">

    <!-- 筛选栏 -->
    <div class="filter-bar">
      <div class="filter-group">
        <span class="filter-label">数据月份</span>
        <el-select v-model="selectedMonth" @change="loadAll" style="width:120px" size="small">
          <el-option v-for="m in [4,5,6]" :key="m" :label="`第${m}月`" :value="m" />
        </el-select>
      </div>
      <div class="filter-group">
        <span class="filter-label">场景</span>
        <el-radio-group v-model="selectedPeriod" @change="loadAll" size="small">
          <el-radio-button label="all">全部</el-radio-button>
          <el-radio-button label="regular">平销期</el-radio-button>
          <el-radio-button label="promotion">促销期</el-radio-button>
        </el-radio-group>
      </div>
    </div>

    <!-- 指标卡 -->
    <el-row :gutter="16" class="metrics-row">
      <el-col :span="6">
        <div class="stat-card stat-blue">
          <div class="stat-bg-icon"><el-icon :size="52" color="rgba(255,255,255,0.12)"><Pointer /></el-icon></div>
          <div class="stat-top"><div class="stat-icon-wrap"><el-icon :size="18" color="#fff"><Pointer /></el-icon></div></div>
          <div class="stat-value">{{ funnelStats.click_users?.toLocaleString() || '—' }}</div>
          <div class="stat-label">点击用户数</div>
          <div class="stat-bar"><div class="stat-bar-fill" style="width:100%"></div></div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card stat-green">
          <div class="stat-bg-icon"><el-icon :size="52" color="rgba(255,255,255,0.12)"><Ticket /></el-icon></div>
          <div class="stat-top"><div class="stat-icon-wrap"><el-icon :size="18" color="#fff"><Ticket /></el-icon></div></div>
          <div class="stat-value">{{ funnelStats.coupon_users?.toLocaleString() || '—' }}</div>
          <div class="stat-label">领券用户数</div>
          <div class="stat-bar"><div class="stat-bar-fill" style="width:70%"></div></div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card stat-orange">
          <div class="stat-bg-icon"><el-icon :size="52" color="rgba(255,255,255,0.12)"><ShoppingCart /></el-icon></div>
          <div class="stat-top"><div class="stat-icon-wrap"><el-icon :size="18" color="#fff"><ShoppingCart /></el-icon></div></div>
          <div class="stat-value">{{ funnelStats.purchase_users?.toLocaleString() || '—' }}</div>
          <div class="stat-label">购买用户数</div>
          <div class="stat-bar"><div class="stat-bar-fill" style="width:50%"></div></div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card stat-purple">
          <div class="stat-bg-icon"><el-icon :size="52" color="rgba(255,255,255,0.12)"><TrendCharts /></el-icon></div>
          <div class="stat-top"><div class="stat-icon-wrap"><el-icon :size="18" color="#fff"><TrendCharts /></el-icon></div></div>
          <div class="stat-value">{{ funnelStats.overall_cvr?.toFixed(2) || '—' }}%</div>
          <div class="stat-label">整体转化率</div>
          <div class="stat-bar"><div class="stat-bar-fill" :style="`width:${Math.min(funnelStats.overall_cvr || 0, 100)}%`"></div></div>
        </div>
      </el-col>
    </el-row>

    <!-- 图表行1: 漏斗 + 桑基 -->
    <el-row :gutter="16" class="charts-row">
      <el-col :span="9">
        <div class="chart-card">
          <div class="chart-header" style="border-left-color:#3b82f6">
            <div class="chart-header-left">
              <span class="chart-dot" style="background:#3b82f6;box-shadow:0 0 6px rgba(59,130,246,0.6)"></span>
              <span class="chart-title">用户转化漏斗（含阶段转化率）</span>
            </div>
            <span class="chart-badge">{{ periodLabel }}</span>
          </div>
          <div v-loading="loading.funnel" id="funnel-chart" style="height:300px"></div>
        </div>
      </el-col>
      <el-col :span="15">
        <div class="chart-card">
          <div class="chart-header" style="border-left-color:#a855f7">
            <div class="chart-header-left">
              <span class="chart-dot" style="background:#a855f7;box-shadow:0 0 6px rgba(168,85,247,0.6)"></span>
              <span class="chart-title">用户行为路径桑基图</span>
            </div>
            <el-tooltip content="展示用户从点击→领券→购买的流向分布" placement="top">
              <span class="chart-badge" style="cursor:help">说明</span>
            </el-tooltip>
          </div>
          <div v-loading="loading.sankey" id="sankey-chart" style="height:300px"></div>
        </div>
      </el-col>
    </el-row>

    <!-- 图表行2: 分群转化率 + 分时段CVR -->
    <el-row :gutter="16" class="charts-row">
      <el-col :span="11">
        <div class="chart-card">
          <div class="chart-header" style="border-left-color:#10b981">
            <div class="chart-header-left">
              <span class="chart-dot" style="background:#10b981;box-shadow:0 0 6px rgba(16,185,129,0.6)"></span>
              <span class="chart-title">不同用户群体转化率对比</span>
            </div>
            <span class="chart-badge">{{ selectedMonth }}月</span>
          </div>
          <div v-loading="loading.group" id="group-chart" style="height:280px"></div>
        </div>
      </el-col>
      <el-col :span="13">
        <div class="chart-card">
          <div class="chart-header" style="border-left-color:#06b6d4">
            <div class="chart-header-left">
              <span class="chart-dot" style="background:#06b6d4;box-shadow:0 0 6px rgba(6,182,212,0.6)"></span>
              <span class="chart-title">分时段购买量与转化率</span>
            </div>
            <span class="chart-badge">全周期·小时维度</span>
          </div>
          <div v-loading="loading.hourly" id="hourly-chart" style="height:280px"></div>
        </div>
      </el-col>
    </el-row>

    <!-- 图表行3: 月度CVR趋势 + 月度用户留存 -->
    <el-row :gutter="16" class="charts-row">
      <el-col :span="12">
        <div class="chart-card">
          <div class="chart-header" style="border-left-color:#f43f5e">
            <div class="chart-header-left">
              <span class="chart-dot" style="background:#f43f5e;box-shadow:0 0 6px rgba(244,63,94,0.6)"></span>
              <span class="chart-title">月度转化率趋势</span>
            </div>
            <span class="chart-badge">1-6月</span>
          </div>
          <div v-loading="loading.trend" id="cvr-trend-chart" style="height:280px"></div>
        </div>
      </el-col>
      <el-col :span="12">
        <div class="chart-card">
          <div class="chart-header" style="border-left-color:#f59e0b">
            <div class="chart-header-left">
              <span class="chart-dot" style="background:#f59e0b;box-shadow:0 0 6px rgba(245,158,11,0.6)"></span>
              <span class="chart-title">月度用户留存 / 流失 / 新增</span>
            </div>
            <span class="chart-badge">4→5月 / 5→6月</span>
          </div>
          <div v-loading="loading.retention" id="retention-chart" style="height:280px"></div>
        </div>
      </el-col>
    </el-row>

  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { Pointer, Ticket, ShoppingCart, TrendCharts } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import axiosInstance from '@/api/axiosInstance'
import { useTheme } from '@/composables/useTheme'

const { isDark } = useTheme()

const selectedMonth = ref(4)
const selectedPeriod = ref('all')
const funnelStats = ref({})
const loading = ref({ funnel: false, sankey: false, group: false, trend: false, hourly: false, retention: false })
const cache = ref({ funnel: null, sankey: null, group: null, trend: null, hourly: null, retention: null })

const periodLabel = computed(() => ({ all: '全部', regular: '平销期', promotion: '促销期' }[selectedPeriod.value]))

const ecInit = (id) => {
  const el = document.getElementById(id)
  if (!el) return null
  echarts.getInstanceByDom(el)?.dispose()
  return echarts.init(el, isDark.value ? 'dark' : null)
}

const renderFunnel = () => {
  const data = cache.value.funnel
  if (!data) return
  const chart = ecInit('funnel-chart')
  if (!chart) return
  // 计算阶段间转化率
  const stageRates = data.map((item, i) => {
    if (i === 0) return ''
    const prev = data[i - 1].count
    return prev > 0 ? `转化率 ${(item.count / prev * 100).toFixed(1)}%` : ''
  })
  chart.setOption({
    tooltip: { trigger: 'item', formatter: params => {
      const idx = data.findIndex(d => d.stage === params.name)
      const rate = idx > 0 && data[idx-1].count > 0 ? `<br/>较上一层: ${(data[idx].count / data[idx-1].count * 100).toFixed(1)}%` : ''
      return `${params.name}: ${params.value.toLocaleString()}人${rate}`
    }},
    color: ['#3b82f6', '#10b981', '#f59e0b', '#f43f5e'],
    series: [{
      type: 'funnel', left: '8%', width: '60%',
      min: 0, max: data[0]?.count || 1, minSize: '18%', maxSize: '100%',
      sort: 'descending', gap: 4,
      data: data.map(item => ({ name: item.stage, value: item.count })),
      label: {
        show: true, position: 'inside',
        formatter: params => {
          const idx = data.findIndex(d => d.stage === params.name)
          const rate = idx > 0 && data[idx-1].count > 0
            ? `\n↓ ${(data[idx].count / data[idx-1].count * 100).toFixed(1)}%`
            : ''
          return `${params.name}\n${params.value.toLocaleString()}人${rate}`
        },
        color: '#fff', fontSize: 11, lineHeight: 16
      },
      itemStyle: { borderWidth: 0, borderRadius: 3 }
    }]
  })
}

const renderSankey = () => {
  const data = cache.value.sankey
  if (!data) return
  const chart = ecInit('sankey-chart')
  if (!chart) return
  chart.setOption({
    tooltip: {
      trigger: 'item', triggerOn: 'mousemove',
      formatter: params => params.dataType === 'edge'
        ? `${params.data.source} → ${params.data.target}<br/>用户数: ${params.data.value.toLocaleString()}`
        : params.name
    },
    series: [{
      type: 'sankey', layout: 'none', emphasis: { focus: 'adjacency' },
      data: data.nodes, links: data.links,
      lineStyle: { color: 'gradient', curveness: 0.5, opacity: 0.5 },
      label: { fontSize: 12 }, nodeWidth: 18, nodeGap: 10, itemStyle: { borderWidth: 0 }
    }]
  })
}

const renderGroup = () => {
  const data = cache.value.group
  if (!data) return
  const chart = ecInit('group-chart')
  if (!chart) return
  chart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' },
      formatter: params => `${params[0].name}<br/>${params.map(p => `${p.marker}${p.seriesName}: <b>${p.value}%</b>`).join('<br/>')}` },
    legend: { data: ['CTR', '领券率', '核销率', 'CVR'], bottom: 0, itemHeight: 10, textStyle: { fontSize: 11 } },
    grid: { left: '3%', right: '4%', bottom: '16%', top: '6%', containLabel: true },
    xAxis: { type: 'category', data: data.groups, axisLabel: { color: '#334155', fontSize: 11 } },
    yAxis: { type: 'value', name: '(%)', max: 100, splitLine: { lineStyle: { type: 'dashed', color: '#f1f5f9' } }, axisLabel: { color: '#94a3b8', fontSize: 11 } },
    color: ['#3b82f6', '#10b981', '#f59e0b', '#f43f5e'],
    series: [
      { name: 'CTR',   type: 'bar', data: data.ctr,             barMaxWidth: 18, itemStyle: { borderRadius: [3,3,0,0] } },
      { name: '领券率', type: 'bar', data: data.coupon_rate,     barMaxWidth: 18, itemStyle: { borderRadius: [3,3,0,0] } },
      { name: '核销率', type: 'bar', data: data.redemption_rate, barMaxWidth: 18, itemStyle: { borderRadius: [3,3,0,0] } },
      { name: 'CVR',   type: 'bar', data: data.cvr,             barMaxWidth: 18, itemStyle: { borderRadius: [3,3,0,0] } }
    ]
  })
}

const renderTrend = () => {
  const data = cache.value.trend
  if (!data) return
  const chart = ecInit('cvr-trend-chart')
  if (!chart) return
  const months = data.map(d => `${d.month}月`)
  const cvr = data.map(d => d.cvr)
  const couponRate = data.map(d => d.coupons && d.purchases
    ? parseFloat(((d.coupons / (d.purchases + d.coupons)) * 100).toFixed(2)) : 0)
  const purchases = data.map(d => d.purchases)
  chart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['购买量', 'CVR(%)', '领券率(%)'], bottom: 0, itemHeight: 10, textStyle: { fontSize: 11 } },
    grid: { left: '3%', right: '6%', bottom: '16%', top: '8%', containLabel: true },
    xAxis: { type: 'category', data: months, axisLabel: { color: '#334155', fontSize: 12 } },
    yAxis: [
      { type: 'value', name: '购买量', splitLine: { lineStyle: { type: 'dashed', color: '#f1f5f9' } }, axisLabel: { color: '#94a3b8', fontSize: 11 } },
      { type: 'value', name: '转化率(%)', min: 0, splitLine: { show: false }, axisLabel: { color: '#94a3b8', fontSize: 11 } }
    ],
    series: [
      { name: '购买量', type: 'bar', data: purchases, barMaxWidth: 28, yAxisIndex: 0,
        itemStyle: { color: new echarts.graphic.LinearGradient(0,0,0,1,[{offset:0,color:'#93c5fd'},{offset:1,color:'#3b82f6'}]), borderRadius: [4,4,0,0] } },
      { name: 'CVR(%)', type: 'line', yAxisIndex: 1, smooth: true, data: cvr,
        itemStyle: { color: '#f43f5e' }, symbol: 'circle', symbolSize: 7, lineStyle: { width: 2 },
        label: { show: true, position: 'top', formatter: '{c}%', color: '#f43f5e', fontSize: 11 } },
      { name: '领券率(%)', type: 'line', yAxisIndex: 1, smooth: true, data: couponRate,
        itemStyle: { color: '#f59e0b' }, symbol: 'circle', symbolSize: 7, lineStyle: { width: 2 } }
    ]
  })
}

const renderHourly = () => {
  const data = cache.value.hourly
  if (!data || !data.length) return
  const chart = ecInit('hourly-chart')
  if (!chart) return
  const hours = data.map(d => `${d.hour}时`)
  const purchases = data.map(d => d.purchases)
  const cvr = data.map(d => d.cvr)
  chart.setOption({
    tooltip: { trigger: 'axis', formatter: params => {
      const bar = params.find(p => p.seriesName === '购买量')
      const line = params.find(p => p.seriesName === 'CVR(%)')
      return `${params[0].name}<br/>购买量: <b>${bar?.value}</b><br/>CVR: <b>${line?.value}%</b>`
    }},
    legend: { data: ['购买量', 'CVR(%)'], bottom: 0, itemHeight: 10, textStyle: { fontSize: 11 } },
    grid: { left: '3%', right: '6%', bottom: '14%', top: '6%', containLabel: true },
    xAxis: { type: 'category', data: hours, axisLabel: { interval: 1, color: '#334155', fontSize: 10 }, axisLine: { lineStyle: { color: '#e2e8f0' } } },
    yAxis: [
      { type: 'value', name: '购买量', splitLine: { lineStyle: { type: 'dashed', color: '#f1f5f9' } }, axisLabel: { color: '#94a3b8', fontSize: 11 } },
      { type: 'value', name: 'CVR(%)', min: 0, splitLine: { show: false }, axisLabel: { color: '#94a3b8', fontSize: 11 } }
    ],
    series: [
      { name: '购买量', type: 'bar', data: purchases, barMaxWidth: 18, yAxisIndex: 0,
        itemStyle: { color: new echarts.graphic.LinearGradient(0,0,0,1,[{offset:0,color:'#67e8f9'},{offset:1,color:'#06b6d4'}]), borderRadius: [3,3,0,0] } },
      { name: 'CVR(%)', type: 'line', yAxisIndex: 1, smooth: true, data: cvr,
        itemStyle: { color: '#f43f5e' }, symbol: 'circle', symbolSize: 5, lineStyle: { width: 2 } }
    ]
  })
}

const renderRetention = () => {
  const data = cache.value.retention
  if (!data || !data.length) return
  const chart = ecInit('retention-chart')
  if (!chart) return
  const labels = data.map(d => d.label)
  const retained = data.map(d => d.retained_users)
  const newUsers = data.map(d => d.new_users)
  const lost = data.map(d => d.lost_users)
  const rates = data.map(d => d.retention_rate)
  chart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' },
      formatter: params => {
        const idx = labels.indexOf(params[0].name)
        return `${params[0].name}<br/>
          留存用户: <b>${retained[idx].toLocaleString()}</b><br/>
          新增用户: <b>${newUsers[idx].toLocaleString()}</b><br/>
          流失用户: <b>${lost[idx].toLocaleString()}</b><br/>
          留存率: <b>${rates[idx]}%</b>`
      }
    },
    legend: { data: ['留存用户', '新增用户', '流失用户'], bottom: 0, itemHeight: 10, textStyle: { fontSize: 11 } },
    grid: { left: '3%', right: '8%', bottom: '16%', top: '8%', containLabel: true },
    xAxis: { type: 'category', data: labels, axisLabel: { color: '#334155', fontSize: 12 } },
    yAxis: [
      { type: 'value', name: '用户数', splitLine: { lineStyle: { type: 'dashed', color: '#f1f5f9' } }, axisLabel: { color: '#94a3b8', fontSize: 11 } },
      { type: 'value', name: '留存率(%)', min: 0, max: 100, splitLine: { show: false }, axisLabel: { color: '#94a3b8', fontSize: 11 } }
    ],
    series: [
      { name: '留存用户', type: 'bar', stack: 'total', data: retained, barMaxWidth: 50,
        itemStyle: { color: '#10b981', borderRadius: [0,0,0,0] } },
      { name: '新增用户', type: 'bar', stack: 'total', data: newUsers, barMaxWidth: 50,
        itemStyle: { color: '#3b82f6' } },
      { name: '流失用户', type: 'bar', stack: 'total', data: lost, barMaxWidth: 50,
        itemStyle: { color: '#f43f5e', borderRadius: [4,4,0,0] } },
      { name: '留存率', type: 'line', yAxisIndex: 1, data: rates,
        symbol: 'circle', symbolSize: 10, lineStyle: { width: 0 },
        itemStyle: { color: '#f59e0b' },
        label: { show: true, formatter: '{c}%', color: '#f59e0b', fontWeight: 'bold', fontSize: 13, position: 'top' }
      }
    ]
  })
}

const loadFunnel = async () => {
  loading.value.funnel = true
  try {
    const res = await axiosInstance.get('/visualization/conversion-funnel', { params: { month: selectedMonth.value, period: selectedPeriod.value } })
    cache.value.funnel = res.data.funnel
    const clickCount = res.data.funnel.find(d => d.stage === '点击用户')?.count || 0
    const couponCount = res.data.funnel.find(d => d.stage === '领券用户')?.count || 0
    const purchaseCount = res.data.funnel.find(d => d.stage === '购买用户')?.count || 0
    funnelStats.value = {
      click_users: clickCount,
      coupon_users: couponCount,
      purchase_users: purchaseCount,
      overall_cvr: clickCount > 0 ? parseFloat((purchaseCount / clickCount * 100).toFixed(2)) : 0
    }
    renderFunnel()
  } catch (e) { console.error(e) } finally { loading.value.funnel = false }
}

const loadSankey = async () => {
  loading.value.sankey = true
  try {
    const res = await axiosInstance.get('/visualization/behavior-sankey', { params: { month: selectedMonth.value, period: selectedPeriod.value } })
    cache.value.sankey = res.data; renderSankey()
  } catch (e) { console.error(e) } finally { loading.value.sankey = false }
}

const loadGroup = async () => {
  loading.value.group = true
  try {
    const res = await axiosInstance.get('/visualization/group-conversion', { params: { month: selectedMonth.value } })
    cache.value.group = res.data; renderGroup()
  } catch (e) { console.error(e) } finally { loading.value.group = false }
}

const loadTrend = async () => {
  loading.value.trend = true
  try {
    const res = await axiosInstance.get('/visualization/monthly-stats')
    cache.value.trend = res.data.data; renderTrend()
  } catch (e) { console.error(e) } finally { loading.value.trend = false }
}

const loadHourly = async () => {
  loading.value.hourly = true
  try {
    const res = await axiosInstance.get('/visualization/hourly-cvr')
    cache.value.hourly = res.data.data; renderHourly()
  } catch (e) { console.error(e) } finally { loading.value.hourly = false }
}

const loadRetention = async () => {
  loading.value.retention = true
  try {
    const res = await axiosInstance.get('/visualization/monthly-retention')
    cache.value.retention = res.data.data; renderRetention()
  } catch (e) { console.error(e) } finally { loading.value.retention = false }
}

const loadAll = () => { loadFunnel(); loadSankey(); loadGroup(); loadTrend(); loadHourly(); loadRetention() }

watch(isDark, () => { renderFunnel(); renderSankey(); renderGroup(); renderTrend(); renderHourly(); renderRetention() })

onMounted(() => loadAll())
</script>

<style scoped>
.page { padding: 16px 20px; background: var(--bg-page); min-height: 100%; }

.filter-bar { display: flex; align-items: center; gap: 24px; background: var(--bg-filter); border: 1px solid var(--border); border-left: 3px solid #3b82f6; border-radius: 10px; padding: 12px 18px; margin-bottom: 16px; box-shadow: 0 1px 6px rgba(0,0,0,0.05); }
.filter-group { display: flex; align-items: center; gap: 8px; }
.filter-label { font-size: 12px; font-weight: 600; color: var(--text-muted); white-space: nowrap; }

.metrics-row { margin-bottom: 16px; }
.stat-card { border-radius: 12px; padding: 14px 16px; position: relative; overflow: hidden; transition: transform 0.2s; }
.stat-card:hover { transform: translateY(-2px); }
.stat-blue   { background: linear-gradient(135deg, #2563eb, #06b6d4); box-shadow: 0 4px 16px rgba(37,99,235,0.3); }
.stat-green  { background: linear-gradient(135deg, #059669, #10b981); box-shadow: 0 4px 16px rgba(5,150,105,0.3); }
.stat-orange { background: linear-gradient(135deg, #d97706, #f59e0b); box-shadow: 0 4px 16px rgba(217,119,6,0.3); }
.stat-purple { background: linear-gradient(135deg, #7c3aed, #a855f7); box-shadow: 0 4px 16px rgba(124,58,237,0.3); }
.stat-bg-icon { position: absolute; right: -8px; bottom: -8px; pointer-events: none; }
.stat-top { margin-bottom: 8px; }
.stat-icon-wrap { width: 34px; height: 34px; background: rgba(255,255,255,0.2); border-radius: 8px; display: flex; align-items: center; justify-content: center; }
.stat-value { font-size: 22px; font-weight: 800; color: #fff; line-height: 1.2; margin-bottom: 3px; }
.stat-label { font-size: 12px; color: rgba(255,255,255,0.75); margin-bottom: 10px; }
.stat-bar { height: 3px; background: rgba(255,255,255,0.2); border-radius: 2px; overflow: hidden; }
.stat-bar-fill { height: 100%; background: rgba(255,255,255,0.55); border-radius: 2px; transition: width 0.6s; }

.charts-row { margin-bottom: 14px; }
.chart-card { background: var(--bg-card); border-radius: 12px; overflow: hidden; box-shadow: 0 1px 8px rgba(0,0,0,0.06); transition: box-shadow 0.2s; }
.chart-card:hover { box-shadow: 0 4px 18px rgba(0,0,0,0.1); }
.chart-header { display: flex; align-items: center; justify-content: space-between; padding: 11px 16px; border-bottom: 1px solid var(--border); border-left: 3px solid transparent; background: linear-gradient(90deg, rgba(0,0,0,0.02) 0%, transparent 100%); }
.chart-header-left { display: flex; align-items: center; gap: 7px; }
.chart-dot { display: inline-block; width: 7px; height: 7px; border-radius: 50%; flex-shrink: 0; }
.chart-title { font-size: 13px; font-weight: 600; color: var(--text-primary); }
.chart-badge { font-size: 11px; padding: 2px 8px; background: var(--bg-page); color: var(--text-secondary); border-radius: 8px; font-weight: 500; }
</style>
