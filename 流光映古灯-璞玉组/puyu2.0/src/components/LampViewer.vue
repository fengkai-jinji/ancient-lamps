<template>
  <div class="lamp-viewer">
    <!-- 3D 预览容器 -->
    <div class="preview-container">
      <div ref="container" class="viewer-container">
        <canvas ref="canvas" class="viewer-canvas"></canvas>
        
        <!-- 控制按钮 -->
        <div class="viewer-controls">
          <button type="button" @click="resetCamera" class="control-btn" title="重置视角">
            <span>↺</span>
          </button>
          <button type="button" @click="toggleAnimation" class="control-btn" :title="isAnimating ? '停止旋转' : '开始旋转'">
            <span>{{ isAnimating ? '⏸' : '▶' }}</span>
          </button>
          <button type="button" @click="toggleLighting" class="control-btn" :title="isLightingOn ? '关闭灯光' : '开启灯光'">
            <span>{{ isLightingOn ? '💡' : '🌙' }}</span>
          </button>
        </div>
        
        <!-- 操作提示 -->
        <!--  -->
        
        <!-- 加载状态 -->
        <div v-if="isLoading" class="viewer-loading">
          <div class="loading-ring"></div>
          <p>加载古灯模型...</p>
        </div>
      </div>
    </div>
    
    <!-- 模型信息 -->
    <div class="model-info">
      <div class="info-item">
        <label>类型</label>
        <span>传统古灯</span>
      </div>
      <div class="info-item">
        <label>材质</label>
        <span>{{ materialName }}</span>
      </div>
      <div class="info-item">
        <label>尺寸</label>
        <span>{{ settings.size }}x</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import * as THREE from 'three'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls'

// 接收 props
const props = defineProps({
  settings: {
    type: Object,
    default: () => ({
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
  },
  showHint: {
    type: Boolean,
    default: false
  }
})

// 响应式数据
const container = ref(null)
const canvas = ref(null)
const isLoading = ref(true)
const isAnimating = ref(true)
const isLightingOn = ref(true)

// Three.js 相关变量
let scene, camera, renderer, controls, animationFrameId
let lampModel, pointLight, lightSphere, ambientLight, directionalLight

// 计算属性
const materialName = computed(() => {
  const materialMap = {
    ceramic: '陶瓷',
    bronze: '青铜',
    gold: '金色',
    silver: '银色',
    wood: '木质'
  }
  return materialMap[props.settings.material] || props.settings.material
})

// 初始化场景
const initScene = () => {
  if (!container.value || !canvas.value) return
  
  try {
    scene = new THREE.Scene()
    scene.background = new THREE.Color(0x0a0f1c)
    scene.fog = new THREE.FogExp2(0x0a0f1c, 0.015)
    
    const width = container.value.clientWidth
    const height = container.value.clientHeight
    
    camera = new THREE.PerspectiveCamera(50, width / height, 0.1, 1000)
    camera.position.set(4, 2.5, 4)
    camera.lookAt(0, 0, 0)
    
    renderer = new THREE.WebGLRenderer({
      canvas: canvas.value,
      antialias: true,
      alpha: true
    })
    renderer.setSize(width, height)
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
    renderer.shadowMap.enabled = true
    renderer.shadowMap.type = THREE.PCFSoftShadowMap
    renderer.toneMapping = THREE.ACESFilmicToneMapping
    renderer.toneMappingExposure = 1.2
    
    controls = new OrbitControls(camera, renderer.domElement)
    controls.enableDamping = true
    controls.dampingFactor = 0.05
    controls.minDistance = 2
    controls.maxDistance = 12
    controls.maxPolarAngle = Math.PI / 2
    controls.autoRotate = isAnimating.value
    controls.autoRotateSpeed = 1.5
    
    ambientLight = new THREE.AmbientLight(0xffffff, 0.4)
    scene.add(ambientLight)
    
    directionalLight = new THREE.DirectionalLight(0xfff0e0, 1.2)
    directionalLight.position.set(5, 10, 5)
    directionalLight.castShadow = true
    directionalLight.shadow.mapSize.width = 2048
    directionalLight.shadow.mapSize.height = 2048
    directionalLight.shadow.camera.near = 0.5
    directionalLight.shadow.camera.far = 50
    scene.add(directionalLight)
    
    lampModel = createDetailedLamp()
    scene.add(lampModel)
    
    createLampLight()
    createEnvironment()
    
    animate()
    
    setTimeout(() => {
      isLoading.value = false
    }, 800)
    
    setTimeout(() => {
      if (props.showHint) {
        props.showHint = false
      }
    }, 6000)
  } catch (error) {
    console.error('初始化场景失败:', error)
    isLoading.value = false
  }
}

// 创建详细的古灯模型
const createDetailedLamp = () => {
  const group = new THREE.Group()
  
  const { colors, proportions, size } = props.settings
  
  // 底座
  const baseGeometry = new THREE.CylinderGeometry(1.2 * proportions.base, 1.8 * proportions.base, 0.6, 64)
  const baseMaterial = new THREE.MeshStandardMaterial({
    color: new THREE.Color(colors.base),
    metalness: 0.8,
    roughness: 0.2
  })
  const base = new THREE.Mesh(baseGeometry, baseMaterial)
  base.position.y = -1.2
  base.castShadow = true
  base.receiveShadow = true
  base.scale.setScalar(size)
  group.add(base)
  
  // 底座环
  const baseRingGeometry = new THREE.TorusGeometry(1.5 * proportions.base, 0.15, 32, 64)
  const baseRingMaterial = new THREE.MeshStandardMaterial({
    color: new THREE.Color(colors.ring),
    metalness: 0.9,
    roughness: 0.1
  })
  const baseRing = new THREE.Mesh(baseRingGeometry, baseRingMaterial)
  baseRing.position.y = -0.9
  baseRing.rotation.x = Math.PI / 2
  baseRing.castShadow = true
  baseRing.scale.setScalar(size)
  group.add(baseRing)
  
  // 灯身
  const bodyGeometry = new THREE.CylinderGeometry(0.9 * proportions.body, 1.2 * proportions.body, 2.4, 64)
  const bodyMaterial = new THREE.MeshStandardMaterial({
    color: new THREE.Color(colors.body),
    metalness: 0.85,
    roughness: 0.15
  })
  const body = new THREE.Mesh(bodyGeometry, bodyMaterial)
  body.position.y = 0
  body.castShadow = true
  body.receiveShadow = true
  body.scale.setScalar(size)
  group.add(body)
  
  // 装饰环
  for (let i = 0; i < 4; i++) {
    const ringGeometry = new THREE.TorusGeometry(1.05 * proportions.body, 0.08, 32, 64)
    const ringMaterial = new THREE.MeshStandardMaterial({
      color: new THREE.Color(colors.ring),
      metalness: 0.95,
      roughness: 0.05
    })
    const ring = new THREE.Mesh(ringGeometry, ringMaterial)
    ring.position.y = -1.2 + 0.6 * (i + 1)
    ring.rotation.x = Math.PI / 2
    ring.castShadow = true
    ring.scale.setScalar(size)
    group.add(ring)
  }
  
  // 顶部
  const topGeometry = new THREE.CylinderGeometry(0.7 * proportions.top, 0.9 * proportions.top, 0.4, 64)
  const topMaterial = new THREE.MeshStandardMaterial({
    color: new THREE.Color(colors.top),
    metalness: 0.9,
    roughness: 0.1
  })
  const top = new THREE.Mesh(topGeometry, topMaterial)
  top.position.y = 1.5
  top.castShadow = true
  top.receiveShadow = true
  top.scale.setScalar(size)
  group.add(top)
  
  // 顶部装饰
  const topDecorationGeometry = new THREE.SphereGeometry(0.5, 32, 32)
  const topDecorationMaterial = new THREE.MeshStandardMaterial({
    color: 0xFF6347,
    metalness: 0.7,
    roughness: 0.3,
    emissive: 0xFF6347,
    emissiveIntensity: 0.2
  })
  const topDecoration = new THREE.Mesh(topDecorationGeometry, topDecorationMaterial)
  topDecoration.position.y = 1.95
  topDecoration.castShadow = true
  topDecoration.scale.setScalar(size)
  group.add(topDecoration)
  
  return group
}

// 创建灯光
const createLampLight = () => {
  pointLight = new THREE.PointLight(0xFFFF99, 1.5, 8, 2)
  pointLight.position.set(0, 1.2, 0)
  pointLight.castShadow = true
  pointLight.shadow.mapSize.width = 1024
  pointLight.shadow.mapSize.height = 1024
  scene.add(pointLight)
  
  const lightSphereGeometry = new THREE.SphereGeometry(0.15, 32, 32)
  const lightSphereMaterial = new THREE.MeshBasicMaterial({
    color: 0xFFFF99,
    transparent: true,
    opacity: 0.9
  })
  lightSphere = new THREE.Mesh(lightSphereGeometry, lightSphereMaterial)
  lightSphere.position.set(0, 1.2, 0)
  scene.add(lightSphere)
}

// 创建环境
const createEnvironment = () => {
  const groundGeometry = new THREE.PlaneGeometry(30, 30, 1, 1)
  const groundMaterial = new THREE.MeshStandardMaterial({
    color: 0x1a1a2e,
    metalness: 0.1,
    roughness: 0.8
  })
  const ground = new THREE.Mesh(groundGeometry, groundMaterial)
  ground.rotation.x = -Math.PI / 2
  ground.position.y = -1.5
  ground.receiveShadow = true
  scene.add(ground)
  
  const gridHelper = new THREE.GridHelper(30, 30, 0x444444, 0x222222)
  gridHelper.position.y = -1.49
  scene.add(gridHelper)
}

// 动画循环
const animate = () => {
  animationFrameId = requestAnimationFrame(animate)
  
  try {
    if (controls) {
      controls.update()
    }
    
    if (isAnimating.value && lampModel) {
      lampModel.rotation.y += 0.003
    }
    
    if (pointLight && lightSphere && isLightingOn.value) {
      const pulse = 1 + 0.15 * Math.sin(Date.now() * 0.002)
      pointLight.intensity = 1.5 * pulse
      lightSphere.material.opacity = 0.8 + 0.15 * Math.sin(Date.now() * 0.002)
    }
    
    if (renderer && scene && camera) {
      renderer.render(scene, camera)
    }
  } catch (error) {
    console.error('动画循环错误:', error)
  }
}

// 重置相机
const resetCamera = () => {
  if (camera && controls) {
    camera.position.set(4, 2.5, 4)
    camera.lookAt(0, 0, 0)
    controls.reset()
  }
}

// 切换动画
const toggleAnimation = () => {
  isAnimating.value = !isAnimating.value
  if (controls) {
    controls.autoRotate = isAnimating.value
  }
}

// 切换灯光
const toggleLighting = () => {
  isLightingOn.value = !isLightingOn.value
  if (pointLight) {
    pointLight.intensity = isLightingOn.value ? 1.5 : 0
  }
  if (lightSphere) {
    lightSphere.material.opacity = isLightingOn.value ? 0.9 : 0.1
  }
}

// 处理窗口大小变化
const handleResize = () => {
  if (!container.value || !camera || !renderer) return
  
  const width = container.value.clientWidth
  const height = container.value.clientHeight
  
  camera.aspect = width / height
  camera.updateProjectionMatrix()
  
  renderer.setSize(width, height)
}

// 清理资源
const cleanup = () => {
  if (animationFrameId) {
    cancelAnimationFrame(animationFrameId)
  }
  
  if (renderer) {
    renderer.dispose()
  }
  
  if (controls) {
    controls.dispose()
  }
}

// 监听设置变化，更新模型
watch(() => props.settings, () => {
  if (lampModel) {
    scene.remove(lampModel)
    lampModel = createDetailedLamp()
    scene.add(lampModel)
  }
}, { deep: true })

// 生命周期钩子
onMounted(() => {
  setTimeout(() => {
    if (container.value && canvas.value) {
      initScene()
      window.addEventListener('resize', handleResize)
    }
  }, 100)
})

onUnmounted(() => {
  cleanup()
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.lamp-viewer {
  width: 100%;
  height: 100%;
  position: relative;
  background: linear-gradient(135deg, #faf8f5 0%, #f5f0e6 100%);
  border-radius: 12px;
  overflow: hidden;
}

.preview-container {
  width: 100%;
  height: 100%;
  position: relative;
}

.viewer-container {
  width: 100%;
  height: 100%;
  position: relative;
  overflow: hidden;
}

.viewer-canvas {
  width: 100%;
  height: 100%;
  display: block;
}

.viewer-controls {
  position: absolute;
  top: 15px;
  right: 15px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  z-index: 10;
}

.control-btn {
  width: 40px;
  height: 40px;
  background: rgba(139, 107, 70, 0.2);
  border: 1px solid rgba(139, 107, 70, 0.3);
  border-radius: 8px;
  color: #8b6b46;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  backdrop-filter: blur(10px);
}

.control-btn:hover {
  background: rgba(139, 107, 70, 0.4);
  border-color: #8b6b46;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(139, 107, 70, 0.3);
}

.control-btn:active {
  transform: translateY(0);
}

.viewer-hint {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  background: rgba(248, 245, 240, 0.95);
  border: 1px solid rgba(139, 107, 70, 0.3);
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
  backdrop-filter: blur(10px);
  animation: fadeIn 0.5s ease-out;
  z-index: 5;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translate(-50%, -50%) scale(0.9);
  }
  to {
    opacity: 1;
    transform: translate(-50%, -50%) scale(1);
  }
}

.hint-icon {
  font-size: 2rem;
}

.hint-text {
  text-align: center;
  color: #5d4037;
}

.hint-text p {
  margin: 4px 0;
  font-size: 0.9rem;
}

.viewer-loading {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(250, 248, 245, 0.9);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  z-index: 20;
}

.loading-ring {
  width: 60px;
  height: 60px;
  border: 4px solid rgba(139, 107, 70, 0.2);
  border-top: 4px solid #8b6b46;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 15px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.viewer-loading p {
  color: #8b6b46;
  font-size: 1rem;
  font-weight: 600;
}

.model-info {
  position: absolute;
  bottom: 20px;
  left: 20px;
  right: 20px;
  background: rgba(250, 248, 245, 0.8);
/*  border: 1px solid rgba(139, 107, 70, 0.2); */
  border-radius: 8px;
  padding: 12px 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  backdrop-filter: blur(10px);
  animation: fadeInUp 0.5s ease-out;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.info-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.info-item label {
  font-size: 0.8rem;
  color: #8b6b46;
  margin-bottom: 4px;
}

.info-item span {
  font-size: 1rem;
  font-weight: 600;
  color: #5d4037;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .viewer-controls {
    top: 10px;
    right: 10px;
  }
  
  .control-btn {
    width: 36px;
    height: 36px;
    font-size: 1rem;
  }
  
  .viewer-hint {
    padding: 15px;
    width: 80%;
  }
  
  .hint-icon {
    font-size: 1.5rem;
  }
  
  .hint-text p {
    font-size: 0.8rem;
  }
  
  .model-info {
    flex-direction: column;
    gap: 8px;
    padding: 10px;
  }
  
  .info-item {
    flex-direction: row;
    gap: 8px;
  }
}

@media (max-width: 480px) {
  .viewer-controls {
    top: 8px;
    right: 8px;
  }
  
  .control-btn {
    width: 32px;
    height: 32px;
    font-size: 0.9rem;
  }
  
  .model-info {
    bottom: 10px;
    left: 10px;
    right: 10px;
  }
}
</style>