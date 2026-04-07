// 1. 导入 axios
// 2. 创建 axios 实例，baseURL 设为 http://localhost:8000/api/v1
// 3. 请求拦截器：
//    - 从 localStorage 或 sessionStorage 读取 token
//    - 将 token 加到请求头的 Authorization 字段（格式：Bearer <token>）
// 4. 响应拦截器：
//    - 如果状态码是 401（未授权），就清除本地存储的 token、username、nickname、role、token_expire
//    - 跳转到 /login 页面
//    - 其他错误显示错误信息
// 5. 导出：
//    - 导出 axios 实例
//    - 导出一个 clearAuth() 函数（清除认证信息用）
import axios from 'axios'
import router from '../router'

// 创建 axios 实例
const axiosInstance = axios.create({
  baseURL: 'http://localhost:8000/api/v1'
})

// 请求拦截器
axiosInstance.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token') || sessionStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
axiosInstance.interceptors.response.use(
  response => {
    return response
  },
  error => {
    if (error.response && error.response.status === 401) {
      clearAuth()
      router.push('/login')
    } else {
      console.error(error.response ? error.response.data : error.message)
    }
    return Promise.reject(error)
  }
)

// 清除认证信息
export function clearAuth() {
  localStorage.removeItem('token')
  localStorage.removeItem('username')
  localStorage.removeItem('nickname')
  localStorage.removeItem('role')
  localStorage.removeItem('token_expire')
  sessionStorage.removeItem('token')
  sessionStorage.removeItem('username')
  sessionStorage.removeItem('nickname')
  sessionStorage.removeItem('role')
  sessionStorage.removeItem('token_expire')
}

// 导出 axios 实例
export default axiosInstance
