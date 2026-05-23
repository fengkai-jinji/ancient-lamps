<template>
  <div ref="chartRef" class="echarts-chart"></div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue';
import axios from 'axios';

// 导入 ECharts
import * as echartsLib from 'echarts';

// 使用局部变量存储 echarts 实例
let echarts = echartsLib;

// 图表配置常量
const CHART_CONFIG = {
  centerNodeSize: 1,
  normalNodeSize: 120,
  screenBreakpoint: 768,
  resizeDebounceDelay: 200 // 防抖延迟
};

const chartRef = ref(null);
let chartInstance = null;
let initTimer = null;
let adjustTimer = null;
let graphData = ref({ nodes: [], edges: [] });

// 从后端获取知识图谱数据
const fetchGraphData = async () => {
  try {
    const res = await axios.get('http://localhost:5000/api/graph');
    console.log('Graph data:', res.data);
    graphData.value = res.data;
  } catch (error) {
    // 静默处理错误，使用默认数据
    console.warn('Failed to fetch graph data:', error);
    // 设置默认数据
    graphData.value = {
      nodes: [
        { name: '古灯文化' }
      ],
      edges: []
    };
  }
};

// 使用最基本的ECharts数据格式
const createOption = () => {
  return {
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(248, 245, 240, 0.95)',
      borderColor: '#8B6B46',
      borderWidth: 2,
      textStyle: {
        color: '#5D4037',
        fontSize: 14,
        fontFamily: '"Ma Shan Zheng", cursive'
      },
      padding: [10, 15],
      borderRadius: 8,
      formatter: function(params) {
        return params.name;
      }
    },
    grid: {
      left: '10%',
      right: '10%',
      top: '10%',
      bottom: '10%',
      containLabel: true
    },
    series: [
      {
        type: 'graph',
        layout: 'force',
        roam: true,
        data: graphData.value.nodes,
        edges: graphData.value.edges,
        // 设置节点大小
        symbolSize: (params) => {
          // 根据节点类型调整大小
          if (!params) {
            return CHART_CONFIG.normalNodeSize;
          }
          if (params.name === '古灯文化') {
            return CHART_CONFIG.centerNodeSize;
          }
          // 图片节点使用数据中设置的原始大小，不进行缩放
          return params.data.symbolSize || CHART_CONFIG.normalNodeSize;
        },
        label: {
          show: false
        },
        itemStyle: {
          color: (params) => {
            if (!params) {
              return '#f8f5f0';
            }
            if (params.name === '古灯文化') {
              return '#8B6B46';
            }
            return '#f8f5f0';
          },
          borderColor: (params) => {
            if (!params) {
              return '#8B6B46';
            }
            if (params.name === '古灯文化') {
              return '#D4AF37';
            }
            return '#8B6B46';
          },
          borderWidth: (params) => {
            if (!params) {
              return 2;
            }
            if (params.name === '古灯文化') {
              return 3;
            }
            return 2;
          },
          shadowBlur: 10,
          shadowColor: 'rgba(139, 107, 70, 0.3)'
        },
        // 节点悬停效果
        emphasis: {
          focus: 'adjacency',
          blurScope: 'coordinateSystem',
          itemStyle: {
            shadowBlur: 30,
            shadowColor: 'rgba(255, 215, 0, 0.8)',
            scale: 1.4
          },
          label: {
            show: false
          },
          lineStyle: {
            width: 4,
            color: '#FFD700',
            type: 'dashed'
          }
        },
        // 节点选中效果
        select: {
          itemStyle: {
            shadowBlur: 40,
            shadowColor: 'rgba(255, 215, 0, 1)',
            scale: 1.5
          },
          label: {
            show: false
          },
          lineStyle: {
            width: 5,
            color: '#FFD700',
            type: 'solid'
          }
        },
        // 启用节点点击交互
        roam: true,
        // 启用鼠标缩放和平移
        zoom: true,
        // 启用节点拖拽
        draggable: true,
        // 边的样式和动画
        lineStyle: {
            color: '#8B7355',
            width: 2,
            type: 'solid',
            curveness: 0.1,
            // 线条动画效果
            animation: true,
            animationDuration: 2000,
            animationEasing: 'cubicInOut'
        },
        // 力导向布局参数
        force: {
          // 优化力导向布局参数
          repulsion: 2000,
          edgeLength: 200,
          gravity: 0.05,
          // 确保中心节点固定在中心位置
          center: ['50%', '50%'],
          // 添加动画效果
          friction: 0.1,
          animation: true,
          animationDuration: 3000,
          animationEasing: 'cubicOut',
          // 持续动画
          animationDurationUpdate: 1500,
          animationEasingUpdate: 'cubicInOut',
          // 增加布局迭代次数，提高布局稳定性
          iterations: 100
        }
      }
    ]
  };
};

// 防抖函数
const debounce = (func, delay) => {
  let timeoutId;
  return (...args) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => func.apply(null, args), delay);
  };
};

// 初始化图表
const initChart = () => {
  try {
    if (chartRef.value) {
      // 确保 chartRef.value 是有效的 DOM 元素
      if (chartRef.value.nodeType === 1) {
        chartInstance = echarts.init(chartRef.value);
        chartInstance.setOption(createOption());
      }
    }
  } catch (error) {
    console.warn('Error initializing ECharts:', error);
  }
};

// 检查是否已加载 echarts
if (typeof echarts === 'undefined') {
  // 动态加载 echarts CDN
  const script = document.createElement('script');
  script.src = 'https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js';
  script.onload = function() {
    echarts = window.echarts;
  };
  document.head.appendChild(script);
}

// 处理窗口大小变化（带防抖）
const handleResize = debounce(() => {
  try {
    if (chartInstance && typeof chartInstance.resize === 'function') {
      chartInstance.resize();
      // 根据屏幕尺寸动态调整图表参数
      adjustChartParams();
    }
  } catch (error) {
    console.warn('Error resizing ECharts:', error);
  }
}, CHART_CONFIG.resizeDebounceDelay);

// 根据屏幕尺寸调整图表参数
const adjustChartParams = () => {
  try {
    const width = window.innerWidth;
    
    // 根据屏幕尺寸调整节点大小
    const baseCenterSize = width < CHART_CONFIG.screenBreakpoint ? 0.8 : CHART_CONFIG.centerNodeSize;
    
    // 更新图表参数
    if (chartInstance && typeof chartInstance.setOption === 'function') {
      chartInstance.setOption({
        series: [{
          symbolSize: (params) => {
            if (!params) {
              return CHART_CONFIG.normalNodeSize;
            }
            if (params.name === '古灯文化') {
              return baseCenterSize;
            }
            // 图片节点使用数据中设置的原始大小，不进行缩放
            return params.data.symbolSize;
          },
          force: {
            edgeLength: 200,
            repulsion: 2000
          }
        }]
      });
    }
  } catch (error) {
    console.warn('Error adjusting chart parameters:', error);
  }
};

// 挂载时初始化图表
onMounted(async () => {
  // 确保页面和容器都已完全加载
  initTimer = setTimeout(async () => {
    // 先获取数据
    await fetchGraphData();
    
    nextTick(() => {
      // 如果 echarts 已加载，直接初始化
      if (typeof echarts !== 'undefined') {
        initChart();
        // 初始化时调整图表参数
        adjustTimer = setTimeout(() => {
          adjustChartParams();
        }, 100);
      }
      // 否则，CDN 加载完成后会自动调用 initChart
    });
  }, 100);
  
  // 窗口大小变化时重新调整图表
  window.addEventListener('resize', handleResize);
});

// 卸载时销毁图表和事件监听
onUnmounted(() => {
  // 清理定时器
  if (initTimer) {
    clearTimeout(initTimer);
    initTimer = null;
  }
  if (adjustTimer) {
    clearTimeout(adjustTimer);
    adjustTimer = null;
  }

  // 销毁图表实例
  if (chartInstance) {
    try {
      chartInstance.dispose();
      chartInstance = null;
    } catch (error) {
      console.warn('Error disposing ECharts instance:', error);
    }
  }

  // 移除事件监听器
  window.removeEventListener('resize', handleResize);
});
</script>

<style scoped>
.echarts-chart {
  width: 100%;
  height: 100%;
  min-height: 500px;
  background-image: url('../assets/images/bac.png');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
}
</style>