<template>
  <div class="app">
    <header class="header">
      <div class="logo">
        <h1>WAF for Feiniu NAS</h1>
      </div>
      <nav class="nav">
        <router-link to="/" class="nav-item">仪表盘</router-link>
        <router-link to="/access-logs" class="nav-item">访问日志</router-link>
        <router-link to="/attack-logs" class="nav-item">攻击日志</router-link>
        <router-link to="/ipv6-stats" class="nav-item">IPv6 统计</router-link>
      </nav>
    </header>
    <main class="main">
      <router-view />
    </main>
    <footer class="footer">
      <p>&copy; 2026 WAF for Feiniu NAS. All rights reserved.</p>
    </footer>
  </div>
</template>

<script>
export default {
  name: 'App'
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
  background-color: #f5f5f5;
  color: #333;
}

.app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.header {
  background-color: #1890ff;
  color: white;
  padding: 0 20px;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.logo h1 {
  font-size: 20px;
  font-weight: 600;
}

.nav {
  display: flex;
  gap: 20px;
}

.nav-item {
  color: white;
  text-decoration: none;
  padding: 8px 16px;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.nav-item:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.nav-item.router-link-active {
  background-color: rgba(255, 255, 255, 0.2);
  font-weight: 600;
}

.main {
  flex: 1;
  padding: 20px;
}

.footer {
  background-color: #f0f0f0;
  text-align: center;
  padding: 20px;
  margin-top: auto;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .header {
    flex-direction: column;
    height: auto;
    padding: 10px;
  }
  
  .nav {
    margin-top: 10px;
    justify-content: center;
  }
  
  .main {
    padding: 10px;
  }
}
</style>
