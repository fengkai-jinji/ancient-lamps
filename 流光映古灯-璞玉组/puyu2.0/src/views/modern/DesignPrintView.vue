<template>
  <div class="design-print-view">
    <div class="ambient-lighting"></div>
    <div class="floating-particles">
      <div v-for="i in 30" :key="'particle-' + i" class="particle" :style="{ '--i': i, '--delay': i * 0.2 }"></div>
    </div>
    
    <!-- 返回按钮 -->
    <div class="back-button-container">
      <button type="button" @click="goBack" class="back-button">
        <span class="back-icon">←</span>
        <span class="back-text">返回</span>
      </button>
    </div>
    
    <!-- 页面标题 -->
    <div class="page-header">
      <h1 class="page-title">设计与打印</h1>
    </div>
    
    <!-- 主要内容区域 -->
    <div class="main-content">
      <!-- 左侧预览区 -->
      <div class="preview-area">
        <div class="preview-container">
          <LampViewer :settings="designSettings" :show-hint="true" />
        </div>
      </div>
      
      <!-- 右侧控制面板 -->
      <div class="settings-area">
        <!-- 选项卡切换 -->
        <div class="tabs">
          <button 
            :class="['tab', { active: activeTab === 'design' }]"
            @click="activeTab = 'design'"
          >
            设计定制
          </button>
          <button 
            :class="['tab', { active: activeTab === 'print' }]"
            @click="activeTab = 'print'"
          >
            3D打印
          </button>
        </div>
        
        <!-- 设计设置面板 -->
        <div v-if="activeTab === 'design'" class="tab-content">
          <!-- 材质设置 -->
          <div class="setting-card">
            <h3 class="card-title">材质设置</h3>
            <div class="material-options">
              <div 
                v-for="option in materialOptions" 
                :key="option.value"
                :class="['material-option', { active: designSettings.material === option.value }]"
                @click="designSettings.material = option.value"
              >
                <span class="material-name">{{ option.name }}</span>
                <span class="material-desc">{{ option.description }}</span>
              </div>
            </div>
          </div>
          
          <!-- 颜色设置 -->
          <div class="setting-card">
            <h3 class="card-title">颜色调整</h3>
            <div class="color-options">
              <div 
                v-for="color in materialColors" 
                :key="color.value"
                :class="['color-option', { active: designSettings.colors.base === color.value }]"
                :style="{ backgroundColor: color.value }"
                @click="updateAllColors(color.value)"
              >
                <span v-if="designSettings.colors.base === color.value" class="color-check">✓</span>
              </div>
            </div>
          </div>
          

          
          <!-- 尺寸设置 -->
          <div class="setting-card">
            <h3 class="card-title">尺寸设置</h3>
            <div class="setting-group">
              <label>整体尺寸</label>
              <div class="slider-container">
                <input 
                  type="range" 
                  v-model.number="designSettings.size" 
                  min="0.5" 
                  max="2" 
                  step="0.1"
                  class="slider"
                />
                <span class="slider-value">{{ designSettings.size }}x</span>
              </div>
            </div>
            
            <div class="setting-group">
              <label>比例调整</label>
              <div class="slider-container">
                <input 
                  type="range" 
                  v-model.number="designSettings.proportions.base" 
                  min="0.5" 
                  max="1.5" 
                  step="0.1"
                  class="slider"
                />
                <span class="slider-label">灯座</span>
                <span class="slider-value">{{ designSettings.proportions.base }}x</span>
              </div>
              <div class="slider-container">
                <input 
                  type="range" 
                  v-model.number="designSettings.proportions.body" 
                  min="0.5" 
                  max="1.5" 
                  step="0.1"
                  class="slider"
                />
                <span class="slider-label">灯身</span>
                <span class="slider-value">{{ designSettings.proportions.body }}x</span>
              </div>
              <div class="slider-container">
                <input 
                  type="range" 
                  v-model.number="designSettings.proportions.top" 
                  min="0.5" 
                  max="1.5" 
                  step="0.1"
                  class="slider"
                />
                <span class="slider-label">灯顶</span>
                <span class="slider-value">{{ designSettings.proportions.top }}x</span>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 打印设置面板 -->
        <div v-if="activeTab === 'print'" class="tab-content">
          <!-- 打印参数 -->
          <div class="setting-card">
            <div class="card-header">
              <h3 class="card-title">打印参数</h3>
              <button class="recommend-btn" @click="recommendPrintSettings">智能推荐</button>
            </div>
            
            <!-- 打印质量 -->
            <div class="setting-group">
              <label>打印质量</label>
              <div class="quality-options">
                <div 
                  v-for="option in qualityOptions" 
                  :key="option.value"
                  :class="['quality-option', { active: printSettings.quality === option.value }]"
                  @click="printSettings.quality = option.value"
                >
                  <span class="quality-name">{{ option.name }}</span>
                  <span class="quality-desc">{{ option.description }}</span>
                </div>
              </div>
            </div>
            
            <!-- 填充密度 -->
            <div class="setting-group">
              <label>填充密度</label>
              <div class="slider-container">
                <input 
                  type="range" 
                  v-model.number="printSettings.infill" 
                  min="10" 
                  max="100" 
                  step="5"
                  class="slider"
                />
                <span class="slider-value">{{ printSettings.infill }}%</span>
              </div>
            </div>
            
            <!-- 打印速度 -->
            <div class="setting-group">
              <label>打印速度</label>
              <div class="slider-container">
                <input 
                  type="range" 
                  v-model.number="printSettings.speed" 
                  min="20" 
                  max="100" 
                  step="5"
                  class="slider"
                />
                <span class="slider-value">{{ printSettings.speed }}mm/s</span>
              </div>
            </div>
            
            <!-- 材料类型 -->
            <div class="setting-group">
              <label>材料类型</label>
              <div class="material-type-options">
                <div 
                  v-for="type in materialTypes" 
                  :key="type.value"
                  :class="['material-type-option', { active: printSettings.material === type.value }]"
                  @click="printSettings.material = type.value"
                >
                  <span class="material-type-name">{{ type.name }}</span>
                  <span class="material-type-desc">{{ type.description }}</span>
                </div>
              </div>
            </div>
            
            <!-- 支撑结构 -->
            <div class="setting-group">
              <label>支撑结构</label>
              <div class="switch-container">
                <input 
                  type="checkbox" 
                  v-model="printSettings.supports" 
                  class="switch"
                  id="supports-switch"
                />
                <label for="supports-switch" class="switch-label">{{ printSettings.supports ? '启用' : '禁用' }}</label>
              </div>
            </div>
          </div>
          
          <!-- 打印估算 -->
          <div class="setting-card">
            <h3 class="card-title">打印估算</h3>
            <div class="estimation-group">
              <div class="estimation-item">
                <span class="estimation-label">打印时间</span>
                <span class="estimation-value">{{ estimatedTime }}</span>
              </div>
              <div class="estimation-item">
                <span class="estimation-label">耗材用量</span>
                <span class="estimation-value">{{ estimatedMaterial }}g</span>
              </div>
              <div class="estimation-item">
                <span class="estimation-label">预计成本</span>
                <span class="estimation-value">¥{{ estimatedCost }}</span>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 操作按钮 -->
        <div class="action-buttons">
          <button class="action-btn preview-btn" @click="previewModel">预览模型</button>
          <button class="action-btn export-btn" @click="exportModel">导出STL</button>
          <button class="action-btn order-btn" @click="orderPrint">在线打印</button>
          <button class="action-btn reset-btn" @click="resetAll">重置设置</button>
        </div>
        
        <!-- 模型预览对话框 -->
        <div v-if="showPreview" class="model-preview-overlay" @click="closePreview">
          <div class="model-preview-dialog" @click.stop>
            <div class="preview-header">
              <h3>3D模型预览</h3>
              <button class="close-btn" @click="closePreview">×</button>
            </div>
            <div class="preview-canvas-container" ref="previewCanvasContainer">
              <canvas ref="previewCanvas"></canvas>
            </div>
            <div class="preview-info">
              <div class="info-item">
                <span class="label">模型体积:</span>
                <span class="value">{{ modelVolume }} cm³</span>
              </div>
              <div class="info-item">
                <span class="label">表面积:</span>
                <span class="value">{{ modelSurfaceArea }} cm²</span>
              </div>
              <div class="info-item">
                <span class="label">尺寸:</span>
                <span class="value">{{ modelDimensions }}</span>
              </div>
              <div class="info-item">
                <span class="label">打印建议:</span>
                <span class="value">{{ printRecommendation }}</span>
              </div>
            </div>
            <div class="preview-actions">
              <button class="preview-action-btn" @click="exportModelFromPreview">导出STL</button>
              <button class="preview-action-btn secondary" @click="closePreview">关闭</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import * as THREE from 'three'
import { STLExporter } from 'three/examples/jsm/exporters/STLExporter'
import LampViewer from '@/components/LampViewer.vue'

const router = useRouter()

let scene, camera, renderer, lampModel, animationFrameId
const previewCanvas = ref(null)
const previewCanvasContainer = ref(null)
const showPreview = ref(false)

const goBack = () => router.push('/modern')

// 选项卡状态
const activeTab = ref('design')

// 设计设置
const designSettings = reactive({
  material: 'ceramic',
  colors: {
    base: '#FFD700',
    body: '#FFD700',
    top: '#FFD700',
    ring: '#FFD700'
  },
  size: 1,
  proportions: {
    base: 1,
    body: 1,
    top: 1
  }
})

// 材质选项
const materialOptions = [
  { value: 'ceramic', name: '陶瓷', description: '传统质感，色泽温润' },
  { value: 'bronze', name: '青铜', description: '古朴典雅，金属光泽' },
  { value: 'gold', name: '金色', description: '华丽高贵，光芒四射' },
  { value: 'silver', name: '银色', description: '简约现代，优雅大方' },
  { value: 'wood', name: '木质', description: '自然质朴，温暖舒适' }
]

// 颜色选项
const materialColors = [
  { name: '金色', value: '#FFD700' },
  { name: '青铜', value: '#CD7F32' },
  { name: '银色', value: '#C0C0C0' },
  { name: '黑色', value: '#000000' },
  { name: '白色', value: '#FFFFFF' },
  { name: '红色', value: '#FF0000' },
  { name: '蓝色', value: '#0000FF' },
  { name: '绿色', value: '#00FF00' },
  { name: '橙色', value: '#FFA500' },
  { name: '紫色', value: '#800080' },
  { name: '粉色', value: '#FFC0CB' },
  { name: '青色', value: '#00FFFF' }
]



// 打印设置
const printSettings = reactive({
  material: 'pla',
  quality: 'medium',
  infill: 20,
  speed: 50,
  supports: false,
  layerHeight: 0.2
})

// 打印质量选项
const qualityOptions = [
  { value: 'low', name: '快速', description: '0.3mm层高，适合原型' },
  { value: 'medium', name: '标准', description: '0.2mm层高，平衡质量' },
  { value: 'high', name: '精细', description: '0.1mm层高，高质量' }
]

// 材料类型
const materialTypes = [
  { value: 'pla', name: 'PLA', description: '环保易用，适合初学者' },
  { value: 'abs', name: 'ABS', description: '耐用耐热，适合功能性部件' },
  { value: 'petg', name: 'PETG', description: '强度高，耐化学腐蚀' },
  { value: 'resin', name: '树脂', description: '高精度，适合精细模型' }
]

// 更新所有颜色
const updateAllColors = (color) => {
  designSettings.colors.base = color
  designSettings.colors.body = color
  designSettings.colors.top = color
  designSettings.colors.ring = color
}



// 智能推荐打印参数
const recommendPrintSettings = () => {
  const size = designSettings.size
  
  if (size > 1.5) {
    printSettings.quality = 'medium'
    printSettings.infill = 30
    printSettings.speed = 40
    printSettings.supports = true
  } else {
    printSettings.quality = 'low'
    printSettings.infill = 20
    printSettings.speed = 60
    printSettings.supports = false
  }
}

// 打印时间估算
const estimatedTime = computed(() => {
  const baseTime = 60
  const sizeMultiplier = designSettings.size
  const complexityMultiplier = (designSettings.proportions.base + designSettings.proportions.body + designSettings.proportions.top) / 3
  const materialMultiplier = { pla: 1, abs: 1.2, petg: 1.1, resin: 1.5 }[printSettings.material] || 1
  const qualityMultiplier = { low: 0.5, medium: 1, high: 2 }[printSettings.quality] || 1
  const infillMultiplier = printSettings.infill / 20
  const speedMultiplier = 100 / printSettings.speed
  const supportsMultiplier = printSettings.supports ? 1.3 : 1
  
  const totalMinutes = baseTime * sizeMultiplier * complexityMultiplier * materialMultiplier * qualityMultiplier * infillMultiplier * speedMultiplier * supportsMultiplier
  
  if (totalMinutes < 60) {
    return `${Math.round(totalMinutes)}分钟`
  } else {
    const hours = Math.floor(totalMinutes / 60)
    const minutes = Math.round(totalMinutes % 60)
    return `${hours}小时${minutes}分钟`
  }
})

// 耗材用量估算
const estimatedMaterial = computed(() => {
  const baseMaterial = 200
  const sizeMultiplier = designSettings.size * designSettings.size
  const complexityMultiplier = (designSettings.proportions.base + designSettings.proportions.body + designSettings.proportions.top) / 3
  const infillMultiplier = printSettings.infill / 20
  const supportsMultiplier = printSettings.supports ? 1.2 : 1
  
  return Math.round(baseMaterial * sizeMultiplier * complexityMultiplier * infillMultiplier * supportsMultiplier)
})

// 成本估算
const estimatedCost = computed(() => {
  const materialCost = { pla: 0.05, abs: 0.06, petg: 0.07, resin: 0.15 }[printSettings.material] || 0.05
  const materialAmount = estimatedMaterial.value
  const baseLaborCost = 50
  const timeCostPerHour = 30
  const timeInHours = estimatedTime.value.includes('小时') ? 
    parseInt(estimatedTime.value.split('小时')[0]) + parseInt(estimatedTime.value.split('小时')[1])/60 : 
    parseInt(estimatedTime.value)/60
  const qualityPremium = { low: 0, medium: 10, high: 20 }[printSettings.quality] || 0
  
  const totalCost = materialAmount * materialCost + baseLaborCost + timeCostPerHour * timeInHours + qualityPremium
  
  return Math.round(totalCost)
})

// 模型信息计算
const modelVolume = computed(() => {
  const size = designSettings.size
  const baseVolume = Math.PI * 1.5 * 1.5 * 0.6 * size * size * size
  const bodyVolume = Math.PI * 1.05 * 1.05 * 2.4 * size * size * size
  const topVolume = Math.PI * 0.8 * 0.8 * 0.4 * size * size * size
  const sphereVolume = (4/3) * Math.PI * 0.5 * 0.5 * 0.5 * size * size * size
  const totalVolume = baseVolume + bodyVolume + topVolume + sphereVolume
  return Math.round(totalVolume * 10) / 10
})

const modelSurfaceArea = computed(() => {
  const size = designSettings.size
  const baseArea = 2 * Math.PI * 1.5 * 1.5 + 2 * Math.PI * 1.5 * 0.6 * size
  const bodyArea = 2 * Math.PI * 1.05 * 1.05 + 2 * Math.PI * 1.05 * 2.4 * size
  const topArea = 2 * Math.PI * 0.8 * 0.8 + 2 * Math.PI * 0.8 * 0.4 * size
  const sphereArea = 4 * Math.PI * 0.5 * 0.5 * size * size
  const totalArea = baseArea + bodyArea + topArea + sphereArea
  return Math.round(totalArea * 10) / 10
})

const modelDimensions = computed(() => {
  const size = designSettings.size
  const height = (0.6 + 2.4 + 0.4 + 1.0) * size
  const width = 1.8 * size * 2
  return `约 ${Math.round(height * 10) / 10}cm × ${Math.round(width * 10) / 10}cm`
})

const printRecommendation = computed(() => {
  const size = designSettings.size
  if (size > 1.5) {
    return '建议使用支撑结构，选择PLA或PETG材料'
  } else if (size > 1.0) {
    return '建议使用PLA材料，标准打印质量'
  } else {
    return '可快速打印，适合初学者'
  }
})

// 创建可打印的3D模型
const createPrintableLamp = (settings) => {
  const group = new THREE.Group()
  
  const { size, proportions, colors } = settings
  
  // 1. 创建灯座（圆柱体）
  const baseGeometry = new THREE.CylinderGeometry(
    1.2 * size,
    1.8 * size,
    0.6 * size * proportions.base,
    64
  )
  const baseMaterial = new THREE.MeshStandardMaterial({
    color: colors.base,
    metalness: 0.8,
    roughness: 0.2
  })
  const baseMesh = new THREE.Mesh(baseGeometry, baseMaterial)
  baseMesh.position.y = -1.2 * size
  baseMesh.castShadow = true
  baseMesh.receiveShadow = true
  group.add(baseMesh)
  
  // 2. 创建灯身（带装饰环）
  const bodyHeight = 2.4 * size * proportions.body
  const bodyGeometry = new THREE.CylinderGeometry(
    0.9 * size,
    1.2 * size,
    bodyHeight,
    64
  )
  const bodyMaterial = new THREE.MeshStandardMaterial({
    color: colors.body,
    metalness: 0.85,
    roughness: 0.15
  })
  const bodyMesh = new THREE.Mesh(bodyGeometry, bodyMaterial)
  bodyMesh.position.y = -0.9 * size + bodyHeight / 2
  bodyMesh.castShadow = true
  bodyMesh.receiveShadow = true
  group.add(bodyMesh)
  
  // 3. 创建装饰环（圆环体）
  for (let i = 0; i < 4; i++) {
    const ringGeometry = new THREE.TorusGeometry(
      1.05 * size,
      0.08 * size,
      32,
      64
    )
    const ringMaterial = new THREE.MeshStandardMaterial({
      color: colors.ring,
      metalness: 0.9,
      roughness: 0.1
    })
    const ringMesh = new THREE.Mesh(ringGeometry, ringMaterial)
    ringMesh.position.y = -1.2 * size + 0.6 * (i + 1) * size
    ringMesh.rotation.x = Math.PI / 2
    ringMesh.castShadow = true
    group.add(ringMesh)
  }
  
  // 4. 创建灯顶
  const topHeight = 0.4 * size * proportions.top
  const topGeometry = new THREE.CylinderGeometry(
    0.7 * size,
    0.9 * size,
    topHeight,
    64
  )
  const topMaterial = new THREE.MeshStandardMaterial({
    color: colors.top,
    metalness: 0.9,
    roughness: 0.1
  })
  const topMesh = new THREE.Mesh(topGeometry, topMaterial)
  topMesh.position.y = -0.9 * size + bodyHeight + topHeight / 2
  topMesh.castShadow = true
  topMesh.receiveShadow = true
  group.add(topMesh)
  
  // 5. 创建灯芯/装饰球
  const decorationGeometry = new THREE.SphereGeometry(0.5 * size, 32, 32)
  const decorationMaterial = new THREE.MeshStandardMaterial({
    color: colors.base,
    metalness: 0.7,
    roughness: 0.3,
    emissive: colors.base,
    emissiveIntensity: 0.2
  })
  const decorationMesh = new THREE.Mesh(decorationGeometry, decorationMaterial)
  decorationMesh.position.y = -0.9 * size + bodyHeight + topHeight + 0.5 * size
  decorationMesh.castShadow = true
  group.add(decorationMesh)
  
  return group
}

// 导出STL文件
const exportToSTL = (scene, filename = 'ancient-lamp.stl') => {
  try {
    const exporter = new STLExporter()
    const stlBinary = exporter.parse(scene, { binary: true })
    
    const blob = new Blob([stlBinary], { type: 'application/octet-stream' })
    const url = URL.createObjectURL(blob)
    
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
    
    return true
  } catch (error) {
    console.error('STL导出失败:', error)
    return false
  }
}

// 导出模型
const exportModel = () => {
  try {
    const lampGroup = createPrintableLamp(designSettings)
    
    const success = exportToSTL(lampGroup, `ancient-lamp-${Date.now()}.stl`)
    
    if (success) {
      alert('STL模型导出成功！\n\n您可以使用任何3D打印软件（如Cura、PrusaSlicer等）打开此文件进行切片和打印。')
    } else {
      alert('模型导出失败，请重试')
    }
  } catch (error) {
    console.error('导出模型时出错:', error)
    alert('导出失败：' + error.message)
  }
}

// 下单打印
const orderPrint = () => {
  const orderInfo = {
    design: designSettings,
    print: printSettings,
    estimated: {
      time: estimatedTime.value,
      material: estimatedMaterial.value,
      cost: estimatedCost.value
    },
    orderId: `ORDER-${Date.now()}`,
    orderTime: new Date().toLocaleString('zh-CN')
  }
  
  const confirmMessage = `确认下单打印？\n\n订单编号：${orderInfo.orderId}\n下单时间：${orderInfo.orderTime}\n预计打印时间：${orderInfo.estimated.time}\n预计耗材用量：${orderInfo.estimated.material}g\n预计成本：¥${orderInfo.estimated.cost}\n\n点击"确定"选择打印服务，点击"取消"取消订单。`
  
  if (confirm(confirmMessage)) {
    showPrintServiceDialog()
  }
}

// 显示打印服务选择对话框
const showPrintServiceDialog = () => {
  const services = [
    { name: '未来工场', url: 'https://www.wenext.com', desc: '国内专业3D打印服务，速度快' },
    { name: '魔猴网', url: 'https://www.mohou.com', desc: '性价比高，材料选择多' },
    { name: 'i.materialise', url: 'https://i.materialise.com', desc: '国际知名，质量优秀' },
    { name: 'Shapeways', url: 'https://www.shapeways.com', desc: '全球最大3D打印社区' }
  ]
  
  let message = '请选择3D打印服务：\n\n'
  services.forEach((s, i) => {
    message += `${i + 1}. ${s.name}\n   ${s.desc}\n   ${s.url}\n\n`
  })
  message += '点击"确定"将打开未来工场（推荐），您也可以手动访问其他服务。\n\n提示：请先导出STL文件，然后在打印服务网站上上传文件下单。'
  
  if (confirm(message)) {
    window.open('https://www.wenext.com', '_blank')
    alert('已打开未来工场网站。\n\n请按以下步骤操作：\n1. 先点击"导出模型"按钮下载STL文件\n2. 在打印网站上注册/登录账号\n3. 上传STL文件\n4. 选择材料、颜色、质量等参数\n5. 确认订单并支付\n6. 等待快递送达')
  }
}

// 预览模型
const previewModel = () => {
  showPreview.value = true
  
  setTimeout(() => {
    initPreviewScene()
  }, 100)
}

// 初始化预览场景
const initPreviewScene = () => {
  if (!previewCanvas.value || !previewCanvasContainer.value) return
  
  const container = previewCanvasContainer.value
  const canvas = previewCanvas.value
  const width = container.clientWidth
  const height = container.clientHeight
  
  scene = new THREE.Scene()
  scene.background = new THREE.Color(0xf5f5f5)
  
  camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000)
  camera.position.set(5, 5, 5)
  camera.lookAt(0, 0, 0)
  
  renderer = new THREE.WebGLRenderer({ canvas, antialias: true })
  renderer.setSize(width, height)
  renderer.setPixelRatio(window.devicePixelRatio)
  renderer.shadowMap.enabled = true
  
  const ambientLight = new THREE.AmbientLight(0xffffff, 0.6)
  scene.add(ambientLight)
  
  const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8)
  directionalLight.position.set(5, 10, 5)
  directionalLight.castShadow = true
  scene.add(directionalLight)
  
  lampModel = createPrintableLamp(designSettings)
  scene.add(lampModel)
  
  const gridHelper = new THREE.GridHelper(10, 10, 0xcccccc, 0xeeeeee)
  scene.add(gridHelper)
  
  animatePreview()
}

// 预览动画
const animatePreview = () => {
  if (!showPreview.value) return
  
  animationFrameId = requestAnimationFrame(animatePreview)
  
  if (lampModel) {
    lampModel.rotation.y += 0.005
  }
  
  renderer.render(scene, camera)
}

// 关闭预览
const closePreview = () => {
  showPreview.value = false
  
  if (animationFrameId) {
    cancelAnimationFrame(animationFrameId)
    animationFrameId = null
  }
  
  if (renderer) {
    renderer.dispose()
    renderer = null
  }
  
  if (lampModel) {
    lampModel.traverse((child) => {
      if (child.geometry) child.geometry.dispose()
      if (child.material) child.material.dispose()
    })
    lampModel = null
  }
  
  scene = null
  camera = null
}

// 从预览导出
const exportModelFromPreview = () => {
  exportModel()
  closePreview()
}

// 重置所有设置
const resetAll = () => {
  Object.assign(designSettings, {
    material: 'ceramic',
    colors: {
      base: '#FFD700',
      body: '#FFD700',
      top: '#FFD700',
      ring: '#FFD700'
    },
    size: 1,
    proportions: {
      base: 1,
      body: 1,
      top: 1
    }
  })
  
  Object.assign(printSettings, {
    material: 'pla',
    quality: 'medium',
    infill: 20,
    speed: 50,
    supports: false,
    layerHeight: 0.2
  })
}
</script>

<style scoped>
.design-print-view {
  height: 100vh;
  background: linear-gradient(135deg, #f8f5f0 0%, #e8e0d5 100%);
  color: #5d4037;
  padding: 20px;
  position: relative;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.ambient-lighting {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: radial-gradient(ellipse at 50% 0%, rgba(139, 107, 70, 0.08) 0%, transparent 60%);
  pointer-events: none;
  z-index: 0;
}

.floating-particles {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 1;
}

.particle {
  position: absolute;
  width: 3px;
  height: 3px;
  background: radial-gradient(circle, rgba(139, 107, 70, 0.9) 0%, rgba(139, 107, 70, 0) 70%);
  border-radius: 50%;
  animation: particleFloat 20s linear infinite;
  animation-delay: var(--delay);
  opacity: 0.4;
}

@keyframes particleFloat {
  0% { transform: translateY(100vh) translateX(0); opacity: 0; }
  10% { opacity: 0.4; }
  90% { opacity: 0.4; }
  100% { transform: translateY(-100px) translateX(100px); opacity: 0; }
}

.back-button-container {
  position: absolute;
  top: 30px;
  left: 40px;
  z-index: 100;
}

.back-button {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: rgba(139, 107, 70, 0.1);
  border: 1px solid rgba(139, 107, 70, 0.2);
  border-radius: 10px;
  color: #5d4037;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  font-size: 0.95rem;
  font-family: "SimSun", serif;
  box-shadow: 0 2px 8px rgba(139, 107, 70, 0.1);
}

.back-button:hover {
  background: rgba(139, 107, 70, 0.2);
  border-color: rgba(139, 107, 70, 0.4);
  color: #8b6b46;
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(139, 107, 70, 0.3);
}

.back-icon {
  font-size: 1.1rem;
}

/* 页面标题 */
.page-header {
  text-align: center;
  margin-bottom: 15px;
  position: relative;
  z-index: 10;
  flex-shrink: 0;
}

.page-title {
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 10px;
  background: linear-gradient(135deg, #8b6b46, #d4b88c);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  font-family: "SimSun", serif;
  text-shadow: 0 0 20px rgba(139, 107, 70, 0.5);
  letter-spacing: 2px;
  animation: titleGradient 3s linear infinite;
  background-size: 200% auto;
}

@keyframes titleGradient {
  0% { background-position: 0% center; }
  100% { background-position: 200% center; }
}

.page-description {
  font-size: 1.1rem;
  color: #8b6b46;
  background: rgba(139, 107, 70, 0.03);
  padding: 16px 24px;
  border-radius: 16px;
  border-left: 4px solid #8b6b46;
  backdrop-filter: blur(10px);
  display: inline-block;
  margin: 0 auto;
  font-family: "SimSun", serif;
}

/* 主要内容区域 */
.main-content {
  display: grid;
  grid-template-columns: 1fr 420px;
  gap: 20px;
  max-width: 1400px;
  margin: 0 auto;
  align-items: stretch;
  position: relative;
  z-index: 10;
  flex: 1;
  min-height: 0;
}

/* 预览区 */
.preview-area {
  position: relative;
  height: 100%;
}

.preview-container {
  width: 100%;
  height: 100%;
  border-radius: 16px;
  overflow: hidden;
  border: 1px solid rgba(139, 107, 70, 0.2);
  background: rgba(139, 107, 70, 0.1);
  box-shadow: 0 24px 48px rgba(139, 107, 70, 0.2);
  backdrop-filter: blur(20px);
  animation: cardFloat 8s ease-in-out infinite;
}

@keyframes cardFloat {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-12px); }
}

/* 设置区 */
.settings-area {
  display: flex;
  flex-direction: column;
  gap: 15px;
  overflow-y: auto;
  padding-right: 10px;
  background: rgba(139, 107, 70, 0.05);
  border-radius: 16px;
  padding: 15px;
  border: 1px solid rgba(139, 107, 70, 0.1);
  height: 100%;
}

.settings-area::-webkit-scrollbar {
  width: 6px;
}

.settings-area::-webkit-scrollbar-track {
  background: rgba(248, 245, 240, 0.5);
  border-radius: 3px;
}

.settings-area::-webkit-scrollbar-thumb {
  background: rgba(139, 107, 70, 0.3);
  border-radius: 3px;
}

.settings-area::-webkit-scrollbar-thumb:hover {
  background: rgba(139, 107, 70, 0.5);
}

/* 选项卡 */
.tabs {
  display: flex;
  gap: 8px;
  background: rgba(139, 107, 70, 0.1);
  border-radius: 12px;
  border: 1px solid rgba(139, 107, 70, 0.2);
  padding: 8px;
  margin-bottom: 20px;
}

.tab {
  flex: 1;
  padding: 12px 16px;
  background: transparent;
  border: none;
  border-radius: 8px;
  color: #8b6b46;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  font-family: "SimSun", serif;
}

.tab:hover {
  background: rgba(139, 107, 70, 0.1);
}

.tab.active {
  background: linear-gradient(135deg, rgba(139, 107, 70, 0.2), rgba(150, 123, 86, 0.2));
  color: #8b6b46;
  border: 1px solid rgba(139, 107, 70, 0.3);
}

/* 选项卡内容 */
.tab-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 设置卡片 */
.setting-card {
  background: rgba(139, 107, 70, 0.1);
  border: 1px solid rgba(139, 107, 70, 0.2);
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 4px 15px rgba(139, 107, 70, 0.1);
  backdrop-filter: blur(10px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.card-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: #8b6b46;
  margin-bottom: 15px;
  font-family: "SimSun", serif;
  text-shadow: 0 0 10px rgba(139, 107, 70, 0.5);
}

.recommend-btn {
  background: linear-gradient(135deg, #8b6b46, #d4b88c);
  border: none;
  color: white;
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(139, 107, 70, 0.3);
  font-family: "SimSun", serif;
}

.recommend-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(139, 107, 70, 0.4);
  background: linear-gradient(135deg, #9a7b56, #e3c9a1);
}

/* 设置组 */
.setting-group {
  margin-bottom: 20px;
}

.setting-group label {
  display: block;
  font-size: 0.95rem;
  font-weight: 600;
  color: #8b6b46;
  margin-bottom: 10px;
  font-family: "SimSun", serif;
}

.section-subtitle {
  font-size: 0.9rem;
  font-weight: 600;
  color: #8b6b46;
  margin-bottom: 10px;
  font-family: "SimSun", serif;
}

/* 材质选项 */
.material-options {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

.material-option {
  padding: 12px;
  background: rgba(139, 107, 70, 0.1);
  border: 2px solid rgba(139, 107, 70, 0.2);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.material-option:hover {
  border-color: rgba(139, 107, 70, 0.4);
  background: rgba(139, 107, 70, 0.2);
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(139, 107, 70, 0.3);
}

.material-option.active {
  border-color: #8b6b46;
  background: rgba(139, 107, 70, 0.2);
  box-shadow: 0 0 15px rgba(139, 107, 70, 0.4);
}

.material-name {
  display: block;
  font-weight: 600;
  color: #8b6b46;
  margin-bottom: 4px;
  font-family: "SimSun", serif;
}

.material-desc {
  display: block;
  font-size: 0.75rem;
  color: #8b6b46;
  font-family: "SimSun", serif;
}

/* 颜色选项 */
.color-options {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 8px;
}

.color-option {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  cursor: pointer;
  position: relative;
  border: 3px solid transparent;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.color-option:hover {
  transform: scale(1.1);
  border-color: rgba(139, 107, 70, 0.5);
  box-shadow: 0 4px 12px rgba(139, 107, 70, 0.3);
}

.color-option.active {
  border-color: #8b6b46;
  box-shadow: 0 0 15px rgba(139, 107, 70, 0.5);
}

.color-check {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: white;
  font-weight: bold;
  text-shadow: 0 0 3px rgba(0, 0, 0, 0.8);
}



/* 滑块容器 */
.slider-container {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 10px;
}

.slider {
  flex: 1;
  height: 6px;
  border-radius: 3px;
  background: rgba(139, 107, 70, 0.2);
  outline: none;
  -webkit-appearance: none;
  appearance: none;
}

.slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: #8b6b46;
  cursor: pointer;
  border: 2px solid #f5f0e6;
  box-shadow: 0 0 10px rgba(139, 107, 70, 0.5);
}

.slider::-moz-range-thumb {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: #8b6b46;
  cursor: pointer;
  border: 2px solid #f5f0e6;
  box-shadow: 0 0 10px rgba(139, 107, 70, 0.5);
}

.slider-value {
  min-width: 60px;
  font-size: 0.9rem;
  font-weight: 600;
  color: #8b6b46;
  text-align: right;
  font-family: "SimSun", serif;
}

.slider-label {
  min-width: 40px;
  font-size: 0.9rem;
  color: #8b6b46;
  font-family: "SimSun", serif;
}

/* 打印质量选项 */
.quality-options {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.quality-option {
  flex: 1;
  min-width: 100px;
  padding: 12px;
  background: rgba(139, 107, 70, 0.1);
  border: 2px solid rgba(139, 107, 70, 0.2);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  text-align: center;
  backdrop-filter: blur(10px);
}

.quality-option:hover {
  border-color: rgba(139, 107, 70, 0.4);
  background: rgba(139, 107, 70, 0.2);
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(139, 107, 70, 0.3);
}

.quality-option.active {
  border-color: #8b6b46;
  background: rgba(139, 107, 70, 0.2);
  box-shadow: 0 0 15px rgba(139, 107, 70, 0.4);
}

.quality-name {
  display: block;
  font-weight: 600;
  color: #8b6b46;
  margin-bottom: 4px;
  font-family: "SimSun", serif;
}

.quality-desc {
  display: block;
  font-size: 0.75rem;
  color: #8b6b46;
  font-family: "SimSun", serif;
}

/* 材料类型选项 */
.material-type-options {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

.material-type-option {
  padding: 12px;
  background: rgba(139, 107, 70, 0.1);
  border: 2px solid rgba(139, 107, 70, 0.2);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.material-type-option:hover {
  border-color: rgba(139, 107, 70, 0.4);
  background: rgba(139, 107, 70, 0.2);
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(139, 107, 70, 0.3);
}

.material-type-option.active {
  border-color: #8b6b46;
  background: rgba(139, 107, 70, 0.2);
  box-shadow: 0 0 15px rgba(139, 107, 70, 0.4);
}

.material-type-name {
  display: block;
  font-weight: 600;
  color: #8b6b46;
  margin-bottom: 4px;
  font-family: "SimSun", serif;
}

.material-type-desc {
  display: block;
  font-size: 0.75rem;
  color: #8b6b46;
  font-family: "SimSun", serif;
}

/* 开关控制 */
.switch-container {
  display: flex;
  align-items: center;
  gap: 15px;
}

.switch {
  position: relative;
  width: 50px;
  height: 24px;
  -webkit-appearance: none;
  appearance: none;
  background: rgba(139, 107, 70, 0.2);
  border: 2px solid rgba(139, 107, 70, 0.3);
  border-radius: 12px;
  outline: none;
  cursor: pointer;
  transition: all 0.3s ease;
}

.switch:checked {
  background: #8b6b46;
  border-color: #8b6b46;
}

.switch:before {
  content: '';
  position: absolute;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: white;
  top: 2px;
  left: 2px;
  transition: all 0.3s ease;
}

.switch:checked:before {
  transform: translateX(26px);
}

.switch-label {
  font-size: 0.9rem;
  color: #5d4037;
  cursor: pointer;
  font-family: "SimSun", serif;
}

/* 估算组 */
.estimation-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.estimation-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: rgba(139, 107, 70, 0.1);
  border-radius: 8px;
  border: 1px solid rgba(139, 107, 70, 0.2);
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.estimation-item:hover {
  border-color: rgba(139, 107, 70, 0.4);
  box-shadow: 0 4px 12px rgba(139, 107, 70, 0.3);
  transform: translateX(4px);
}

.estimation-label {
  font-size: 0.9rem;
  color: #8b6b46;
  font-family: "SimSun", serif;
}

.estimation-value {
  font-size: 1.1rem;
  font-weight: 700;
  color: #8b6b46;
  text-shadow: 0 0 8px rgba(139, 107, 70, 0.5);
  font-family: "SimSun", serif;
}

/* 操作按钮 */
.action-buttons {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  justify-content: center;
  padding: 15px;
  background: rgba(139, 107, 70, 0.1);
  border: 1px solid rgba(139, 107, 70, 0.2);
  border-radius: 16px;
  box-shadow: 0 4px 15px rgba(139, 107, 70, 0.1);
  backdrop-filter: blur(10px);
  margin-top: 15px;
  margin-bottom: 10px;
}

.action-btn {
  flex: 1;
  min-width: 100px;
  padding: 12px 20px;
  border: none;
  border-radius: 10px;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  font-family: "SimSun", serif;
}

.action-btn:before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: linear-gradient(45deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transform: rotate(45deg);
  transition: all 0.6s ease;
  opacity: 0;
}

.action-btn:hover:before {
  left: 130%;
  opacity: 1;
}

.action-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 16px rgba(139, 107, 70, 0.4);
}

.export-btn {
  background: linear-gradient(135deg, #8b6b46, #d4b88c);
  color: white;
}

.order-btn {
  background: linear-gradient(135deg, #8b6b46, #d4b88c);
  color: white;
}

.reset-btn {
  background: rgba(139, 107, 70, 0.1);
  border: 2px solid rgba(139, 107, 70, 0.3);
  color: #8b6b46;
}

.reset-btn:hover {
  background: rgba(139, 107, 70, 0.2);
  border-color: rgba(139, 107, 70, 0.5);
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .main-content {
    grid-template-columns: 1fr;
    gap: 30px;
  }
  
  .preview-container {
    height: 500px;
  }
  
  .settings-area {
    max-height: none;
    overflow-y: visible;
    max-width: 600px;
    margin: 0 auto;
  }
}

@media (max-width: 768px) {
  .design-print-view {
    padding: 20px 10px;
  }
  
  .page-header {
    margin-bottom: 40px;
  }
  
  .page-title {
    font-size: 2rem;
  }
  
  .material-options,
  .material-type-options {
    grid-template-columns: 1fr;
  }
  
  .color-options {
    grid-template-columns: repeat(4, 1fr);
  }
  
  .quality-options {
    flex-direction: column;
  }
  
  .action-buttons {
    flex-direction: column;
  }
  
  .action-btn {
    width: 100%;
  }
}

@media (max-width: 480px) {
  .preview-container {
    height: 350px;
  }
  
  .setting-card {
    padding: 15px;
  }
  
  .color-options {
    grid-template-columns: repeat(3, 1fr);
  }
}

/* 模型预览对话框 */
.model-preview-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  backdrop-filter: blur(5px);
}

.model-preview-dialog {
  background: #ffffff;
  border-radius: 20px;
  width: 90%;
  max-width: 900px;
  max-height: 90vh;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  animation: dialogSlideIn 0.3s ease-out;
}

@keyframes dialogSlideIn {
  from {
    opacity: 0;
    transform: translateY(-30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 30px;
  border-bottom: 2px solid #f0f0f0;
  background: linear-gradient(135deg, #8b6b46, #d4b88c);
}

.preview-header h3 {
  margin: 0;
  font-size: 1.5rem;
  color: #ffffff;
  font-family: "SimSun", serif;
}

.close-btn {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  color: #ffffff;
  font-size: 24px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: rotate(90deg);
}

.preview-canvas-container {
  width: 100%;
  height: 400px;
  background: #f5f5f5;
  position: relative;
}

.preview-canvas-container canvas {
  width: 100%;
  height: 100%;
  display: block;
}

.preview-info {
  padding: 20px 30px;
  background: #fafafa;
  border-top: 1px solid #f0f0f0;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
}

.info-item:last-child {
  border-bottom: none;
}

.info-item .label {
  font-size: 0.95rem;
  color: #666;
  font-weight: 500;
}

.info-item .value {
  font-size: 1rem;
  color: #8b6b46;
  font-weight: 600;
  font-family: "SimSun", serif;
}

.preview-actions {
  padding: 20px 30px;
  display: flex;
  gap: 15px;
  justify-content: flex-end;
  background: #ffffff;
  border-top: 2px solid #f0f0f0;
}

.preview-action-btn {
  padding: 12px 30px;
  background: linear-gradient(135deg, #8b6b46, #d4b88c);
  color: #ffffff;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  font-family: "SimSun", serif;
  box-shadow: 0 4px 15px rgba(139, 107, 70, 0.3);
}

.preview-action-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(139, 107, 70, 0.4);
}

.preview-action-btn.secondary {
  background: rgba(139, 107, 70, 0.1);
  color: #8b6b46;
  border: 2px solid rgba(139, 107, 70, 0.3);
}

.preview-action-btn.secondary:hover {
  background: rgba(139, 107, 70, 0.2);
  border-color: rgba(139, 107, 70, 0.5);
}

/* 预览按钮样式 */
.preview-btn {
  background: linear-gradient(135deg, #4CAF50, #45a049) !important;
}

.preview-btn:hover {
  background: linear-gradient(135deg, #45a049, #3d8b40) !important;
}
</style>