<template>
  <div class="protected-apps">
    <!-- 页面标题和操作 -->
    <div class="page-header">
      <h2>防护应用</h2>
      <div class="header-actions">
        <div class="search-box">
          <input 
            type="text" 
            v-model="searchKeyword" 
            placeholder="搜索应用名称或后端服务" 
            class="search-input"
          />
          <button class="btn btn-outline">高级搜索</button>
        </div>
        <button class="btn btn-primary" @click="$router.push('/protected-apps/add')">
          <span class="btn-icon">+</span>
          添加应用
        </button>
      </div>
    </div>
    
    <!-- 错误信息 -->
    <div v-if="error" class="error-message">
      <div class="error-alert">
        <span class="error-icon">⚠️</span>
        <span class="error-text">{{ error }}</span>
        <button class="btn btn-sm btn-outline" @click="fetchApps">重试</button>
      </div>
    </div>
    
    <!-- 加载状态 -->
    <div v-if="loading" class="loading-state">
      <div class="loading-spinner"></div>
      <div class="loading-text">加载应用列表中...</div>
    </div>
    
    <!-- 应用列表 -->
    <div v-else class="apps-grid">
      <div 
        v-for="app in filteredApps" 
        :key="app.id" 
        class="app-card"
      >
        <div class="app-card-header">
          <div class="app-status" :class="app.status">
            {{ app.statusText }}
          </div>
          <div class="app-name">{{ app.name }}</div>
          <div class="app-actions">
            <button class="btn btn-sm btn-outline" @click="$router.push(`/protected-apps/${app.id}`)">
              详情
            </button>
            <button 
              class="btn btn-sm" 
              :class="app.isProtected ? 'btn-outline' : 'btn-primary'"
              @click="toggleProtection(app.id)"
            >
              {{ app.isProtected ? '取消防护' : '开始防护' }}
            </button>
            <button 
              class="btn btn-sm btn-outline" 
              @click="toggleStatus(app.id)"
            >
              {{ app.status === 'running' ? '停止' : '启动' }}
            </button>
          </div>
        </div>
        <div class="app-card-body">
          <div class="app-info">
            <div class="info-item">
              <span class="info-label">后端服务:</span>
              <span class="info-value">{{ app.backend }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">协议:</span>
              <span class="info-value">{{ app.protocol.toUpperCase() }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">端口:</span>
              <span class="info-value">{{ app.port }}</span>
            </div>
            <div class="app-stats">
              <div class="stat-item">
                <span class="stat-value">{{ app.requestsCount }}</span>
                <span class="stat-label">请求数</span>
              </div>
              <div class="stat-item danger">
                <span class="stat-value">{{ app.attacksCount }}</span>
                <span class="stat-label">攻击数</span>
              </div>
              <div class="stat-item">
                <span class="stat-value">{{ app.ccProtection ? '开启' : '关闭' }}</span>
                <span class="stat-label">CC防护</span>
              </div>
              <div class="stat-item">
                <span class="stat-value">{{ app.botProtection ? '开启' : '关闭' }}</span>
                <span class="stat-label">机器人防护</span>
              </div>
              <div class="stat-item">
                <span class="stat-value">{{ app.authProtection ? '开启' : '关闭' }}</span>
                <span class="stat-label">身份认证</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 空状态 -->
    <div v-if="!loading && filteredApps.length === 0" class="empty-state">
      <div class="empty-icon">📱</div>
      <div class="empty-title">暂无防护应用</div>
      <div class="empty-desc">点击"添加应用"按钮开始保护您的网站</div>
      <button class="btn btn-primary" @click="$router.push('/protected-apps/add')">
        添加应用
      </button>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

export default {
  name: 'ProtectedApps',
  setup() {
    const searchKeyword = ref('')
    const apps = ref([])
    const loading = ref(false)
    const error = ref('')
    
    // 过滤应用
    const filteredApps = computed(() => {
      if (!searchKeyword.value) return apps.value
      return apps.value.filter(app => 
        app.name.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
        app.backend.toLowerCase().includes(searchKeyword.value.toLowerCase())
      )
    })
    
    // 从API获取应用列表
    const fetchApps = async () => {
      loading.value = true
      error.value = ''
      try {
        const response = await axios.get('http://localhost:8010/api/protected-apps')
        apps.value = response.data.apps
      } catch (err) {
        error.value = '加载应用列表失败，请重试'
        console.error('Failed to fetch apps:', err)
      } finally {
        loading.value = false
      }
    }
    
    // 切换防护状态
    const toggleProtection = async (appId) => {
      try {
        const response = await axios.post(`http://localhost:8010/api/protected-apps/${appId}`, {
          action: 'toggle-protection'
        })
        const updatedApp = response.data.app
        const index = apps.value.findIndex(a => a.id === appId)
        if (index !== -1) {
          apps.value[index] = updatedApp
        }
      } catch (err) {
        error.value = '切换防护状态失败，请重试'
        console.error('Failed to toggle protection:', err)
      }
    }
    
    // 切换应用状态（运行/停止）
    const toggleStatus = async (appId) => {
      try {
        const response = await axios.post(`http://localhost:8010/api/protected-apps/${appId}`, {
          action: 'toggle-status'
        })
        const updatedApp = response.data.app
        const index = apps.value.findIndex(a => a.id === appId)
        if (index !== -1) {
          apps.value[index] = updatedApp
        }
      } catch (err) {
        error.value = '切换应用状态失败，请重试'
        console.error('Failed to toggle status:', err)
      }
    }
    
    onMounted(() => {
      fetchApps()
    })
    
    return {
      searchKeyword,
      filteredApps,
      loading,
      error,
      toggleProtection,
      toggleStatus,
      fetchApps
    }
  }
}
</script>

<style scoped>
.protected-apps {
  padding: 20px;
  background-color: #f5f5f5;
  min-height: 100vh;
}

/* 页面标题和操作 */
.page-header {
  background: white;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.page-header h2 {
  font-size: 20px;
  font-weight: 600;
  color: #333;
  margin-bottom: 20px;
}

.header-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-box {
  display: flex;
  gap: 8px;
  align-items: center;
}

.search-input {
  padding: 8px 12px;
  border: 1px solid #d0d7de;
  border-radius: 4px;
  font-size: 14px;
  width: 300px;
}

/* 应用列表 */
.apps-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(450px, 1fr));
  gap: 20px;
}

/* 应用卡片 */
.app-card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
  overflow: hidden;
}

.app-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
  transform: translateY(-2px);
}

.app-card-header {
  padding: 16px 20px;
  border-bottom: 1px solid #f0f0f0;
  background-color: #fafafa;
}

.app-status {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 500;
  margin-bottom: 8px;
}

.app-status.running {
  background-color: #f6ffed;
  color: #52c41a;
}

.app-status.stopped {
  background-color: #fff1f0;
  color: #f5222d;
}

.app-name {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin-bottom: 12px;
}

.app-actions {
  display: flex;
  gap: 8px;
}

.app-card-body {
  padding: 20px;
}

.app-info {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.info-item {
  display: flex;
  gap: 8px;
  align-items: center;
}

.info-label {
  font-size: 14px;
  color: #666;
  font-weight: 500;
}

.info-value {
  font-size: 14px;
  color: #333;
  font-family: monospace;
}

/* 应用统计 */
.app-stats {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 80px;
}

.stat-value {
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.stat-item.danger .stat-value {
  color: #f5222d;
}

.stat-label {
  font-size: 12px;
  color: #666;
}

/* 空状态 */
.empty-state {
  background: white;
  border-radius: 8px;
  padding: 60px 20px;
  text-align: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.empty-title {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin-bottom: 8px;
}

.empty-desc {
  font-size: 14px;
  color: #666;
  margin-bottom: 24px;
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

/* 加载状态 */
.loading-state {
  background: white;
  border-radius: 8px;
  padding: 60px 20px;
  text-align: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  margin-bottom: 20px;
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

/* 按钮样式 */
.btn {
  padding: 6px 12px;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  border: none;
}

.btn-sm {
  padding: 4px 8px;
  font-size: 12px;
}

.btn-primary {
  background-color: #1890ff;
  color: white;
}

.btn-primary:hover {
  background-color: #40a9ff;
}

.btn-outline {
  background-color: white;
  border: 1px solid #d0d7de;
  color: #666;
}

.btn-outline:hover {
  background-color: #f6f8fa;
  border-color: #c9d1d9;
  color: #333;
}

.btn-icon {
  margin-right: 4px;
  font-weight: bold;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .protected-apps {
    padding: 10px;
  }
  
  .header-actions {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .search-box {
    width: 100%;
  }
  
  .search-input {
    width: 100%;
  }
  
  .apps-grid {
    grid-template-columns: 1fr;
  }
  
  .app-actions {
    flex-direction: column;
    gap: 4px;
  }
  
  .app-stats {
    flex-wrap: wrap;
    gap: 12px;
  }
  
  .stat-item {
    min-width: 70px;
  }
}
</style>