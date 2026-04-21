<!-- Profile.vue - 个人资料设置页面 -->
<template>
  <div class="profile-page">
    <div class="profile-container">
      <!-- 用户头像信息卡 -->
      <div class="user-card">
        <div class="card-banner">
          <div class="banner-orb orb-a"></div>
          <div class="banner-orb orb-b"></div>
          <div class="banner-grid"></div>
        </div>
        <div class="card-body">
          <div class="avatar-wrap">
            <div class="avatar">{{ avatarLetter }}</div>
            <div class="avatar-ring"></div>
          </div>
          <div class="user-info">
            <div class="user-name">
              {{ nickname }}
              <span class="role-badge" :class="`role-${role}`">{{ roleLabel }}</span>
            </div>
            <div class="user-meta">
              <el-icon><User /></el-icon>
              <span>@{{ username }}</span>
            </div>
          </div>
        </div>
      </div>

      <div class="grid-2">
      <!-- 修改资料 -->
      <div class="section-card">
        <div class="section-title">
          <div class="title-icon icon-blue"><el-icon :size="18"><EditPen /></el-icon></div>
          <div>
            <div class="title-text">修改个人资料</div>
            <div class="title-sub">更新昵称或用户名</div>
          </div>
        </div>
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
        <div class="section-title">
          <div class="title-icon icon-purple"><el-icon :size="18"><Lock /></el-icon></div>
          <div>
            <div class="title-text">修改密码</div>
            <div class="title-sub">定期更换以保障账号安全</div>
          </div>
        </div>
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
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { User, Lock, EditPen } from '@element-plus/icons-vue'
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
  background: linear-gradient(180deg, #eef2f9 0%, #f1f5f9 100%);
}

.profile-container {
  max-width: 1100px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* ===== 用户信息卡 ===== */
.user-card {
  background: #fff;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(15, 23, 42, 0.06);
  position: relative;
}

.card-banner {
  position: relative;
  height: 120px;
  background: linear-gradient(120deg, #3b82f6 0%, #6366f1 45%, #8b5cf6 100%);
  overflow: hidden;
}
.banner-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(40px);
  opacity: 0.6;
}
.orb-a {
  width: 220px; height: 220px;
  background: rgba(255,255,255,0.25);
  top: -80px; right: -40px;
}
.orb-b {
  width: 180px; height: 180px;
  background: rgba(6, 182, 212, 0.45);
  bottom: -100px; left: 20%;
}
.banner-grid {
  position: absolute; inset: 0;
  background-image: radial-gradient(circle, rgba(255,255,255,0.18) 1px, transparent 1px);
  background-size: 22px 22px;
  opacity: 0.4;
}

.card-body {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 0 32px 24px;
  margin-top: -40px;
  position: relative;
}

.avatar-wrap {
  position: relative;
  width: 88px; height: 88px;
  flex-shrink: 0;
}
.avatar {
  width: 88px; height: 88px;
  border-radius: 50%;
  background: linear-gradient(135deg, #3b82f6, #6366f1);
  color: #fff;
  font-size: 36px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 4px solid #fff;
  box-shadow: 0 8px 24px rgba(59, 130, 246, 0.35);
  position: relative;
  z-index: 1;
}
.avatar-ring {
  position: absolute;
  inset: -4px;
  border-radius: 50%;
  border: 2px solid transparent;
  background: linear-gradient(135deg, rgba(59,130,246,0.5), rgba(139,92,246,0.5)) border-box;
  -webkit-mask: linear-gradient(#fff 0 0) padding-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: destination-out;
  mask-composite: exclude;
  animation: ringPulse 3s ease-in-out infinite;
}
@keyframes ringPulse {
  0%, 100% { opacity: 0.5; transform: scale(1); }
  50%      { opacity: 1;   transform: scale(1.06); }
}

.user-info { padding-top: 44px; flex: 1; min-width: 0; }

.user-name {
  font-size: 20px;
  font-weight: 700;
  color: #0f172a;
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.role-badge {
  font-size: 12px;
  font-weight: 600;
  padding: 3px 10px;
  border-radius: 20px;
  letter-spacing: 0.3px;
}
.role-admin   { background: linear-gradient(90deg, #fef3c7, #fde68a); color: #b45309; }
.role-viewer  { background: #f1f5f9; color: #64748b; }
.role-analyst { background: linear-gradient(90deg, #dbeafe, #bfdbfe); color: #1d4ed8; }

.user-meta {
  font-size: 13px;
  color: #94a3b8;
  margin-top: 6px;
  display: flex;
  align-items: center;
  gap: 6px;
}

/* ===== 两列布局 ===== */
.grid-2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}
@media (max-width: 900px) {
  .grid-2 { grid-template-columns: 1fr; }
}

/* ===== 功能卡片 ===== */
.section-card {
  background: #fff;
  border-radius: 16px;
  padding: 24px 28px;
  box-shadow: 0 4px 20px rgba(15, 23, 42, 0.06);
  border: 1px solid rgba(226, 232, 240, 0.8);
  transition: box-shadow 0.25s, transform 0.25s;
}
.section-card:hover {
  box-shadow: 0 8px 28px rgba(15, 23, 42, 0.1);
  transform: translateY(-2px);
}

.section-title {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 22px;
  padding-bottom: 14px;
  border-bottom: 1px solid #f1f5f9;
}
.title-icon {
  width: 38px; height: 38px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  flex-shrink: 0;
}
.icon-blue   { background: linear-gradient(135deg, #3b82f6, #6366f1); box-shadow: 0 4px 12px rgba(59,130,246,0.3); }
.icon-purple { background: linear-gradient(135deg, #8b5cf6, #d946ef); box-shadow: 0 4px 12px rgba(139,92,246,0.3); }

.title-text {
  font-size: 15px;
  font-weight: 700;
  color: #1e293b;
  line-height: 1.3;
}
.title-sub {
  font-size: 12px;
  color: #94a3b8;
  margin-top: 2px;
}

/* 输入 / 按钮微调 */
.section-card :deep(.el-input__wrapper) {
  border-radius: 8px;
  box-shadow: 0 0 0 1px #e2e8f0;
  transition: box-shadow 0.2s;
}
.section-card :deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px #cbd5e1;
}
.section-card :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 2px #3b82f6 !important;
}

.section-card :deep(.el-button--primary) {
  border-radius: 8px;
  background: linear-gradient(90deg, #3b82f6, #6366f1);
  border: none;
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
  transition: transform 0.15s, box-shadow 0.15s;
}
.section-card :deep(.el-button--primary:hover) {
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(99, 102, 241, 0.45);
}
.section-card :deep(.el-button) { border-radius: 8px; }
</style>
