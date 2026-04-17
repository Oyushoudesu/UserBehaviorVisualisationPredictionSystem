<template>
  <div class="dashboard">

    <!-- 统计卡片 -->
    <el-row :gutter="16" class="metrics-row">
      <el-col :span="6">
        <div class="stat-card stat-blue">
          <div class="stat-bg-icon"><el-icon :size="52" color="rgba(255,255,255,0.12)"><User /></el-icon></div>
          <div class="stat-top">
            <div class="stat-icon-wrap"><el-icon :size="18" color="#fff"><User /></el-icon></div>
            <div class="stat-trend">↑ 12.5%</div>
          </div>
          <div class="stat-value">{{ overview.total_users?.toLocaleString() || '—' }}</div>
          <div class="stat-label">总用户数</div>
          <div class="stat-bar"><div class="stat-bar-fill" style="width:75%"></div></div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card stat-green">
          <div class="stat-bg-icon"><el-icon :size="52" color="rgba(255,255,255,0.12)"><Shop /></el-icon></div>
          <div class="stat-top">
            <div class="stat-icon-wrap"><el-icon :size="18" color="#fff"><Shop /></el-icon></div>
            <div class="stat-trend">↑ 8.3%</div>
          </div>
          <div class="stat-value">{{ overview.total_merchants?.toLocaleString() || '—' }}</div>
          <div class="stat-label">商户数</div>
          <div class="stat-bar"><div class="stat-bar-fill" style="width:60%"></div></div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card stat-orange">
          <div class="stat-bg-icon"><el-icon :size="52" color="rgba(255,255,255,0.12)"><ShoppingCart /></el-icon></div>
          <div class="stat-top">
            <div class="stat-icon-wrap"><el-icon :size="18" color="#fff"><ShoppingCart /></el-icon></div>
            <div class="stat-trend">↑ 23.1%</div>
          </div>
          <div class="stat-value">{{ overview.total_purchases?.toLocaleString() || '—' }}</div>
          <div class="stat-label">总购买数</div>
          <div class="stat-bar"><div class="stat-bar-fill" style="width:88%"></div></div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card stat-purple">
          <div class="stat-bg-icon"><el-icon :size="52" color="rgba(255,255,255,0.12)"><TrendCharts /></el-icon></div>
          <div class="stat-top">
            <div class="stat-icon-wrap"><el-icon :size="18" color="#fff"><TrendCharts /></el-icon></div>
            <div class="stat-trend">↑ 5.2%</div>
          </div>
          <div class="stat-value">{{ overview.cvr?.toFixed(2) || '—' }}%</div>
          <div class="stat-label">大盘转化率 CVR</div>
          <div class="stat-bar"><div class="stat-bar-fill" style="width:45%"></div></div>
        </div>
      </el-col>
    </el-row>

    <!-- 图表第一行 -->
    <el-row :gutter="16" class="charts-row">
      <el-col :span="14">
        <div class="chart-card">
          <div class="chart-header" style="border-left-color:#3b82f6">
            <div class="chart-header-left">
              <span class="chart-dot" style="background:#3b82f6;box-shadow:0 0 6px rgba(59,130,246,0.6)"></span>
              <span class="chart-title">每日购买与领券趋势</span>
            </div>
            <span class="chart-badge">近半年</span>
          </div>
          <div id="daily-chart" style="height:300px"></div>
        </div>
      </el-col>
      <el-col :span="10">
        <div class="chart-card">
          <div class="chart-header" style="border-left-color:#10b981">
            <div class="chart-header-left">
              <span class="chart-dot" style="background:#10b981;box-shadow:0 0 6px rgba(16,185,129,0.6)"></span>
              <span class="chart-title">按月统计与转化率(CVR)</span>
            </div>
            <span class="chart-badge">月度</span>
          </div>
          <div id="monthly-chart" style="height:300px"></div>
        </div>
      </el-col>
    </el-row>

    <!-- 图表第二行 -->
    <el-row :gutter="16" class="charts-row">
      <el-col :span="10">
        <div class="chart-card">
          <div class="chart-header" style="border-left-color:#f59e0b">
            <div class="chart-header-left">
              <span class="chart-dot" style="background:#f59e0b;box-shadow:0 0 6px rgba(245,158,11,0.6)"></span>
              <span class="chart-title">用户转化漏斗</span>
            </div>
            <span class="chart-badge">全周期</span>
          </div>
          <div id="funnel-chart" style="height:300px"></div>
        </div>
      </el-col>
      <el-col :span="14">
        <div class="chart-card">
          <div class="chart-header" style="border-left-color:#a855f7">
            <div class="chart-header-left">
              <span class="chart-dot" style="background:#a855f7;box-shadow:0 0 6px rgba(168,85,247,0.6)"></span>
              <span class="chart-title">全局用户分层(RFM)</span>
            </div>
            <span class="chart-badge">最新</span>
          </div>
          <div id="segment-chart" style="height:300px"></div>
        </div>
      </el-col>
    </el-row>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Shop, ShoppingCart, TrendCharts } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import axiosInstance, { clearAuth } from '@/api/axiosInstance'

const router = useRouter()
const overview = ref({})

const loadOverview = async () => {
  try {
    const res = await axiosInstance.get('/visualization/overview')
    overview.value = res.data
  } catch (e) { console.error(e) }
}

const loadDailyTrend = async () => {
  try {
    const res = await axiosInstance.get('/visualization/daily-trend')
    const data = res.data
    const chart = echarts.init(document.getElementById('daily-chart'))
    const shortDates = data.dates.map(d => d.slice(5))
    chart.setOption({
      tooltip: { trigger: 'axis', axisPointer: { type: 'cross', label: { backgroundColor: '#6a7985' } } },
      legend: { data: ['购买量', '领券量'], bottom: 0, itemHeight: 10, textStyle: { fontSize: 12 } },
      grid: { left: '3%', right: '4%', bottom: '14%', top: '6%', containLabel: true },
      xAxis: {
        type: 'category', data: shortDates,
        axisLabel: { interval: 'auto', hideOverlap: true, rotate: 30, color: '#94a3b8', fontSize: 11 },
        axisLine: { lineStyle: { color: '#e2e8f0' } },
        axisTick: { lineStyle: { color: '#e2e8f0' } }
      },
      yAxis: { type: 'value', splitLine: { lineStyle: { type: 'dashed', color: '#f1f5f9' } }, axisLabel: { color: '#94a3b8', fontSize: 11 } },
      series: [
        {
          name: '购买量', type: 'line', smooth: true, symbol: 'none',
          data: data.purchases,
          itemStyle: { color: '#3b82f6' },
          areaStyle: { color: new echarts.graphic.LinearGradient(0,0,0,1,[{offset:0,color:'rgba(59,130,246,0.35)'},{offset:1,color:'rgba(59,130,246,0.02)'}]) }
        },
        {
          name: '领券量', type: 'line', smooth: true, symbol: 'none',
          data: data.coupons,
          itemStyle: { color: '#10b981' },
          areaStyle: { color: new echarts.graphic.LinearGradient(0,0,0,1,[{offset:0,color:'rgba(16,185,129,0.25)'},{offset:1,color:'rgba(16,185,129,0.02)'}]) }
        }
      ]
    })
  } catch (e) { console.error(e) }
}

const loadMonthlyStats = async () => {
  try {
    const res = await axiosInstance.get('/visualization/monthly-stats')
    const data = res.data.data
    const months = data.map(d => `${d.month}月`)
    const purchases = data.map(d => d.purchases)
    const coupons = data.map(d => d.coupons)
    const cvr = [8.5, 5.2, 11.4, 9.8, 14.2, 17.5]
    const chart = echarts.init(document.getElementById('monthly-chart'))
    chart.setOption({
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
      legend: { data: ['购买量', '领券量', 'CVR (%)'], bottom: 0, itemHeight: 10, textStyle: { fontSize: 12 } },
      grid: { left: '3%', right: '4%', bottom: '14%', top: '6%', containLabel: true },
      xAxis: { type: 'category', data: months, axisLabel: { color: '#94a3b8', fontSize: 11 }, axisLine: { lineStyle: { color: '#e2e8f0' } } },
      yAxis: [
        { type: 'value', name: '数量级', nameTextStyle: { fontSize: 11, color: '#94a3b8' }, splitLine: { lineStyle: { type: 'dashed', color: '#f1f5f9' } }, axisLabel: { color: '#94a3b8', fontSize: 11 } },
        { type: 'value', name: '转化率(%)', nameTextStyle: { fontSize: 11, color: '#94a3b8' }, splitLine: { show: false }, axisLabel: { color: '#94a3b8', fontSize: 11 } }
      ],
      series: [
        { name: '购买量', type: 'bar', barMaxWidth: 22, data: purchases, itemStyle: { color: new echarts.graphic.LinearGradient(0,0,0,1,[{offset:0,color:'#60a5fa'},{offset:1,color:'#3b82f6'}]), borderRadius: [4,4,0,0] } },
        { name: '领券量', type: 'bar', barMaxWidth: 22, data: coupons, itemStyle: { color: new echarts.graphic.LinearGradient(0,0,0,1,[{offset:0,color:'#34d399'},{offset:1,color:'#10b981'}]), borderRadius: [4,4,0,0] } },
        { name: 'CVR (%)', type: 'line', yAxisIndex: 1, data: cvr, itemStyle: { color: '#f43f5e' }, symbol: 'circle', symbolSize: 7, lineStyle: { width: 2 }, label: { show: true, position: 'top', formatter: '{c}%', color: '#f43f5e', fontSize: 11, fontWeight: 'bold' } }
      ]
    })
  } catch (e) { console.error(e) }
}

const loadFunnel = async () => {
  try {
    const res = await axiosInstance.get('/visualization/conversion-funnel')
    const data = res.data.funnel
    const chart = echarts.init(document.getElementById('funnel-chart'))
    chart.setOption({
      tooltip: { trigger: 'item', formatter: '{b} : {c}人' },
      color: ['#3b82f6', '#10b981', '#f59e0b', '#f43f5e'],
      series: [{
        type: 'funnel', left: '10%', width: '80%', sort: 'descending', gap: 2,
        data: data.map(item => ({ name: item.stage, value: item.count })),
        label: { show: true, position: 'inside', formatter: '{b}\n{c}人', color: '#fff', fontSize: 12 },
        itemStyle: { borderColor: '#fff', borderWidth: 2, borderRadius: 3 }
      }]
    })
  } catch (e) { console.error(e) }
}

const loadSegmentation = async () => {
  try {
    const res = await axiosInstance.get('/visualization/user-segmentation', { params: { month: 4 } })
    const data = res.data.segments
    const chart = echarts.init(document.getElementById('segment-chart'))
    chart.setOption({
      tooltip: { trigger: 'item', formatter: '{b}: {c}人 ({d}%)' },
      legend: { orient: 'vertical', left: 'left', top: 'center', textStyle: { color: '#64748b', fontSize: 12 } },
      color: ['#3b82f6', '#f59e0b', '#10b981', '#f43f5e'],
      series: [{
        type: 'pie', radius: ['42%', '68%'], center: ['60%', '50%'],
        data,
        itemStyle: { borderRadius: 6, borderColor: '#fff', borderWidth: 3 },
        label: { show: true, formatter: '{b}\n{d}%', fontSize: 12, color: '#64748b' },
        emphasis: { itemStyle: { shadowBlur: 12, shadowColor: 'rgba(0,0,0,0.12)' } }
      }]
    })
  } catch (e) { console.error(e) }
}

onMounted(() => {
  loadOverview()
  loadDailyTrend()
  loadMonthlyStats()
  loadFunnel()
  loadSegmentation()
})
</script>

<style scoped>
.dashboard {
  padding: 16px 20px;
  background: #f0f4f8;
  min-height: 100%;
}

/* ===== 统计卡片 ===== */
.metrics-row { margin-bottom: 16px; }

.stat-card {
  border-radius: 12px;
  padding: 14px 16px;
  position: relative;
  overflow: hidden;
  transition: transform 0.2s, box-shadow 0.2s;
}
.stat-card:hover { transform: translateY(-2px); }

.stat-blue   { background: linear-gradient(135deg, #2563eb, #06b6d4); box-shadow: 0 4px 16px rgba(37,99,235,0.3); }
.stat-green  { background: linear-gradient(135deg, #059669, #10b981); box-shadow: 0 4px 16px rgba(5,150,105,0.3); }
.stat-orange { background: linear-gradient(135deg, #d97706, #f59e0b); box-shadow: 0 4px 16px rgba(217,119,6,0.3); }
.stat-purple { background: linear-gradient(135deg, #7c3aed, #a855f7); box-shadow: 0 4px 16px rgba(124,58,237,0.3); }

.stat-bg-icon { position: absolute; right: -8px; bottom: -8px; pointer-events: none; }

.stat-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }

.stat-icon-wrap {
  width: 34px; height: 34px;
  background: rgba(255,255,255,0.2);
  border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
}

.stat-trend {
  font-size: 11px; font-weight: 600;
  padding: 2px 7px; border-radius: 10px;
  background: rgba(255,255,255,0.2); color: #fff;
}

.stat-value { font-size: 22px; font-weight: 800; color: #fff; line-height: 1.2; margin-bottom: 3px; }
.stat-label { font-size: 12px; color: rgba(255,255,255,0.75); margin-bottom: 10px; }

.stat-bar { height: 3px; background: rgba(255,255,255,0.2); border-radius: 2px; overflow: hidden; }
.stat-bar-fill { height: 100%; background: rgba(255,255,255,0.55); border-radius: 2px; }

/* ===== 图表卡片 ===== */
.charts-row { margin-bottom: 16px; }

.chart-card {
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 1px 8px rgba(0,0,0,0.06);
  transition: box-shadow 0.2s;
}
.chart-card:hover { box-shadow: 0 4px 18px rgba(0,0,0,0.1); }

.chart-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 11px 16px;
  border-bottom: 1px solid #f1f5f9;
  border-left: 3px solid transparent;
  background: linear-gradient(90deg, rgba(0,0,0,0.02) 0%, transparent 100%);
}

.chart-header-left { display: flex; align-items: center; gap: 7px; }

.chart-dot { display: inline-block; width: 7px; height: 7px; border-radius: 50%; flex-shrink: 0; }

.chart-title { font-size: 13px; font-weight: 600; color: #334155; }

.chart-badge {
  font-size: 11px; padding: 2px 8px;
  background: #f1f5f9; color: #64748b;
  border-radius: 8px; font-weight: 500;
}
</style>
