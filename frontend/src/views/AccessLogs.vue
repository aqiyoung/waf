<template>
  <div class="access-logs">
    <h2>访问日志</h2>
    
    <div class="filter-bar">
      <a-input-search
        v-model:value="searchQuery"
        placeholder="搜索 IP 地址或路径"
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
        <template v-else-if="column.key === 'query'">
          <span class="query">{{ formatQuery(record.query) }}</span>
        </template>
        <template v-else-if="column.key === 'user_agent'">
          <span class="user-agent">{{ record.user_agent }}</span>
        </template>
        <template v-else-if="column.key === 'is_attack'">
          <a-tag :color="record.is_attack ? 'red' : 'green'">
            {{ record.is_attack ? '攻击' : '正常' }}
          </a-tag>
        </template>
        <template v-else-if="column.key === 'attack_message'">
          <span v-if="record.attack_message" class="attack-message">{{ record.attack_message }}</span>
          <span v-else class="empty">-</span>
        </template>
      </template>
    </a-table>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { getAccessLogs } from '../services/api'

export default {
  name: 'AccessLogs',
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
        title: '路径',
        dataIndex: 'path',
        key: 'path',
        ellipsis: true
      },
      {
        title: '查询参数',
        dataIndex: 'query',
        key: 'query',
        width: 200,
        ellipsis: true
      },
      {
        title: '状态',
        dataIndex: 'is_attack',
        key: 'is_attack',
        width: 80
      },
      {
        title: '攻击信息',
        dataIndex: 'attack_message',
        key: 'attack_message',
        ellipsis: true
      }
    ]
    
    // 格式化查询参数
    const formatQuery = (query) => {
      if (!query || Object.keys(query).length === 0) {
        return '-'
      }
      return JSON.stringify(query)
    }
    
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
    
    // 加载日志
    const loadLogs = async () => {
      loading.value = true
      try {
        const response = await getAccessLogs(1000) // 加载更多日志用于过滤
        logs.value = response.data.logs
      } catch (error) {
        console.error('Failed to load access logs:', error)
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
      formatQuery,
      refreshLogs,
      handleSearch,
      handleFilterChange
    }
  }
}
</script>

<style scoped>
.access-logs {
  max-width: 1200px;
  margin: 0 auto;
}

.access-logs h2 {
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

.query {
  word-break: break-all;
  font-family: monospace;
  font-size: 12px;
}

.user-agent {
  word-break: break-all;
  font-size: 12px;
}

.attack-message {
  color: #f5222d;
  word-break: break-all;
}

.empty {
  color: #999;
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
}
</style>
