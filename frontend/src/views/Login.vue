<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-header">
        <h2>WAF 登录</h2>
        <p>请输入用户名和密码登录系统</p>
      </div>
      <div class="login-form">
        <a-form
          :model="formState"
          :rules="rules"
          ref="formRef"
          @finish="handleLogin"
        >
          <a-form-item field="username" label="用户名">
            <a-input
              v-model:value="formState.username"
              placeholder="请输入用户名"
              size="large"
            >
              <template #prefix>
                <user-outlined />
              </template>
            </a-input>
          </a-form-item>
          
          <a-form-item field="password" label="密码">
            <a-input-password
              v-model:value="formState.password"
              placeholder="请输入密码"
              size="large"
              :visibilityToggle="true"
            >
              <template #prefix>
                <lock-outlined />
              </template>
            </a-input-password>
          </a-form-item>
          
          <a-form-item>
            <a-button
              type="primary"
              html-type="submit"
              class="login-button"
              :loading="loading"
              size="large"
            >
              登录
            </a-button>
          </a-form-item>
          
          <a-form-item v-if="errorMessage" class="error-message">
            <a-alert
              :message="errorMessage"
              type="error"
              show-icon
              banner
            />
          </a-form-item>
          
          <div class="login-footer">
            <p>默认用户名：admin</p>
            <p>默认密码：admin123</p>
          </div>
        </a-form>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { UserOutlined, LockOutlined } from '@ant-design/icons-vue'
import { login } from '../services/auth'

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
        
        const response = await login(formState.username, formState.password)
        
        // 存储 token 到 localStorage
        localStorage.setItem('token', response.access_token)
        localStorage.setItem('token_type', response.token_type)
        
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

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  padding: 20px;
}

.login-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 400px;
  overflow: hidden;
}

.login-header {
  text-align: center;
  padding: 30px 30px 0;
}

.login-header h2 {
  margin: 0 0 10px;
  color: #333;
  font-size: 24px;
  font-weight: 600;
}

.login-header p {
  margin: 0;
  color: #666;
  font-size: 14px;
}

.login-form {
  padding: 30px;
}

.login-button {
  width: 100%;
  height: 48px;
  font-size: 16px;
  font-weight: 500;
}

.error-message {
  margin-bottom: 16px;
}

.login-footer {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #f0f0f0;
  text-align: center;
}

.login-footer p {
  margin: 5px 0;
  color: #999;
  font-size: 12px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .login-card {
    margin: 0 20px;
  }
  
  .login-header,
  .login-form {
    padding: 20px;
  }
}
</style>
