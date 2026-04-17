<template>
  <div class="page">

    <!-- 说明栏 -->
    <div class="info-bar">
      <el-icon :size="14" color="#3b82f6"><InfoFilled /></el-icon>
      <span>平销期：2016-01 ~ 2016-04 &nbsp;|&nbsp; 促销期（含618）：2016-05 ~ 2016-06</span>
    </div>

    <!-- 差异指标卡 -->
    <el-row :gutter="16" class="metrics-row">
      <el-col :span="6" v-for="item in diffMetrics" :key="item.key">
        <div class="diff-card">
          <div class="diff-card-title">{{ item.label }}</div>
          <div class="diff-body">
            <div class="diff-side">
              <div class="diff-num diff-regular">{{ item.regular }}</div>
              <div class="diff-period-tag">平销期</div>
            </div>
            <div class="diff-center">
              <div class="diff-arrow-icon" :class="item.trend === 'up' ? 'arrow-up' : 'arrow-down'">
                {{ item.trend === 'up' ? '▲' : '▼' }}
              </div>
              <div class="diff-change" :class="item.trend === 'up' ? 'change-up' : 'change-down'">
                {{ item.change }}
              </div>
            </div>
            <div class="diff-side">
              <div class="diff-num diff-promotion">{{ item.promotion }}</div>
              <div class="diff-period-tag">促销期</div>
            </div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 图表行1 -->
    <el-row :gutter="16" class="charts-row">
      <el-col :span="14">
        <div class="chart-card">
          <div class="chart-header" style="border-left-color:#3b82f6">
            <div class="chart-header-left">
              <span class="chart-dot" style="background:#3b82f6;box-shadow:0 0 6px rgba(59,130,246,0.6)"></span>
              <span class="chart-title">全周期每日购买趋势</span>
            </div>
            <el-tooltip content="蓝色区域=平销期，红色区域=促销期（5-6月）" placement="top">
              <span class="chart-badge" style="cursor:help">区域说明</span>
            </el-tooltip>
          </div>
          <div v-loading="loading.trend" id="trend-chart" style="height:300px"></div>
        </div>
      </el-col>
      <el-col :span="10">
        <div class="chart-card">
          <div class="chart-header" style="border-left-color:#a855f7">
            <div class="chart-header-left">
              <span class="chart-dot" style="background:#a855f7;box-shadow:0 0 6px rgba(168,85,247,0.6)"></span>
              <span class="chart-title">多维指标对比雷达图</span>
            </div>
          </div>
          <div v-loading="loading.radar" id="compare-radar-chart" style="height:300px"></div>
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
              <span class="chart-title">月度用户活跃度对比</span>
            </div>
            <span class="chart-badge period-badge-promo">5-6月促销</span>
          </div>
          <div v-loading="loading.active" id="active-chart" style="height:280px"></div>
        </div>
      </el-col>
      <el-col :span="12">
        <div class="chart-card">
          <div class="chart-header" style="border-left-color:#f43f5e">
            <div class="chart-header-left">
              <span class="chart-dot" style="background:#f43f5e;box-shadow:0 0 6px rgba(244,63,94,0.6)"></span>
              <span class="chart-title">618 促销效果分析</span>
            </div>
            <span class="chart-badge period-badge-618">6月</span>
          </div>
          <div v-loading="loading.effect618" id="effect618-chart" style="height:280px"></div>
        </div>
      </el-col>
    </el-row>

  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { InfoFilled } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import axios from 'axios'
import { useTheme } from '@/composables/useTheme'

const API_BASE = 'http://localhost:8000/api/v1'
const { isDark } = useTheme()

const loading = ref({ trend: false, radar: false, active: false, effect618: false })
const cache = ref({ trend: null, radar: null, active: null, effect618: null })

const diffMetrics = ref([
  { key: 'cvr',             label: '整体转化率(CVR)', regular: '—', promotion: '—', change: '—', trend: 'up' },
  { key: 'daily_purchases', label: '日均购买量',       regular: '—', promotion: '—', change: '—', trend: 'up' },
  { key: 'coupon_rate',     label: '领券率',           regular: '—', promotion: '—', change: '—', trend: 'up' },
  { key: 'active_users',   label: '月均活跃用户',      regular: '—', promotion: '—', change: '—', trend: 'up' },
])

const ecInit = (id) => {
  const el = document.getElementById(id)
  if (!el) return null
  echarts.getInstanceByDom(el)?.dispose()
  return echarts.init(el, isDark.value ? 'dark' : null)
}

const renderRadar = () => {
  const d = cache.value.radar
  if (!d) return
  const chart = ecInit('compare-radar-chart')
  if (!chart) return
  chart.setOption({
    tooltip: {},
    legend: { data: ['平销期', '促销期'], bottom: 0, itemHeight: 10, textStyle: { fontSize: 11 } },
    radar: {
      indicator: [
        { name: '转化率', max: 100 }, { name: '购买量', max: 100 }, { name: '领券率', max: 100 },
        { name: '活跃用户', max: 100 }, { name: '复购率', max: 100 }, { name: '核销率', max: 100 }
      ],
      splitNumber: 4
    },
    series: [{
      type: 'radar',
      data: [
        { name: '平销期',  value: d.radar?.regular   || [60,50,55,65,45,50], areaStyle: { opacity: 0.2 }, itemStyle: { color: '#3b82f6' }, lineStyle: { color: '#3b82f6' } },
        { name: '促销期',  value: d.radar?.promotion || [80,85,75,90,65,70], areaStyle: { opacity: 0.2 }, itemStyle: { color: '#f43f5e' }, lineStyle: { color: '#f43f5e' } }
      ]
    }]
  })
}

const renderTrend = () => {
  const data = cache.value.trend
  if (!data) return
  const chart = ecInit('trend-chart')
  if (!chart) return
  chart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['购买量'], bottom: 0, itemHeight: 10, textStyle: { fontSize: 11 } },
    grid: { left: '3%', right: '4%', bottom: '14%', top: '4%', containLabel: true },
    xAxis: { type: 'category', data: data.dates, axisLabel: { rotate: 45, fontSize: 10, interval: 14 } },
    yAxis: { type: 'value', name: '购买量' },
    series: [{
      name: '购买量', type: 'line', data: data.purchases, smooth: true, symbol: 'none',
      lineStyle: { width: 2 }, itemStyle: { color: '#3b82f6' },
      areaStyle: { color: new echarts.graphic.LinearGradient(0,0,0,1,[{offset:0,color:'rgba(59,130,246,0.35)'},{offset:1,color:'rgba(59,130,246,0.02)'}]) },
      markArea: {
        silent: true,
        data: [[
          { name: '促销期（618）', xAxis: data.dates.find(d => d >= '2016-05-01') || '' },
          { xAxis: data.dates[data.dates.length - 1] }
        ]],
        itemStyle: { color: 'rgba(244,63,94,0.07)', borderWidth: 1, borderColor: '#f43f5e', borderType: 'dashed' },
        label: { color: '#f43f5e', position: 'insideTopRight', fontSize: 11 }
      },
      markLine: {
        silent: true,
        data: [{ name: '618', xAxis: data.dates.find(d => d === '2016-06-18') || '' }],
        lineStyle: { color: '#f43f5e', type: 'solid', width: 2 },
        label: { formatter: '618', color: '#f43f5e' }
      }
    }]
  })
}

const renderActive = () => {
  const data = cache.value.active
  if (!data) return
  const chart = ecInit('active-chart')
  if (!chart) return
  chart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    legend: { data: ['购买量', '领券量'], bottom: 0, itemHeight: 10, textStyle: { fontSize: 11 } },
    grid: { left: '3%', right: '4%', bottom: '16%', top: '6%', containLabel: true },
    xAxis: { type: 'category', data: data.map(d => `${d.month}月`) },
    yAxis: { type: 'value', name: '数量' },
    series: [
      {
        name: '购买量', type: 'bar', data: data.map(d => d.purchases), barMaxWidth: 28,
        itemStyle: { borderRadius: [4,4,0,0], color: params => params.dataIndex >= 4 ? new echarts.graphic.LinearGradient(0,0,0,1,[{offset:0,color:'#f87171'},{offset:1,color:'#f43f5e'}]) : new echarts.graphic.LinearGradient(0,0,0,1,[{offset:0,color:'#60a5fa'},{offset:1,color:'#3b82f6'}]) }
      },
      {
        name: '领券量', type: 'bar', data: data.map(d => d.coupons), barMaxWidth: 28,
        itemStyle: { borderRadius: [4,4,0,0], color: params => params.dataIndex >= 4 ? new echarts.graphic.LinearGradient(0,0,0,1,[{offset:0,color:'#fbbf24'},{offset:1,color:'#f59e0b'}]) : new echarts.graphic.LinearGradient(0,0,0,1,[{offset:0,color:'#34d399'},{offset:1,color:'#10b981'}]) }
      }
    ]
  })
}

const render618 = () => {
  const data = cache.value.effect618
  if (!data) return
  const chart = ecInit('effect618-chart')
  if (!chart) return
  const maxVal = Math.max(...data.purchases)
  const maxIdx = data.purchases.indexOf(maxVal)
  chart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { left: '3%', right: '4%', bottom: '8%', top: '6%', containLabel: true },
    xAxis: { type: 'category', data: data.dates.map(d => d.slice(5)), axisLabel: { rotate: 45, fontSize: 10 } },
    yAxis: { type: 'value', name: '购买量' },
    series: [
      {
        type: 'bar', data: data.purchases, barMaxWidth: 20,
        itemStyle: { borderRadius: [3,3,0,0], color: params => params.dataIndex === maxIdx ? new echarts.graphic.LinearGradient(0,0,0,1,[{offset:0,color:'#f87171'},{offset:1,color:'#f43f5e'}]) : new echarts.graphic.LinearGradient(0,0,0,1,[{offset:0,color:'#fbbf24'},{offset:1,color:'#f59e0b'}]) },
        markPoint: { data: [{ type: 'max', name: '峰值', label: { formatter: '峰值\n{c}', fontSize: 11 } }] }
      },
      { type: 'line', data: data.purchases, smooth: true, symbol: 'none', itemStyle: { color: '#f43f5e' }, lineStyle: { width: 2 } }
    ]
  })
}

const loadSummary = async () => {
  loading.value.radar = true
  try {
    const res = await axios.get(`${API_BASE}/visualization/comparison-summary`)
    const d = res.data
    diffMetrics.value = [
      { key: 'cvr', label: '整体转化率(CVR)', regular: `${d.regular.cvr}%`, promotion: `${d.promotion.cvr}%`, change: `${d.changes.cvr > 0 ? '+' : ''}${d.changes.cvr}%`, trend: d.changes.cvr >= 0 ? 'up' : 'down' },
      { key: 'daily_purchases', label: '日均购买量', regular: d.regular.daily_purchases?.toLocaleString(), promotion: d.promotion.daily_purchases?.toLocaleString(), change: `${d.changes.daily_purchases > 0 ? '+' : ''}${d.changes.daily_purchases?.toLocaleString()}`, trend: d.changes.daily_purchases >= 0 ? 'up' : 'down' },
      { key: 'coupon_rate', label: '领券率', regular: `${d.regular.coupon_rate}%`, promotion: `${d.promotion.coupon_rate}%`, change: `${d.changes.coupon_rate > 0 ? '+' : ''}${d.changes.coupon_rate}%`, trend: d.changes.coupon_rate >= 0 ? 'up' : 'down' },
      { key: 'active_users', label: '月均活跃用户', regular: d.regular.active_users?.toLocaleString(), promotion: d.promotion.active_users?.toLocaleString(), change: `${d.changes.active_users > 0 ? '+' : ''}${d.changes.active_users?.toLocaleString()}`, trend: d.changes.active_users >= 0 ? 'up' : 'down' },
    ]
    cache.value.radar = d
    renderRadar()
  } catch (e) { console.error(e) } finally { loading.value.radar = false }
}

const loadTrend = async () => {
  loading.value.trend = true
  try {
    const res = await axios.get(`${API_BASE}/visualization/daily-trend`)
    cache.value.trend = res.data; renderTrend()
  } catch (e) { console.error(e) } finally { loading.value.trend = false }
}

const loadActive = async () => {
  loading.value.active = true
  try {
    const res = await axios.get(`${API_BASE}/visualization/monthly-stats`)
    cache.value.active = res.data.data; renderActive()
  } catch (e) { console.error(e) } finally { loading.value.active = false }
}

const load618 = async () => {
  loading.value.effect618 = true
  try {
    const res = await axios.get(`${API_BASE}/visualization/daily-trend`, { params: { start_date: '2016-06-01', end_date: '2016-06-30' } })
    cache.value.effect618 = res.data; render618()
  } catch (e) { console.error(e) } finally { loading.value.effect618 = false }
}

watch(isDark, () => { renderRadar(); renderTrend(); renderActive(); render618() })

onMounted(() => { loadSummary(); loadTrend(); loadActive(); load618() })
</script>

<style scoped>
.page { padding: 16px 20px; background: var(--bg-page); min-height: 100%; }

/* 说明栏 */
.info-bar {
  display: flex; align-items: center; gap: 8px;
  background: rgba(59,130,246,0.08);
  border: 1px solid rgba(59,130,246,0.2);
  border-left: 3px solid #3b82f6;
  border-radius: 8px;
  padding: 9px 14px;
  margin-bottom: 16px;
  font-size: 12px; color: var(--text-secondary);
}

/* 差异指标卡 */
.metrics-row { margin-bottom: 16px; }
.diff-card {
  background: var(--bg-card);
  border-radius: 12px;
  padding: 14px 16px;
  box-shadow: 0 1px 8px rgba(0,0,0,0.06);
  transition: transform 0.2s, box-shadow 0.2s;
}
.diff-card:hover { transform: translateY(-2px); box-shadow: 0 4px 16px rgba(0,0,0,0.1); }

.diff-card-title { font-size: 11px; font-weight: 600; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 12px; }

.diff-body { display: flex; align-items: center; justify-content: space-between; }
.diff-side { text-align: center; flex: 1; }

.diff-num { font-size: 18px; font-weight: 800; line-height: 1.2; margin-bottom: 3px; }
.diff-regular   { color: #3b82f6; }
.diff-promotion { color: #f43f5e; }

.diff-period-tag { font-size: 10px; color: var(--text-muted); }

.diff-center { display: flex; flex-direction: column; align-items: center; gap: 2px; padding: 0 10px; }
.diff-arrow-icon { font-size: 14px; }
.arrow-up   { color: #10b981; }
.arrow-down { color: #f43f5e; }
.diff-change { font-size: 12px; font-weight: 700; white-space: nowrap; }
.change-up   { color: #10b981; }
.change-down { color: #f43f5e; }

/* 图表卡片 */
.charts-row { margin-bottom: 16px; }
.chart-card { background: var(--bg-card); border-radius: 12px; overflow: hidden; box-shadow: 0 1px 8px rgba(0,0,0,0.06); transition: box-shadow 0.2s; }
.chart-card:hover { box-shadow: 0 4px 18px rgba(0,0,0,0.1); }
.chart-header { display: flex; align-items: center; justify-content: space-between; padding: 11px 16px; border-bottom: 1px solid var(--border); border-left: 3px solid transparent; background: linear-gradient(90deg, rgba(0,0,0,0.02) 0%, transparent 100%); }
.chart-header-left { display: flex; align-items: center; gap: 7px; }
.chart-dot { display: inline-block; width: 7px; height: 7px; border-radius: 50%; flex-shrink: 0; }
.chart-title { font-size: 13px; font-weight: 600; color: var(--text-primary); }
.chart-badge { font-size: 11px; padding: 2px 8px; background: var(--bg-page); color: var(--text-secondary); border-radius: 8px; font-weight: 500; }
.period-badge-promo { background: rgba(244,63,94,0.1); color: #f43f5e; }
.period-badge-618   { background: rgba(244,63,94,0.15); color: #f43f5e; font-weight: 700; }
</style>
