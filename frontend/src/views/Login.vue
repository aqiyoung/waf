<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-header">
        <div class="logo">
          <div class="logo-icon">
            <div class="shield">
              <div class="lightning">⚡</div>
            </div>
          </div>
          <h2>下一代Web应用防火墙</h2>
        </div>
        <p>请输入用户名和密码登录系统</p>
      </div>
      <div class="login-form">
        <div class="form-item">
          <label class="form-label">用户名：</label>
          <div class="form-input-wrapper">
            <input
              v-model="formState.username"
              type="text"
              placeholder="请输入用户名"
              class="form-input"
              size="large"
            />
          </div>
        </div>
        
        <div class="form-item">
          <label class="form-label">密码：</label>
          <div class="form-input-wrapper">
            <input
              v-model="formState.password"
              type="password"
              placeholder="请输入密码"
              class="form-input"
              size="large"
            />
          </div>
        </div>
        
        <div class="form-item">
          <button
            type="button"
            class="login-button"
            :disabled="loading"
            @click="handleLogin"
          >
            {{ loading ? '登录中...' : '登录' }}
          </button>
        </div>
        
        <div v-if="errorMessage" class="error-message">
          <div class="error-alert">
            <span class="error-icon">⚠️</span>
            <span class="error-text">{{ errorMessage }}</span>
          </div>
        </div>
        
        <div class="login-footer">
          <p>默认用户名：admin</p>
          <p>默认密码：admin123</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { UserOutlined, LockOutlined } from '@ant-design/icons-vue'
import axios from 'axios'

export default {
  name: 'Login',
  components: {
    UserOutlined,
    LockOutlined
  },
  setup() {
    const router = useRouter()
    const formRef = ref(null)
    const loading = ref(false)
    const errorMessage = ref('')
    
    const formState = reactive({
      username: '',
      password: ''
    })
    
    const rules = {
      username: [
        {
          required: true,
          message: '请输入用户名',
          trigger: 'blur'
        }
      ],
      password: [
        {
          required: true,
          message: '请输入密码',
          trigger: 'blur'
        }
      ]
    }
    
    const handleLogin = async () => {
      try {
        loading.value = true
        errorMessage.value = ''
        
        // 直接使用 axios 发送登录请求
        const response = await axios.post('http://localhost:8009/api/auth/login', 
          new URLSearchParams({
            username: formState.username,
            password: formState.password
          }), {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
          }
        })
        
        // 存储 token 到 localStorage
        localStorage.setItem('token', response.data.access_token)
        localStorage.setItem('token_type', response.data.token_type)
        
        // 跳转到仪表盘
        router.push('/')
      } catch (error) {
        errorMessage.value = error.response?.data?.detail || '登录失败，请检查用户名和密码'
      } finally {
        loading.value = false
      }
    }
    
    return {
      formRef,
      formState,
      rules,
      loading,
      errorMessage,
      handleLogin
    }
  }
}
</script>

<style>
/* 全局重置样式 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  margin: 0;
  padding: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}
</style>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #f0f2f5 0%, #e6f7ff 100%);
  padding: 20px;
  margin: 0;
  box-sizing: border-box;
  position: relative;
  overflow: hidden;
  width: 100%;
}

.login-card {
  background: white;
  border-radius: 16px;
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.12);
  width: 100%;
  max-width: 420px;
  margin: 0 auto;
  overflow: hidden;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  padding: 40px;
}

.login-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 16px 50px rgba(0, 0, 0, 0.15);
}

.login-header {
  text-align: center;
  margin-bottom: 32px;
}

.logo {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-bottom: 16px;
}

.logo-icon {
  position: relative;
}

.shield {
  position: relative;
  width: 40px;
  height: 36px;
  background: linear-gradient(135deg, #1890ff 0%, #096dd9 100%);
  border-radius: 4px 4px 0 0;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 8px rgba(24, 144, 255, 0.3);
}

.shield::before {
  content: '';
  position: absolute;
  bottom: -10px;
  left: 0;
  width: 0;
  height: 0;
  border-left: 20px solid transparent;
  border-right: 20px solid transparent;
  border-top: 10px solid #096dd9;
}

.lightning {
  font-size: 20px;
  position: relative;
  z-index: 1;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.1);
    opacity: 0.8;
  }
  100% {
    transform: scale(1);
    opacity: 1;
  }
}

.logo h2 {
  margin: 0;
  color: #1f2329;
  font-size: 24px;
  font-weight: 600;
}

.login-header p {
  margin: 0;
  color: #666;
  font-size: 14px;
}

.login-form {
  width: 100%;
}

.form-item {
  margin-bottom: 24px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-label {
  font-size: 14px;
  font-weight: 500;
  color: #333;
  width: 100%;
  text-align: left;
}

.form-input-wrapper {
  width: 100%;
}

.form-input {
  width: 100%;
  height: 48px;
  padding: 0 16px;
  border: 1px solid #d0d7de;
  border-radius: 8px;
  font-size: 14px;
  transition: all 0.3s ease;
  box-sizing: border-box;
}

.form-input:focus {
  outline: none;
  border-color: #1890ff;
  box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.1);
}

.login-button {
  width: 100%;
  height: 48px;
  font-size: 16px;
  font-weight: 500;
  background-color: #1890ff;
  border: 1px solid #1890ff;
  color: white;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-top: 8px;
}

.login-button:hover:not(:disabled) {
  background-color: #40a9ff;
  border-color: #40a9ff;
}

.login-button:disabled {
  background-color: #e6f7ff;
  border-color: #91d5ff;
  color: #69c0ff;
  cursor: not-allowed;
}

.error-message {
  margin: 20px 0;
}

.error-alert {
  background-color: #fff1f0;
  border: 1px solid #ffccc7;
  border-radius: 8px;
  padding: 12px 16px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.error-icon {
  font-size: 16px;
}

.error-text {
  color: #cf1322;
  font-size: 14px;
}

.login-footer {
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px solid #f0f0f0;
  text-align: center;
}

.login-footer p {
  margin: 8px 0;
  color: #888;
  font-size: 13px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .login-card {
    margin: 0 20px;
    padding: 30px;
  }
  
  .logo h2 {
    font-size: 22px;
  }
  
  .form-input {
    height: 44px;
  }
  
  .login-button {
    height: 44px;
    font-size: 15px;
  }
}

@media (max-width: 480px) {
  .login-card {
    padding: 24px;
  }
  
  .logo h2 {
    font-size: 20px;
  }
  
  .form-item {
    margin-bottom: 20px;
  }
  
  .form-input {
    height: 40px;
    font-size: 13px;
  }
  
  .login-button {
    height: 40px;
    font-size: 14px;
  }
  
  .login-footer {
    margin-top: 24px;
    padding-top: 20px;
  }
}
</style>
