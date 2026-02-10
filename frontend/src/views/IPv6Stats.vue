<template>
  <div class="ipv6-stats">
    <h2>IPv6 访问统计</h2>
    
    <!-- 统计卡片 -->
    <div class="stats-cards">
      <div class="stat-card">
        <div class="stat-card-title">IPv6 访问次数</div>
        <div class="stat-card-value">{{ ipv6Stats.ipv6_count }}</div>
        <div class="stat-card-desc">来自 IPv6 地址的请求</div>
      </div>
      <div class="stat-card">
        <div class="stat-card-title">总访问次数</div>
        <div class="stat-card-value">{{ ipv6Stats.total_count }}</div>
        <div class="stat-card-desc">所有 IP 版本的请求</div>
      </div>
      <div class="stat-card primary">
        <div class="stat-card-title">IPv6 占比</div>
        <div class="stat-card-value">{{ ipv6Stats.ipv6_percentage }}%</div>
        <div class="stat-card-desc">IPv6 访问占总访问的比例</div>
      </div>
    </div>
    
    <!-- 图表区域 -->
    <div class="charts">
      <!-- IP 版本分布 -->
      <div class="chart-container">
        <h3>IP 版本分布</h3>
        <div ref="ipVersionChartRef" class="chart"></div>
      </div>
      
      <!-- IPv6 趋势 -->
      <div class="chart-container">
        <h3>IPv6 访问趋势</h3>
        <div ref="ipv6TrendChartRef" class="chart"></div>
      </div>
    </div>
    
    <!-- IPv6 访问列表 -->
    <div class="ipv6-list">
      <h3>最近 IPv6 访问记录</h3>
      <a-table
        :columns="columns"
        :data-source="ipv6Logs"
        :pagination="pagination"
        :loading="loading"
        row-key="index"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'timestamp'">
            <span>{{ formatTime(record.timestamp) }}</span>
          </template>
          <template v-else-if="column.key === 'ip'">
            <span class="ipv6-address">{{ record.ip }}</span>
          </template>
          <template v-else-if="column.key === 'path'">
            <span class="path">{{ record.path }}</span>
          </template>
          <template v-else-if="column.key === 'is_attack'">
            <a-tag :color="record.is_attack ? 'red' : 'green'">
              {{ record.is_attack ? '攻击' : '正常' }}
            </a-tag>
          </template>
        </template>
      </a-table>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue'
import { getIPv6Stats, getAccessLogs } from '../services/api'
import * as echarts from 'echarts'

export default {
  name: 'IPv6Stats',
  setup() {
    const ipv6Stats = ref({
      ipv6_count: 0,
      total_count: 0,
      ipv6_percentage: 0
    })
    const ipv6Logs = ref([])
    const loading = ref(false)
    const ipVersionChartRef = ref(null)
    const ipv6TrendChartRef = ref(null)
    let ipVersionChart = null
    let ipv6TrendChart = null
    let updateInterval = null
    
    const pagination = ref({
      current: 1,
      pageSize: 10,
      total: 0
    })
    
    const columns = [
      {
        title: '时间',
        dataIndex: 'timestamp',
        key: 'timestamp',
        width: 180
      },
      {
        title: 'IPv6 地址',
        dataIndex: 'ip',
        key: 'ip',
        width: 300
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
        title: '状态',
        dataIndex: 'is_attack',
        key: 'is_attack',
        width: 80
      }
    ]
    
    // 格式化时间
    const formatTime = (timestamp) => {
      const date = new Date(timestamp * 1000)
      return date.toLocaleString('zh-CN')
    }
    
    // 加载 IPv6 统计数据
    const loadIPv6Stats = async () => {
      loading.value = true
      try {
        const response = await getIPv6Stats()
        ipv6Stats.value = response.data
        updateCharts()
      } catch (error) {
        console.error('Failed to load IPv6 stats:', error)
      } finally {
        loading.value = false
      }
    }
    
    // 加载 IPv6 访问日志
    const loadIPv6Logs = async () => {
      try {
        const response = await getAccessLogs(1000)
        ipv6Logs.value = response.data.logs.filter(log => log.is_ipv6)
        pagination.value.total = ipv6Logs.value.length
      } catch (error) {
        console.error('Failed to load IPv6 logs:', error)
      }
    }
    
    // 更新图表
    const updateCharts = () => {
      // IP 版本分布图表
      if (ipVersionChart) {
        ipVersionChart.setOption({
          tooltip: {
            trigger: 'item',
            formatter: '{a} <br/>{b}: {c} ({d}%)'
          },
          legend: {
            orient: 'vertical',
            left: 10,
            data: ['IPv6 访问', 'IPv4 访问']
          },
          series: [
            {
              name: 'IP 版本',
              type: 'pie',
              radius: ['50%', '70%'],
              avoidLabelOverlap: false,
              itemStyle: {
                borderRadius: 10,
                borderColor: '#fff',
                borderWidth: 2
              },
              label: {
                show: false,
                position: 'center'
              },
              emphasis: {
                label: {
                  show: true,
                  fontSize: '20',
                  fontWeight: 'bold'
                }
              },
              labelLine: {
                show: false
              },
              data: [
                {
                  value: ipv6Stats.value.ipv6_count,
                  name: 'IPv6 访问',
                  itemStyle: {
                    color: '#1890ff'
                  }
                },
                {
                  value: ipv6Stats.value.total_count - ipv6Stats.value.ipv6_count,
                  name: 'IPv4 访问',
                  itemStyle: {
                    color: '#52c41a'
                  }
                }
              ]
            }
          ]
        })
      }
      
      // IPv6 趋势图表（模拟数据）
      if (ipv6TrendChart) {
        // 生成模拟的最近 24 小时数据
        const hours = []
        const ipv6Data = []
        const totalData = []
        
        for (let i = 23; i >= 0; i--) {
          const hour = new Date()
          hour.setHours(hour.getHours() - i)
          hours.push(hour.getHours() + ':00')
          
          // 模拟数据
          const total = Math.floor(Math.random() * 100) + 50
          const ipv6 = Math.floor(total * (ipv6Stats.value.ipv6_percentage / 100) * (0.8 + Math.random() * 0.4))
          
          totalData.push(total)
          ipv6Data.push(ipv6)
        }
        
        ipv6TrendChart.setOption({
          tooltip: {
            trigger: 'axis'
          },
          legend: {
            data: ['IPv6 访问', '总访问']
          },
          grid: {
            left: '3%',
            right: '4%',
            bottom: '3%',
            containLabel: true
          },
          xAxis: {
            type: 'category',
            boundaryGap: false,
            data: hours
          },
          yAxis: {
            type: 'value'
          },
          series: [
            {
              name: 'IPv6 访问',
              type: 'line',
              stack: 'Total',
              data: ipv6Data,
              itemStyle: {
                color: '#1890ff'
              },
              areaStyle: {
                color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                  {
                    offset: 0,
                    color: 'rgba(24, 144, 255, 0.5)'
                  },
                  {
                    offset: 1,
                    color: 'rgba(24, 144, 255, 0.1)'
                  }
                ])
              }
            },
            {
              name: '总访问',
              type: 'line',
              stack: 'Total',
              data: totalData,
              itemStyle: {
                color: '#52c41a'
              },
              areaStyle: {
                color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                  {
                    offset: 0,
                    color: 'rgba(82, 196, 26, 0.5)'
                  },
                  {
                    offset: 1,
                    color: 'rgba(82, 196, 26, 0.1)'
                  }
                ])
              }
            }
          ]
        })
      }
    }
    
    // 初始化图表
    const initCharts = () => {
      if (ipVersionChartRef.value) {
        ipVersionChart = echarts.init(ipVersionChartRef.value)
      }
      if (ipv6TrendChartRef.value) {
        ipv6TrendChart = echarts.init(ipv6TrendChartRef.value)
      }
    }
    
    // 响应式调整图表大小
    const handleResize = () => {
      ipVersionChart?.resize()
      ipv6TrendChart?.resize()
    }
    
    onMounted(async () => {
      initCharts()
      await loadIPv6Stats()
      await loadIPv6Logs()
      updateCharts()
      
      // 每 10 秒更新一次数据
      updateInterval = setInterval(async () => {
        await loadIPv6Stats()
        await loadIPv6Logs()
      }, 10000)
      
      // 监听窗口大小变化
      window.addEventListener('resize', handleResize)
    })
    
    onUnmounted(() => {
      if (updateInterval) {
        clearInterval(updateInterval)
      }
      window.removeEventListener('resize', handleResize)
      ipVersionChart?.dispose()
      ipv6TrendChart?.dispose()
    })
    
    return {
      ipv6Stats,
      ipv6Logs,
      loading,
      pagination,
      columns,
      ipVersionChartRef,
      ipv6TrendChartRef,
      formatTime
    }
  }
}
</script>

<style scoped>
.ipv6-stats {
  max-width: 1200px;
  margin: 0 auto;
}

.ipv6-stats h2 {
  margin-bottom: 20px;
  color: #333;
}

/* 统计卡片 */
.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
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

.stat-card.primary {
  border-left: 4px solid #1890ff;
  background-color: #e6f7ff;
}

.stat-card-title {
  font-size: 14px;
  color: #666;
  margin-bottom: 10px;
}

.stat-card-value {
  font-size: 32px;
  font-weight: bold;
  margin-bottom: 5px;
}

.stat-card-desc {
  font-size: 12px;
  color: #999;
}

/* 图表区域 */
.charts {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.chart-container {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.chart-container h3 {
  margin-bottom: 15px;
  color: #333;
  font-size: 16px;
}

.chart {
  height: 300px;
}

/* IPv6 访问列表 */
.ipv6-list {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.ipv6-list h3 {
  margin-bottom: 15px;
  color: #333;
  font-size: 16px;
}

.ipv6-address {
  font-family: monospace;
  word-break: break-all;
}

.path {
  word-break: break-all;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .charts {
    grid-template-columns: 1fr;
  }
  
  .chart-container {
    width: 100%;
  }
  
  .chart {
    height: 250px;
  }
  
  .stats-cards {
    grid-template-columns: 1fr;
  }
}
</style>
