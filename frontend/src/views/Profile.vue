<!-- Profile.vue - 个人资料设置页面 -->
<template>
  <div class="profile-page">
    <div class="profile-container">
      <!-- 用户头像信息卡 -->
      <div class="user-card">
        <div class="avatar">{{ avatarLetter }}</div>
        <div class="user-info">
          <div class="user-name">{{ nickname }}</div>
          <div class="user-meta">@{{ username }} · {{ roleLabel }}</div>
        </div>
      </div>

      <!-- 修改资料 -->
      <div class="section-card">
        <div class="section-title">修改个人资料</div>
        <el-form ref="profileFormRef" :model="profileForm" :rules="profileRules" label-width="90px">
          <el-form-item label="昵称" prop="nickname">
            <el-input v-model="profileForm.nickname" placeholder="请输入新昵称" clearable />
          </el-form-item>
          <el-form-item label="新用户名" prop="new_username">
            <el-input v-model="profileForm.new_username" placeholder="留空则不修改用户名" clearable />
          </el-form-item>
          <el-form-item label="当前密码" prop="current_password">
            <el-input
              v-model="profileForm.current_password"
              type="password"
              placeholder="修改用户名时必填"
              show-password
            />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" :loading="profileLoading" @click="handleUpdateProfile">
              保存修改
            </el-button>
            <el-button @click="resetProfileForm">重置</el-button>
          </el-form-item>
        </el-form>
      </div>

      <!-- 修改密码 -->
      <div class="section-card">
        <div class="section-title">修改密码</div>
        <el-form ref="passwordFormRef" :model="passwordForm" :rules="passwordRules" label-width="90px">
          <el-form-item label="原密码" prop="old_password">
            <el-input
              v-model="passwordForm.old_password"
              type="password"
              placeholder="请输入原密码"
              show-password
            />
          </el-form-item>
          <el-form-item label="新密码" prop="new_password">
            <el-input
              v-model="passwordForm.new_password"
              type="password"
              placeholder="至少 6 个字符"
              show-password
            />
          </el-form-item>
          <el-form-item label="确认新密码" prop="confirm_password">
            <el-input
              v-model="passwordForm.confirm_password"
              type="password"
              placeholder="再次输入新密码"
              show-password
            />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" :loading="passwordLoading" @click="handleChangePassword">
              修改密码
            </el-button>
            <el-button @click="resetPasswordForm">重置</el-button>
          </el-form-item>
        </el-form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import axiosInstance from '@/api/axiosInstance'

const router = useRouter()

// 从 storage 读取当前用户信息
const getStorage = (key) =>
  localStorage.getItem(key) || sessionStorage.getItem(key) || ''

const username = ref(getStorage('username'))
const nickname = ref(getStorage('nickname'))
const role     = ref(getStorage('role'))

const avatarLetter = computed(() =>
  (nickname.value || username.value || '?')[0].toUpperCase()
)
const roleLabel = computed(() => {
  const map = { admin: '管理员', viewer: '只读用户', analyst: '分析师' }
  return map[role.value] || role.value
})

// ── 修改资料 ──────────────────────────────────────────
const profileFormRef = ref(null)
const profileLoading = ref(false)

const profileForm = reactive({
  nickname: nickname.value,
  new_username: '',
  current_password: ''
})

const profileRules = {
  nickname: [{ max: 30, message: '昵称不能超过 30 个字符', trigger: 'blur' }],
  new_username: [
    {
      validator: (_, value, cb) => {
        if (value && (value.length < 3 || value.length > 20)) {
          cb(new Error('用户名长度须在 3-20 个字符之间'))
        } else {
          cb()
        }
      },
      trigger: 'blur'
    }
  ]
}

const handleUpdateProfile = async () => {
  const valid = await profileFormRef.value.validate().catch(() => false)
  if (!valid) return

  profileLoading.value = true
  try {
    const payload = {}
    if (profileForm.nickname.trim()) payload.nickname = profileForm.nickname.trim()
    if (profileForm.new_username.trim()) {
      payload.new_username = profileForm.new_username.trim()
      payload.current_password = profileForm.current_password
    }

    const res = await axiosInstance.put('/auth/profile', payload)
    const { username: newUsername, nickname: newNickname } = res.data

    // 同步更新 storage
    const storage = localStorage.getItem('token') ? localStorage : sessionStorage
    storage.setItem('username', newUsername)
    storage.setItem('nickname', newNickname)
    username.value = newUsername
    nickname.value = newNickname

    ElMessage.success('资料更新成功')
    profileForm.current_password = ''
    profileForm.new_username = ''
  } catch (err) {
    ElMessage.error(err.response?.data?.detail || '更新失败，请稍后重试')
  } finally {
    profileLoading.value = false
  }
}

const resetProfileForm = () => {
  profileForm.nickname = nickname.value
  profileForm.new_username = ''
  profileForm.current_password = ''
  profileFormRef.value?.clearValidate()
}

// ── 修改密码 ──────────────────────────────────────────
const passwordFormRef = ref(null)
const passwordLoading = ref(false)

const passwordForm = reactive({
  old_password: '',
  new_password: '',
  confirm_password: ''
})

const passwordRules = {
  old_password: [{ required: true, message: '请输入原密码', trigger: 'blur' }],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '新密码长度不能少于 6 个字符', trigger: 'blur' }
  ],
  confirm_password: [
    { required: true, message: '请再次输入新密码', trigger: 'blur' },
    {
      validator: (_, value, cb) => {
        if (value !== passwordForm.new_password) {
          cb(new Error('两次输入的密码不一致'))
        } else {
          cb()
        }
      },
      trigger: 'blur'
    }
  ]
}

const handleChangePassword = async () => {
  const valid = await passwordFormRef.value.validate().catch(() => false)
  if (!valid) return

  passwordLoading.value = true
  try {
    await axiosInstance.put('/auth/password', {
      old_password: passwordForm.old_password,
      new_password: passwordForm.new_password
    })

    ElMessage.success('密码修改成功，请重新登录')
    // 清除登录态，跳转到登录页
    localStorage.clear()
    sessionStorage.clear()
    setTimeout(() => router.push('/login'), 1200)
  } catch (err) {
    ElMessage.error(err.response?.data?.detail || '密码修改失败，请稍后重试')
  } finally {
    passwordLoading.value = false
  }
}

const resetPasswordForm = () => {
  passwordForm.old_password = ''
  passwordForm.new_password = ''
  passwordForm.confirm_password = ''
  passwordFormRef.value?.clearValidate()
}
</script>

<style scoped>
.profile-page {
  padding: 28px 32px;
  min-height: calc(100vh - 54px);
  background: #f1f5f9;
}

.profile-container {
  max-width: 600px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* 用户信息卡 */
.user-card {
  display: flex;
  align-items: center;
  gap: 18px;
  background: #fff;
  border-radius: 12px;
  padding: 24px 28px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}

.avatar {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: linear-gradient(135deg, #3b82f6, #06b6d4);
  color: #fff;
  font-size: 24px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.user-name {
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
}

.user-meta {
  font-size: 13px;
  color: #94a3b8;
  margin-top: 4px;
}

/* 功能卡片 */
.section-card {
  background: #fff;
  border-radius: 12px;
  padding: 24px 28px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}

.section-title {
  font-size: 15px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f1f5f9;
}
</style>
