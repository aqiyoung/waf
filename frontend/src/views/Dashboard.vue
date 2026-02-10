<template>
  <div class="dashboard">
    <h2>WAF 仪表盘</h2>
    
    <!-- 实时状态卡片 -->
    <div class="status-cards">
      <div class="status-card">
        <div class="status-card-title">总访问量</div>
        <div class="status-card-value">{{ status.total_accesses }}</div>
        <div class="status-card-desc">所有访问请求</div>
      </div>
      <div class="status-card danger">
        <div class="status-card-title">攻击次数</div>
        <div class="status-card-value">{{ status.total_attacks }}</div>
        <div class="status-card-desc">被拦截的攻击</div>
      </div>
      <div class="status-card warning">
        <div class="status-card-title">最近访问</div>
        <div class="status-card-value">{{ status.recent_accesses }}</div>
        <div class="status-card-desc">最近 60 秒</div>
      </div>
      <div class="status-card critical">
        <div class="status-card-title">最近攻击</div>
        <div class="status-card-value">{{ status.recent_attacks }}</div>
        <div class="status-card-desc">最近 60 秒</div>
      </div>
    </div>
    
    <!-- 图表区域 -->
    <div class="charts">
      <!-- IPv6 统计图表 -->
      <div class="chart-container">
        <h3>IPv6 访问统计</h3>
        <div ref="ipv6ChartRef" class="chart"></div>
      </div>
      
      <!-- 攻击类型分布 -->
      <div class="chart-container">
        <h3>攻击类型分布</h3>
        <div ref="attackChartRef" class="chart"></div>
      </div>
    </div>
    
    <!-- 最近攻击日志 -->
    <div class="recent-attacks">
      <h3>最近攻击记录</h3>
      <div class="attack-list">
        <div v-if="attackLogs.length === 0" class="empty-state">
          暂无攻击记录
        </div>
        <div v-else class="attack-item" v-for="(log, index) in attackLogs" :key="index">
          <div class="attack-item-time">{{ formatTime(log.timestamp) }}</div>
          <div class="attack-item-ip">{{ log.ip }} <span v-if="log.is_ipv6" class="ipv6-badge">IPv6</span></div>
          <div class="attack-item-type">{{ log.attack_message }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue'
import { getStatus, getAttackLogs } from '../services/api'
import * as echarts from 'echarts'

export default {
  name: 'Dashboard',
  setup() {
    const status = ref({
      total_accesses: 0,
      total_attacks: 0,
      recent_accesses: 0,
      recent_attacks: 0,
      ipv6_stats: {
        ipv6_count: 0,
        total_count: 0,
        ipv6_percentage: 0
      }
    })
    const attackLogs = ref([])
    const ipv6ChartRef = ref(null)
    const attackChartRef = ref(null)
    let ipv6Chart = null
    let attackChart = null
    let updateInterval = null
    
    // 格式化时间
    const formatTime = (timestamp) => {
      const date = new Date(timestamp * 1000)
      return date.toLocaleString('zh-CN')
    }
    
    // 更新状态数据
    const updateStatus = async () => {
      try {
        const response = await getStatus()
        status.value = response.data
        updateCharts()
      } catch (error) {
        console.error('Failed to update status:', error)
      }
    }
    
    // 更新攻击日志
    const updateAttackLogs = async () => {
      try {
        const response = await getAttackLogs(10)
        attackLogs.value = response.data.logs
      } catch (error) {
        console.error('Failed to update attack logs:', error)
      }
    }
    
    // 更新图表
    const updateCharts = () => {
      // IPv6 统计图表
      if (ipv6Chart) {
        ipv6Chart.setOption({
          tooltip: {
            trigger: 'item'
          },
          legend: {
            top: '5%',
            left: 'center'
          },
          series: [
            {
              name: 'IPv6 统计',
              type: 'pie',
              radius: ['40%', '70%'],
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
                  value: status.value.ipv6_stats.ipv6_count,
                  name: 'IPv6 访问'
                },
                {
                  value: status.value.ipv6_stats.total_count - status.value.ipv6_stats.ipv6_count,
                  name: 'IPv4 访问'
                }
              ]
            }
          ]
        })
      }
      
      // 攻击类型分布图表
      if (attackChart) {
        // 简单的攻击类型统计
        const attackTypes = {
          'SQL 注入': 0,
          'XSS': 0,
          '命令注入': 0,
          '其他攻击': 0
        }
        
        attackLogs.value.forEach(log => {
          if (log.attack_message.includes('SQL injection')) {
            attackTypes['SQL 注入']++
          } else if (log.attack_message.includes('XSS')) {
            attackTypes['XSS']++
          } else if (log.attack_message.includes('Command injection')) {
            attackTypes['命令注入']++
          } else {
            attackTypes['其他攻击']++
          }
        })
        
        attackChart.setOption({
          tooltip: {
            trigger: 'axis',
            axisPointer: {
              type: 'shadow'
            }
          },
          grid: {
            left: '3%',
            right: '4%',
            bottom: '3%',
            containLabel: true
          },
          xAxis: {
            type: 'category',
            data: Object.keys(attackTypes)
          },
          yAxis: {
            type: 'value'
          },
          series: [
            {
              data: Object.values(attackTypes),
              type: 'bar',
              itemStyle: {
                color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                  {
                    offset: 0,
                    color: '#83bff6'
                  },
                  {
                    offset: 0.5,
                    color: '#188df0'
                  },
                  {
                    offset: 1,
                    color: '#188df0'
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
      if (ipv6ChartRef.value) {
        ipv6Chart = echarts.init(ipv6ChartRef.value)
      }
      if (attackChartRef.value) {
        attackChart = echarts.init(attackChartRef.value)
      }
    }
    
    // 响应式调整图表大小
    const handleResize = () => {
      ipv6Chart?.resize()
      attackChart?.resize()
    }
    
    onMounted(async () => {
      initCharts()
      await updateStatus()
      await updateAttackLogs()
      updateCharts()
      
      // 每 5 秒更新一次数据
      updateInterval = setInterval(async () => {
        await updateStatus()
        await updateAttackLogs()
      }, 5000)
      
      // 监听窗口大小变化
      window.addEventListener('resize', handleResize)
    })
    
    onUnmounted(() => {
      if (updateInterval) {
        clearInterval(updateInterval)
      }
      window.removeEventListener('resize', handleResize)
      ipv6Chart?.dispose()
      attackChart?.dispose()
    })
    
    return {
      status,
      attackLogs,
      ipv6ChartRef,
      attackChartRef,
      formatTime
    }
  }
}
</script>

<style scoped>
.dashboard {
  max-width: 1200px;
  margin: 0 auto;
}

.dashboard h2 {
  margin-bottom: 20px;
  color: #333;
}

/* 状态卡片 */
.status-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.status-card {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  text-align: center;
  transition: transform 0.3s;
}

.status-card:hover {
  transform: translateY(-5px);
}

.status-card.danger {
  border-left: 4px solid #f5222d;
}

.status-card.warning {
  border-left: 4px solid #faad14;
}

.status-card.critical {
  border-left: 4px solid #ff4d4f;
}

.status-card-title {
  font-size: 14px;
  color: #666;
  margin-bottom: 10px;
}

.status-card-value {
  font-size: 32px;
  font-weight: bold;
  margin-bottom: 5px;
}

.status-card-desc {
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

/* 最近攻击日志 */
.recent-attacks {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.recent-attacks h3 {
  margin-bottom: 15px;
  color: #333;
  font-size: 16px;
}

.attack-list {
  max-height: 300px;
  overflow-y: auto;
}

.attack-item {
  padding: 12px;
  border-bottom: 1px solid #f0f0f0;
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.attack-item:last-child {
  border-bottom: none;
}

.attack-item-time {
  font-size: 12px;
  color: #999;
}

.attack-item-ip {
  font-size: 14px;
  font-weight: 500;
}

.ipv6-badge {
  background-color: #1890ff;
  color: white;
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 10px;
  margin-left: 8px;
}

.attack-item-type {
  font-size: 14px;
  color: #f5222d;
  font-weight: 500;
}

.empty-state {
  text-align: center;
  padding: 40px 0;
  color: #999;
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
}
</style>
