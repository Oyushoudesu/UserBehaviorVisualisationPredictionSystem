import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import 'element-plus/theme-chalk/dark/css-vars.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import App from './App.vue'
import router from './router'
import axiosInstance from '@/api/axiosInstance'

const app = createApp(App)

// ============================================================================
// 初始化：启动时恢复登录状态
// ============================================================================
const token = localStorage.getItem('token') || sessionStorage.getItem('token')
const tokenExpire = localStorage.getItem('token_expire') || sessionStorage.getItem('token_expire')

if (token && tokenExpire && Date.now() < parseInt(tokenExpire)) {
  // Token 存在且未过期，设置 axios 默认请求头
  axiosInstance.defaults.headers.common['Authorization'] = `Bearer ${token}`
  console.log('✓ 恢复登录状态')
} else {
  // Token 不存在或已过期，清除存储
  localStorage.removeItem('token')
  localStorage.removeItem('token_expire')
  sessionStorage.removeItem('token')
  sessionStorage.removeItem('token_expire')
}

// 注册 Element Plus 图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
    app.component(key, component)
}

app.use(ElementPlus)
app.use(router)
app.mount('#app')


