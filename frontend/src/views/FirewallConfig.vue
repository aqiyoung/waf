<template>
  <div class="firewall-config">
    <h2>防火墙配置</h2>
    
    <!-- 配置加载状态 -->
    <div v-if="loading" class="loading">
      <p>加载配置中...</p>
    </div>
    
    <!-- 配置内容 -->
    <div v-else class="config-content">
      <!-- 速率限制配置 -->
      <section class="config-section">
        <h3>速率限制配置</h3>
        <div class="config-form">
          <div class="form-group">
            <label for="rate-limit-window">时间窗口 (秒):</label>
            <input 
              type="number" 
              id="rate-limit-window" 
              v-model.number="rateLimitConfig.window"
              min="1"
            >
          </div>
          <div class="form-group">
            <label for="rate-limit-max">最大请求数:</label>
            <input 
              type="number" 
              id="rate-limit-max" 
              v-model.number="rateLimitConfig.max_requests"
              min="1"
            >
          </div>
          <button @click="updateRateLimit" class="btn btn-primary">更新速率限制</button>
        </div>
      </section>
      
      <!-- IP 黑名单管理 -->
      <section class="config-section">
        <h3>IP 黑名单管理</h3>
        <div class="blacklist-section">
          <div class="form-group">
            <label for="ip-input">添加 IP 到黑名单:</label>
            <div class="input-group">
              <input 
                type="text" 
                id="ip-input" 
                v-model="newIp"
                placeholder="输入 IP 地址"
              >
              <button @click="addIpToBlacklist" class="btn btn-primary">添加</button>
            </div>
          </div>
          
          <div class="blacklist-list">
            <h4>当前黑名单:</h4>
            <ul v-if="blacklist.length > 0">
              <li v-for="ip in blacklist" :key="ip">
                {{ ip }}
                <button @click="removeIpFromBlacklist(ip)" class="btn btn-danger btn-sm">移除</button>
              </li>
            </ul>
            <p v-else class="empty-list">黑名单为空</p>
          </div>
          
          <button @click="clearBlacklist" class="btn btn-warning" v-if="blacklist.length > 0">
            清空黑名单
          </button>
        </div>
      </section>
      
      <!-- 防火墙规则管理 -->
      <section class="config-section">
        <h3>防火墙规则管理</h3>
        <div class="rules-section">
          <p class="note">
            注意: 编辑规则需要谨慎，不当的规则可能会导致误报或漏报。
          </p>
          
          <div v-for="(rules, ruleType) in wafRules" :key="ruleType" class="rule-type">
            <h4>{{ ruleType }}</h4>
            <div class="rule-list">
              <div v-for="(rule, index) in rules" :key="index" class="rule-item">
                <input 
                  type="text" 
                  v-model="rules[index]"
                  class="rule-input"
                >
                <button @click="removeRule(ruleType, index)" class="btn btn-danger btn-sm">移除</button>
              </div>
              <div class="add-rule">
                <input 
                  type="text" 
                  v-model="newRules[ruleType]"
                  placeholder="添加新规则"
                  class="rule-input"
                >
                <button @click="addRule(ruleType)" class="btn btn-primary btn-sm">添加</button>
              </div>
            </div>
          </div>
          
          <button @click="updateFirewallRules" class="btn btn-primary">更新防火墙规则</button>
        </div>
      </section>
    </div>
    
    <!-- 操作结果提示 -->
    <div v-if="message" class="message" :class="messageType">
      {{ message }}
    </div>
  </div>
</template>

<script>
export default {
  name: 'FirewallConfig',
  data() {
    return {
      loading: true,
      config: {},
      wafRules: {},
      rateLimitConfig: {
        window: 60,
        max_requests: 100
      },
      blacklist: [],
      newIp: '',
      newRules: {},
      message: '',
      messageType: ''
    }
  },
  mounted() {
    this.loadConfig()
  },
  methods: {
    // 加载配置
    async loadConfig() {
      this.loading = true
      try {
        const response = await fetch('/api/firewall/config')
        if (response.ok) {
          this.config = await response.json()
          this.wafRules = this.config.waf_rules
          this.rateLimitConfig = this.config.rate_limit
          this.blacklist = this.config.blacklist
          
          // 初始化新规则对象
          Object.keys(this.wafRules).forEach(ruleType => {
            this.newRules[ruleType] = ''
          })
        } else {
          this.showMessage('加载配置失败', 'error')
        }
      } catch (error) {
        console.error('Error loading config:', error)
        this.showMessage('加载配置失败', 'error')
      } finally {
        this.loading = false
      }
    },
    
    // 更新速率限制
    async updateRateLimit() {
      try {
        const response = await fetch('/api/firewall/rate-limit', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': localStorage.getItem('token_type') + ' ' + localStorage.getItem('token')
          },
          body: JSON.stringify(this.rateLimitConfig)
        })
        if (response.ok) {
          const result = await response.json()
          this.showMessage(result.message, 'success')
        } else {
          this.showMessage('更新速率限制失败', 'error')
        }
      } catch (error) {
        console.error('Error updating rate limit:', error)
        this.showMessage('更新速率限制失败', 'error')
      }
    },
    
    // 添加 IP 到黑名单
    async addIpToBlacklist() {
      if (!this.newIp) {
        this.showMessage('请输入 IP 地址', 'error')
        return
      }
      
      try {
        const response = await fetch('/api/firewall/blacklist/add', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': localStorage.getItem('token_type') + ' ' + localStorage.getItem('token')
          },
          body: JSON.stringify(this.newIp)
        })
        if (response.ok) {
          const result = await response.json()
          this.blacklist = result.blacklist
          this.newIp = ''
          this.showMessage(result.message, 'success')
        } else {
          this.showMessage('添加 IP 失败', 'error')
        }
      } catch (error) {
        console.error('Error adding IP to blacklist:', error)
        this.showMessage('添加 IP 失败', 'error')
      }
    },
    
    // 从黑名单移除 IP
    async removeIpFromBlacklist(ip) {
      try {
        const response = await fetch('/api/firewall/blacklist/remove', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': localStorage.getItem('token_type') + ' ' + localStorage.getItem('token')
          },
          body: JSON.stringify(ip)
        })
        if (response.ok) {
          const result = await response.json()
          this.blacklist = result.blacklist
          this.showMessage(result.message, 'success')
        } else {
          this.showMessage('移除 IP 失败', 'error')
        }
      } catch (error) {
        console.error('Error removing IP from blacklist:', error)
        this.showMessage('移除 IP 失败', 'error')
      }
    },
    
    // 清空黑名单
    async clearBlacklist() {
      if (confirm('确定要清空黑名单吗？')) {
        try {
          const response = await fetch('/api/firewall/blacklist/clear', {
            method: 'POST',
            headers: {
              'Authorization': localStorage.getItem('token_type') + ' ' + localStorage.getItem('token')
            }
          })
          if (response.ok) {
            const result = await response.json()
            this.blacklist = result.blacklist
            this.showMessage(result.message, 'success')
          } else {
            this.showMessage('清空黑名单失败', 'error')
          }
        } catch (error) {
          console.error('Error clearing blacklist:', error)
          this.showMessage('清空黑名单失败', 'error')
        }
      }
    },
    
    // 添加规则
    addRule(ruleType) {
      if (!this.newRules[ruleType]) {
        this.showMessage('请输入规则内容', 'error')
        return
      }
      
      if (!this.wafRules[ruleType]) {
        this.wafRules[ruleType] = []
      }
      
      this.wafRules[ruleType].push(this.newRules[ruleType])
      this.newRules[ruleType] = ''
    },
    
    // 移除规则
    removeRule(ruleType, index) {
      if (this.wafRules[ruleType] && this.wafRules[ruleType].length > 0) {
        this.wafRules[ruleType].splice(index, 1)
      }
    },
    
    // 更新防火墙规则
    async updateFirewallRules() {
      try {
        const response = await fetch('/api/firewall/rules', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': localStorage.getItem('token_type') + ' ' + localStorage.getItem('token')
          },
          body: JSON.stringify(this.wafRules)
        })
        if (response.ok) {
          const result = await response.json()
          this.showMessage(result.message, 'success')
        } else {
          this.showMessage('更新防火墙规则失败', 'error')
        }
      } catch (error) {
        console.error('Error updating firewall rules:', error)
        this.showMessage('更新防火墙规则失败', 'error')
      }
    },
    
    // 显示消息
    showMessage(message, type) {
      this.message = message
      this.messageType = type
      setTimeout(() => {
        this.message = ''
        this.messageType = ''
      }, 3000)
    }
  }
}
</script>

<style scoped>
.firewall-config {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

h2 {
  margin-bottom: 30px;
  color: #1890ff;
}

h3 {
  margin: 20px 0 15px 0;
  color: #333;
}

h4 {
  margin: 15px 0 10px 0;
  color: #666;
  font-size: 16px;
}

.loading {
  text-align: center;
  padding: 40px;
  font-size: 18px;
  color: #666;
}

.config-section {
  background-color: white;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.config-form {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  align-items: flex-end;
}

.form-group {
  flex: 1;
  min-width: 200px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: 500;
  color: #333;
}

.form-group input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  font-size: 14px;
}

.input-group {
  display: flex;
  gap: 10px;
  align-items: flex-end;
}

.input-group input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  font-size: 14px;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-primary {
  background-color: #1890ff;
  color: white;
}

.btn-primary:hover {
  background-color: #40a9ff;
}

.btn-danger {
  background-color: #ff4d4f;
  color: white;
}

.btn-danger:hover {
  background-color: #ff7875;
}

.btn-warning {
  background-color: #faad14;
  color: white;
}

.btn-warning:hover {
  background-color: #ffc53d;
}

.btn-sm {
  padding: 4px 8px;
  font-size: 12px;
}

.blacklist-section {
  margin-top: 20px;
}

.blacklist-list {
  margin: 15px 0;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  padding: 10px;
  max-height: 300px;
  overflow-y: auto;
}

.blacklist-list ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.blacklist-list li {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.blacklist-list li:last-child {
  border-bottom: none;
}

.empty-list {
  text-align: center;
  padding: 20px;
  color: #999;
  font-style: italic;
}

.rules-section {
  margin-top: 20px;
}

.note {
  background-color: #fff7e6;
  border-left: 4px solid #faad14;
  padding: 10px;
  margin-bottom: 20px;
  color: #d48806;
}

.rule-type {
  margin-bottom: 20px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  padding: 15px;
}

.rule-list {
  margin-top: 10px;
}

.rule-item {
  display: flex;
  gap: 10px;
  margin-bottom: 10px;
  align-items: center;
}

.rule-input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  font-size: 14px;
  font-family: monospace;
}

.add-rule {
  display: flex;
  gap: 10px;
  margin-top: 10px;
  align-items: center;
}

.message {
  position: fixed;
  top: 20px;
  right: 20px;
  padding: 12px 20px;
  border-radius: 4px;
  color: white;
  font-size: 14px;
  z-index: 1000;
  transition: all 0.3s;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.message.success {
  background-color: #52c41a;
}

.message.error {
  background-color: #ff4d4f;
}

@media (max-width: 768px) {
  .firewall-config {
    padding: 10px;
  }
  
  .config-form {
    flex-direction: column;
    align-items: stretch;
  }
  
  .form-group {
    min-width: 100%;
  }
  
  .input-group {
    flex-direction: column;
    align-items: stretch;
  }
  
  .rule-item {
    flex-direction: column;
    align-items: stretch;
  }
  
  .rule-item .btn {
    margin-top: 5px;
    align-self: flex-start;
  }
  
  .add-rule {
    flex-direction: column;
    align-items: stretch;
  }
  
  .add-rule .btn {
    margin-top: 5px;
    align-self: flex-start;
  }
}
</style>
