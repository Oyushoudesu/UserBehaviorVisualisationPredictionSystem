<template>
  <div class="page">

    <!-- 筛选栏 -->
    <div class="filter-bar">
      <div class="filter-group">
        <span class="filter-label">数据月份</span>
        <el-select v-model="selectedMonth" @change="loadAll" style="width:120px" size="small">
          <el-option v-for="m in 6" :key="m" :label="`第${m}月`" :value="m" />
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
          <div class="stat-top">
            <div class="stat-icon-wrap"><el-icon :size="18" color="#fff"><Pointer /></el-icon></div>
          </div>
          <div class="stat-value">{{ funnelStats.click_users?.toLocaleString() || '—' }}</div>
          <div class="stat-label">点击用户数</div>
          <div class="stat-bar"><div class="stat-bar-fill" style="width:100%"></div></div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card stat-green">
          <div class="stat-bg-icon"><el-icon :size="52" color="rgba(255,255,255,0.12)"><Ticket /></el-icon></div>
          <div class="stat-top">
            <div class="stat-icon-wrap"><el-icon :size="18" color="#fff"><Ticket /></el-icon></div>
          </div>
          <div class="stat-value">{{ funnelStats.coupon_users?.toLocaleString() || '—' }}</div>
          <div class="stat-label">领券用户数</div>
          <div class="stat-bar"><div class="stat-bar-fill" style="width:70%"></div></div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card stat-orange">
          <div class="stat-bg-icon"><el-icon :size="52" color="rgba(255,255,255,0.12)"><ShoppingCart /></el-icon></div>
          <div class="stat-top">
            <div class="stat-icon-wrap"><el-icon :size="18" color="#fff"><ShoppingCart /></el-icon></div>
          </div>
          <div class="stat-value">{{ funnelStats.purchase_users?.toLocaleString() || '—' }}</div>
          <div class="stat-label">购买用户数</div>
          <div class="stat-bar"><div class="stat-bar-fill" style="width:50%"></div></div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card stat-purple">
          <div class="stat-bg-icon"><el-icon :size="52" color="rgba(255,255,255,0.12)"><TrendCharts /></el-icon></div>
          <div class="stat-top">
            <div class="stat-icon-wrap"><el-icon :size="18" color="#fff"><TrendCharts /></el-icon></div>
          </div>
          <div class="stat-value">{{ funnelStats.overall_cvr?.toFixed(2) || '—' }}%</div>
          <div class="stat-label">整体转化率</div>
          <div class="stat-bar"><div class="stat-bar-fill" style="width:35%"></div></div>
        </div>
      </el-col>
    </el-row>

    <!-- 图表行1 -->
    <el-row :gutter="16" class="charts-row">
      <el-col :span="10">
        <div class="chart-card">
          <div class="chart-header" style="border-left-color:#3b82f6">
            <div class="chart-header-left">
              <span class="chart-dot" style="background:#3b82f6;box-shadow:0 0 6px rgba(59,130,246,0.6)"></span>
              <span class="chart-title">用户转化漏斗</span>
            </div>
            <span class="chart-badge">{{ selectedPeriod === 'all' ? '全部' : selectedPeriod === 'regular' ? '平销期' : '促销期' }}</span>
          </div>
          <div v-loading="loading.funnel" id="funnel-chart" style="height:300px"></div>
        </div>
      </el-col>
      <el-col :span="14">
        <div class="chart-card">
          <div class="chart-header" style="border-left-color:#a855f7">
            <div class="chart-header-left">
              <span class="chart-dot" style="background:#a855f7;box-shadow:0 0 6px rgba(168,85,247,0.6)"></span>
              <span class="chart-title">用户行为路径桑基图</span>
            </div>
            <el-tooltip content="展示用户从点击→领券→购买的流向分布" placement="top">
              <span class="chart-badge" style="cursor:help">?</span>
            </el-tooltip>
          </div>
          <div v-loading="loading.sankey" id="sankey-chart" style="height:300px"></div>
        </div>
      </el-col>
    </el-row>

    <!-- 图表行2 -->
    <el-row :gutter="16" class="charts-row">
      <el-col :span="12">
        <div class="chart-card">
          <div class="chart-header" style="border-left-color:#10b981">
            <div class="chart-header-left">
              <span class="chart-dot" style="background:#10b981;box-shadow:0 0 6px rgba(16,185,129,0.6)"></span>
              <span class="chart-title">不同用户群体转化率对比</span>
            </div>
          </div>
          <div v-loading="loading.group" id="group-chart" style="height:280px"></div>
        </div>
      </el-col>
      <el-col :span="12">
        <div class="chart-card">
          <div class="chart-header" style="border-left-color:#f43f5e">
            <div class="chart-header-left">
              <span class="chart-dot" style="background:#f43f5e;box-shadow:0 0 6px rgba(244,63,94,0.6)"></span>
              <span class="chart-title">月度转化率趋势</span>
            </div>
          </div>
          <div v-loading="loading.trend" id="cvr-trend-chart" style="height:280px"></div>
        </div>
      </el-col>
    </el-row>

  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { Pointer, Ticket, ShoppingCart, TrendCharts } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import axios from 'axios'
import { useTheme } from '@/composables/useTheme'

const API_BASE = 'http://localhost:8000/api/v1'
const { isDark } = useTheme()

const selectedMonth = ref(4)
const selectedPeriod = ref('all')
const funnelStats = ref({})
const loading = ref({ funnel: false, sankey: false, group: false, trend: false })

// cached data for theme-aware re-render
const cache = ref({ funnel: null, sankey: null, group: null, trend: null })

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
  chart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {c} 人' },
    color: ['#3b82f6', '#10b981', '#f59e0b', '#f43f5e'],
    series: [{
      type: 'funnel', left: '10%', width: '80%',
      min: 0, max: data[0]?.count || 1, minSize: '20%', maxSize: '100%',
      sort: 'descending', gap: 3,
      data: data.map(item => ({ name: item.stage, value: item.count })),
      label: { show: true, position: 'inside', formatter: '{b}\n{c}人', color: '#fff', fontSize: 12 },
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
        ? `${params.data.source} → ${params.data.target}<br/>用户数: ${params.data.value}`
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
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    legend: { data: ['CTR', '领券率', '核销率', 'CVR'], bottom: 0, itemHeight: 10, textStyle: { fontSize: 11 } },
    grid: { left: '3%', right: '4%', bottom: '16%', top: '6%', containLabel: true },
    xAxis: { type: 'category', data: data.groups },
    yAxis: { type: 'value', name: '转化率(%)', max: 100 },
    color: ['#3b82f6', '#10b981', '#f59e0b', '#f43f5e'],
    series: [
      { name: 'CTR',   type: 'bar', data: data.ctr,             barMaxWidth: 20, itemStyle: { borderRadius: [3,3,0,0] } },
      { name: '领券率', type: 'bar', data: data.coupon_rate,     barMaxWidth: 20, itemStyle: { borderRadius: [3,3,0,0] } },
      { name: '核销率', type: 'bar', data: data.redemption_rate, barMaxWidth: 20, itemStyle: { borderRadius: [3,3,0,0] } },
      { name: 'CVR',   type: 'bar', data: data.cvr,             barMaxWidth: 20, itemStyle: { borderRadius: [3,3,0,0] } },
    ]
  })
}

const renderTrend = () => {
  const data = cache.value.trend
  if (!data) return
  const chart = ecInit('cvr-trend-chart')
  if (!chart) return
  chart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['CVR(%)', '领券率(%)'], bottom: 0, itemHeight: 10, textStyle: { fontSize: 11 } },
    grid: { left: '3%', right: '4%', bottom: '16%', top: '6%', containLabel: true },
    xAxis: { type: 'category', data: data.map(d => `${d.month}月`) },
    yAxis: { type: 'value', name: '转化率(%)', min: 0 },
    color: ['#f43f5e', '#f59e0b'],
    series: [
      { name: 'CVR(%)', type: 'line', smooth: true, data: data.map(d => d.cvr), areaStyle: { opacity: 0.12 }, symbol: 'circle', symbolSize: 7, lineStyle: { width: 2 } },
      { name: '领券率(%)', type: 'line', smooth: true, data: data.map(d => d.coupons && d.purchases ? parseFloat(((d.coupons / (d.purchases + d.coupons)) * 100).toFixed(2)) : 0), areaStyle: { opacity: 0.12 }, symbol: 'circle', symbolSize: 7, lineStyle: { width: 2 } }
    ]
  })
}

const loadFunnel = async () => {
  loading.value.funnel = true
  try {
    const res = await axios.get(`${API_BASE}/visualization/conversion-funnel`, { params: { month: selectedMonth.value, period: selectedPeriod.value } })
    cache.value.funnel = res.data.funnel
    funnelStats.value = {
      click_users: res.data.funnel.find(d => d.stage === '点击用户')?.count,
      coupon_users: res.data.funnel.find(d => d.stage === '领券用户')?.count,
      purchase_users: res.data.funnel.find(d => d.stage === '购买用户')?.count,
      overall_cvr: res.data.cvr
    }
    renderFunnel()
  } catch (e) { console.error(e) } finally { loading.value.funnel = false }
}

const loadSankey = async () => {
  loading.value.sankey = true
  try {
    const res = await axios.get(`${API_BASE}/visualization/behavior-sankey`, { params: { month: selectedMonth.value, period: selectedPeriod.value } })
    cache.value.sankey = res.data
    renderSankey()
  } catch (e) { console.error(e) } finally { loading.value.sankey = false }
}

const loadGroup = async () => {
  loading.value.group = true
  try {
    const res = await axios.get(`${API_BASE}/visualization/group-conversion`, { params: { month: selectedMonth.value } })
    cache.value.group = res.data
    renderGroup()
  } catch (e) { console.error(e) } finally { loading.value.group = false }
}

const loadTrend = async () => {
  loading.value.trend = true
  try {
    const res = await axios.get(`${API_BASE}/visualization/monthly-stats`)
    cache.value.trend = res.data.data
    renderTrend()
  } catch (e) { console.error(e) } finally { loading.value.trend = false }
}

const loadAll = () => { loadFunnel(); loadSankey(); loadGroup(); loadTrend() }

watch(isDark, () => { renderFunnel(); renderSankey(); renderGroup(); renderTrend() })

onMounted(() => loadAll())
</script>

<style scoped>
.page { padding: 16px 20px; background: var(--bg-page); min-height: 100%; }

/* 筛选栏 */
.filter-bar {
  display: flex; align-items: center; gap: 24px;
  background: var(--bg-filter);
  border: 1px solid var(--border);
  border-left: 3px solid #3b82f6;
  border-radius: 10px;
  padding: 12px 18px;
  margin-bottom: 16px;
  box-shadow: 0 1px 6px rgba(0,0,0,0.05);
}
.filter-group { display: flex; align-items: center; gap: 8px; }
.filter-label { font-size: 12px; font-weight: 600; color: var(--text-muted); white-space: nowrap; }

/* 统计卡片（与 Dashboard 一致） */
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
.stat-bar-fill { height: 100%; background: rgba(255,255,255,0.55); border-radius: 2px; }

/* 图表卡片 */
.charts-row { margin-bottom: 16px; }
.chart-card { background: var(--bg-card); border-radius: 12px; overflow: hidden; box-shadow: 0 1px 8px rgba(0,0,0,0.06); transition: box-shadow 0.2s; }
.chart-card:hover { box-shadow: 0 4px 18px rgba(0,0,0,0.1); }
.chart-header { display: flex; align-items: center; justify-content: space-between; padding: 11px 16px; border-bottom: 1px solid var(--border); border-left: 3px solid transparent; background: linear-gradient(90deg, rgba(0,0,0,0.02) 0%, transparent 100%); }
.chart-header-left { display: flex; align-items: center; gap: 7px; }
.chart-dot { display: inline-block; width: 7px; height: 7px; border-radius: 50%; flex-shrink: 0; }
.chart-title { font-size: 13px; font-weight: 600; color: var(--text-primary); }
.chart-badge { font-size: 11px; padding: 2px 8px; background: var(--bg-page); color: var(--text-secondary); border-radius: 8px; font-weight: 500; }
</style>
