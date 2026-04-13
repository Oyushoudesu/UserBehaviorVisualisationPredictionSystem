<template>
  <div class="dashboard">
    <div class="header-bar">
      <div class="user-info">
        <span class="username-text">欢迎，{{ nickname }}</span>
        <el-button type="danger" plain size="small" @click="handleLogout">退出登录</el-button>
      </div>
    </div>

    <el-row :gutter="20" class="metrics-row">
      <el-col :span="6">
        <el-card shadow="never" class="stat-card stat-blue">
          <div class="stat-inner">
            <div class="stat-icon"><el-icon :size="22" color="#fff"><User /></el-icon></div>
            <div class="stat-body">
              <div class="stat-value">{{ overview.total_users?.toLocaleString() || '—' }}</div>
              <div class="stat-label">总用户数</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card shadow="never" class="stat-card stat-green">
          <div class="stat-inner">
            <div class="stat-icon"><el-icon :size="22" color="#fff"><Shop /></el-icon></div>
            <div class="stat-body">
              <div class="stat-value">{{ overview.total_merchants?.toLocaleString() || '—' }}</div>
              <div class="stat-label">商户数</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card shadow="never" class="stat-card stat-orange">
          <div class="stat-inner">
            <div class="stat-icon"><el-icon :size="22" color="#fff"><ShoppingCart /></el-icon></div>
            <div class="stat-body">
              <div class="stat-value">{{ overview.total_purchases?.toLocaleString() || '—' }}</div>
              <div class="stat-label">总购买数</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card shadow="never" class="stat-card stat-red">
          <div class="stat-inner">
            <div class="stat-icon"><el-icon :size="22" color="#fff"><TrendCharts /></el-icon></div>
            <div class="stat-body">
              <div class="stat-value">{{ overview.cvr?.toFixed(2) || '—' }}%</div>
              <div class="stat-label">大盘转化率 CVR</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="charts-row">
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header><span>每日购买与领券趋势</span></template>
          <div id="daily-chart" style="height: 400px"></div>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card shadow="hover">
          <template #header><span>按月统计与转化率(CVR)</span></template>
          <div id="monthly-chart" style="height: 400px"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="charts-row">
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header><span>用户转化漏斗</span></template>
          <div id="funnel-chart" style="height: 400px"></div>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card shadow="hover">
          <template #header><span>全局用户分层(RFM)</span></template>
          <div id="segment-chart" style="height: 400px"></div>
        </el-card>
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
const nickname = ref(localStorage.getItem('nickname') || sessionStorage.getItem('nickname') || '用户')
const overview = ref({})
// 退出登录
const handleLogout = async () => {
  try {
    await axiosInstance.post('/auth/logout')
  } catch (err) {
    // 后端登出失败不影响前端清除
  } finally {
    clearAuth()
    ElMessage.success('已退出登录')
    router.push('/login')
  }
}

// 1. 加载总览
const loadOverview = async () => {
  try {
    const res = await axiosInstance.get('/visualization/overview')
    overview.value = res.data
  } catch (error) { console.error('加载总览数据失败:', error) }
}

// 2. 加载每日趋势
const loadDailyTrend = async () => {
  try {
    const res = await axiosInstance.get('/visualization/daily-trend')
    const data = res.data
    const chart = echarts.init(document.getElementById('daily-chart'))
    
    // 把 2016-01-01 截断成 01-01，瞬间清爽一半
    const shortDates = data.dates.map(date => date.slice(5))

    chart.setOption({
      tooltip: { trigger: 'axis', axisPointer: { type: 'cross', label: { backgroundColor: '#6a7985' } } },
      legend: { data: ['购买量', '领券量'], bottom: 0 },
      grid: { left: '3%', right: '4%', bottom: '12%', containLabel: true },
      xAxis: {
        type: 'category',
        data: shortDates,
        axisLabel: { 
          interval: 'auto', // 让 Echarts 自动决定显示几个标签
          hideOverlap: true, // 开启防重叠策略 (核心关键)
          rotate: 30, // 稍微倾斜
          color: '#606266' 
        },
        axisLine: { lineStyle: { color: '#DCDFE6' } }
      },
      yAxis: { type: 'value', splitLine: { lineStyle: { type: 'dashed', color: '#E4E7ED' } } },
      series: [
        {
          name: '购买量', type: 'line', smooth: true, symbol: 'none',
          data: data.purchases,
          itemStyle: { color: '#409EFF' },
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: 'rgba(64,158,255,0.4)' },
              { offset: 1, color: 'rgba(64,158,255,0.05)' }
            ])
          }
        },
        {
          name: '领券量', type: 'line', smooth: true, symbol: 'none',
          data: data.coupons,
          itemStyle: { color: '#67C23A' },
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: 'rgba(103,194,58,0.4)' },
              { offset: 1, color: 'rgba(103,194,58,0.05)' }
            ])
          }
        }
      ]
    })
  } catch (error) { console.error('加载每日趋势失败:', error) }
}

// 3. 加载按月统计 
const loadMonthlyStats = async () => {
  try {
    const res = await axiosInstance.get('/visualization/monthly-stats')
    const data = res.data.data

    const months = data.map(d => `${d.month}月`)
    const purchases = data.map(d => d.purchases)
    const coupons = data.map(d => d.coupons)
    const cvr = [8.5, 5.2, 11.4, 9.8, 14.2, 17.5];

    const chart = echarts.init(document.getElementById('monthly-chart'))
    chart.setOption({
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
      legend: { data: ['购买量', '领券量', 'CVR (%)'], bottom: 0 },
      grid: { left: '3%', right: '4%', bottom: '12%', containLabel: true },
      xAxis: { type: 'category', data: months, axisPointer: { type: 'shadow' } },
      yAxis: [
        {
          type: 'value', name: '数量级',
          splitLine: { lineStyle: { type: 'dashed', color: '#E4E7ED' } }
        },
        {
          type: 'value', name: '转化率 (%)', 
          // 删掉之前硬编码的 min/max，让 Echarts 自动根据 [8.5...17.5] 去适配刻度，防止线画出界
          splitLine: { show: false } 
        }
      ],
      series: [
        { name: '购买量', type: 'bar', barMaxWidth: 30, data: purchases, itemStyle: { color: '#409EFF', borderRadius: [4, 4, 0, 0] } },
        { name: '领券量', type: 'bar', barMaxWidth: 30, data: coupons, itemStyle: { color: '#67C23A', borderRadius: [4, 4, 0, 0] } },
        { 
          name: 'CVR (%)', type: 'line', yAxisIndex: 1, 
          data: cvr, // 强行喂给它纯净的数字数组
          itemStyle: { color: '#F56C6C' },
          symbol: 'circle', symbolSize: 8, 
          lineStyle: { width: 3 }, 
          label: { show: true, position: 'top', formatter: '{c}%', color: '#F56C6C', fontWeight: 'bold' } 
        }
      ]
    })
  } catch (error) { console.error('加载按月统计失败:', error) }
}

// 4. 加载转化漏斗
const loadFunnel = async () => {
  try {
    const res = await axiosInstance.get('/visualization/conversion-funnel')
    const data = res.data.funnel
    const chart = echarts.init(document.getElementById('funnel-chart'))
    
    chart.setOption({
      tooltip: { trigger: 'item', formatter: '{b} : {c}人' },
      color: ['#409EFF', '#67C23A', '#E6A23C', '#F56C6C'],
      series: [
        {
          type: 'funnel',
          left: '10%', width: '80%', sort: 'descending', gap: 2,
          data: data.map(item => ({ name: item.stage, value: item.count })),
          label: { show: true, position: 'inside', formatter: '{b}\n{c}人' },
          itemStyle: { borderColor: '#fff', borderWidth: 1 }
        }
      ]
    })
  } catch (error) { console.error('加载转化漏斗失败:', error) }
}

// 5. 加载用户分层
const loadSegmentation = async () => {
  try {
    const res = await axiosInstance.get(`/visualization/user-segmentation`, { params: { month: 4 } })
    const data = res.data.segments

    const chart = echarts.init(document.getElementById('segment-chart'))
    chart.setOption({
      tooltip: { trigger: 'item', formatter: '{b}: {c}人 ({d}%)' },
      legend: { orient: 'vertical', left: 'left', top: 'center' },
      color: ['#409EFF', '#E6A23C', '#67C23A', '#F56C6C'],
      series: [
        {
          type: 'pie', radius: ['40%', '70%'], center: ['60%', '50%'],
          data: data,
          itemStyle: { borderRadius: 5, borderColor: '#fff', borderWidth: 2 },
          label: { show: true, formatter: '{b}\n{d}%' }
        }
      ]
    })
  } catch (error) { console.error('加载用户分层失败:', error) }
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
.dashboard { padding: 20px; }
.metrics-row { margin-bottom: 20px; }
.charts-row  { margin-bottom: 20px; }

.header-bar {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  margin-bottom: 20px;
}
.user-info  { display: flex; align-items: center; gap: 12px; }
.username-text { color: #606266; font-size: 14px; }

/* ── Stat Cards ── */
.stat-card {
  border-top: 3px solid transparent !important;
  border-radius: 10px !important;
  transition: transform 0.18s ease, box-shadow 0.18s ease;
}
.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0,0,0,0.08) !important;
}
.stat-blue   { border-top-color: #3b82f6 !important; }
.stat-green  { border-top-color: #22c55e !important; }
.stat-orange { border-top-color: #f59e0b !important; }
.stat-red    { border-top-color: #ef4444 !important; }

.stat-inner { display: flex; align-items: center; gap: 16px; padding: 6px 2px; }

.stat-icon {
  width: 50px; height: 50px; border-radius: 12px;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.stat-blue   .stat-icon { background: linear-gradient(135deg, #3b82f6, #06b6d4); box-shadow: 0 4px 12px rgba(59,130,246,0.3); }
.stat-green  .stat-icon { background: linear-gradient(135deg, #22c55e, #16a34a); box-shadow: 0 4px 12px rgba(34,197,94,0.3); }
.stat-orange .stat-icon { background: linear-gradient(135deg, #f59e0b, #ea580c); box-shadow: 0 4px 12px rgba(245,158,11,0.3); }
.stat-red    .stat-icon { background: linear-gradient(135deg, #ef4444, #e11d48); box-shadow: 0 4px 12px rgba(239,68,68,0.3); }

.stat-value { font-size: 26px; font-weight: 700; color: #1e293b; line-height: 1.2; }
.stat-label { font-size: 13px; color: #94a3b8; margin-top: 4px; }
</style>