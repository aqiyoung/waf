<template>
  <div class="edit-protected-app">
    <!-- 页面标题和面包屑 -->
    <div class="page-header">
      <div class="breadcrumb">
        <span @click="$router.push('/protected-apps')" class="breadcrumb-item">防护应用</span>
        <span class="breadcrumb-separator">/</span>
        <span class="breadcrumb-item active">编辑应用</span>
      </div>
      <h2>编辑防护应用</h2>
    </div>
    
    <!-- 加载状态 -->
    <div v-if="loading" class="loading-state">
      <div class="loading-spinner"></div>
      <div class="loading-text">加载应用信息中...</div>
    </div>
    
    <!-- 错误信息 -->
    <div v-else-if="error" class="error-message">
      <div class="error-alert">
        <span class="error-icon">⚠️</span>
        <span class="error-text">{{ error }}</span>
        <button class="btn btn-sm btn-outline" @click="fetchAppDetails">重试</button>
      </div>
    </div>
    
    <!-- 应用表单 -->
    <div v-else class="app-form-container">
      <form @submit.prevent="submitForm" class="app-form">
        <!-- 基本信息 -->
        <div class="form-section">
          <h3>基本信息</h3>
          <div class="form-fields">
            <div class="form-field">
              <label for="app-name">应用名称</label>
              <input 
                type="text" 
                id="app-name" 
                v-model="form.name" 
                placeholder="请输入应用名称" 
                class="form-input"
                required
              />
              <div v-if="errors.name" class="error-message">{{ errors.name }}</div>
            </div>
            
            <div class="form-field">
              <label for="app-backend">后端服务</label>
              <input 
                type="text" 
                id="app-backend" 
                v-model="form.backend" 
                placeholder="例如: http://localhost:8080" 
                class="form-input"
                required
              />
              <div v-if="errors.backend" class="error-message">{{ errors.backend }}</div>
            </div>
            
            <div class="form-field">
              <label for="app-protocol">协议类型</label>
              <select id="app-protocol" v-model="form.protocol" class="form-select">
                <option value="http">HTTP</option>
                <option value="https">HTTPS</option>
              </select>
            </div>
            
            <div class="form-field">
              <label for="app-port">端口</label>
              <input 
                type="number" 
                id="app-port" 
                v-model="form.port" 
                class="form-input"
                required
              />
              <div v-if="errors.port" class="error-message">{{ errors.port }}</div>
            </div>
          </div>
        </div>
        
        <!-- 防护配置 -->
        <div class="form-section">
          <h3>防护配置</h3>
          <div class="form-fields">
            <div class="form-field checkbox">
              <input 
                type="checkbox" 
                id="enable-cc" 
                v-model="form.ccProtection"
              />
              <label for="enable-cc">启用 CC 防护</label>
            </div>
            
            <div class="form-field checkbox">
              <input 
                type="checkbox" 
                id="enable-bot" 
                v-model="form.botProtection"
              />
              <label for="enable-bot">启用机器人防护</label>
            </div>
            
            <div class="form-field checkbox">
              <input 
                type="checkbox" 
                id="enable-auth" 
                v-model="form.authProtection"
              />
              <label for="enable-auth">启用身份认证</label>
            </div>
            
            <div class="form-field checkbox">
              <input 
                type="checkbox" 
                id="enable-dynamic" 
                v-model="form.dynamicProtection"
              />
              <label for="enable-dynamic">启用动态防护</label>
            </div>
          </div>
        </div>
        
        <!-- CC 防护配置 -->
        <div v-if="form.ccProtection" class="form-section">
          <h3>CC 防护配置</h3>
          <div class="form-fields">
            <div class="form-field">
              <label for="cc-rate-limit">请求频率限制 (次/分钟)</label>
              <input 
                type="number" 
                id="cc-rate-limit" 
                v-model="form.ccRateLimit" 
                class="form-input"
                min="1"
              />
            </div>
            
            <div class="form-field">
              <label for="cc-penalty">惩罚时间 (分钟)</label>
              <input 
                type="number" 
                id="cc-penalty" 
                v-model="form.ccPenaltyTime" 
                class="form-input"
                min="1"
              />
            </div>
          </div>
        </div>
        
        <!-- 提交错误信息 -->
        <div v-if="submitError" class="submit-error">
          <div class="error-alert">
            <span class="error-icon">⚠️</span>
            <span class="error-text">{{ submitError }}</span>
          </div>
        </div>
        
        <!-- 提交按钮 -->
        <div class="form-actions">
          <button type="button" class="btn btn-outline" @click="$router.push('/protected-apps')" :disabled="submitting">
            取消
          </button>
          <button type="submit" class="btn btn-primary" :disabled="submitting">
            {{ submitting ? '保存中...' : '保存修改' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import axios from 'axios'

export default {
  name: 'EditProtectedApp',
  setup() {
    const router = useRouter()
    const route = useRoute()
    const appId = route.params.id
    
    // 表单数据
    const form = reactive({
      name: '',
      backend: '',
      protocol: 'http',
      port: 80,
      ccProtection: true,
      botProtection: true,
      authProtection: false,
      dynamicProtection: false,
      ccRateLimit: 100,
      ccPenaltyTime: 5
    })
    
    // 状态
    const loading = ref(true)
    const submitting = ref(false)
    const error = ref('')
    const submitError = ref('')
    const errors = reactive({})
    
    // 从API获取应用详情
    const fetchAppDetails = async () => {
      loading.value = true
      error.value = ''
      try {
        const response = await axios.get(`http://localhost:8010/api/protected-apps/${appId}`)
        const appData = response.data
        
        // 填充表单数据
        form.name = appData.name
        form.backend = appData.backend
        form.protocol = appData.protocol
        form.port = appData.port
        form.ccProtection = appData.ccProtection
        form.botProtection = appData.botProtection
        form.authProtection = appData.authProtection
        form.dynamicProtection = appData.dynamicProtection
        form.ccRateLimit = appData.ccRateLimit
        form.ccPenaltyTime = appData.ccPenaltyTime
      } catch (err) {
        error.value = '加载应用信息失败，请重试'
        console.error('Failed to fetch app details:', err)
      } finally {
        loading.value = false
      }
    }
    
    // 验证表单
    const validateForm = () => {
      let isValid = true
      
      // 重置错误
      Object.keys(errors).forEach(key => delete errors[key])
      submitError.value = ''
      
      // 验证应用名称
      if (!form.name.trim()) {
        errors.name = '请输入应用名称'
        isValid = false
      }
      
      // 验证后端服务
      if (!form.backend.trim()) {
        errors.backend = '请输入后端服务地址'
        isValid = false
      } else {
        // 验证后端服务地址格式
        const urlRegex = /^(http|https):\/\/[^\s]+$/i
        if (!urlRegex.test(form.backend)) {
          errors.backend = '请输入有效的后端服务地址，例如: http://localhost:8080'
          isValid = false
        }
      }
      
      // 验证端口
      if (!form.port || form.port < 1 || form.port > 65535) {
        errors.port = '请输入有效的端口号 (1-65535)'
        isValid = false
      }
      
      return isValid
    }
    
    // 提交表单
    const submitForm = async () => {
      if (validateForm()) {
        submitting.value = true
        try {
          const response = await axios.post(`http://localhost:8010/api/protected-apps/${appId}`, form)
          console.log('应用更新成功:', response.data)
          alert('应用更新成功！')
          router.push('/protected-apps')
        } catch (error) {
          submitError.value = '应用更新失败，请重试'
          console.error('更新应用失败:', error)
        } finally {
          submitting.value = false
        }
      }
    }
    
    onMounted(() => {
      fetchAppDetails()
    })
    
    return {
      form,
      loading,
      submitting,
      error,
      submitError,
      errors,
      fetchAppDetails,
      submitForm
    }
  }
}
</script>

<style scoped>
.edit-protected-app {
  padding: 20px;
  background-color: #f5f5f5;
  min-height: 100vh;
}

/* 页面标题和面包屑 */
.page-header {
  background: white;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.breadcrumb {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
  font-size: 14px;
}

.breadcrumb-item {
  color: #666;
  cursor: pointer;
  transition: color 0.3s ease;
}

.breadcrumb-item:hover {
  color: #1890ff;
}

.breadcrumb-item.active {
  color: #333;
  font-weight: 500;
  cursor: default;
}

.breadcrumb-separator {
  margin: 0 8px;
  color: #999;
}

.page-header h2 {
  font-size: 20px;
  font-weight: 600;
  color: #333;
  margin: 0;
}

/* 加载状态 */
.loading-state {
  background: white;
  border-radius: 8px;
  padding: 60px 20px;
  text-align: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #1890ff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-text {
  font-size: 14px;
  color: #666;
}

/* 错误信息 */
.error-message {
  margin-bottom: 20px;
}

.error-alert {
  background-color: #fff1f0;
  border: 1px solid #ffccc7;
  border-radius: 8px;
  padding: 12px 16px;
  display: flex;
  align-items: center;
  gap: 8px;
  justify-content: space-between;
}

.error-icon {
  font-size: 16px;
}

.error-text {
  color: #cf1322;
  font-size: 14px;
  flex: 1;
}

/* 表单容器 */
.app-form-container {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  overflow: hidden;
}

/* 表单 */
.app-form {
  padding: 24px;
}

/* 表单章节 */
.form-section {
  margin-bottom: 32px;
}

.form-section h3 {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 1px solid #f0f0f0;
}

/* 表单字段 */
.form-fields {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-field.checkbox {
  flex-direction: row;
  align-items: center;
}

.form-field.checkbox input[type="checkbox"] {
  margin-right: 8px;
}

.form-field label {
  font-size: 14px;
  font-weight: 500;
  color: #333;
}

.form-input {
  padding: 10px 12px;
  border: 1px solid #d0d7de;
  border-radius: 4px;
  font-size: 14px;
  transition: all 0.3s ease;
}

.form-input:focus {
  outline: none;
  border-color: #1890ff;
  box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.2);
}

.form-select {
  padding: 10px 12px;
  border: 1px solid #d0d7de;
  border-radius: 4px;
  font-size: 14px;
  background-color: white;
  cursor: pointer;
  transition: all 0.3s ease;
}

.form-select:focus {
  outline: none;
  border-color: #1890ff;
  box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.2);
}

/* 错误信息 */
.error-message {
  font-size: 12px;
  color: #f5222d;
  margin-top: 4px;
}

/* 提交错误信息 */
.submit-error {
  margin: 20px 0;
}

/* 表单操作 */
.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 40px;
  padding-top: 24px;
  border-top: 1px solid #f0f0f0;
}

/* 按钮样式 */
.btn {
  padding: 10px 20px;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  border: none;
}

.btn-primary {
  background-color: #1890ff;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: #40a9ff;
}

.btn-primary:disabled {
  background-color: #e6f7ff;
  border-color: #91d5ff;
  color: #69c0ff;
  cursor: not-allowed;
}

.btn-outline {
  background-color: white;
  border: 1px solid #d0d7de;
  color: #666;
}

.btn-outline:hover:not(:disabled) {
  background-color: #f6f8fa;
  border-color: #c9d1d9;
  color: #333;
}

.btn-outline:disabled {
  background-color: #f6f8fa;
  border-color: #e1e4e8;
  color: #959da5;
  cursor: not-allowed;
}

.btn-sm {
  padding: 4px 8px;
  font-size: 12px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .edit-protected-app {
    padding: 10px;
  }
  
  .app-form {
    padding: 16px;
  }
  
  .form-fields {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .form-actions {
    flex-direction: column;
    gap: 8px;
  }
  
  .btn {
    width: 100%;
    text-align: center;
  }
}
</style>