<!-- Register.vue
注册页面 —— 风格与 Login.vue 一致
-->
<template>
  <div class="login-page">
    <!-- 背景装饰 -->
    <div class="bg-decoration">
      <div class="circle circle-1"></div>
      <div class="circle circle-2"></div>
      <div class="circle circle-3"></div>
    </div>

    <!-- 注册卡片 -->
    <div class="login-card">
      <!-- Logo 区 -->
      <div class="login-header">
        <div class="logo-icon">
          <el-icon :size="36" color="#fff"><DataAnalysis /></el-icon>
        </div>
        <h2>创建账号</h2>
        <p class="subtitle">电商用户行为分析系统</p>
      </div>

      <!-- 表单 -->
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        class="login-form"
        @keyup.enter="handleRegister"
      >
        <el-form-item prop="username">
          <el-input
            v-model="form.username"
            placeholder="用户名（3-20个字符）"
            size="large"
            :prefix-icon="User"
            clearable
            autocomplete="username"
          />
        </el-form-item>

        <el-form-item prop="nickname">
          <el-input
            v-model="form.nickname"
            placeholder="昵称（选填，默认同用户名）"
            size="large"
            :prefix-icon="EditPen"
            clearable
          />
        </el-form-item>

        <el-form-item prop="password">
          <el-input
            v-model="form.password"
            placeholder="密码（不少于6个字符）"
            type="password"
            size="large"
            :prefix-icon="Lock"
            show-password
            autocomplete="new-password"
          />
        </el-form-item>

        <el-form-item prop="confirm">
          <el-input
            v-model="form.confirm"
            placeholder="确认密码"
            type="password"
            size="large"
            :prefix-icon="Lock"
            show-password
            autocomplete="new-password"
          />
        </el-form-item>

        <el-button
          type="primary"
          size="large"
          :loading="loading"
          class="login-btn"
          @click="handleRegister"
        >
          {{ loading ? '注册中...' : '注 册' }}
        </el-button>
      </el-form>

      <!-- 跳转登录 -->
      <div class="to-login">
        已有账号？
        <el-link type="primary" @click="router.push('/login')">返回登录</el-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { User, Lock, EditPen, DataAnalysis } from '@element-plus/icons-vue'
import axiosInstance from '@/api/axiosInstance'

const router  = useRouter()
const formRef = ref(null)
const loading = ref(false)

const form = reactive({ username: '', nickname: '', password: '', confirm: '' })

const validateConfirm = (rule, value, callback) => {
  if (value !== form.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度须在 3-20 个字符之间', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于 6 个字符', trigger: 'blur' }
  ],
  confirm: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    { validator: validateConfirm, trigger: 'blur' }
  ]
}

const handleRegister = async () => {
  if (!formRef.value) return
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    await axiosInstance.post('/auth/register', {
      username: form.username.trim(),
      password: form.password,
      nickname: form.nickname.trim() || undefined
    })
    await ElMessageBox.alert(
      '账号注册成功！请使用新账号登录。',
      '注册成功',
      { confirmButtonText: '去登录', type: 'success' }
    )
    router.push('/login')
  } catch (err) {
    const msg = err.response?.data?.detail || '注册失败，请稍后重试'
    ElMessage.error(msg)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
/* 复用 Login.vue 的全部样式 */
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #1a2a4a 0%, #2d4a7a 50%, #1a3a5c 100%);
  position: relative;
  overflow: hidden;
}

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

.login-card {
  width: 420px;
  background: rgba(255, 255, 255, 0.97);
  border-radius: 16px;
  padding: 40px 40px 32px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  position: relative;
  z-index: 1;
}

.login-header { text-align: center; margin-bottom: 28px; }

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

.subtitle { font-size: 13px; color: #909399; margin: 0; }

.login-form { margin-bottom: 8px; }
.login-form :deep(.el-input__wrapper) { border-radius: 8px; }

.login-btn {
  width: 100%;
  border-radius: 8px;
  font-size: 16px;
  letter-spacing: 4px;
  height: 44px;
}

.to-login {
  text-align: center;
  margin-top: 16px;
  font-size: 13px;
  color: #909399;
}
</style>
