<template>
  <div class="app">
    <!-- 登录页面不显示导航栏和页脚 -->
    <template v-if="$route.path !== '/login'">
      <!-- 侧边栏导航 -->
      <aside :class="['sidebar', { collapsed: sidebarCollapsed }]">
        <div class="sidebar-header">
          <div class="logo">
            <div class="logo-icon">
              <div class="shield">
                <div class="lightning">⚡</div>
              </div>
            </div>
            <h1>应用防火墙</h1>
          </div>
        </div>
        <nav class="sidebar-nav">
          <router-link to="/" class="nav-item">
            <span class="nav-icon">📊</span>
            <span class="nav-text">仪表盘</span>
          </router-link>
          <router-link to="/access-logs" class="nav-item">
            <span class="nav-icon">📋</span>
            <span class="nav-text">访问日志</span>
          </router-link>
          <router-link to="/attack-logs" class="nav-item">
            <span class="nav-icon">⚠️</span>
            <span class="nav-text">攻击日志</span>
          </router-link>
          <router-link to="/firewall-config" class="nav-item">
            <span class="nav-icon">⚙️</span>
            <span class="nav-text">防火墙配置</span>
          </router-link>
          <router-link to="/protection-rules" class="nav-item">
            <span class="nav-icon">🛑</span>
            <span class="nav-text">防护规则</span>
          </router-link>
          <router-link to="/rate-limiting" class="nav-item">
            <span class="nav-icon">⏱️</span>
            <span class="nav-text">速率限制</span>
          </router-link>
        </nav>
        <div class="sidebar-footer">
          <div class="version">v1.0.0</div>
        </div>
      </aside>
      <!-- 主内容区域 -->
      <main :class="['main-content', { expanded: sidebarCollapsed }]">
        <!-- 顶部栏 -->
        <header class="top-bar">
          <div class="top-bar-left">
            <button class="menu-toggle" @click="toggleSidebar">
              <span class="menu-icon">☰</span>
            </button>
            <h2 class="page-title">{{ pageTitle }}</h2>
          </div>
          <div class="top-bar-right">
            <div class="user-info">
              <span class="user-role">管理员</span>
              <button class="logout-btn" @click="handleLogout">登出</button>
            </div>
          </div>
        </header>
        <!-- 页面内容 -->
        <div class="page-content">
          <router-view />
        </div>
        <!-- 页脚 -->
        <footer class="app-footer">
          <div class="footer-content">
            <div class="footer-left">
              <div class="footer-logo">
                <span class="footer-icon">🛡️</span>
                <span class="footer-title">应用防火墙</span>
              </div>
              <div class="footer-info">
                <p>保护您的应用免受恶意攻击</p>
              </div>
            </div>
            <div class="footer-right">
              <div class="footer-links">
                <a href="#" class="footer-link">文档</a>
                <a href="#" class="footer-link">帮助</a>
                <a href="#" class="footer-link">关于</a>
              </div>
              <div class="footer-copyright">
                <p>© 2026 应用防火墙. 保留所有权利.</p>
              </div>
            </div>
          </div>
        </footer>
      </main>
    </template>
    <!-- 登录页面只显示内容 -->
    <template v-else>
      <router-view />
    </template>
  </div>
</template>

<script>
import { ref, computed, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { logout, clearAuthData } from './services/auth'

export default {
  name: 'App',
  setup() {
    const router = useRouter()
    const route = useRoute()
    const sidebarCollapsed = ref(false)
    
    // 页面标题映射
    const pageTitles = {
      '/': '仪表盘',
      '/access-logs': '访问日志',
      '/attack-logs': '攻击日志',
      '/firewall-config': '防火墙配置',
      '/protection-rules': '防护规则',
      '/rate-limiting': '速率限制'
    }
    
    // 计算当前页面标题
    const pageTitle = computed(() => {
      return pageTitles[route.path] || '应用防火墙'
    })
    
    // 切换侧边栏
    const toggleSidebar = () => {
      sidebarCollapsed.value = !sidebarCollapsed.value
    }
    
    // 处理登出
    const handleLogout = async () => {
      try {
        await logout()
        clearAuthData()
        router.push('/login')
      } catch (error) {
        console.error('Logout error:', error)
        clearAuthData()
        router.push('/login')
      }
    }
    
    return {
      sidebarCollapsed,
      pageTitle,
      toggleSidebar,
      handleLogout
    }
  }
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  background-color: #f0f2f5;
  color: #333;
  overflow-x: hidden;
}

.app {
  min-height: 100vh;
  display: flex;
}

/* 侧边栏 */
.sidebar {
  width: 240px;
  background: #1f2329;
  color: white;
  height: 100vh;
  position: fixed;
  left: 0;
  top: 0;
  transition: width 0.3s ease;
  z-index: 1000;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.15);
}

.sidebar.collapsed {
  width: 80px;
}

.sidebar-header {
  padding: 20px;
  border-bottom: 1px solid #30363d;
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-icon {
  position: relative;
}

.shield {
  position: relative;
  width: 32px;
  height: 28px;
  background: linear-gradient(135deg, #1890ff 0%, #096dd9 100%);
  border-radius: 3px 3px 0 0;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 6px rgba(24, 144, 255, 0.3);
}

.shield::before {
  content: '';
  position: absolute;
  bottom: -8px;
  left: 0;
  width: 0;
  height: 0;
  border-left: 16px solid transparent;
  border-right: 16px solid transparent;
  border-top: 8px solid #096dd9;
}

.lightning {
  font-size: 16px;
  position: relative;
  z-index: 1;
  animation: pulse 2s infinite;
  color: white;
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

.logo h1 {
  font-size: 18px;
  font-weight: 600;
}

.sidebar-nav {
  padding: 20px 0;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 20px;
  color: #c9d1d9;
  text-decoration: none;
  transition: all 0.3s ease;
  border-left: 3px solid transparent;
}

.nav-item:hover {
  background-color: rgba(255, 255, 255, 0.1);
  color: white;
}

.nav-item.router-link-active {
  background-color: rgba(30, 111, 239, 0.2);
  border-left-color: #1e6ff3;
  color: white;
  font-weight: 500;
}

.nav-icon {
  font-size: 18px;
  width: 24px;
  text-align: center;
}

.nav-text {
  font-size: 14px;
}

.sidebar-footer {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 16px 20px;
  border-top: 1px solid #30363d;
}

.version {
  font-size: 12px;
  color: #8b949e;
}

/* 主内容区域 */
.main-content {
  flex: 1;
  margin-left: 240px;
  transition: margin-left 0.3s ease;
  min-height: 100vh;
}

.main-content.expanded {
  margin-left: 80px;
}

/* 顶部栏 */
.top-bar {
  background: white;
  padding: 0 24px;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  position: sticky;
  top: 0;
  z-index: 100;
}

.top-bar-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.menu-toggle {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  padding: 4px;
  color: #666;
  transition: color 0.3s ease;
}

.menu-toggle:hover {
  color: #333;
}

.page-title {
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.top-bar-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-role {
  font-size: 14px;
  color: #666;
}

.logout-btn {
  background: none;
  border: 1px solid #d0d7de;
  border-radius: 6px;
  padding: 6px 12px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
  color: #666;
}

.logout-btn:hover {
  background-color: #f6f8fa;
  border-color: #c9d1d9;
}

/* 页面内容 */
.page-content {
  padding: 24px;
  min-height: calc(100vh - 64px - 120px); /* 预留页脚空间 */
}

/* 页脚 */
.app-footer {
  background: #1f2329;
  color: white;
  padding: 24px;
  margin-top: 24px;
}

.footer-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  max-width: 1200px;
  margin: 0 auto;
}

.footer-left {
  flex: 1;
}

.footer-logo {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.footer-icon {
  font-size: 24px;
}

.footer-title {
  font-size: 18px;
  font-weight: 600;
}

.footer-info {
  margin-top: 8px;
}

.footer-info p {
  font-size: 14px;
  color: #c9d1d9;
  margin: 0;
}

.footer-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 16px;
}

.footer-links {
  display: flex;
  gap: 24px;
}

.footer-link {
  color: #c9d1d9;
  text-decoration: none;
  font-size: 14px;
  transition: color 0.3s ease;
}

.footer-link:hover {
  color: white;
}

.footer-copyright {
  font-size: 12px;
  color: #8b949e;
  text-align: right;
}

.footer-copyright p {
  margin: 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .footer-content {
    flex-direction: column;
    gap: 24px;
  }
  
  .footer-right {
    align-items: flex-start;
  }
  
  .footer-links {
    gap: 16px;
  }
  
  .footer-copyright {
    text-align: left;
  }
  
  .page-content {
    min-height: calc(100vh - 64px - 200px); /* 调整移动端页脚空间 */
  }
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .sidebar {
    width: 80px;
  }
  
  .sidebar .nav-text,
  .sidebar .logo h1,
  .sidebar .version {
    display: none;
  }
  
  .sidebar .logo {
    justify-content: center;
  }
  
  .sidebar .nav-item {
    justify-content: center;
    padding: 12px;
  }
  
  .main-content {
    margin-left: 80px;
  }
}

@media (max-width: 768px) {
  .sidebar {
    transform: translateX(-100%);
    transition: transform 0.3s ease;
  }
  
  .sidebar.open {
    transform: translateX(0);
  }
  
  .main-content {
    margin-left: 0;
  }
  
  .page-content {
    padding: 16px;
  }
  
  .top-bar {
    padding: 0 16px;
  }
}
</style>
