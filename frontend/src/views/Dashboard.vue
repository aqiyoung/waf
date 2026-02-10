<template>
  <div class="dashboard">
    <!-- 顶部统计卡片 -->
    <div class="top-stats-section">
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-label">请求次数</div>
          <div class="stat-value">{{ status.total_accesses || 20800 }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">页面浏览 (PV)</div>
          <div class="stat-value">{{ status.total_accesses || 5200 }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">独立访客 (UV)</div>
          <div class="stat-value">{{ status.total_accesses || 1100 }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">独立 IP</div>
          <div class="stat-value">{{ status.total_accesses || 1100 }}</div>
        </div>
        <div class="stat-card danger">
          <div class="stat-label">拦截次数</div>
          <div class="stat-value">{{ status.total_attacks || 13100 }}</div>
        </div>
        <div class="stat-card danger">
          <div class="stat-label">攻击 IP</div>
          <div class="stat-value">{{ status.total_attacks || 114 }}</div>
        </div>
      </div>
    </div>
    
    <!-- 主内容区域 -->
    <div class="main-content">
      <!-- 地理位置和攻击来源 -->
      <div class="geo-attack-section">
        <!-- 地理位置地图 -->
        <div class="geo-map-section">
          <div class="section-header">
            <h3>地理位置</h3>
            <div class="map-controls">
              <button 
                v-for="option in mapOptions" 
                :key="option.value"
                :class="['btn', 'btn-sm', { active: currentMap === option.value }]"
                @click="currentMap = option.value"
              >
                {{ option.label }}
              </button>
              <span class="control-separator"></span>
              <button 
                v-for="option in mapModeOptions" 
                :key="option.value"
                :class="['btn', 'btn-sm', { active: currentMapMode === option.value }]"
                @click="() => { currentMapMode = option.value; console.log('Map mode changed to:', option.value); }"
              >
                {{ option.label }}
              </button>
            </div>
          </div>
          <div class="map-container">
            <!-- 3D 球形地图 -->
            <div v-if="currentMapMode === '3d'" class="spherical-map">
              <div class="map-title">攻击来源分布 (3D 球形)</div>
              <div class="sphere-container">
                <!-- 球体 -->
                <div class="sphere" :style="{ transform: `rotateY(${sphereRotation}deg) rotateX(20deg)` }">
                  <!-- 攻击来源标记 -->
                  <div class="attack-marker beijing" title="北京: 15000次攻击">
                    <div class="marker-dot large"></div>
                    <div class="marker-label">北京</div>
                  </div>
                  <div class="attack-marker shanghai" title="上海: 10000次攻击">
                    <div class="marker-dot large"></div>
                    <div class="marker-label">上海</div>
                  </div>
                  <div class="attack-marker guangzhou" title="广州: 8000次攻击">
                    <div class="marker-dot medium"></div>
                    <div class="marker-label">广州</div>
                  </div>
                  <div class="attack-marker chengdu" title="成都: 12000次攻击">
                    <div class="marker-dot large"></div>
                    <div class="marker-label">成都</div>
                  </div>
                  <div class="attack-marker newyork" title="纽约: 2000次攻击">
                    <div class="marker-dot small"></div>
                    <div class="marker-label">纽约</div>
                  </div>
                  <div class="attack-marker tokyo" title="东京: 1800次攻击">
                    <div class="marker-dot small"></div>
                    <div class="marker-label">东京</div>
                  </div>
                </div>
                <!-- 旋转控制 -->
                <div class="map-controls-3d">
                  <button class="rotate-btn" @click="rotateMap('left')">← 左转</button>
                  <button class="rotate-btn" @click="rotateMap('right')">右转 →</button>
                  <button class="rotate-btn" @click="rotateMap('reset')">重置</button>
                </div>
              </div>
              <!-- 攻击次数图例 -->
              <div class="attack-legend">
                <div class="legend-item">
                  <div class="legend-dot large"></div>
                  <span>高攻击 (10000+)</span>
                </div>
                <div class="legend-item">
                  <div class="legend-dot medium"></div>
                  <span>中攻击 (5000-10000)</span>
                </div>
                <div class="legend-item">
                  <div class="legend-dot small"></div>
                  <span>低攻击 (5000以下)</span>
                </div>
              </div>
            </div>
            <!-- 2D 地图 -->
            <div v-else ref="ipMapChartRef" class="map-chart"></div>
          </div>
        </div>
        
        <!-- 攻击来源国家 -->
        <div class="attack-source-section">
          <div class="section-header">
            <h3>攻击来源</h3>
          </div>
          <div class="source-list">
            <div v-for="(source, index) in attackSources" :key="index" class="source-item">
              <div class="source-country">{{ source.country }}</div>
              <div class="source-bar">
                <div class="source-progress" :style="{ width: source.percentage + '%' }"></div>
              </div>
              <div class="source-count">{{ source.count }}</div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 防御情况和趋势 -->
      <div class="defense-trend-section">
        <!-- 防御情况 -->
        <div class="defense-section">
          <div class="section-header">
            <h3>防御情况</h3>
            <button class="btn btn-sm btn-outline">查看更多</button>
          </div>
          <div class="defense-charts">
            <div class="defense-chart">
              <div ref="clientChartRef" class="small-chart"></div>
            </div>
            <div class="defense-chart">
              <div ref="defenseStatusChartRef" class="small-chart"></div>
            </div>
          </div>
        </div>
        
        <!-- 攻击趋势 -->
        <div class="trend-section">
          <div class="section-header">
            <h3>攻击趋势</h3>
          </div>
          <div class="trend-chart-container">
            <div ref="trendChartRef" class="trend-chart"></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { getStatus, getAttackLogs, getAccessLogs } from '../services/api'
import * as echarts from 'echarts'

export default {
  name: 'Dashboard',
  setup() {
    const status = ref({
      total_accesses: 0,
      total_attacks: 0,
      recent_accesses: 0,
      recent_attacks: 0,
      blacklist_count: 0
    })
    const attackLogs = ref([])
    const accessLogs = ref([])
    const ipMapChartRef = ref(null)
    const trendChartRef = ref(null)
    const clientChartRef = ref(null)
    const defenseStatusChartRef = ref(null)
    let ipMapChart = null
    let trendChart = null
    let clientChart = null
    let defenseStatusChart = null
    let updateInterval = null
    
    // 地图切换选项
    const currentMap = ref('global')
    const currentMapMode = ref('2d') // '2d' 或 '3d'
    const mapOptions = [
      { label: '全球', value: 'global' },
      { label: '中国', value: 'china' }
    ]
    const mapModeOptions = [
      { label: '2D', value: '2d' },
      { label: '3D', value: '3d' }
    ]
    
    // 球体旋转角度
    const sphereRotation = ref(0)
    
    // 旋转地图
    const rotateMap = (direction) => {
      if (direction === 'left') {
        sphereRotation.value -= 30
      } else if (direction === 'right') {
        sphereRotation.value += 30
      } else if (direction === 'reset') {
        sphereRotation.value = 0
      }
    }
    
    // 攻击来源数据
    const attackSources = ref([
      { country: '中国', count: 20140, percentage: 95 },
      { country: '美国', count: 218, percentage: 1 },
      { country: '英国', count: 18, percentage: 0.1 },
      { country: '荷兰', count: 14, percentage: 0.07 },
      { country: '芬兰', count: 6, percentage: 0.03 },
      { country: '法国', count: 6, percentage: 0.03 },
      { country: '新加坡', count: 3, percentage: 0.01 }
    ])
    
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
    
    // 更新访问日志
    const updateAccessLogs = async () => {
      try {
        const response = await getAccessLogs(10)
        accessLogs.value = response.data.logs
      } catch (error) {
        console.error('Failed to update access logs:', error)
      }
    }
    
    // 更新图表
    const updateCharts = () => {
      // 更新地图图表
      updateMapChart()
      
      // 更新攻击趋势图表
      updateTrendChart()
      
      // 更新客户端分布图表
      updateClientChart()
      
      // 更新防御状态图表
      updateDefenseStatusChart()
    }
    
    // 更新地图图表
    const updateMapChart = () => {
      if (!ipMapChart) return
      
      console.log('Updating map chart, current mode:', currentMapMode.value, 'current map:', currentMap.value)
      
      // 模拟攻击来源数据
      const mockGeoData = [
        { value: [116.4074, 39.9042, 15000], name: '北京' },
        { value: [121.4737, 31.2304, 10000], name: '上海' },
        { value: [113.2644, 23.1291, 8000], name: '广州' },
        { value: [120.1551, 30.2741, 5000], name: '杭州' },
        { value: [104.0668, 30.5728, 12000], name: '成都' },
        { value: [-74.0060, 40.7128, 2000], name: '纽约' },
        { value: [139.6917, 35.6895, 1800], name: '东京' },
        { value: [100.5018, 13.7563, 700], name: '曼谷' }
      ]
      
      // 检查是否已经注册了地图
      const isMapRegistered = echarts.getMap('world') || echarts.getMap('china')
      
      // 清除之前的配置，确保完全切换
      ipMapChart.clear()
      
      if (currentMapMode.value === '3d') {
        // 3D 球形地图模式 - 使用简单的 3D 散点图
        console.log('Setting 3D spherical map option')
        
        // 直接使用经纬度作为 3D 坐标（简化版本）
        const scatter3DData = mockGeoData.map(item => {
          const [lng, lat, value] = item.value
          return {
            name: item.name,
            value: [lng, lat, value]
          }
        })
        
        // 简单的 3D 散点图配置
        const option = {
          title: {
            text: '攻击来源分布 (3D 球形)',
            left: 'center'
          },
          tooltip: {
            trigger: 'item',
            formatter: function(params) {
              return params.name + '<br/>攻击次数: ' + params.value[2]
            }
          },
          xAxis3D: {
            type: 'value',
            name: '经度'
          },
          yAxis3D: {
            type: 'value',
            name: '纬度'
          },
          zAxis3D: {
            type: 'value',
            name: '攻击次数'
          },
          grid3D: {
            viewControl: {
              projection: 'perspective',
              autoRotate: false,
              autoRotateSpeed: 10,
              zoomSensitivity: 1.2,
              rotateSensitivity: 1,
              panSensitivity: 1
            }
          },
          series: [
            {
              name: '攻击来源',
              type: 'scatter3D',
              data: scatter3DData,
              symbolSize: function(val) {
                return Math.max(10, Math.min(30, val[2] / 800))
              },
              itemStyle: {
                color: function(params) {
                  const value = params.value[2]
                  if (value > 10000) return '#f5222d'
                  if (value > 5000) return '#fa8c16'
                  if (value > 2000) return '#faad14'
                  return '#52c41a'
                }
              },
              label: {
                show: true,
                formatter: '{b}',
                fontSize: 12
              }
            }
          ]
        }
        
        console.log('Setting 3D option:', option)
        ipMapChart.setOption(option)
        
        // 检查图表是否初始化成功
        console.log('3D chart initialized:', !!ipMapChart)
        console.log('Chart instance:', ipMapChart)
        
      } else if (isMapRegistered) {
        // 2D 地图模式
        console.log('Setting 2D map option')
        ipMapChart.setOption({
          title: {
            text: '攻击来源分布',
            left: 'center'
          },
          tooltip: {
            trigger: 'item',
            formatter: function(params) {
              if (params.data) {
                return params.data.name + '<br/>攻击次数: ' + params.data.value[2]
              }
              return params.name
            }
          },
          visualMap: {
            min: 0,
            max: 20000,
            left: 'left',
            bottom: '10%',
            text: ['高', '低'],
            calculable: true,
            inRange: {
              color: ['#e6f7ff', '#bae7ff', '#69c0ff', '#2f9cf0', '#1890ff', '#096dd9']
            }
          },
          geo: {
            map: currentMap.value === 'china' ? 'china' : 'world',
            roam: true,
            zoom: currentMap.value === 'china' ? 2 : 1.2,
            center: currentMap.value === 'china' ? [104.1141, 37.5503] : [0, 30],
            itemStyle: {
              areaColor: '#f0f0f0',
              borderColor: '#999'
            },
            emphasis: {
              itemStyle: {
                areaColor: '#e6f7ff'
              }
            }
          },
          series: [
            {
              name: '攻击来源',
              type: 'scatter',
              coordinateSystem: 'geo',
              data: mockGeoData,
              symbolSize: function(val) {
                return Math.max(8, Math.min(30, val[2] / 800))
              },
              itemStyle: {
                color: function(params) {
                  const value = params.value[2]
                  if (value > 10000) return '#f5222d'
                  if (value > 5000) return '#fa8c16'
                  if (value > 2000) return '#faad14'
                  return '#52c41a'
                }
              },
              label: {
                show: true,
                formatter: '{b}',
                position: 'right',
                fontSize: 12
              }
            }
          ]
        })
      } else {
        // 地图未注册，使用 2D 散点图模式
        console.log('Map not registered, using 2D scatter plot')
        ipMapChart.setOption({
          title: {
            text: '攻击来源分布',
            left: 'center'
          },
          tooltip: {
            trigger: 'item',
            formatter: function(params) {
              return params.data.name + '<br/>攻击次数: ' + params.data.value[2]
            }
          },
          xAxis: {
            type: 'value',
            show: false
          },
          yAxis: {
            type: 'value',
            show: false
          },
          series: [
            {
              name: '攻击来源',
              type: 'scatter',
              data: mockGeoData,
              symbolSize: function(val) {
                return Math.max(8, Math.min(30, val[2] / 800))
              },
              itemStyle: {
                color: function(params) {
                  const value = params.value[2]
                  if (value > 10000) return '#f5222d'
                  if (value > 5000) return '#fa8c16'
                  if (value > 2000) return '#faad14'
                  return '#52c41a'
                }
              },
              label: {
                show: true,
                formatter: '{b}',
                position: 'right',
                fontSize: 12
              }
            }
          ]
        })
      }
    }
    
    // 更新攻击趋势图表
    const updateTrendChart = () => {
      if (!trendChart) return
      
      // 生成模拟的攻击趋势数据
      const hours = 24
      const trendData = []
      const now = new Date()
      
      for (let i = hours - 1; i >= 0; i--) {
        const hour = new Date(now.getTime() - i * 60 * 60 * 1000)
        const hourStr = hour.getHours().toString().padStart(2, '0') + ':00'
        // 生成模拟数据，在某些时间点创建峰值
        let value = Math.floor(Math.random() * 100)
        if (i === 8) value = 1500
        if (i === 16) value = 1200
        trendData.push([hourStr, value])
      }
      
      trendChart.setOption({
        tooltip: {
          trigger: 'axis',
          formatter: function(params) {
            return params[0].name + '<br/>攻击次数: ' + params[0].value[1]
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
          data: trendData.map(item => item[0]),
          axisLabel: {
            rotate: 45,
            interval: 3
          }
        },
        yAxis: {
          type: 'value'
        },
        series: [
          {
            name: '攻击次数',
            type: 'line',
            data: trendData.map(item => item[1]),
            smooth: true,
            itemStyle: {
              color: '#f5222d'
            },
            areaStyle: {
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                {
                  offset: 0,
                  color: 'rgba(245, 34, 45, 0.3)'
                },
                {
                  offset: 1,
                  color: 'rgba(245, 34, 45, 0.1)'
                }
              ])
            }
          }
        ]
      })
    }
    
    // 更新客户端分布图表
    const updateClientChart = () => {
      if (!clientChart) return
      
      clientChart.setOption({
        tooltip: {
          trigger: 'item'
        },
        series: [
          {
            name: '客户端分布',
            type: 'pie',
            radius: '50%',
            data: [
              { value: 17500, name: 'Chrome' },
              { value: 2000, name: 'Safari' },
              { value: 1500, name: 'Edge' },
              { value: 147, name: 'Unknown' },
              { value: 133, name: 'Firefox' }
            ],
            emphasis: {
              itemStyle: {
                shadowBlur: 10,
                shadowOffsetX: 0,
                shadowColor: 'rgba(0, 0, 0, 0.5)'
              }
            }
          }
        ]
      })
    }
    
    // 更新防御状态图表
    const updateDefenseStatusChart = () => {
      if (!defenseStatusChart) return
      
      defenseStatusChart.setOption({
        tooltip: {
          trigger: 'item'
        },
        series: [
          {
            name: '防御状态',
            type: 'pie',
            radius: '50%',
            data: [
              { value: 4604, name: 'SQL注入' },
              { value: 2206, name: 'XSS攻击' },
              { value: 1577, name: 'CSRF攻击' },
              { value: 405, name: '命令注入' }
            ],
            emphasis: {
              itemStyle: {
                shadowBlur: 10,
                shadowOffsetX: 0,
                shadowColor: 'rgba(0, 0, 0, 0.5)'
              }
            }
          }
        ]
      })
    }
    
    // 初始化图表
    const initCharts = () => {
      if (ipMapChartRef.value) {
        // 确保容器有足够的高度和宽度
        ipMapChartRef.value.style.height = '400px'
        ipMapChartRef.value.style.width = '100%'
        ipMapChartRef.value.style.position = 'relative'
        
        console.log('Initializing ECharts instance for map')
        
        // 初始化 ECharts 实例
        ipMapChart = echarts.init(ipMapChartRef.value)
        
        // 检查 ECharts 版本和功能
        console.log('ECharts version:', echarts.version)
        console.log('ECharts has geo3D:', typeof echarts.graphic3D !== 'undefined')
        
        // 加载世界地图数据
        const loadMapData = async () => {
          try {
            console.log('Starting to load map data')
            
            // 尝试加载世界地图
            const worldResponse = await fetch('https://cdn.jsdelivr.net/npm/echarts/map/json/world.json')
            console.log('World map response status:', worldResponse.status)
            if (worldResponse.ok) {
              const worldMapData = await worldResponse.json()
              echarts.registerMap('world', worldMapData)
              console.log('World map data loaded successfully')
            }
            
            // 尝试加载中国地图
            const chinaResponse = await fetch('https://geo.datav.aliyun.com/areas_v3/bound/100000_full.json')
            console.log('China map response status:', chinaResponse.status)
            if (chinaResponse.ok) {
              const chinaMapData = await chinaResponse.json()
              echarts.registerMap('china', chinaMapData)
              console.log('China map data loaded successfully')
            }
            
            // 无论地图是否加载成功，都更新图表
            console.log('Map data loading completed, updating chart')
            updateMapChart()
          } catch (error) {
            console.error('Failed to load map data:', error)
            // 加载失败时也更新图表（使用散点图模式）
            updateMapChart()
          }
        }
        
        // 立即加载地图数据
        loadMapData()
      }
      if (trendChartRef.value) {
        trendChart = echarts.init(trendChartRef.value)
        updateTrendChart()
      }
      if (clientChartRef.value) {
        clientChart = echarts.init(clientChartRef.value)
        updateClientChart()
      }
      if (defenseStatusChartRef.value) {
        defenseStatusChart = echarts.init(defenseStatusChartRef.value)
        updateDefenseStatusChart()
      }
    }
    
    // 加载地图数据
    const loadMapData = (mapType) => {
      if (mapType === 'world') {
        // 加载世界地图数据
        fetch('https://cdn.jsdelivr.net/npm/echarts/map/json/world.json')
          .then(response => response.json())
          .then(data => {
            echarts.registerMap('world', data)
            console.log('World map data loaded, updating chart...')
            updateMapChart()
          })
          .catch(error => {
            console.error('Failed to load world map data:', error)
            // 即使加载失败也尝试更新图表
            updateMapChart()
          })
      } else if (mapType === 'china') {
        // 加载中国地图数据
        fetch('https://geo.datav.aliyun.com/areas_v3/bound/100000_full.json')
          .then(response => response.json())
          .then(data => {
            echarts.registerMap('china', data)
            console.log('China map data loaded, updating chart...')
            updateMapChart()
          })
          .catch(error => {
            console.error('Failed to load china map data:', error)
            // 即使加载失败也尝试更新图表
            updateMapChart()
          })
      }
    }
    
    // 响应式调整图表大小
    const handleResize = () => {
      ipMapChart?.resize()
      trendChart?.resize()
      clientChart?.resize()
      defenseStatusChart?.resize()
    }
    
    // 监听地图类型变化
    watch(currentMap, (newMapType) => {
      loadMapData(newMapType)
    })
    
    // 监听地图模式变化
    watch(currentMapMode, (newMode) => {
      updateMapChart()
    })
    
    onMounted(async () => {
      // 先确保 DOM 元素已经渲染完成
      setTimeout(async () => {
        initCharts()
        // 等待一下让地图数据有时间加载
        setTimeout(() => {
          updateMapChart()
        }, 500)
      }, 100)
      
      await updateStatus()
      await updateAttackLogs()
      await updateAccessLogs()
      
      // 每 5 秒更新一次数据
      updateInterval = setInterval(async () => {
        await updateStatus()
        await updateAttackLogs()
        await updateAccessLogs()
        // 定期更新地图图表
        updateMapChart()
      }, 5000)
      
      // 监听窗口大小变化
      window.addEventListener('resize', handleResize)
    })
    
    onUnmounted(() => {
      if (updateInterval) {
        clearInterval(updateInterval)
      }
      window.removeEventListener('resize', handleResize)
      ipMapChart?.dispose()
      trendChart?.dispose()
      clientChart?.dispose()
      defenseStatusChart?.dispose()
    })
    
    return {
      status,
      attackLogs,
      accessLogs,
      ipMapChartRef,
      trendChartRef,
      clientChartRef,
      defenseStatusChartRef,
      formatTime,
      currentMap,
      mapOptions,
      currentMapMode,
      mapModeOptions,
      attackSources,
      sphereRotation,
      rotateMap
    }
  }
}
</script>

<style scoped>
/* 全局样式重置 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.dashboard {
  width: 100%;
  padding: 20px;
  background-color: #f5f5f5;
  min-height: 100vh;
}

/* 顶部统计卡片 */
.top-stats-section {
  margin-bottom: 24px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 16px;
}

.stat-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  text-align: center;
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
}

.stat-card.danger {
  border-left: 3px solid #f5222d;
}

.stat-label {
  font-size: 12px;
  color: #666;
  margin-bottom: 8px;
  font-weight: 500;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #333;
  margin-bottom: 4px;
}

.stat-card.danger .stat-value {
  color: #f5222d;
}

/* 主内容区域 */
.main-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* 地理位置和攻击来源 */
.geo-attack-section {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 20px;
}

@media (max-width: 1200px) {
  .geo-attack-section {
    grid-template-columns: 1fr;
  }
}

/* 地理位置地图 */
.geo-map-section {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
}

.geo-map-section:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f0f0f0;
}

.section-header h3 {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.map-controls {
  display: flex;
  gap: 8px;
  align-items: center;
}

.control-separator {
  width: 1px;
  height: 20px;
  background-color: #e0e0e0;
  margin: 0 4px;
}

.map-container {
  height: 400px;
  border-radius: 4px;
  overflow: hidden;
  position: relative;
}

.map-chart {
  width: 100%;
  height: 100%;
  position: absolute;
  top: 0;
  left: 0;
}

/* 3D 球形地图样式 */
.spherical-map {
  width: 100%;
  height: 100%;
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.map-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin-bottom: 20px;
}

.sphere-container {
  position: relative;
  width: 300px;
  height: 300px;
  perspective: 1000px;
  margin-bottom: 20px;
}

.sphere {
  position: absolute;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: radial-gradient(circle at 30% 30%, #e6f7ff 0%, #bae7ff 40%, #69c0ff 100%);
  box-shadow: 
    0 0 20px rgba(0, 0, 0, 0.1),
    inset -10px -10px 20px rgba(0, 0, 0, 0.1),
    inset 10px 10px 20px rgba(255, 255, 255, 0.8);
  transform-style: preserve-3d;
  transform: rotateY(0deg) rotateX(20deg);
  transition: transform 1s ease;
  border: 2px solid #1890ff;
  perspective: 1000px;
}

/* 增强3D效果的伪元素 */
.sphere::before {
  content: '';
  position: absolute;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: radial-gradient(circle at 70% 70%, transparent 0%, transparent 60%, rgba(0, 0, 0, 0.1) 100%);
  pointer-events: none;
}

/* 攻击来源标记 */
.attack-marker {
  position: absolute;
  transform-style: preserve-3d;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  align-items: center;
  transform: translateZ(50px); /* 让标记突出在球体表面 */
}

.attack-marker:hover {
  transform: scale(1.1) translateZ(60px);
  z-index: 10;
}

/* 为不同位置的标记添加不同的3D效果 */
.attack-marker.beijing {
  transform: translate(-50%, -50%) translateZ(50px);
}

.attack-marker.shanghai {
  transform: translate(-50%, -50%) translateZ(45px);
}

.attack-marker.guangzhou {
  transform: translate(-50%, -50%) translateZ(40px);
}

.attack-marker.chengdu {
  transform: translate(-50%, -50%) translateZ(48px);
}

.attack-marker.newyork {
  transform: translate(-50%, -50%) translateZ(52px);
}

.attack-marker.tokyo {
  transform: translate(-50%, -50%) translateZ(46px);
}

/* 悬停效果 */
.attack-marker.beijing:hover {
  transform: translate(-50%, -50%) scale(1.1) translateZ(60px);
}

.attack-marker.shanghai:hover {
  transform: translate(-50%, -50%) scale(1.1) translateZ(55px);
}

.attack-marker.guangzhou:hover {
  transform: translate(-50%, -50%) scale(1.1) translateZ(50px);
}

.attack-marker.chengdu:hover {
  transform: translate(-50%, -50%) scale(1.1) translateZ(58px);
}

.attack-marker.newyork:hover {
  transform: translate(-50%, -50%) scale(1.1) translateZ(62px);
}

.attack-marker.tokyo:hover {
  transform: translate(-50%, -50%) scale(1.1) translateZ(56px);
}

.marker-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background-color: #f5222d;
  border: 2px solid white;
  box-shadow: 0 0 4px rgba(0, 0, 0, 0.3);
  animation: pulse 2s infinite;
  margin-bottom: 4px;
}

.marker-dot.large {
  width: 14px;
  height: 14px;
  background-color: #f5222d;
}

.marker-dot.medium {
  width: 12px;
  height: 12px;
  background-color: #fa8c16;
}

.marker-dot.small {
  width: 10px;
  height: 10px;
  background-color: #52c41a;
}

.marker-label {
  background-color: rgba(0, 0, 0, 0.7);
  color: white;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 10px;
  font-weight: 500;
  white-space: nowrap;
  text-align: center;
}

/* 标记位置 */
.attack-marker.beijing {
  top: 30%;
  left: 60%;
  transform: translate(-50%, -50%);
}

.attack-marker.shanghai {
  top: 40%;
  left: 70%;
  transform: translate(-50%, -50%);
}

.attack-marker.guangzhou {
  top: 60%;
  left: 65%;
  transform: translate(-50%, -50%);
}

.attack-marker.chengdu {
  top: 45%;
  left: 30%;
  transform: translate(-50%, -50%);
}

.attack-marker.newyork {
  top: 35%;
  left: 10%;
  transform: translate(-50%, -50%);
}

.attack-marker.tokyo {
  top: 30%;
  left: 80%;
  transform: translate(-50%, -50%);
}

/* 3D 控制按钮 */
.map-controls-3d {
  display: flex;
  gap: 10px;
  margin-top: 20px;
}

.rotate-btn {
  padding: 6px 12px;
  border: 1px solid #1890ff;
  background-color: white;
  color: #1890ff;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.3s ease;
}

.rotate-btn:hover {
  background-color: #e6f7ff;
}

/* 攻击次数图例 */
.attack-legend {
  display: flex;
  gap: 20px;
  margin-top: 20px;
  font-size: 12px;
  color: #666;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
}

.legend-dot {
  border-radius: 50%;
  border: 2px solid white;
  box-shadow: 0 0 2px rgba(0, 0, 0, 0.3);
}

.legend-dot.large {
  width: 12px;
  height: 12px;
  background-color: #f5222d;
}

.legend-dot.medium {
  width: 10px;
  height: 10px;
  background-color: #fa8c16;
}

.legend-dot.small {
  width: 8px;
  height: 8px;
  background-color: #52c41a;
}

/* 静态 HTML 地图样式 */
.html-map {
  width: 100%;
  height: 100%;
  position: relative;
  background-color: #f5f5f5;
  border-radius: 4px;
  overflow: hidden;
}

.map-background {
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #e6f7ff 0%, #f0f0f0 100%);
  position: absolute;
  top: 0;
  left: 0;
  z-index: 1;
}

.map-title {
  position: absolute;
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 16px;
  font-weight: 600;
  color: #333;
  z-index: 3;
}

.attack-marker {
  position: absolute;
  display: flex;
  align-items: center;
  gap: 8px;
  z-index: 2;
  cursor: pointer;
  transition: all 0.3s ease;
}

.attack-marker:hover {
  transform: scale(1.05);
}

.marker-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  border: 2px solid white;
  box-shadow: 0 0 4px rgba(0, 0, 0, 0.3);
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.2);
    opacity: 0.8;
  }
  100% {
    transform: scale(1);
    opacity: 1;
  }
}

.marker-label {
  background-color: rgba(0, 0, 0, 0.7);
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
  white-space: nowrap;
  transition: all 0.3s ease;
}

.attack-marker:hover .marker-label {
  background-color: rgba(0, 0, 0, 0.9);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

/* 静态地图样式 */
.static-map {
  width: 100%;
  height: 100%;
  position: relative;
}

.map-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 4px;
}

.map-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.attack-marker {
  position: absolute;
  display: flex;
  align-items: center;
  gap: 8px;
  pointer-events: auto;
  cursor: pointer;
}

.marker-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background-color: #f5222d;
  border: 2px solid white;
  box-shadow: 0 0 4px rgba(0, 0, 0, 0.3);
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.2);
    opacity: 0.8;
  }
  100% {
    transform: scale(1);
    opacity: 1;
  }
}

.marker-label {
  background-color: rgba(0, 0, 0, 0.7);
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
  white-space: nowrap;
}

.attack-marker:hover .marker-label {
  background-color: rgba(0, 0, 0, 0.9);
}

/* 攻击来源国家 */
.attack-source-section {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
}

.attack-source-section:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
}

.source-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.source-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 0;
}

.source-country {
  width: 80px;
  font-size: 14px;
  color: #666;
  font-weight: 500;
}

.source-bar {
  flex: 1;
  height: 8px;
  background: #f0f0f0;
  border-radius: 4px;
  overflow: hidden;
}

.source-progress {
  height: 100%;
  background: linear-gradient(90deg, #1890ff 0%, #40a9ff 100%);
  border-radius: 4px;
  transition: width 0.6s ease;
}

.source-count {
  width: 70px;
  font-size: 14px;
  font-weight: 600;
  color: #333;
  text-align: right;
}

/* 防御情况和趋势 */
.defense-trend-section {
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 20px;
}

@media (max-width: 1200px) {
  .defense-trend-section {
    grid-template-columns: 1fr;
  }
}

/* 防御情况 */
.defense-section {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
}

.defense-section:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
}

.defense-charts {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.defense-chart {
  height: 180px;
  border-radius: 4px;
  overflow: hidden;
}

.small-chart {
  width: 100%;
  height: 100%;
}

/* 攻击趋势 */
.trend-section {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
}

.trend-section:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
}

.trend-chart-container {
  height: 380px;
  border-radius: 4px;
  overflow: hidden;
}

.trend-chart {
  width: 100%;
  height: 100%;
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
  outline: none;
}

.btn-sm {
  padding: 4px 8px;
  font-size: 12px;
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

.btn.active {
  background-color: #e6f7ff;
  border-color: #1890ff;
  color: #1890ff;
}

.btn.active:hover {
  background-color: #bae7ff;
  border-color: #40a9ff;
  color: #096dd9;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .dashboard {
    padding: 10px;
  }
  
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
  }
  
  .stat-card {
    padding: 16px;
  }
  
  .stat-value {
    font-size: 20px;
  }
  
  .geo-attack-section {
    gap: 16px;
  }
  
  .defense-trend-section {
    gap: 16px;
  }
  
  .map-container {
    height: 300px;
  }
  
  .trend-chart-container {
    height: 300px;
  }
  
  .defense-chart {
    height: 150px;
  }
}

@media (max-width: 480px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .map-controls {
    width: 100%;
    justify-content: flex-start;
  }
}
</style>