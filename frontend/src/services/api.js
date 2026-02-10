import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000
})

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
