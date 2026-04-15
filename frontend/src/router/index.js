// frontend/src/router/index.js
// 路由配置 + 登录守卫
import {
    createRouter,
    createWebHistory
}from 'vue-router'

import Login      from '@/views/Login.vue'
import Register   from '@/views/Register.vue'
import Dashboard from '../views/Dashboard.vue'
import BehaviorFlow from '../views/BehaviorFlow.vue'
import UserAnalysis from '../views/UserAnalysis.vue'
import Prediction from '../views/Prediction.vue'
import Comparison from '../views/Comparison.vue'

const routes = [
    {
        path: '/login',
        name: 'Login',
        component: Login,
        meta: { requiresAuth: false, title: '登录' }
    },
    {
        path: '/register',
        name: 'Register',
        component: Register,
        meta: { requiresAuth: false, title: '注册' }
    },
    {
        path: '/',
        redirect: '/dashboard',
    },
    {
        path: '/dashboard',
        name: 'Dashboard',
        component: Dashboard,
        meta: { requiresAuth: true, title: '总览仪表盘' }
    },
    {
        path: '/behavior-flow',
        name: 'BehaviorFlow',
        component: BehaviorFlow,
        meta: { requiresAuth: true, title: '行为流分析' }
    },
    {
        path: '/user-analysis',
        name: 'UserAnalysis',
        component: UserAnalysis,
        meta: { requiresAuth: true, title: '用户分析' }
    },
    {
        path: '/prediction',
        name: 'Prediction',
        component: Prediction,
        meta: { requiresAuth: true, title: '智能预测' }
    },
    {
        path: '/comparison',
        name: 'Comparison',
        component: Comparison,
        meta: { requiresAuth: true, title: '平销期vs促销期' }
    },
     // 兜底重定向
    { path: '/:pathMatch(.*)*', redirect: '/dashboard' }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

// ============================================================================
// 全局路由守卫：未登录跳转到 /login
// ============================================================================
router.beforeEach((to, from, next) => {
  // 不需要鉴权的路由直接放行
  if (!to.meta.requiresAuth) {
    return next()
  }

  // 从 localStorage / sessionStorage 读取 token
  const token = localStorage.getItem('token') || sessionStorage.getItem('token')
  const expire = localStorage.getItem('token_expire') || sessionStorage.getItem('token_expire')

  // 检查 token 是否存在且未过期
  if (token && expire && Date.now() < parseInt(expire)) {
    // // 恢复 axios 默认请求头
    // import('axios').then(({ default: axios }) => {
    //   axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
    // })
    // 直接 next()（拦截器会处理）
    return next()
  }

  // Token 不存在或已过期，清除并跳转登录
  localStorage.removeItem('token')
  localStorage.removeItem('token_expire')
  sessionStorage.removeItem('token')
  sessionStorage.removeItem('token_expire')

  next({ path: '/login', query: { redirect: to.fullPath } })
})

// 设置页面标题
router.afterEach((to) => {
  document.title = to.meta.title
    ? `${to.meta.title} - 电商行为分析系统`
    : '电商用户行为分析系统'
})

export default router