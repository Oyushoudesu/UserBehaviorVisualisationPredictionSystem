<template>
  <div class="page">

    <!-- 筛选栏 -->
    <div class="filter-bar">
      <div class="filter-group">
        <span class="filter-label">数据周期</span>
        <el-select v-model="selectedMonth" @change="loadAll" style="width:150px" size="small">
          <el-option v-for="m in [4,5,6]" :key="m" :label="`第${m}月`" :value="m" />
        </el-select>
      </div>
      <el-tag type="info" size="small" style="margin-left:4px">
        基于 user_features_month{{ selectedMonth }}.csv
      </el-tag>
    </div>

    <!-- 指标卡 -->
    <el-row :gutter="16" class="metrics-row">
      <el-col :span="6">
        <div class="stat-card stat-blue">
          <div class="stat-bg-icon"><el-icon :size="52" color="rgba(255,255,255,0.12)"><User /></el-icon></div>
          <div class="stat-top"><div class="stat-icon-wrap"><el-icon :size="18" color="#fff"><User /></el-icon></div></div>
          <div class="stat-value">{{ stats.total_users?.toLocaleString() || '—' }}</div>
          <div class="stat-label">分析用户数</div>
          <div class="stat-bar"><div class="stat-bar-fill" style="width:100%"></div></div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card stat-green">
          <div class="stat-bg-icon"><el-icon :size="52" color="rgba(255,255,255,0.12)"><Star /></el-icon></div>
          <div class="stat-top"><div class="stat-icon-wrap"><el-icon :size="18" color="#fff"><Star /></el-icon></div></div>
          <div class="stat-value">{{ stats.high_value_users?.toLocaleString() || '—' }}</div>
          <div class="stat-label">高价值用户</div>
          <div class="stat-bar"><div class="stat-bar-fill" style="width:65%"></div></div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card stat-orange">
          <div class="stat-bg-icon"><el-icon :size="52" color="rgba(255,255,255,0.12)"><Clock /></el-icon></div>
          <div class="stat-top"><div class="stat-icon-wrap"><el-icon :size="18" color="#fff"><Clock /></el-icon></div></div>
          <div class="stat-value">{{ stats.avg_recency?.toFixed(0) || '—' }} 天</div>
          <div class="stat-label">平均最近购买间隔</div>
          <div class="stat-bar"><div class="stat-bar-fill" style="width:55%"></div></div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card stat-red">
          <div class="stat-bg-icon"><el-icon :size="52" color="rgba(255,255,255,0.12)"><Warning /></el-icon></div>
          <div class="stat-top"><div class="stat-icon-wrap"><el-icon :size="18" color="#fff"><Warning /></el-icon></div></div>
          <div class="stat-value">{{ stats.churn_risk_users?.toLocaleString() || '—' }}</div>
          <div class="stat-label">流失风险用户</div>
          <div class="stat-bar"><div class="stat-bar-fill" style="width:30%"></div></div>
        </div>
      </el-col>
    </el-row>

    <!-- 图表行1: RFM散点 + 生命周期饼 -->
    <el-row :gutter="16" class="charts-row">
      <el-col :span="14">
        <div class="chart-card">
          <div class="chart-header" style="border-left-color:#3b82f6">
            <div class="chart-header-left">
              <span class="chart-dot" style="background:#3b82f6;box-shadow:0 0 6px rgba(59,130,246,0.6)"></span>
              <span class="chart-title">RFM 用户分层散点图</span>
            </div>
            <el-tooltip content="X轴：购买频率，Y轴：距今天数（越小越近），气泡大小：购买总量" placement="top">
              <span class="chart-badge" style="cursor:help">说明</span>
            </el-tooltip>
          </div>
          <div v-loading="loading.rfm" id="rfm-chart" style="height:300px"></div>
        </div>
      </el-col>
      <el-col :span="10">
        <div class="chart-card">
          <div class="chart-header" style="border-left-color:#a855f7">
            <div class="chart-header-left">
              <span class="chart-dot" style="background:#a855f7;box-shadow:0 0 6px rgba(168,85,247,0.6)"></span>
              <span class="chart-title">用户生命周期分布</span>
            </div>
          </div>
          <div v-loading="loading.lifecycle" id="lifecycle-chart" style="height:300px"></div>
        </div>
      </el-col>
    </el-row>

    <!-- 图表行2: 双段雷达 + 优惠券领/用率分群对比 -->
    <el-row :gutter="16" class="charts-row">
      <el-col :span="11">
        <div class="chart-card">
          <div class="chart-header" style="border-left-color:#10b981">
            <div class="chart-header-left">
              <span class="chart-dot" style="background:#10b981;box-shadow:0 0 6px rgba(16,185,129,0.6)"></span>
              <span class="chart-title">用户画像对比雷达（高价值 vs 普通）</span>
            </div>
          </div>
          <div v-loading="loading.radar" id="radar-chart" style="height:300px"></div>
        </div>
      </el-col>
      <el-col :span="13">
        <div class="chart-card">
          <div class="chart-header" style="border-left-color:#f43f5e">
            <div class="chart-header-left">
              <span class="chart-dot" style="background:#f43f5e;box-shadow:0 0 6px rgba(244,63,94,0.6)"></span>
              <span class="chart-title">各用户群优惠券领取 vs 核销率</span>
            </div>
            <span class="chart-badge">{{ selectedMonth }}月</span>
          </div>
          <div v-loading="loading.coupon" id="coupon-chart" style="height:300px"></div>
        </div>
      </el-col>
    </el-row>

    <!-- 图表行3: 活跃天数分布 + 跨月用户规模趋势 -->
    <el-row :gutter="16" class="charts-row">
      <el-col :span="11">
        <div class="chart-card">
          <div class="chart-header" style="border-left-color:#06b6d4">
            <div class="chart-header-left">
              <span class="chart-dot" style="background:#06b6d4;box-shadow:0 0 6px rgba(6,182,212,0.6)"></span>
              <span class="chart-title">用户活跃时长分布（生命周期跨度）</span>
            </div>
            <span class="chart-badge">{{ selectedMonth }}月</span>
          </div>
          <div v-loading="loading.featDist" id="feat-dist-chart" style="height:300px"></div>
        </div>
      </el-col>
      <el-col :span="13">
        <div class="chart-card">
          <div class="chart-header" style="border-left-color:#f59e0b">
            <div class="chart-header-left">
              <span class="chart-dot" style="background:#f59e0b;box-shadow:0 0 6px rgba(245,158,11,0.6)"></span>
              <span class="chart-title">跨月用户规模趋势（4-6月）</span>
            </div>
            <span class="chart-badge">月度对比</span>
          </div>
          <div v-loading="loading.monthTrend" id="month-trend-chart" style="height:300px"></div>
        </div>
      </el-col>
    </el-row>

    <!-- 图表行4: 热力图 -->
    <el-row :gutter="16" class="charts-row">
      <el-col :span="24">
        <div class="chart-card">
          <div class="chart-header" style="border-left-color:#f59e0b">
            <div class="chart-header-left">
              <span class="chart-dot" style="background:#f59e0b;box-shadow:0 0 6px rgba(245,158,11,0.6)"></span>
              <span class="chart-title">行为时段热力图（小时 × 星期）</span>
            </div>
            <span class="chart-badge">{{ selectedMonth }}月</span>
          </div>
          <div v-loading="loading.heatmap" id="heatmap-chart" style="height:280px"></div>
        </div>
      </el-col>
    </el-row>

  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { User, Star, Clock, Warning } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import axiosInstance from '@/api/axiosInstance'
import { useTheme } from '@/composables/useTheme'

const { isDark } = useTheme()

const selectedMonth = ref(4)
const stats = ref({})
const loading = ref({ rfm: false, lifecycle: false, radar: false, heatmap: false, coupon: false, featDist: false, monthTrend: false })
const cache = ref({ rfm: null, lifecycle: null, radar: null, heatmap: null, coupon: null, featDist: null })

const ecInit = (id) => {
  const el = document.getElementById(id)
  if (!el) return null
  echarts.getInstanceByDom(el)?.dispose()
  return echarts.init(el, isDark.value ? 'dark' : null)
}

const colorMap = { '高价值用户': '#3b82f6', '重要挽留用户': '#f59e0b', '新用户': '#10b981', '流失用户': '#f43f5e', '其他': '#94a3b8' }

const renderRFM = () => {
  const data = cache.value.rfm
  if (!data) return
  const chart = ecInit('rfm-chart')
  if (!chart) return
  const seriesMap = {}
  data.points.forEach(p => {
    if (!seriesMap[p.segment]) seriesMap[p.segment] = []
    seriesMap[p.segment].push([p.frequency, p.recency, p.purchase_count, p.user_id])
  })
  chart.setOption({
    tooltip: { formatter: params => { const [freq, rec, cnt, uid] = params.data; return `用户ID: ${uid}<br/>频率: ${freq}<br/>距今: ${rec}天<br/>总量: ${cnt}` } },
    legend: { data: Object.keys(seriesMap), bottom: 0, itemHeight: 10, textStyle: { fontSize: 11 } },
    grid: { left: '3%', right: '4%', bottom: '14%', top: '4%', containLabel: true },
    xAxis: { name: '购买频率', nameLocation: 'center', nameGap: 28, splitLine: { show: false } },
    yAxis: { name: '距今天数', nameLocation: 'center', nameGap: 40, inverse: true, splitLine: { lineStyle: { type: 'dashed' } } },
    series: Object.entries(seriesMap).map(([name, points]) => ({
      name, type: 'scatter', data: points,
      symbolSize: val => Math.max(5, Math.min(28, val[2] / 20)),
      itemStyle: { color: colorMap[name] || '#94a3b8', opacity: 0.75 }
    }))
  })
}

const renderLifecycle = () => {
  const data = cache.value.lifecycle
  if (!data) return
  const chart = ecInit('lifecycle-chart')
  if (!chart) return
  chart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
    legend: { orient: 'vertical', left: 'left', top: 'center', textStyle: { fontSize: 12 } },
    color: ['#3b82f6', '#10b981', '#f59e0b', '#f43f5e'],
    series: [{
      type: 'pie', radius: ['40%', '65%'], center: ['60%', '50%'], data,
      itemStyle: { borderRadius: 6, borderColor: 'transparent', borderWidth: 2 },
      label: { formatter: '{b}\n{d}%', fontSize: 12 },
      emphasis: { itemStyle: { shadowBlur: 12, shadowColor: 'rgba(0,0,0,0.2)' } }
    }]
  })
}

const renderRadar = () => {
  const data = cache.value.radar
  if (!data) return
  const chart = ecInit('radar-chart')
  if (!chart) return
  chart.setOption({
    tooltip: { trigger: 'item' },
    legend: { data: ['高价值用户', '普通用户'], bottom: 0, itemHeight: 10, textStyle: { fontSize: 11 } },
    radar: {
      indicator: [
        { name: '购买频率', max: 100 }, { name: '活跃天数', max: 100 }, { name: '领券率', max: 100 },
        { name: '转化率', max: 100 }, { name: '商户多样性', max: 100 }, { name: '用户新鲜度', max: 100 }
      ],
      radius: '60%',
      splitNumber: 5,
      axisName: { fontSize: 11, color: '#64748b' }
    },
    series: [{
      type: 'radar',
      data: [
        {
          name: '高价值用户',
          value: data.high_value || [0,0,0,0,0,0],
          areaStyle: { color: 'rgba(59,130,246,0.2)' },
          lineStyle: { color: '#3b82f6', width: 2 },
          itemStyle: { color: '#3b82f6' }
        },
        {
          name: '普通用户',
          value: data.normal || [0,0,0,0,0,0],
          areaStyle: { color: 'rgba(16,185,129,0.15)' },
          lineStyle: { color: '#10b981', width: 2 },
          itemStyle: { color: '#10b981' }
        }
      ]
    }]
  })
}

const renderCoupon = () => {
  const data = cache.value.coupon
  if (!data) return
  const chart = ecInit('coupon-chart')
  if (!chart) return
  chart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, formatter: params => {
      return `${params[0].name}<br/>${params.map(p => `${p.marker}${p.seriesName}: <b>${p.value}%</b>`).join('<br/>')}`
    }},
    legend: { data: ['领券率', '核销率'], bottom: 0, itemHeight: 10, textStyle: { fontSize: 12 } },
    grid: { left: '3%', right: '4%', bottom: '14%', top: '6%', containLabel: true },
    xAxis: { type: 'category', data: data.groups, axisLabel: { color: '#334155', fontSize: 12 }, axisLine: { lineStyle: { color: '#e2e8f0' } } },
    yAxis: { type: 'value', name: '比率(%)', axisLabel: { formatter: '{value}%', color: '#94a3b8', fontSize: 11 }, splitLine: { lineStyle: { type: 'dashed', color: '#f1f5f9' } } },
    series: [
      {
        name: '领券率', type: 'bar', barMaxWidth: 28, data: data.coupon_rate,
        itemStyle: { color: new echarts.graphic.LinearGradient(0,0,0,1,[{offset:0,color:'#f43f5e'},{offset:1,color:'#fb7185'}]), borderRadius: [4,4,0,0] },
        label: { show: true, position: 'top', formatter: '{c}%', fontSize: 11, color: '#f43f5e' }
      },
      {
        name: '核销率', type: 'bar', barMaxWidth: 28, data: data.redemption_rate,
        itemStyle: { color: new echarts.graphic.LinearGradient(0,0,0,1,[{offset:0,color:'#a855f7'},{offset:1,color:'#c084fc'}]), borderRadius: [4,4,0,0] },
        label: { show: true, position: 'top', formatter: '{c}%', fontSize: 11, color: '#a855f7' }
      }
    ]
  })
}

const renderFeatDist = () => {
  const data = cache.value.featDist
  if (!data || !data.active_days) return
  const chart = ecInit('feat-dist-chart')
  if (!chart) return
  const labels = data.active_days.map(d => d.label)
  const counts = data.active_days.map(d => d.count)
  const colors = ['#3b82f6', '#06b6d4', '#10b981', '#f59e0b', '#f43f5e', '#a855f7']
  chart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, formatter: '{b}: <b>{c}</b> 人' },
    grid: { left: '3%', right: '4%', bottom: '8%', top: '10%', containLabel: true },
    xAxis: { type: 'category', data: labels, axisLabel: { color: '#334155', fontSize: 12 }, axisLine: { lineStyle: { color: '#e2e8f0' } } },
    yAxis: { type: 'value', name: '用户数', axisLabel: { color: '#94a3b8', fontSize: 11 }, splitLine: { lineStyle: { type: 'dashed', color: '#f1f5f9' } } },
    series: [{
      type: 'bar', barMaxWidth: 40,
      data: counts.map((v, i) => ({
        value: v,
        itemStyle: { color: new echarts.graphic.LinearGradient(0,0,0,1,[{offset:0,color:colors[i]},{offset:1,color:colors[i]+'88'}]), borderRadius: [5,5,0,0] }
      })),
      label: { show: true, position: 'top', color: '#64748b', fontSize: 11 }
    }]
  })
}

const renderMonthTrend = (allStats) => {
  const chart = ecInit('month-trend-chart')
  if (!chart) return
  const months = ['4月', '5月', '6月']
  const total = allStats.map(s => s.total_users || 0)
  const highValue = allStats.map(s => s.high_value_users || 0)
  const churnRisk = allStats.map(s => s.churn_risk_users || 0)
  chart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['总用户数', '高价值用户', '流失风险用户'], bottom: 0, itemHeight: 10, textStyle: { fontSize: 11 } },
    grid: { left: '3%', right: '4%', bottom: '14%', top: '6%', containLabel: true },
    xAxis: { type: 'category', data: months, axisLabel: { color: '#334155', fontSize: 13 }, axisLine: { lineStyle: { color: '#e2e8f0' } } },
    yAxis: { type: 'value', splitLine: { lineStyle: { type: 'dashed', color: '#f1f5f9' } }, axisLabel: { color: '#94a3b8', fontSize: 11 } },
    series: [
      {
        name: '总用户数', type: 'line', smooth: true, data: total,
        symbol: 'circle', symbolSize: 8, lineStyle: { width: 2.5, color: '#3b82f6' },
        itemStyle: { color: '#3b82f6' },
        areaStyle: { color: new echarts.graphic.LinearGradient(0,0,0,1,[{offset:0,color:'rgba(59,130,246,0.2)'},{offset:1,color:'rgba(59,130,246,0)'}]) },
        label: { show: true, position: 'top', fontSize: 11, color: '#3b82f6' }
      },
      {
        name: '高价值用户', type: 'line', smooth: true, data: highValue,
        symbol: 'circle', symbolSize: 8, lineStyle: { width: 2.5, color: '#10b981' },
        itemStyle: { color: '#10b981' },
        areaStyle: { color: new echarts.graphic.LinearGradient(0,0,0,1,[{offset:0,color:'rgba(16,185,129,0.15)'},{offset:1,color:'rgba(16,185,129,0)'}]) },
        label: { show: true, position: 'top', fontSize: 11, color: '#10b981' }
      },
      {
        name: '流失风险用户', type: 'line', smooth: true, data: churnRisk,
        symbol: 'circle', symbolSize: 8, lineStyle: { width: 2.5, color: '#f43f5e' },
        itemStyle: { color: '#f43f5e' },
        label: { show: true, position: 'top', fontSize: 11, color: '#f43f5e' }
      }
    ]
  })
}

const renderHeatmap = () => {
  const data = cache.value.heatmap
  if (!data) return
  const chart = ecInit('heatmap-chart')
  if (!chart) return
  const hours = Array.from({ length: 24 }, (_, i) => `${i}时`)
  const days = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
  chart.setOption({
    tooltip: { position: 'top', formatter: params => `${days[params.data[1]]} ${hours[params.data[0]]}<br/>行为次数: ${params.data[2]}` },
    grid: { top: '5%', left: '8%', right: '5%', bottom: '16%' },
    xAxis: { type: 'category', data: hours, splitArea: { show: true } },
    yAxis: { type: 'category', data: days, splitArea: { show: true } },
    visualMap: { min: 0, max: data.max_value || 100, calculable: true, orient: 'horizontal', left: 'center', bottom: '0%', inRange: { color: ['#e0f2fe', '#3b82f6', '#1d4ed8'] } },
    series: [{ type: 'heatmap', data: data.matrix, emphasis: { itemStyle: { shadowBlur: 10, shadowColor: 'rgba(0,0,0,0.3)' } } }]
  })
}

const loadStats = async () => {
  try {
    const res = await axiosInstance.get('/visualization/user-stats', { params: { month: selectedMonth.value } })
    stats.value = res.data
  } catch (e) { console.error(e) }
}

const loadRFM = async () => {
  loading.value.rfm = true
  try {
    const res = await axiosInstance.get('/visualization/user-rfm', { params: { month: selectedMonth.value } })
    cache.value.rfm = res.data; renderRFM()
  } catch (e) { console.error(e) } finally { loading.value.rfm = false }
}

const loadLifecycle = async () => {
  loading.value.lifecycle = true
  try {
    const res = await axiosInstance.get('/visualization/user-segmentation', { params: { month: selectedMonth.value } })
    cache.value.lifecycle = res.data.segments; renderLifecycle()
  } catch (e) { console.error(e) } finally { loading.value.lifecycle = false }
}

const loadRadar = async () => {
  loading.value.radar = true
  try {
    const res = await axiosInstance.get('/visualization/user-profile', { params: { month: selectedMonth.value } })
    cache.value.radar = res.data; renderRadar()
  } catch (e) { console.error(e) } finally { loading.value.radar = false }
}

const loadCoupon = async () => {
  loading.value.coupon = true
  try {
    const res = await axiosInstance.get('/visualization/group-conversion', { params: { month: selectedMonth.value } })
    cache.value.coupon = res.data; renderCoupon()
  } catch (e) { console.error(e) } finally { loading.value.coupon = false }
}

const loadFeatDist = async () => {
  loading.value.featDist = true
  try {
    const res = await axiosInstance.get('/visualization/user-feature-dist', { params: { month: selectedMonth.value } })
    cache.value.featDist = res.data; renderFeatDist()
  } catch (e) { console.error(e) } finally { loading.value.featDist = false }
}

const loadMonthTrend = async () => {
  loading.value.monthTrend = true
  try {
    const results = await Promise.all([4, 5, 6].map(m => axiosInstance.get('/visualization/user-stats', { params: { month: m } })))
    renderMonthTrend(results.map(r => r.data))
  } catch (e) { console.error(e) } finally { loading.value.monthTrend = false }
}

const loadHeatmap = async () => {
  loading.value.heatmap = true
  try {
    const res = await axiosInstance.get('/visualization/behavior-heatmap', { params: { month: selectedMonth.value } })
    cache.value.heatmap = res.data; renderHeatmap()
  } catch (e) { console.error(e) } finally { loading.value.heatmap = false }
}

const loadAll = () => {
  loadStats()
  loadRFM()
  loadLifecycle()
  loadRadar()
  loadCoupon()
  loadFeatDist()
  loadHeatmap()
  loadMonthTrend()
}

watch(isDark, () => { renderRFM(); renderLifecycle(); renderRadar(); renderCoupon(); renderFeatDist(); renderHeatmap() })

onMounted(() => loadAll())
</script>

<style scoped>
.page { padding: 16px 20px; background: var(--bg-page); min-height: 100%; }

.filter-bar { display: flex; align-items: center; gap: 24px; background: var(--bg-filter); border: 1px solid var(--border); border-left: 3px solid #a855f7; border-radius: 10px; padding: 12px 18px; margin-bottom: 16px; box-shadow: 0 1px 6px rgba(0,0,0,0.05); }
.filter-group { display: flex; align-items: center; gap: 8px; }
.filter-label { font-size: 12px; font-weight: 600; color: var(--text-muted); white-space: nowrap; }

.metrics-row { margin-bottom: 16px; }
.stat-card { border-radius: 12px; padding: 14px 16px; position: relative; overflow: hidden; transition: transform 0.2s; }
.stat-card:hover { transform: translateY(-2px); }
.stat-blue   { background: linear-gradient(135deg, #2563eb, #06b6d4); box-shadow: 0 4px 16px rgba(37,99,235,0.3); }
.stat-green  { background: linear-gradient(135deg, #059669, #10b981); box-shadow: 0 4px 16px rgba(5,150,105,0.3); }
.stat-orange { background: linear-gradient(135deg, #d97706, #f59e0b); box-shadow: 0 4px 16px rgba(217,119,6,0.3); }
.stat-red    { background: linear-gradient(135deg, #dc2626, #f43f5e); box-shadow: 0 4px 16px rgba(220,38,38,0.3); }
.stat-bg-icon { position: absolute; right: -8px; bottom: -8px; pointer-events: none; }
.stat-top { margin-bottom: 8px; }
.stat-icon-wrap { width: 34px; height: 34px; background: rgba(255,255,255,0.2); border-radius: 8px; display: flex; align-items: center; justify-content: center; }
.stat-value { font-size: 22px; font-weight: 800; color: #fff; line-height: 1.2; margin-bottom: 3px; }
.stat-label { font-size: 12px; color: rgba(255,255,255,0.75); margin-bottom: 10px; }
.stat-bar { height: 3px; background: rgba(255,255,255,0.2); border-radius: 2px; overflow: hidden; }
.stat-bar-fill { height: 100%; background: rgba(255,255,255,0.55); border-radius: 2px; }

.charts-row { margin-bottom: 14px; }
.chart-card { background: var(--bg-card); border-radius: 12px; overflow: hidden; box-shadow: 0 1px 8px rgba(0,0,0,0.06); transition: box-shadow 0.2s; }
.chart-card:hover { box-shadow: 0 4px 18px rgba(0,0,0,0.1); }
.chart-header { display: flex; align-items: center; justify-content: space-between; padding: 11px 16px; border-bottom: 1px solid var(--border); border-left: 3px solid transparent; background: linear-gradient(90deg, rgba(0,0,0,0.02) 0%, transparent 100%); }
.chart-header-left { display: flex; align-items: center; gap: 7px; }
.chart-dot { display: inline-block; width: 7px; height: 7px; border-radius: 50%; flex-shrink: 0; }
.chart-title { font-size: 13px; font-weight: 600; color: var(--text-primary); }
.chart-badge { font-size: 11px; padding: 2px 8px; background: var(--bg-page); color: var(--text-secondary); border-radius: 8px; font-weight: 500; }
</style>
