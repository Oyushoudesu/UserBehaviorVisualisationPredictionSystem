<!-- Login.vue
登录页面
Vue3 Composition API + Element Plus + Axios + Vue Router
-->
<template>
  <div class="login-page">
    <!-- 背景装饰 -->
    <div class="bg-decoration">
      <div class="circle circle-1"></div>
      <div class="circle circle-2"></div>
      <div class="circle circle-3"></div>
    </div>

    <!-- 登录卡片 -->
    <div class="login-card">
      <!-- Logo区 -->
      <div class="login-header">
        <div class="logo-icon">
          <el-icon :size="36" color="#fff"><DataAnalysis /></el-icon>
        </div>
        <h2>电商用户行为分析系统</h2>
        <p class="subtitle">基于阿里O2O数据集的智能分析平台</p>
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

      <!-- 演示账号提示 -->
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
import axios from 'axios'

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
    // OAuth2PasswordRequestForm 要求 x-www-form-urlencoded
    const params = new URLSearchParams()
    params.append('username', form.username)
    params.append('password', form.password)

    const res = await axiosInstance.post('/auth/login', params, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }})

    const { access_token, expires_in, username, nickname, role } = res.data

    // 存储 Token
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
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #1a2a4a 0%, #2d4a7a 50%, #1a3a5c 100%);
  position: relative;
  overflow: hidden;
}

/* 背景动态圆圈 */
.bg-decoration { position: absolute; inset: 0; pointer-events: none; }

.circle {
  position: absolute;
  border-radius: 50%;
  background: rgba(64, 158, 255, 0.08);
  animation: float 8s ease-in-out infinite;
}
.circle-1 { width: 400px; height: 400px; top: -100px; right: -100px; animation-delay: 0s; }
.circle-2 { width: 300px; height: 300px; bottom: -80px; left: -80px; animation-delay: 2s; }
.circle-3 { width: 200px; height: 200px; top: 40%; left: 10%; animation-delay: 4s; }

@keyframes float {
  0%, 100% { transform: translateY(0) scale(1); }
  50%       { transform: translateY(-20px) scale(1.05); }
}

/* 卡片 */
.login-card {
  width: 420px;
  background: rgba(255, 255, 255, 0.97);
  border-radius: 16px;
  padding: 40px 40px 32px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  position: relative;
  z-index: 1;
}

/* Header */
.login-header { text-align: center; margin-bottom: 32px; }

.logo-icon {
  width: 70px;
  height: 70px;
  background: linear-gradient(135deg, #409EFF, #1a6bc7);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 16px;
  box-shadow: 0 8px 20px rgba(64, 158, 255, 0.4);
}

.login-header h2 {
  font-size: 20px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 6px;
}

.subtitle {
  font-size: 13px;
  color: #909399;
  margin: 0;
}

/* 表单 */
.login-form { margin-bottom: 8px; }

.login-form :deep(.el-input__wrapper) {
  border-radius: 8px;
}

.login-btn {
  width: 100%;
  border-radius: 8px;
  font-size: 16px;
  letter-spacing: 4px;
  height: 44px;
}

/* 演示账号 */
.demo-hint { margin-top: 8px; }

.demo-hint :deep(.el-divider__text) {
  font-size: 12px;
  color: #C0C4CC;
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
}

.demo-tag:hover {
  transform: translateX(4px);
  box-shadow: 2px 2px 8px rgba(0,0,0,0.1);
}
</style>
