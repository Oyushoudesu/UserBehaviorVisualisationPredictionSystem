<!-- Dashboard.vue 
仪表盘页面，展示总览数据、每日趋势、按月统计、转化漏斗、用户分层
使用Element Plus组件库，使用ECharts库绘制图表
使用Axios库发送请求
使用Vue3 Composition API
使用Vue Router进行路由
使用Vuex进行状态管理
使用Vuex进行状态管理
启动指令：cd frontend && npm run dev
-->
<template>
  <div class="dashboard">
    <h1>电商用户行为分析系统</h1>
    
    <!-- 核心指标卡片 -->
    <el-row :gutter="20" class="metrics-row">
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="metric-card">
            <el-icon :size="40" color="#409EFF"><User /></el-icon>
            <div class="metric-content">
              <div class="metric-value">{{ overview.total_users?.toLocaleString() || '-' }}</div>
              <div class="metric-label">总用户数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="metric-card">
            <el-icon :size="40" color="#67C23A"><Shop /></el-icon>
            <div class="metric-content">
              <div class="metric-value">{{ overview.total_merchants?.toLocaleString() || '-' }}</div>
              <div class="metric-label">商户数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="metric-card">
            <el-icon :size="40" color="#E6A23C"><ShoppingCart /></el-icon>
            <div class="metric-content">
              <div class="metric-value">{{ overview.total_purchases?.toLocaleString() || '-' }}</div>
              <div class="metric-label">总购买数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="metric-card">
            <el-icon :size="40" color="#F56C6C"><TrendCharts /></el-icon>
            <div class="metric-content">
              <div class="metric-value">{{ overview.cvr?.toFixed(2) || '-' }}%</div>
              <div class="metric-label">转化率(CVR)</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表区域 -->
    <el-row :gutter="20" class="charts-row">
      <!-- 每日趋势 -->
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>
            <span>每日购买与领券趋势</span>
          </template>
          <div id="daily-chart" style="height: 400px"></div>
        </el-card>
      </el-col>

      <!-- 按月统计 -->
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>
            <span>按月统计与CVR</span>
          </template>
          <div id="monthly-chart" style="height: 400px"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="charts-row">
      <!-- 转化漏斗 -->
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>
            <span>用户转化漏斗</span>
          </template>
          <div id="funnel-chart" style="height: 400px"></div>
        </el-card>
      </el-col>

      <!-- 用户分层 -->
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>
            <span>用户分层(RFM)</span>
          </template>
          <div id="segment-chart" style="height: 400px"></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { User, Shop, ShoppingCart, TrendCharts } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import axios from 'axios'

// API基础URL
const API_BASE = 'http://localhost:8000/api/v1'

// 数据
const overview = ref({})

// 加载总览数据
const loadOverview = async () => {
  try {
    const res = await axios.get(`${API_BASE}/visualization/overview`)
    overview.value = res.data
  } catch (error) {
    console.error('加载总览数据失败:', error)
  }
}

// 加载每日趋势
const loadDailyTrend = async () => {
  try {
    const res = await axios.get(`${API_BASE}/visualization/daily-trend`)
    const data = res.data

    const chart = echarts.init(document.getElementById('daily-chart'))
    chart.setOption({
      tooltip: {
        trigger: 'axis'
      },
      legend: {
        data: ['购买', '领券']
      },
      xAxis: {
        type: 'category',
        data: data.dates,
        axisLabel: {
          rotate: 45
        }
      },
      yAxis: {
        type: 'value'
      },
      series: [
        {
          name: '购买',
          type: 'line',
          data: data.purchases,
          smooth: true,
          itemStyle: { color: '#409EFF' }
        },
        {
          name: '领券',
          type: 'line',
          data: data.coupons,
          smooth: true,
          itemStyle: { color: '#67C23A' }
        }
      ]
    })
  } catch (error) {
    console.error('加载每日趋势失败:', error)
  }
}

// 加载按月统计
const loadMonthlyStats = async () => {
  try {
    const res = await axios.get(`${API_BASE}/visualization/monthly-stats`)
    const data = res.data.data

    const months = data.map(d => `${d.month}月`)
    const purchases = data.map(d => d.purchases)
    const coupons = data.map(d => d.coupons)
    const cvr = data.map(d => d.cvr)

    const chart = echarts.init(document.getElementById('monthly-chart'))
    chart.setOption({
      tooltip: {
        trigger: 'axis'
      },
      legend: {
        data: ['购买', '领券', 'CVR']
      },
      xAxis: {
        type: 'category',
        data: months
      },
      yAxis: [
        {
          type: 'value',
          name: '数量'
        },
        {
          type: 'value',
          name: 'CVR (%)',
          min: 0,
          max: 20
        }
      ],
      series: [
        {
          name: '购买',
          type: 'bar',
          data: purchases,
          itemStyle: { color: '#409EFF' }
        },
        {
          name: '领券',
          type: 'bar',
          data: coupons,
          itemStyle: { color: '#67C23A' }
        },
        {
          name: 'CVR',
          type: 'line',
          yAxisIndex: 1,
          data: cvr,
          itemStyle: { color: '#F56C6C' }
        }
      ]
    })
  } catch (error) {
    console.error('加载按月统计失败:', error)
  }
}

// 加载转化漏斗
const loadFunnel = async () => {
  try {
    const res = await axios.get(`${API_BASE}/visualization/conversion-funnel`)
    const data = res.data.funnel

    const chart = echarts.init(document.getElementById('funnel-chart'))
    chart.setOption({
      tooltip: {
        trigger: 'item',
        formatter: '{b} : {c}'
      },
      series: [
        {
          type: 'funnel',
          data: data.map(item => ({
            name: item.stage,
            value: item.count
          })),
          label: {
            show: true,
            position: 'inside'
          }
        }
      ]
    })
  } catch (error) {
    console.error('加载转化漏斗失败:', error)
  }
}

// 加载用户分层
const loadSegmentation = async () => {
  try {
    const res = await axios.get(`${API_BASE}/visualization/user-segmentation`)
    const data = res.data.segments

    const chart = echarts.init(document.getElementById('segment-chart'))
    chart.setOption({
      tooltip: {
        trigger: 'item'
      },
      legend: {
        orient: 'vertical',
        left: 'left'
      },
      series: [
        {
          type: 'pie',
          radius: '60%',
          data: data,
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          }
        }
      ]
    })
  } catch (error) {
    console.error('加载用户分层失败:', error)
  }
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
  padding: 20px;
}

h1 {
  margin-bottom: 30px;
  color: #303133;
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
</style>