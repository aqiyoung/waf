import axios from 'axios'
import { getAuthHeader, clearAuthData } from './auth'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000
})

// 请求拦截器：添加认证头
api.interceptors.request.use(
  (config) => {
    const authHeader = getAuthHeader()
    if (authHeader) {
      config.headers.Authorization = authHeader
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器：处理认证错误
api.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    // 处理 401 未授权错误
    if (error.response && error.response.status === 401) {
      // 清除认证数据
      clearAuthData()
      // 跳转到登录页
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// 获取访问日志
export const getAccessLogs = (limit = 100) => {
  return api.get('/access-logs', { params: { limit } })
}

// 获取攻击日志
export const getAttackLogs = (limit = 100) => {
  return api.get('/attack-logs', { params: { limit } })
}

// 获取 IPv6 统计
export const getIPv6Stats = () => {
  return api.get('/ipv6-stats')
}

// 获取实时状态
export const getStatus = () => {
  return api.get('/status')
}

export default api
