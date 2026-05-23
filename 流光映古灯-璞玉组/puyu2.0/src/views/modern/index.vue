<template>
  <div class="modern-container">
    <div class="ambient-lighting"></div>
    <div class="floating-particles">
      <div v-for="i in 30" :key="'particle-' + i" class="particle" :style="{ '--i': i, '--delay': i * 0.2 }"></div>
    </div>
    
    <main class="modern-main" v-if="$route.path === '/modern'">
      <section class="hero-section">
        <div class="hero-content">
          <h1 class="hero-title">
            <span class="title-line">现代互动</span>
          </h1>
          
          <p class="hero-description">
            融合千年古灯文化与现代智能科技，通过AI对话了解历史，
            用3D打印重现传统工艺，打造专属您的古灯艺术品。
          </p>
          
          <div class="hero-actions">
            <button type="button" @click="goToAIChat" class="action-btn primary">
              <span class="btn-icon">🤖</span>
              <span class="btn-text">AI对话</span>
              <span class="btn-arrow">→</span>
            </button>
            <button type="button" @click="goToVirtualLampAnimation" class="action-btn secondary">
              <span class="btn-icon">🏮</span>
              <span class="btn-text">虚拟古灯</span>
              <span class="btn-arrow">→</span>
            </button>
          </div>
        </div>
        
        <div class="hero-visual">
          <div class="visual-container">
            <div class="visual-card">
              <div class="visual-header">
                <div class="header-info">
                  <h3>古灯3D预览</h3>
                  <p>拖动旋转 · 滚轮缩放 · 右键平移</p>
                </div>
                <div class="header-controls">
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
              </div>
              
              <div class="visual-body">
                <div class="lamp-viewer">
                  <div ref="container" class="viewer-container">
                    <canvas ref="canvas" class="viewer-canvas"></canvas>
                    
                    <!-- <div v-if="showHint" class="viewer-hint">
                      <div class="hint-icon">🖱️</div>
                      <div class="hint-text">
                        <p>点击并拖动旋转视角</p>
                        <p>滚轮缩放 · 右键平移</p>
                      </div>
                    </div> -->
                    
                    <div v-if="isLoading" class="viewer-loading">
                      <div class="loading-ring"></div>
                      <p>加载古灯模型...</p>
                    </div>
                  </div>
                </div>
              </div>
              
              <div class="visual-footer">
                <div class="lamp-info">
                  <div class="info-item">
                    <span class="info-label">类型</span>
                    <span class="info-value">传统古灯</span>
                  </div>
                  <div class="info-item">
                    <span class="info-label">材质</span>
                    <span class="info-value">青铜合金</span>
                  </div>
                  <div class="info-item">
                    <span class="info-label">年代</span>
                    <span class="info-value">汉代风格</span>
                  </div>
                </div>
                <button type="button" @click="goToDesignPrint" class="design-btn">
                  <span class="btn-icon">✏️</span>
                  <span class="btn-text">设计此灯</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </section>
    </main>
    
    <router-view v-slot="{ Component }">
      <transition name="page-transition" mode="out-in">
        <component :is="Component" />
      </transition>
    </router-view>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import * as THREE from 'three'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls'

const router = useRouter()
const route = useRoute()

const goToDesignPrint = () => router.push('/modern/design-print')
const goToAIChat = () => router.push('/modern/ai-chat')
const goToVirtualLampAnimation = () => router.push('/modern/virtual-lamp-animation')

const container = ref(null)
const canvas = ref(null)
const showHint = ref(true)
const isLoading = ref(true)
const isAnimating = ref(true)
const isLightingOn = ref(true)

let scene, camera, renderer, controls, animationFrameId
let lampModel, pointLight, lightSphere, ambientLight, directionalLight

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
      showHint.value = false
    }, 6000)
  } catch (error) {
    console.error('初始化场景失败:', error)
    isLoading.value = false
  }
}

const createDetailedLamp = () => {
  const group = new THREE.Group()
  
  const baseGeometry = new THREE.CylinderGeometry(1.2, 1.8, 0.6, 64)
  const baseMaterial = new THREE.MeshStandardMaterial({
    color: 0x8B4513,
    metalness: 0.8,
    roughness: 0.2
  })
  const base = new THREE.Mesh(baseGeometry, baseMaterial)
  base.position.y = -1.2
  base.castShadow = true
  base.receiveShadow = true
  group.add(base)
  
  const baseRingGeometry = new THREE.TorusGeometry(1.5, 0.15, 32, 64)
  const baseRingMaterial = new THREE.MeshStandardMaterial({
    color: 0xDAA520,
    metalness: 0.9,
    roughness: 0.1
  })
  const baseRing = new THREE.Mesh(baseRingGeometry, baseRingMaterial)
  baseRing.position.y = -0.9
  baseRing.rotation.x = Math.PI / 2
  baseRing.castShadow = true
  group.add(baseRing)
  
  const bodyGeometry = new THREE.CylinderGeometry(0.9, 1.2, 2.4, 64)
  const bodyMaterial = new THREE.MeshStandardMaterial({
    color: 0xDAA520,
    metalness: 0.85,
    roughness: 0.15
  })
  const body = new THREE.Mesh(bodyGeometry, bodyMaterial)
  body.position.y = 0
  body.castShadow = true
  body.receiveShadow = true
  group.add(body)
  
  for (let i = 0; i < 4; i++) {
    const ringGeometry = new THREE.TorusGeometry(1.05, 0.08, 32, 64)
    const ringMaterial = new THREE.MeshStandardMaterial({
      color: 0xFFD700,
      metalness: 0.95,
      roughness: 0.05
    })
    const ring = new THREE.Mesh(ringGeometry, ringMaterial)
    ring.position.y = -1.2 + 0.6 * (i + 1)
    ring.rotation.x = Math.PI / 2
    ring.castShadow = true
    group.add(ring)
  }
  
  const topGeometry = new THREE.CylinderGeometry(0.7, 0.9, 0.4, 64)
  const topMaterial = new THREE.MeshStandardMaterial({
    color: 0xFFD700,
    metalness: 0.9,
    roughness: 0.1
  })
  const top = new THREE.Mesh(topGeometry, topMaterial)
  top.position.y = 1.5
  top.castShadow = true
  top.receiveShadow = true
  group.add(top)
  
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
  group.add(topDecoration)
  
  return group
}

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

const resetCamera = () => {
  if (camera && controls) {
    camera.position.set(4, 2.5, 4)
    camera.lookAt(0, 0, 0)
    controls.reset()
  }
}

const toggleAnimation = () => {
  isAnimating.value = !isAnimating.value
  if (controls) {
    controls.autoRotate = isAnimating.value
  }
}

const toggleLighting = () => {
  isLightingOn.value = !isLightingOn.value
  if (pointLight) {
    pointLight.intensity = isLightingOn.value ? 1.5 : 0
  }
  if (lightSphere) {
    lightSphere.material.opacity = isLightingOn.value ? 0.9 : 0.1
  }
}

const handleResize = () => {
  if (!container.value || !camera || !renderer) return
  
  const width = container.value.clientWidth
  const height = container.value.clientHeight
  
  camera.aspect = width / height
  camera.updateProjectionMatrix()
  
  renderer.setSize(width, height)
}

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

watch(() => route.path, (newPath) => {
  if (!newPath.startsWith('/modern')) {
    cleanup()
  }
})

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
.modern-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #f8f5f0 0%, #e8e0d5 100%);
  color: #5d4037;
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;
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

.modern-main {
  flex: 1;
  position: relative;
  z-index: 10;
}

.hero-section {
  max-width: 1600px;
  margin: 0 auto;
  padding: 80px 40px;
  display: grid;
  grid-template-columns: 1fr 1.2fr;
  gap: 80px;
  align-items: center;
}

.hero-content {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.hero-badges {
  display: flex;
  gap: 16px;
}

.hero-badge {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 20px;
  background: rgba(139, 107, 70, 0.2);
  border: 1px solid rgba(139, 107, 70, 0.3);
  border-radius: 20px;
  font-size: 0.9rem;
  color: #8b6b46;
  animation: badgePulse 3s ease-in-out infinite;
  font-family: "SimSun", serif;
  box-shadow: 0 2px 8px rgba(139, 107, 70, 0.2);
}

.badge-icon {
  font-size: 1.1rem;
}

@keyframes badgePulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
}

.hero-title {
  font-size: 3rem;
  font-weight: 700;
  line-height: 1.1;
  display: flex;
  flex-direction: column;
  gap: 8px;
  font-family: "Ma Shan Zheng", cursive;
}

.title-line {
  background: linear-gradient(135deg, #8b6b46 0%, #d4b88c 50%, #8b6b46 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  background-size: 200% auto;
  animation: titleGradient 3s linear infinite;
  text-shadow: 0 0 20px rgba(139, 107, 70, 0.5);
  letter-spacing: 2px;
}

@keyframes titleGradient {
  0% { background-position: 0% center; }
  100% { background-position: 200% center; }
}

.hero-description {
  font-size: 1.2rem;
  color: #5d4037;
  line-height: 1.8;
  background: rgba(139, 107, 70, 0.03);
  padding: 24px;
  border-radius: 16px;
  border-left: 4px solid #8b6b46;
  backdrop-filter: blur(10px);
}

.hero-features {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.feature-card {
  background: rgba(139, 107, 70, 0.1);
  border: 1px solid rgba(139, 107, 70, 0.2);
  border-radius: 16px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  transition: all 0.3s ease;
  cursor: pointer;
  font-family: "SimSun", serif;
}

.feature-card:hover {
  background: rgba(139, 107, 70, 0.2);
  border-color: rgba(139, 107, 70, 0.4);
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(139, 107, 70, 0.15);
}

.feature-icon-wrapper {
  width: 48px;
  height: 48px;
  background: rgba(139, 107, 70, 0.2);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 8px rgba(139, 107, 70, 0.2);
}

.feature-icon {
  font-size: 1.8rem;
  color: #8b6b46;
  text-shadow: 0 0 10px rgba(139, 107, 70, 0.5);
}

.feature-content h3 {
  font-size: 1.1rem;
  font-weight: 600;
  color: #8b6b46;
  margin: 0;
  text-shadow: 0 0 10px rgba(139, 107, 70, 0.5);
}

.feature-content p {
  font-size: 0.9rem;
  color: #5d4037;
  margin: 0;
  font-family: "SimSun", serif;
}

.hero-actions {
  display: flex;
  gap: 16px;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 32px;
  border-radius: 14px;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
  font-family: "SimSun", serif;
  border: none;
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
  box-shadow: 0 8px 24px rgba(139, 107, 70, 0.3);
}

.action-btn.primary {
  background: linear-gradient(135deg, #8b6b46, #d4b88c);
  color: white;
}

.action-btn.secondary {
  background: rgba(139, 107, 70, 0.1);
  border: 2px solid rgba(139, 107, 70, 0.3);
  color: #8b6b46;
}

.action-btn.secondary:hover {
  background: rgba(139, 107, 70, 0.2);
  border-color: rgba(139, 107, 70, 0.5);
}

.btn-icon {
  font-size: 1.3rem;
}

.btn-text {
  font-weight: 600;
}

.btn-arrow {
  transition: transform 0.3s ease;
}

.action-btn:hover .btn-arrow {
  transform: translateX(4px);
}

.hero-visual {
  position: relative;
}

.visual-container {
  position: relative;
  width: 100%;
  height: 100%;
}

.visual-card {
  background: rgba(139, 107, 70, 0.1);
  border: 1px solid rgba(139, 107, 70, 0.2);
  border-radius: 24px;
  overflow: hidden;
  box-shadow: 0 24px 48px rgba(139, 107, 70, 0.2);
  backdrop-filter: blur(20px);
  animation: cardFloat 8s ease-in-out infinite;
}

@keyframes cardFloat {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-12px); }
}

.visual-header {
  background: rgba(139, 107, 70, 0.15);
  border-bottom: 1px solid rgba(139, 107, 70, 0.2);
  padding: 20px 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-info h3 {
  margin: 0 0 4px;
  font-size: 1.2rem;
  font-weight: 600;
  color: #8b6b46;
  font-family: "SimSun", serif;
}

.header-info p {
  margin: 0;
  font-size: 0.9rem;
  color: #8b6b46;
  opacity: 0.8;
  font-family: "SimSun", serif;
}

.header-controls {
  display: flex;
  gap: 8px;
}

.control-btn {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: rgba(139, 107, 70, 0.1);
  border: 1px solid rgba(139, 107, 70, 0.2);
  color: #8b6b46;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  font-family: "SimSun", serif;
}

.control-btn:hover {
  background: rgba(139, 107, 70, 0.2);
  border-color: rgba(139, 107, 70, 0.4);
  transform: scale(1.1);
}

.visual-body {
  position: relative;
  height: 500px;
  background: linear-gradient(180deg, rgba(10, 15, 28, 0.9) 0%, rgba(10, 15, 28, 0.7) 100%);
}

.lamp-viewer {
  width: 100%;
  height: 100%;
  position: relative;
}

.viewer-container {
  width: 100%;
  height: 100%;
  position: relative;
}

.viewer-canvas {
  width: 100%;
  height: 100%;
  display: block;
}

.viewer-hint {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: rgba(139, 107, 70, 0.9);
  color: white;
  padding: 24px 32px;
  border-radius: 16px;
  text-align: center;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translate(-50%, -50%) scale(0.9); }
  to { opacity: 1; transform: translate(-50%, -50%) scale(1); }
}

.hint-icon {
  font-size: 2.5rem;
  margin-bottom: 12px;
}

.hint-text p {
  margin: 4px 0;
  font-size: 1rem;
  font-family: "SimSun", serif;
}

.viewer-loading {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
  color: white;
}

.loading-ring {
  width: 60px;
  height: 60px;
  border: 4px solid rgba(139, 107, 70, 0.3);
  border-top: 4px solid #8b6b46;
  border-radius: 50%;
  margin: 0 auto 16px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.viewer-loading p {
  font-size: 1rem;
  font-family: "SimSun", serif;
  margin: 0;
}

.visual-footer {
  background: rgba(139, 107, 70, 0.15);
  border-top: 1px solid rgba(139, 107, 70, 0.2);
  padding: 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.lamp-info {
  display: flex;
  gap: 24px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.info-label {
  font-size: 0.85rem;
  color: #5d4037;
  font-weight: 600;
  font-family: "SimSun", serif;
}

.info-value {
  font-size: 1rem;
  color: #5d4037;
  font-weight: 700;
  font-family: "SimSun", serif;
}

.design-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  background: linear-gradient(135deg, #8b6b46, #d4b88c);
  border: none;
  border-radius: 12px;
  color: white;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  font-family: "SimSun", serif;
  box-shadow: 0 4px 12px rgba(139, 107, 70, 0.3);
}

.design-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(139, 107, 70, 0.4);
  background: linear-gradient(135deg, #9a7b56, #e3c9a1);
}

.design-btn .btn-icon {
  font-size: 1.1rem;
}

.page-transition-enter-active,
.page-transition-leave-active {
  transition: all 0.3s ease;
}

.page-transition-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

.page-transition-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}

@media (max-width: 1200px) {
  .hero-section {
    grid-template-columns: 1fr;
    gap: 60px;
  }
  
  .hero-content {
    text-align: center;
  }
  
  .hero-actions {
    justify-content: center;
  }
  
  .visual-card {
    max-width: 600px;
    margin: 0 auto;
  }
}

@media (max-width: 768px) {
  .hero-section {
    padding: 40px 20px;
  }
  
  .hero-title {
    font-size: 2.5rem;
  }
  
  .hero-description {
    font-size: 1rem;
    padding: 16px;
  }
  
  .hero-actions {
    flex-direction: column;
  }
  
  .action-btn {
    width: 100%;
    justify-content: center;
  }
  
  .visual-body {
    height: 400px;
  }
  
  .lamp-info {
    flex-direction: column;
    gap: 12px;
  }
  
  .visual-footer {
    flex-direction: column;
    gap: 16px;
  }
}

@media (max-width: 480px) {
  .hero-title {
    font-size: 2rem;
  }
  
  .visual-body {
    height: 300px;
  }
}
</style>