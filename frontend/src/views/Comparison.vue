<!-- Comparison.vue
平销期 vs 促销期对比分析页面
Vue3 Composition API + Element Plus + ECharts + Axios
-->
<template>
  <div class="comparison">
    <h1>平销期 vs 促销期对比分析</h1>

    <!-- 说明栏 -->
    <el-alert
      title="平销期：2016-01 ~ 2016-04；促销期（含618）：2016-05 ~ 2016-06"
      type="info"
      :closable="false"
      show-icon
      style="margin-bottom: 20px"
    />

    <!-- 核心差异指标卡 -->
    <el-row :gutter="20" class="metrics-row">
      <el-col :span="6" v-for="item in diffMetrics" :key="item.key">
        <el-card shadow="hover">
          <div class="diff-card">
            <div class="diff-title">{{ item.label }}</div>
            <div class="diff-values">
              <div class="diff-val regular">
                <div class="val-num">{{ item.regular }}</div>
                <div class="val-tag">平销期</div>
              </div>
              <div class="diff-arrow">
                <el-icon :color="item.upIsGood ? '#67C23A' : '#F56C6C'">
                  <component :is="item.trend === 'up' ? 'Top' : 'Bottom'" />
                </el-icon>
                <span :style="{ color: item.upIsGood === (item.trend === 'up') ? '#67C23A' : '#F56C6C' }">
                  {{ item.change }}
                </span>
              </div>
              <div class="diff-val promotion">
                <div class="val-num">{{ item.promotion }}</div>
                <div class="val-tag">促销期</div>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表第一行：双时段行为趋势 + 转化率对比雷达图 -->
    <el-row :gutter="20" class="charts-row">
      <el-col :span="14">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>全周期每日购买趋势</span>
              <el-tooltip content="蓝色=平销期，红色=促销期（5-6月）" placement="top">
                <el-icon color="#909399"><QuestionFilled /></el-icon>
              </el-tooltip>
            </div>
          </template>
          <div v-loading="loading.trend" id="trend-chart" style="height: 400px"></div>
        </el-card>
      </el-col>

      <el-col :span="10">
        <el-card shadow="hover">
          <template #header><span>多维指标对比雷达图</span></template>
          <div v-loading="loading.radar" id="compare-radar-chart" style="height: 400px"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表第二行：用户活跃度对比 + 618效果分析 -->
    <el-row :gutter="20" class="charts-row">
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header><span>月度用户活跃度对比</span></template>
          <div v-loading="loading.active" id="active-chart" style="height: 360px"></div>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>
            <span>618 促销效果分析</span>
            <el-tag type="danger" size="small" style="margin-left: 8px">6月</el-tag>
          </template>
          <div v-loading="loading.effect618" id="effect618-chart" style="height: 360px"></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { QuestionFilled } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import axios from 'axios'

const API_BASE = 'http://localhost:8000/api/v1'

const loading = ref({ trend: false, radar: false, active: false, effect618: false })

// 顶部差异指标（从接口加载后填充）
const diffMetrics = ref([
  { key: 'cvr',             label: '整体转化率(CVR)',   regular: '-', promotion: '-', change: '-', trend: 'up', upIsGood: true },
  { key: 'daily_purchases', label: '日均购买量',         regular: '-', promotion: '-', change: '-', trend: 'up', upIsGood: true },
  { key: 'coupon_rate',     label: '领券率',             regular: '-', promotion: '-', change: '-', trend: 'up', upIsGood: true },
  { key: 'active_users',   label: '月均活跃用户',        regular: '-', promotion: '-', change: '-', trend: 'up', upIsGood: true }
])

// ============================================================================
// 加载对比摘要指标 + 雷达图（合并为一次请求）
// ============================================================================
const loadComparisonSummary = async () => {
  loading.value.radar = true
  try {
    const res = await axios.get(`${API_BASE}/visualization/comparison-summary`)
    const d = res.data

    // 填充顶部差异指标卡
    diffMetrics.value = [
      {
        key: 'cvr', label: '整体转化率(CVR)',
        regular: `${d.regular.cvr}%`, promotion: `${d.promotion.cvr}%`,
        change: `${d.changes.cvr > 0 ? '+' : ''}${d.changes.cvr}%`,
        trend: d.changes.cvr >= 0 ? 'up' : 'down', upIsGood: true
      },
      {
        key: 'daily_purchases', label: '日均购买量',
        regular: d.regular.daily_purchases?.toLocaleString(),
        promotion: d.promotion.daily_purchases?.toLocaleString(),
        change: `${d.changes.daily_purchases > 0 ? '+' : ''}${d.changes.daily_purchases?.toLocaleString()}`,
        trend: d.changes.daily_purchases >= 0 ? 'up' : 'down', upIsGood: true
      },
      {
        key: 'coupon_rate', label: '领券率',
        regular: `${d.regular.coupon_rate}%`, promotion: `${d.promotion.coupon_rate}%`,
        change: `${d.changes.coupon_rate > 0 ? '+' : ''}${d.changes.coupon_rate}%`,
        trend: d.changes.coupon_rate >= 0 ? 'up' : 'down', upIsGood: true
      },
      {
        key: 'active_users', label: '月均活跃用户',
        regular: d.regular.active_users?.toLocaleString(),
        promotion: d.promotion.active_users?.toLocaleString(),
        change: `${d.changes.active_users > 0 ? '+' : ''}${d.changes.active_users?.toLocaleString()}`,
        trend: d.changes.active_users >= 0 ? 'up' : 'down', upIsGood: true
      }
    ]

    // 同一份数据直接渲染雷达图，无需第二次请求
    const chart = echarts.init(document.getElementById('compare-radar-chart'))
    chart.setOption({
      tooltip: {},
      legend: { data: ['平销期', '促销期'], bottom: 0 },
      radar: {
        indicator: [
          { name: '转化率',   max: 100 },
          { name: '购买量',   max: 100 },
          { name: '领券率',   max: 100 },
          { name: '活跃用户', max: 100 },
          { name: '复购率',   max: 100 },
          { name: '核销率',   max: 100 }
        ],
        splitNumber: 4,
        axisName: { color: '#606266', fontSize: 12 }
      },
      series: [{
        type: 'radar',
        data: [
          {
            name: '平销期',
            value: d.radar?.regular || [60, 50, 55, 65, 45, 50],
            areaStyle: { opacity: 0.2 },
            itemStyle: { color: '#409EFF' },
            lineStyle: { color: '#409EFF' }
          },
          {
            name: '促销期',
            value: d.radar?.promotion || [80, 85, 75, 90, 65, 70],
            areaStyle: { opacity: 0.2 },
            itemStyle: { color: '#F56C6C' },
            lineStyle: { color: '#F56C6C' }
          }
        ]
      }]
    })
  } catch (e) {
    console.error('加载对比摘要失败:', e)
  } finally {
    loading.value.radar = false
  }
}

// ============================================================================
// 全周期每日趋势（颜色区分平销期/促销期）
// ============================================================================
const loadTrend = async () => {
  loading.value.trend = true
  try {
    const res = await axios.get(`${API_BASE}/visualization/daily-trend`)
    const data = res.data

    const chart = echarts.init(document.getElementById('trend-chart'))

    // 5月1日起为促销期，用 markArea 标注
    chart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['购买量'], bottom: 0 },
      grid: { left: '3%', right: '4%', bottom: '12%', containLabel: true },
      xAxis: {
        type: 'category',
        data: data.dates,
        axisLabel: { rotate: 45, fontSize: 10, interval: 14 }
      },
      yAxis: { type: 'value', name: '购买量' },
      series: [
        {
          name: '购买量',
          type: 'line',
          data: data.purchases,
          smooth: true,
          symbol: 'none',
          lineStyle: { width: 2 },
          areaStyle: { opacity: 0.1 },
          itemStyle: { color: '#409EFF' },
          markArea: {
            silent: true,
            data: [[
              { name: '促销期（618）', xAxis: data.dates.find(d => d >= '2016-05-01') || '' },
              { xAxis: data.dates[data.dates.length - 1] }
            ]],
            itemStyle: { color: 'rgba(245,108,108,0.08)', borderWidth: 1, borderColor: '#F56C6C', borderType: 'dashed' },
            label: { color: '#F56C6C', position: 'insideTopRight' }
          },
          markLine: {
            silent: true,
            data: [{ name: '618', xAxis: data.dates.find(d => d === '2016-06-18') || '' }],
            lineStyle: { color: '#F56C6C', type: 'solid', width: 2 },
            label: { formatter: '618', color: '#F56C6C' }
          }
        }
      ]
    })
  } catch (e) {
    console.error('加载趋势失败:', e)
  } finally {
    loading.value.trend = false
  }
}

// ============================================================================
// 月度活跃用户对比（分组柱状图）
// ============================================================================
const loadActiveUsers = async () => {
  loading.value.active = true
  try {
    const res = await axios.get(`${API_BASE}/visualization/monthly-stats`)
    const data = res.data.data

    const chart = echarts.init(document.getElementById('active-chart'))
    chart.setOption({
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
      legend: { data: ['购买量', '领券量'], bottom: 0 },
      grid: { left: '3%', right: '4%', bottom: '12%', containLabel: true },
      xAxis: {
        type: 'category',
        data: data.map(d => `${d.month}月`),
        axisLabel: {
          color: params => parseInt(params) >= 5 ? '#F56C6C' : '#606266',
          fontWeight: params => parseInt(params) >= 5 ? 'bold' : 'normal'
        }
      },
      yAxis: { type: 'value', name: '数量' },
      color: ['#409EFF', '#67C23A'],
      series: [
        {
          name: '购买量', type: 'bar', data: data.map(d => d.purchases), barMaxWidth: 40,
          itemStyle: {
            color: params => params.dataIndex >= 4 ? '#F56C6C' : '#409EFF'
          }
        },
        {
          name: '领券量', type: 'bar', data: data.map(d => d.coupons), barMaxWidth: 40,
          itemStyle: {
            color: params => params.dataIndex >= 4 ? '#E6A23C' : '#67C23A'
          }
        }
      ]
    })
  } catch (e) {
    console.error('加载月度活跃失败:', e)
  } finally {
    loading.value.active = false
  }
}

// ============================================================================
// 618 效果分析（6月每日趋势 + 峰值标注）
// ============================================================================
const load618Effect = async () => {
  loading.value.effect618 = true
  try {
    const res = await axios.get(`${API_BASE}/visualization/daily-trend`, {
      params: { start_date: '2016-06-01', end_date: '2016-06-30' }
    })
    const data = res.data

    const chart = echarts.init(document.getElementById('effect618-chart'))
    const maxVal = Math.max(...data.purchases)
    const maxIdx = data.purchases.indexOf(maxVal)

    chart.setOption({
      tooltip: { trigger: 'axis' },
      grid: { left: '3%', right: '4%', bottom: '5%', containLabel: true },
      xAxis: {
        type: 'category',
        data: data.dates.map(d => d.slice(5)),
        axisLabel: { rotate: 45, fontSize: 10 }
      },
      yAxis: { type: 'value', name: '购买量' },
      series: [
        {
          type: 'bar',
          data: data.purchases,
          itemStyle: {
            color: params => params.dataIndex === maxIdx ? '#F56C6C' : '#E6A23C'
          },
          markPoint: {
            data: [{ type: 'max', name: '峰值', label: { formatter: '峰值\n{c}' } }]
          }
        },
        {
          type: 'line',
          data: data.purchases,
          smooth: true,
          symbol: 'none',
          itemStyle: { color: '#F56C6C' },
          lineStyle: { width: 2 }
        }
      ]
    })
  } catch (e) {
    console.error('加载618数据失败:', e)
  } finally {
    loading.value.effect618 = false
  }
}

onMounted(() => {
  loadComparisonSummary()
  loadTrend()
  loadActiveUsers()
  load618Effect()
})
</script>

<style scoped>
.comparison { padding: 20px; }
h1 { margin-bottom: 20px; color: #303133; }
.metrics-row { margin-bottom: 20px; }
.charts-row { margin-bottom: 20px; }

.diff-card { padding: 4px 0; }
.diff-title { font-size: 13px; color: #909399; margin-bottom: 12px; }
.diff-values { display: flex; align-items: center; justify-content: space-between; }
.diff-val { text-align: center; flex: 1; }
.val-num { font-size: 20px; font-weight: bold; color: #303133; }
.val-tag { font-size: 11px; color: #C0C4CC; margin-top: 2px; }
.diff-val.promotion .val-num { color: #F56C6C; }
.diff-val.regular .val-num { color: #409EFF; }
.diff-arrow { display: flex; flex-direction: column; align-items: center; gap: 2px; font-size: 12px; font-weight: bold; }
.card-header { display: flex; align-items: center; }
</style>
