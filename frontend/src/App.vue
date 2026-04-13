<template>
  <div class="app-shell">
    <!-- 侧边栏（登录页隐藏） -->
    <aside v-if="!isLoginPage" class="sidebar">
      <div class="sidebar-brand">
        <div class="brand-icon">
          <el-icon :size="20" color="#fff"><DataAnalysis /></el-icon>
        </div>
        <div class="brand-text">
          <div class="brand-title">智能分析平台</div>
          <div class="brand-sub">User Behavior System</div>
        </div>
      </div>

      <div class="sidebar-divider" />

      <nav class="sidebar-nav">
        <router-link
          v-for="item in navItems"
          :key="item.path"
          :to="item.path"
          class="nav-item"
          :class="{ active: route.path === item.path }"
        >
          <el-icon :size="17"><component :is="item.icon" /></el-icon>
          <span class="nav-label">{{ item.label }}</span>
          <span v-if="item.tag" class="nav-tag">{{ item.tag }}</span>
        </router-link>
      </nav>

      <div class="sidebar-footer">
        <div class="status-row">
          <span class="status-dot" />
          <span class="status-text">系统运行正常</span>
        </div>
        <div class="version-text">v1.0.0</div>
      </div>
    </aside>

    <!-- 主内容区 -->
    <div class="main-wrapper" :class="{ 'full-width': isLoginPage }">
      <!-- 顶部栏（登录页隐藏） -->
      <header v-if="!isLoginPage" class="topbar">
        <div class="page-title">{{ currentPageTitle }}</div>
        <div class="topbar-time">{{ currentTime }}</div>
      </header>

      <main class="content">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { DataAnalysis, Odometer, Share, UserFilled, MagicStick, DataLine } from '@element-plus/icons-vue'

const route = useRoute()
const isLoginPage = computed(() => route.path === '/login')

const navItems = [
  { path: '/dashboard',     label: 'Dashboard',     icon: Odometer,   tag: null },
  { path: '/behavior-flow', label: 'Behavior Flow', icon: Share,      tag: null },
  { path: '/user-analysis', label: 'User Analysis', icon: UserFilled, tag: null },
  { path: '/prediction',    label: 'Prediction',    icon: MagicStick, tag: 'AI' },
  { path: '/comparison',    label: 'Comparison',    icon: DataLine,   tag: null },
]

const pageTitleMap = {
  '/dashboard':     'Dashboard · 数据总览',
  '/behavior-flow': 'Behavior Flow · 行为流转',
  '/user-analysis': 'User Analysis · 用户分析',
  '/prediction':    'Prediction · 智能预测',
  '/comparison':    'Comparison · 对比分析',
}
const currentPageTitle = computed(() => pageTitleMap[route.path] || '电商用户行为分析系统')

const currentTime = ref('')
let timer = null
const updateTime = () => {
  currentTime.value = new Date().toLocaleString('zh-CN', {
    year: 'numeric', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit', second: '2-digit'
  })
}
onMounted(() => { updateTime(); timer = setInterval(updateTime, 1000) })
onUnmounted(() => clearInterval(timer))
</script>

<style>
*, *::before, *::after { box-sizing: border-box; }
body {
  margin: 0; padding: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto,
    'PingFang SC', 'Microsoft YaHei', sans-serif;
  -webkit-font-smoothing: antialiased;
  background: #f1f5f9;
}
#app { min-height: 100vh; }

.app-shell { display: flex; min-height: 100vh; }

/* ── Sidebar ── */
.sidebar {
  width: 220px; min-height: 100vh;
  background: #0f172a;
  display: flex; flex-direction: column;
  position: fixed; left: 0; top: 0; bottom: 0;
  z-index: 100;
  border-right: 1px solid rgba(148,163,184,0.08);
}

.sidebar-brand {
  display: flex; align-items: center; gap: 12px;
  padding: 24px 20px 20px;
}
.brand-icon {
  width: 40px; height: 40px; border-radius: 10px;
  background: linear-gradient(135deg, #3b82f6, #06b6d4);
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 4px 12px rgba(59,130,246,0.4);
}
.brand-title { font-size: 14px; font-weight: 700; color: #f1f5f9; letter-spacing: 0.5px; }
.brand-sub { font-size: 10px; color: #475569; margin-top: 2px; }

.sidebar-divider { height: 1px; background: rgba(148,163,184,0.08); margin: 0 16px 8px; }

.sidebar-nav {
  flex: 1; padding: 4px 12px;
  display: flex; flex-direction: column; gap: 2px;
}
.nav-item {
  display: flex; align-items: center; gap: 10px;
  padding: 10px 12px; border-radius: 8px;
  color: #64748b; text-decoration: none;
  font-size: 13.5px; font-weight: 500;
  transition: all 0.18s ease;
  border-left: 2px solid transparent;
}
.nav-item:hover { background: rgba(59,130,246,0.08); color: #93c5fd; }
.nav-item.active {
  background: rgba(59,130,246,0.15);
  color: #60a5fa;
  border-left-color: #3b82f6;
}
.nav-item.active .el-icon { filter: drop-shadow(0 0 5px rgba(96,165,250,0.6)); }
.nav-label { flex: 1; }
.nav-tag {
  font-size: 10px; font-weight: 700;
  padding: 1px 6px; border-radius: 4px;
  background: linear-gradient(135deg, #3b82f6, #06b6d4);
  color: #fff;
}

.sidebar-footer {
  padding: 16px 20px;
  border-top: 1px solid rgba(148,163,184,0.08);
}
.status-row { display: flex; align-items: center; gap: 8px; margin-bottom: 4px; }
.status-dot {
  width: 7px; height: 7px; border-radius: 50%;
  background: #22c55e;
  box-shadow: 0 0 6px rgba(34,197,94,0.7);
  animation: pulse-dot 2s ease-in-out infinite;
}
@keyframes pulse-dot {
  0%,100% { opacity:1; transform:scale(1); }
  50%     { opacity:0.6; transform:scale(1.3); }
}
.status-text { font-size: 12px; color: #475569; }
.version-text { font-size: 11px; color: #334155; }

/* ── Main ── */
.main-wrapper {
  margin-left: 220px; flex: 1;
  display: flex; flex-direction: column;
  min-height: 100vh;
}
.main-wrapper.full-width { margin-left: 0; }

.topbar {
  height: 54px;
  background: rgba(255,255,255,0.92);
  backdrop-filter: blur(8px);
  border-bottom: 1px solid rgba(226,232,240,0.9);
  padding: 0 24px;
  display: flex; align-items: center; justify-content: space-between;
  position: sticky; top: 0; z-index: 50;
}
.page-title { font-size: 14px; font-weight: 600; color: #1e293b; letter-spacing: 0.3px; }
.topbar-time { font-size: 12px; color: #94a3b8; font-variant-numeric: tabular-nums; }

.content { flex: 1; background: #f1f5f9; }
</style>
