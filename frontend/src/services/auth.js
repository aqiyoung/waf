import api from './api'

// 登录
export const login = async (username, password) => {
  console.log('Login request:', { username, password })
  try {
    const response = await api.post('/auth/login', new URLSearchParams({
      username,
      password
    }), {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    })
    console.log('Login response:', response.data)
    return response.data
  } catch (error) {
    console.error('Login error:', error.response || error)
    throw error
  }
}

// 获取当前用户信息
export const getCurrentUser = async () => {
  const response = await api.get('/auth/me')
  return response.data
}

// 登出
export const logout = async () => {
  const response = await api.post('/auth/logout')
  return response.data
}

// 清除本地存储的认证信息
export const clearAuthData = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('token_type')
  localStorage.removeItem('user')
}

// 检查是否已登录
export const isLoggedIn = () => {
  return localStorage.getItem('token') !== null
}

// 获取认证头
export const getAuthHeader = () => {
  const token = localStorage.getItem('token')
  const tokenType = localStorage.getItem('token_type')
  if (token && tokenType) {
    // 将token_type首字母大写，以匹配后端的要求
    const formattedTokenType = tokenType.charAt(0).toUpperCase() + tokenType.slice(1)
    return `${formattedTokenType} ${token}`
  }
  return null
}

// 保存用户信息
export const saveUserInfo = (user) => {
  localStorage.setItem('user', JSON.stringify(user))
}

// 获取保存的用户信息
export const getUserInfo = () => {
  const userStr = localStorage.getItem('user')
  return userStr ? JSON.parse(userStr) : null
}
