<!-- Login.vue -->
<template>
  <div class="login-page">
    <!-- 动态背景层 -->
    <div class="bg-layer">
      <!-- 光晕球 -->
      <div class="orb orb-1"></div>
      <div class="orb orb-2"></div>
      <div class="orb orb-3"></div>
      <!-- 网格 -->
      <div class="grid-overlay"></div>
      <!-- 粒子 -->
      <div class="particles">
        <span v-for="i in 24" :key="i" class="particle" :style="particleStyle(i)"></span>
      </div>
    </div>

    <!-- 左侧装饰面板（宽屏可见） -->
    <div class="side-panel">
      <div class="side-content">
        <div class="side-title">智能数据分析</div>
        <div class="side-sub">洞察电商用户行为，驱动业务增长</div>
        <!-- 迷你统计卡片 -->
        <div class="stat-cards">
          <div v-for="s in stats" :key="s.label" class="stat-card">
            <div class="stat-value">{{ s.value }}</div>
            <div class="stat-label">{{ s.label }}</div>
          </div>
        </div>
        <!-- 装饰图表 -->
        <div class="deco-chart">
          <svg viewBox="0 0 200 80" preserveAspectRatio="none">
            <defs>
              <linearGradient id="lineGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stop-color="#60a5fa" stop-opacity="0.5"/>
                <stop offset="100%" stop-color="#60a5fa" stop-opacity="0"/>
              </linearGradient>
            </defs>
            <path d="M0,70 C30,55 50,20 80,30 S130,10 160,25 S185,15 200,20 L200,80 L0,80 Z"
                  fill="url(#lineGrad)"/>
            <path d="M0,70 C30,55 50,20 80,30 S130,10 160,25 S185,15 200,20"
                  fill="none" stroke="#60a5fa" stroke-width="2" class="chart-line"/>
          </svg>
        </div>
        <!-- 底部标签 -->
        <div class="feature-tags">
          <span v-for="t in features" :key="t" class="ftag">{{ t }}</span>
        </div>
      </div>
    </div>

    <!-- 登录卡片 -->
    <div class="login-card">
      <!-- 卡片顶部光条 -->
      <div class="card-glow-bar"></div>

      <!-- Logo区 -->
      <div class="login-header">
        <div class="logo-wrap">
          <div class="logo-icon">
            <el-icon :size="34" color="#fff"><DataAnalysis /></el-icon>
          </div>
          <div class="logo-ring"></div>
        </div>
        <h2>电商用户行为分析系统</h2>
        <p class="subtitle">基于阿里电商的智能分析平台</p>
      </div>

      <!-- 表单区 -->
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        class="login-form"
        @keyup.enter="handleLogin"
      >
        <el-form-item prop="username">
          <el-input
            v-model="form.username"
            placeholder="用户名"
            size="large"
            :prefix-icon="User"
            clearable
            autocomplete="username"
          />
        </el-form-item>

        <el-form-item prop="password">
          <el-input
            v-model="form.password"
            placeholder="密码"
            type="password"
            size="large"
            :prefix-icon="Lock"
            show-password
            autocomplete="current-password"
          />
        </el-form-item>

        <el-form-item>
          <el-checkbox v-model="rememberMe">记住我（8小时内免登录）</el-checkbox>
        </el-form-item>

        <el-button
          type="primary"
          size="large"
          :loading="loading"
          class="login-btn"
          @click="handleLogin"
        >
          {{ loading ? '登录中...' : '登 录' }}
        </el-button>
      </el-form>

      <!-- 注册入口 -->
      <div class="to-register">
        还没有账号？
        <el-link type="primary" @click="router.push('/register')">立即注册</el-link>
      </div>

      <!-- 演示账号 -->
      <div class="demo-hint">
        <el-divider>演示账号</el-divider>
        <div class="demo-accounts">
          <el-tag
            v-for="acc in demoAccounts"
            :key="acc.username"
            class="demo-tag"
            :type="acc.type"
            effect="plain"
            @click="fillDemo(acc)"
          >
            {{ acc.label }}：{{ acc.username }} / {{ acc.password }}
          </el-tag>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock, DataAnalysis } from '@element-plus/icons-vue'
import axiosInstance from '@/api/axiosInstance'

const router = useRouter()
const formRef = ref(null)
const loading = ref(false)
const rememberMe = ref(false)
const form = reactive({ username: '', password: '' })

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

const demoAccounts = [
  { username: 'admin',  password: 'Admin@123', label: '管理员', type: '' },
  { username: 'demo',   password: 'Demo@123',  label: '演示',   type: 'success' },
  { username: 'viewer', password: 'View@123',  label: '只读',   type: 'info' }
]

const stats = [
  { value: '1.2亿+', label: '行为记录' },
  { value: '98.7%', label: '预测准确率' },
  { value: '5大', label: '分析维度' },
  { value: '实时', label: '数据更新' },
]

const features = ['用户画像', '行为预测', '漏斗分析', '留存分析', '智能推荐']

const particleStyle = (i) => {
  const size = 2 + (i % 4)
  const left = (i * 17 + 5) % 95
  const top = (i * 23 + 10) % 90
  const delay = (i * 0.4) % 6
  const dur = 6 + (i % 5)
  return {
    width: `${size}px`,
    height: `${size}px`,
    left: `${left}%`,
    top: `${top}%`,
    animationDelay: `${delay}s`,
    animationDuration: `${dur}s`,
    opacity: 0.15 + (i % 5) * 0.08,
  }
}

const fillDemo = (acc) => {
  form.username = acc.username
  form.password = acc.password
}

const handleLogin = async () => {
  if (!formRef.value) return
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    const params = new URLSearchParams()
    params.append('username', form.username)
    params.append('password', form.password)

    const res = await axiosInstance.post('/auth/login', params, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    })

    const { access_token, expires_in, username, nickname, role } = res.data
    const storage = rememberMe.value ? localStorage : sessionStorage
    storage.setItem('token', access_token)
    storage.setItem('username', username)
    storage.setItem('nickname', nickname)
    storage.setItem('role', role)
    storage.setItem('token_expire', Date.now() + expires_in * 1000)
    ElMessage.success(`欢迎回来，${nickname}！`)
    router.push('/')
  } catch (err) {
    const msg = err.response?.data?.detail || '登录失败，请检查用户名和密码'
    ElMessage.error(msg)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
/* ===== 整体布局 ===== */
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #0d1b2e 0%, #112240 40%, #0d2137 70%, #0a1628 100%);
  position: relative;
  overflow: hidden;
  gap: 60px;
  padding: 40px 20px;
}

/* ===== 背景层 ===== */
.bg-layer { position: absolute; inset: 0; pointer-events: none; }

/* 光晕球 */
.orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  animation: orbFloat 10s ease-in-out infinite;
}
.orb-1 {
  width: 500px; height: 500px;
  background: radial-gradient(circle, rgba(56, 139, 253, 0.18) 0%, transparent 70%);
  top: -150px; right: -100px;
  animation-delay: 0s;
}
.orb-2 {
  width: 400px; height: 400px;
  background: radial-gradient(circle, rgba(88, 101, 242, 0.15) 0%, transparent 70%);
  bottom: -120px; left: -80px;
  animation-delay: 3s;
}
.orb-3 {
  width: 300px; height: 300px;
  background: radial-gradient(circle, rgba(32, 201, 151, 0.10) 0%, transparent 70%);
  top: 40%; left: 20%;
  animation-delay: 6s;
}
@keyframes orbFloat {
  0%, 100% { transform: translateY(0) scale(1); }
  50%       { transform: translateY(-30px) scale(1.08); }
}

/* 网格点阵 */
.grid-overlay {
  position: absolute;
  inset: 0;
  background-image:
    radial-gradient(circle, rgba(96, 165, 250, 0.12) 1px, transparent 1px);
  background-size: 36px 36px;
}

/* 粒子 */
.particles { position: absolute; inset: 0; }
.particle {
  position: absolute;
  border-radius: 50%;
  background: rgba(96, 165, 250, 0.8);
  animation: particleDrift linear infinite;
}
@keyframes particleDrift {
  0%   { transform: translateY(0) translateX(0); opacity: 0; }
  10%  { opacity: 1; }
  90%  { opacity: 0.6; }
  100% { transform: translateY(-80px) translateX(20px); opacity: 0; }
}

/* ===== 左侧装饰面板 ===== */
.side-panel {
  display: none;
  width: 340px;
  flex-shrink: 0;
  position: relative;
  z-index: 1;
}
@media (min-width: 960px) {
  .side-panel { display: block; }
}

.side-content { color: #fff; }

.side-title {
  font-size: 28px;
  font-weight: 700;
  background: linear-gradient(90deg, #60a5fa, #a78bfa);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 8px;
}

.side-sub {
  font-size: 14px;
  color: rgba(255,255,255,0.55);
  margin-bottom: 28px;
  line-height: 1.6;
}

.stat-cards {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-bottom: 24px;
}

.stat-card {
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 12px;
  padding: 14px 16px;
  backdrop-filter: blur(8px);
  transition: background 0.3s;
}
.stat-card:hover { background: rgba(255,255,255,0.1); }

.stat-value {
  font-size: 20px;
  font-weight: 700;
  color: #60a5fa;
  margin-bottom: 2px;
}

.stat-label {
  font-size: 12px;
  color: rgba(255,255,255,0.5);
}

/* 装饰折线图 */
.deco-chart {
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 12px;
  padding: 12px 16px;
  margin-bottom: 20px;
  overflow: hidden;
}
.deco-chart svg { width: 100%; height: 70px; display: block; }

.chart-line {
  stroke-dasharray: 400;
  stroke-dashoffset: 400;
  animation: drawLine 2.5s ease forwards;
}
@keyframes drawLine {
  to { stroke-dashoffset: 0; }
}

/* 特性标签 */
.feature-tags { display: flex; flex-wrap: wrap; gap: 8px; }

.ftag {
  font-size: 12px;
  padding: 4px 12px;
  border-radius: 20px;
  background: rgba(96, 165, 250, 0.12);
  border: 1px solid rgba(96, 165, 250, 0.25);
  color: rgba(255,255,255,0.65);
}

/* ===== 登录卡片 ===== */
.login-card {
  width: 420px;
  flex-shrink: 0;
  background: rgba(255, 255, 255, 0.97);
  border-radius: 20px;
  padding: 0 40px 32px;
  box-shadow:
    0 0 0 1px rgba(255,255,255,0.08),
    0 25px 60px rgba(0, 0, 0, 0.5),
    0 0 40px rgba(56, 139, 253, 0.15);
  position: relative;
  z-index: 1;
  overflow: hidden;
}

/* 顶部彩虹光条 */
.card-glow-bar {
  height: 4px;
  background: linear-gradient(90deg, #3b82f6, #8b5cf6, #06b6d4, #10b981);
  background-size: 200% 100%;
  animation: shiftGrad 4s linear infinite;
  margin: 0 -40px 32px;
}
@keyframes shiftGrad {
  0%   { background-position: 0% 50%; }
  100% { background-position: 200% 50%; }
}

/* Logo */
.login-header { text-align: center; margin-bottom: 28px; }

.logo-wrap {
  position: relative;
  width: 76px;
  height: 76px;
  margin: 0 auto 16px;
}

.logo-icon {
  width: 76px;
  height: 76px;
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8px 24px rgba(59, 130, 246, 0.45);
  position: relative;
  z-index: 1;
}

.logo-ring {
  position: absolute;
  inset: -6px;
  border-radius: 26px;
  border: 2px solid transparent;
  background: linear-gradient(135deg, rgba(59,130,246,0.4), rgba(139,92,246,0.4)) border-box;
  -webkit-mask: linear-gradient(#fff 0 0) padding-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: destination-out;
  mask-composite: exclude;
  animation: ringPulse 3s ease-in-out infinite;
}
@keyframes ringPulse {
  0%, 100% { opacity: 0.4; transform: scale(1); }
  50%       { opacity: 1;   transform: scale(1.05); }
}

.login-header h2 {
  font-size: 20px;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 6px;
  letter-spacing: 0.5px;
}

.subtitle {
  font-size: 13px;
  color: #94a3b8;
  margin: 0;
}

/* 表单 */
.login-form { margin-bottom: 8px; }

.login-form :deep(.el-input__wrapper) {
  border-radius: 10px;
  box-shadow: 0 0 0 1px #e2e8f0;
  transition: box-shadow 0.2s;
}
.login-form :deep(.el-input__wrapper:hover),
.login-form :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 2px #3b82f6 !important;
}

.login-btn {
  width: 100%;
  border-radius: 10px;
  font-size: 16px;
  letter-spacing: 4px;
  height: 46px;
  background: linear-gradient(90deg, #3b82f6, #6366f1);
  border: none;
  box-shadow: 0 4px 16px rgba(99, 102, 241, 0.4);
  transition: transform 0.15s, box-shadow 0.15s;
}
.login-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(99, 102, 241, 0.55);
}
.login-btn:active { transform: translateY(0); }

/* 注册 */
.to-register {
  text-align: center;
  margin-top: 12px;
  margin-bottom: 4px;
  font-size: 13px;
  color: #94a3b8;
}

/* 演示账号 */
.demo-hint { margin-top: 8px; }

.demo-hint :deep(.el-divider__text) {
  font-size: 12px;
  color: #cbd5e1;
  background: #fff;
}

.demo-accounts {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.demo-tag {
  cursor: pointer;
  font-size: 12px;
  transition: all 0.2s;
  text-align: center;
  border-radius: 8px;
}
.demo-tag:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.12);
}
</style>
