<template>
  <div class="attack-logs">
    <h2>攻击日志</h2>
    
    <div class="filter-bar">
      <a-input-search
        v-model:value="searchQuery"
        placeholder="搜索 IP 地址或攻击类型"
        style="width: 300px"
        @search="handleSearch"
      />
      <a-select
        v-model:value="ipVersionFilter"
        style="width: 120px; margin-left: 10px"
        @change="handleFilterChange"
      >
        <a-select-option value="all">全部 IP</a-select-option>
        <a-select-option value="ipv4">仅 IPv4</a-select-option>
        <a-select-option value="ipv6">仅 IPv6</a-select-option>
      </a-select>
      <a-button type="primary" style="margin-left: 10px" @click="refreshLogs">
        刷新
      </a-button>
    </div>
    
    <a-table
      :columns="columns"
      :data-source="filteredLogs"
      :pagination="pagination"
      :loading="loading"
      row-key="index"
    >
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'ip'">
          <span>{{ record.ip }} <span v-if="record.is_ipv6" class="ipv6-badge">IPv6</span></span>
        </template>
        <template v-else-if="column.key === 'path'">
          <span class="path">{{ record.path }}</span>
        </template>
        <template v-else-if="column.key === 'attack_message'">
          <span class="attack-message">{{ record.attack_message }}</span>
        </template>
        <template v-else-if="column.key === 'user_agent'">
          <span class="user-agent">{{ record.user_agent }}</span>
        </template>
      </template>
    </a-table>
    
    <!-- 攻击统计卡片 -->
    <div class="stats-cards">
      <div class="stat-card">
        <div class="stat-card-title">总攻击次数</div>
        <div class="stat-card-value">{{ totalAttacks }}</div>
      </div>
      <div class="stat-card danger">
        <div class="stat-card-title">SQL 注入攻击</div>
        <div class="stat-card-value">{{ sqlInjectionCount }}</div>
      </div>
      <div class="stat-card warning">
        <div class="stat-card-title">XSS 攻击</div>
        <div class="stat-card-value">{{ xssCount }}</div>
      </div>
      <div class="stat-card critical">
        <div class="stat-card-title">命令注入攻击</div>
        <div class="stat-card-value">{{ commandInjectionCount }}</div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { getAttackLogs } from '../services/api'

export default {
  name: 'AttackLogs',
  setup() {
    const logs = ref([])
    const loading = ref(false)
    const searchQuery = ref('')
    const ipVersionFilter = ref('all')
    const pagination = ref({
      current: 1,
      pageSize: 20,
      total: 0,
      showSizeChanger: true,
      pageSizeOptions: ['10', '20', '50', '100'],
      onShowSizeChange: (current, pageSize) => {
        pagination.value.pageSize = pageSize
        pagination.value.current = 1
      },
      onChange: (current) => {
        pagination.value.current = current
      }
    })
    
    const columns = [
      {
        title: '时间',
        dataIndex: 'timestamp',
        key: 'timestamp',
        width: 180,
        render: (timestamp) => {
          const date = new Date(timestamp * 1000)
          return date.toLocaleString('zh-CN')
        }
      },
      {
        title: 'IP 地址',
        dataIndex: 'ip',
        key: 'ip',
        width: 180
      },
      {
        title: '方法',
        dataIndex: 'method',
        key: 'method',
        width: 80
      },
      {
        title: '攻击路径',
        dataIndex: 'path',
        key: 'path',
        ellipsis: true
      },
      {
        title: '攻击类型',
        dataIndex: 'attack_message',
        key: 'attack_message',
        ellipsis: true
      },
      {
        title: '用户代理',
        dataIndex: 'user_agent',
        key: 'user_agent',
        ellipsis: true
      }
    ]
    
    // 过滤日志
    const filteredLogs = computed(() => {
      let result = logs.value
      
      // IP 版本过滤
      if (ipVersionFilter.value === 'ipv4') {
        result = result.filter(log => !log.is_ipv6)
      } else if (ipVersionFilter.value === 'ipv6') {
        result = result.filter(log => log.is_ipv6)
      }
      
      // 搜索过滤
      if (searchQuery.value) {
        const query = searchQuery.value.toLowerCase()
        result = result.filter(log => {
          return (
            log.ip.toLowerCase().includes(query) ||
            log.path.toLowerCase().includes(query) ||
            (log.attack_message && log.attack_message.toLowerCase().includes(query))
          )
        })
      }
      
      // 更新分页总数
      pagination.value.total = result.length
      
      // 分页
      const start = (pagination.value.current - 1) * pagination.value.pageSize
      const end = start + pagination.value.pageSize
      return result.slice(start, end)
    })
    
    // 统计数据
    const totalAttacks = computed(() => {
      return logs.value.length
    })
    
    const sqlInjectionCount = computed(() => {
      return logs.value.filter(log => log.attack_message && log.attack_message.includes('SQL injection')).length
    })
    
    const xssCount = computed(() => {
      return logs.value.filter(log => log.attack_message && log.attack_message.includes('XSS')).length
    })
    
    const commandInjectionCount = computed(() => {
      return logs.value.filter(log => log.attack_message && log.attack_message.includes('Command injection')).length
    })
    
    // 加载日志
    const loadLogs = async () => {
      loading.value = true
      try {
        const response = await getAttackLogs(1000) // 加载更多日志用于过滤
        logs.value = response.data.logs
      } catch (error) {
        console.error('Failed to load attack logs:', error)
      } finally {
        loading.value = false
      }
    }
    
    // 刷新日志
    const refreshLogs = () => {
      loadLogs()
    }
    
    // 处理搜索
    const handleSearch = () => {
      pagination.value.current = 1
    }
    
    // 处理过滤变化
    const handleFilterChange = () => {
      pagination.value.current = 1
    }
    
    onMounted(() => {
      loadLogs()
    })
    
    return {
      logs,
      loading,
      searchQuery,
      ipVersionFilter,
      pagination,
      columns,
      filteredLogs,
      totalAttacks,
      sqlInjectionCount,
      xssCount,
      commandInjectionCount,
      refreshLogs,
      handleSearch,
      handleFilterChange
    }
  }
}
</script>

<style scoped>
.attack-logs {
  max-width: 1200px;
  margin: 0 auto;
}

.attack-logs h2 {
  margin-bottom: 20px;
  color: #333;
}

.filter-bar {
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.ipv6-badge {
  background-color: #1890ff;
  color: white;
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 10px;
  margin-left: 8px;
}

.path {
  word-break: break-all;
}

.attack-message {
  color: #f5222d;
  word-break: break-all;
  font-weight: 500;
}

.user-agent {
  word-break: break-all;
  font-size: 12px;
}

/* 统计卡片 */
.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-top: 30px;
}

.stat-card {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  text-align: center;
  transition: transform 0.3s;
}

.stat-card:hover {
  transform: translateY(-5px);
}

.stat-card.danger {
  border-left: 4px solid #f5222d;
}

.stat-card.warning {
  border-left: 4px solid #faad14;
}

.stat-card.critical {
  border-left: 4px solid #ff4d4f;
}

.stat-card-title {
  font-size: 14px;
  color: #666;
  margin-bottom: 10px;
}

.stat-card-value {
  font-size: 28px;
  font-weight: bold;
  margin-bottom: 5px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .filter-bar {
    flex-direction: column;
    align-items: stretch;
  }
  
  .filter-bar .ant-input-search {
    width: 100%;
  }
  
  .filter-bar .ant-select {
    width: 100%;
    margin-left: 0;
  }
  
  .filter-bar .ant-button {
    width: 100%;
    margin-left: 0;
  }
  
  .stats-cards {
    grid-template-columns: 1fr;
  }
}
</style>
