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
            <button type="button" @click="goToDesignPrint" class="action-btn primary">
              <span class="btn-icon">✏️</span>
              <span class="btn-text">设计此灯</span>
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
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader'

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
    // scene.fog = new THREE.FogExp2(0x0a0f1c, 0.015)
    
    const width = container.value.clientWidth
    const height = container.value.clientHeight
    
    camera = new THREE.PerspectiveCamera(50, width / height, 0.1, 1000)
    camera.position.set(2.5, 2, 2.5)
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
    renderer.toneMappingExposure = 2.0
    
    controls = new OrbitControls(camera, renderer.domElement)
    controls.enableDamping = true
    controls.dampingFactor = 0.05
    controls.minDistance = 1
    controls.maxDistance = 8
    controls.maxPolarAngle = Math.PI / 2
    controls.autoRotate = isAnimating.value
    controls.autoRotateSpeed = 1.5
    controls.target.set(0, 0, 0)  // 设置旋转中心为原点
    
    ambientLight = new THREE.AmbientLight(0xffffff, 2.0)
    scene.add(ambientLight)
    
    directionalLight = new THREE.DirectionalLight(0xffffff, 4.0)
    directionalLight.position.set(5, 10, 5)
    directionalLight.castShadow = true
    directionalLight.shadow.mapSize.width = 2048
    directionalLight.shadow.mapSize.height = 2048
    directionalLight.shadow.camera.near = 0.5
    directionalLight.shadow.camera.far = 50
    scene.add(directionalLight)
    
    const fillLight = new THREE.DirectionalLight(0xffffff, 1.5)
    fillLight.position.set(-3, 5, -3)
    scene.add(fillLight)
    
    createLampLight()
    createEnvironment()
    
    // 加载真实的西汉长信宫灯GLTF模型（异步加载）
    loadRealLampModel()
    
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

// 加载西汉长信宫灯GLTF模型
const loadRealLampModel = () => {
  const loader = new GLTFLoader()
  const modelPath = '/models/西汉长信宫灯.gltf'
  
  loader.load(
    modelPath,
    (gltf) => {
      const group = gltf.scene
      
      // ===== 确保模型居中于(0,0,0) =====
      const box = new THREE.Box3().setFromObject(group)
      const center = new THREE.Vector3()
      box.getCenter(center)
      
      group.traverse((child) => {
        if (child !== group && child.position) {
          child.position.sub(center)
        }
      })
      
      // 验证居中结果
      const newBox = new THREE.Box3().setFromObject(group)
      const newCenter = new THREE.Vector3()
      newBox.getCenter(newCenter)
      console.log('长信宫灯模型中心:', newCenter)
      
      // 调整模型整体大小
      group.scale.set(5, 5, 5)
      
      lampModel = group
      scene.add(group)
      isLoading.value = false
      
      // 在灯腔位置添加内部光源（模拟灯火效果）
      addLampInternalLight(group)
      
      console.log('✅ 西汉长信宫灯GLTF模型加载成功，已居中于(0,0,0)')
    },
    (xhr) => {
      console.log(`模型加载进度: ${(xhr.loaded / xhr.total) * 100}%`)
    },
    (error) => {
      console.error('❌ GLTF模型加载失败:', error)
      console.log('使用程序生成的五灯连枝灯模型')
      lampModel = createFiveBranchLamp()
      scene.add(lampModel)
      isLoading.value = false
    }
  )
}

// 在灯腔内部添加光源（模拟灯火从内部发光）
const addLampInternalLight = (group) => {
  // 创建一个点光源放在灯腔内部
  const internalLight = new THREE.PointLight(0xFFFF99, 15, 15, 1)
  internalLight.position.set(-0.3, 1.6, 0.1)
  internalLight.castShadow = true
  internalLight.shadow.mapSize.width = 1024
  internalLight.shadow.mapSize.height = 1024
  internalLight.name = 'internalLampLight'
  group.add(internalLight)
  
  // 添加小火焰效果
  const flameGeom = new THREE.SphereGeometry(0.15, 16, 16)
  const flameMat = new THREE.MeshBasicMaterial({ color: 0xFFFF99, transparent: true, opacity: 0.9 })
  const flame = new THREE.Mesh(flameGeom, flameMat)
  flame.position.set(-0.3, 1.8, 0.1)
  flame.name = 'flame'
  group.add(flame)
  
  console.log('✅ 已在灯腔内部添加光源')
}

// 在灯的位置添加灯火效果
const createFlameEffect = (group) => {
  // 火焰核心（白色）
  const flameCoreGeom = new THREE.SphereGeometry(0.06, 16, 16)
  const flameCoreMat = new THREE.MeshBasicMaterial({ color: 0xFFFFFF, transparent: true, opacity: 0.95 })
  const flameCore = new THREE.Mesh(flameCoreGeom, flameCoreMat)
  flameCore.position.set(0.35, 0.55, 0.35)
  flameCore.name = 'flameCore'
  group.add(flameCore)
  
  // 火焰内层（黄色）
  const flameInnerGeom = new THREE.ConeGeometry(0.05, 0.15, 12)
  const flameInnerMat = new THREE.MeshBasicMaterial({ color: 0xFFFF99, transparent: true, opacity: 0.9 })
  const flameInner = new THREE.Mesh(flameInnerGeom, flameInnerMat)
  flameInner.position.set(0.35, 0.52, 0.35)
  flameInner.name = 'flameInner'
  group.add(flameInner)
  
  // 火焰中层（橙色）
  const flameMidGeom = new THREE.ConeGeometry(0.07, 0.18, 12)
  const flameMidMat = new THREE.MeshBasicMaterial({ color: 0xFFAA33, transparent: true, opacity: 0.75 })
  const flameMid = new THREE.Mesh(flameMidGeom, flameMidMat)
  flameMid.position.set(0.35, 0.48, 0.35)
  flameMid.name = 'flameMid'
  group.add(flameMid)
  
  // 火焰外层（红色）
  const flameOuterGeom = new THREE.ConeGeometry(0.09, 0.22, 12)
  const flameOuterMat = new THREE.MeshBasicMaterial({ color: 0xFF6633, transparent: true, opacity: 0.5 })
  const flameOuter = new THREE.Mesh(flameOuterGeom, flameOuterMat)
  flameOuter.position.set(0.35, 0.45, 0.35)
  flameOuter.name = 'flameOuter'
  group.add(flameOuter)
  
  // 点光源（灯火）
  const flameLight = new THREE.PointLight(0xFFBB44, 2.5, 6, 2)
  flameLight.position.set(0.35, 0.5, 0.35)
  flameLight.castShadow = true
  flameLight.name = 'flameLight'
  group.add(flameLight)
  
  // 发光球体
  const flameSphereGeom = new THREE.SphereGeometry(0.05, 12, 12)
  const flameSphereMat = new THREE.MeshBasicMaterial({ color: 0xFFFFCC, transparent: true, opacity: 0.9 })
  const flameSphere = new THREE.Mesh(flameSphereGeom, flameSphereMat)
  flameSphere.position.set(0.35, 0.52, 0.35)
  flameSphere.name = 'flameSphere'
  group.add(flameSphere)
  
  // 光晕效果
  const glowGeom = new THREE.SphereGeometry(0.4, 16, 16)
  const glowMat = new THREE.MeshBasicMaterial({
    color: 0xFF8822,
    transparent: true,
    opacity: 0.12,
    side: THREE.BackSide
  })
  const glow = new THREE.Mesh(glowGeom, glowMat)
  glow.position.set(0.35, 0.45, 0.35)
  glow.name = 'hoodGlow'
  group.add(glow)
}

// 创建汉代五灯连枝灯模型（历史依据：河北满城汉墓出土的青铜连枝灯）
// 五灯连枝灯是汉代常见的灯具形式，具有明确的考古发现依据
const createFiveBranchLamp = () => {
  const group = new THREE.Group()
  
  // 青铜材质
  const bronzeMaterial = new THREE.MeshStandardMaterial({
    color: 0xCD7F32, // 青铜色
    metalness: 0.85,
    roughness: 0.25
  })
  
  const goldMaterial = new THREE.MeshStandardMaterial({
    color: 0xFFD700, // 金色
    metalness: 0.9,
    roughness: 0.1
  })
  
  // ===== 底座 =====
  // 三足底座（汉代典型样式）
  const baseGeometry = new THREE.CylinderGeometry(1.8, 2.2, 0.25, 64)
  const base = new THREE.Mesh(baseGeometry, bronzeMaterial)
  base.position.y = -2.1
  base.castShadow = true
  base.receiveShadow = true
  group.add(base)
  
  // 三足
  for (let i = 0; i < 3; i++) {
    const legGeometry = new THREE.CylinderGeometry(0.15, 0.2, 0.5, 32)
    const leg = new THREE.Mesh(legGeometry, bronzeMaterial)
    const angle = (i * 2 * Math.PI) / 3
    leg.position.set(
      Math.cos(angle) * 0.9,
      -2.45,
      Math.sin(angle) * 0.9
    )
    leg.castShadow = true
    group.add(leg)
  }
  
  // ===== 主干 =====
  const trunkGeometry = new THREE.CylinderGeometry(0.25, 0.35, 2.5, 32)
  const trunk = new THREE.Mesh(trunkGeometry, bronzeMaterial)
  trunk.position.y = -0.75
  trunk.castShadow = true
  trunk.receiveShadow = true
  group.add(trunk)
  
  // 主干装饰环
  for (let i = 0; i < 3; i++) {
    const ringGeometry = new THREE.TorusGeometry(0.4, 0.06, 16, 32)
    const ring = new THREE.Mesh(ringGeometry, goldMaterial)
    ring.position.y = -1.8 + i * 1
    ring.rotation.x = Math.PI / 2
    ring.castShadow = true
    group.add(ring)
  }
  
  // ===== 主灯盏（顶部）=====
  // 灯盏托盘
  const mainTrayGeometry = new THREE.CylinderGeometry(0.5, 0.7, 0.15, 32)
  const mainTray = new THREE.Mesh(mainTrayGeometry, bronzeMaterial)
  mainTray.position.y = 0.9
  mainTray.castShadow = true
  group.add(mainTray)
  
  // 灯盏边缘
  const mainRimGeometry = new THREE.TorusGeometry(0.65, 0.08, 16, 32)
  const mainRim = new THREE.Mesh(mainRimGeometry, goldMaterial)
  mainRim.position.y = 1
  mainRim.rotation.x = Math.PI / 2
  mainRim.castShadow = true
  group.add(mainRim)
  
  // ===== 四个分支灯盏 =====
  const branchAngles = [0, Math.PI/2, Math.PI, 3*Math.PI/2] // 四个方向
  
  branchAngles.forEach((angle, index) => {
    // 分支臂
    const branchGeometry = new THREE.CylinderGeometry(0.08, 0.12, 1.2, 16)
    const branch = new THREE.Mesh(branchGeometry, bronzeMaterial)
    branch.position.set(
      Math.cos(angle) * 0.8,
      0.2,
      Math.sin(angle) * 0.8
    )
    branch.rotation.y = angle
    branch.rotation.z = Math.PI / 6 * (index % 2 === 0 ? 1 : -1)
    branch.castShadow = true
    group.add(branch)
    
    // 分支灯盏托盘
    const trayGeometry = new THREE.CylinderGeometry(0.35, 0.5, 0.12, 32)
    const tray = new THREE.Mesh(trayGeometry, bronzeMaterial)
    tray.position.set(
      Math.cos(angle) * 1.5,
      0.6,
      Math.sin(angle) * 1.5
    )
    tray.castShadow = true
    group.add(tray)
    
    // 分支灯盏边缘
    const rimGeometry = new THREE.TorusGeometry(0.45, 0.06, 16, 32)
    const rim = new THREE.Mesh(rimGeometry, goldMaterial)
    rim.position.set(
      Math.cos(angle) * 1.5,
      0.7,
      Math.sin(angle) * 1.5
    )
    rim.rotation.x = Math.PI / 2
    rim.castShadow = true
    group.add(rim)
    
    // 为每个分支灯盏添加火焰效果
    createSingleFlame(group, Math.cos(angle) * 1.5, 0.85, Math.sin(angle) * 1.5, `flame_${index}`)
  })
  
  // 为主灯盏添加火焰效果
  createSingleFlame(group, 0, 1.2, 0, 'flame_main')
  
  // 验证居中
  const box = new THREE.Box3().setFromObject(group)
  const center = new THREE.Vector3()
  box.getCenter(center)
  console.log('五灯连枝灯模型中心:', center)
  
  return group
}

// 创建单个火焰效果
const createSingleFlame = (group, x, y, z, namePrefix) => {
  // 火焰核心（白色）
  const flameCoreGeom = new THREE.SphereGeometry(0.05, 12, 12)
  const flameCoreMat = new THREE.MeshBasicMaterial({ color: 0xFFFFFF, transparent: true, opacity: 0.95 })
  const flameCore = new THREE.Mesh(flameCoreGeom, flameCoreMat)
  flameCore.position.set(x, y, z)
  flameCore.name = `${namePrefix}_core`
  group.add(flameCore)
  
  // 火焰内层（黄色）
  const flameInnerGeom = new THREE.ConeGeometry(0.04, 0.12, 10)
  const flameInnerMat = new THREE.MeshBasicMaterial({ color: 0xFFFF99, transparent: true, opacity: 0.9 })
  const flameInner = new THREE.Mesh(flameInnerGeom, flameInnerMat)
  flameInner.position.set(x, y - 0.02, z)
  flameInner.name = `${namePrefix}_inner`
  group.add(flameInner)
  
  // 火焰中层（橙色）
  const flameMidGeom = new THREE.ConeGeometry(0.06, 0.15, 10)
  const flameMidMat = new THREE.MeshBasicMaterial({ color: 0xFFAA33, transparent: true, opacity: 0.75 })
  const flameMid = new THREE.Mesh(flameMidGeom, flameMidMat)
  flameMid.position.set(x, y - 0.05, z)
  flameMid.name = `${namePrefix}_mid`
  group.add(flameMid)
  
  // 火焰外层（红色）
  const flameOuterGeom = new THREE.ConeGeometry(0.08, 0.18, 10)
  const flameOuterMat = new THREE.MeshBasicMaterial({ color: 0xFF6633, transparent: true, opacity: 0.5 })
  const flameOuter = new THREE.Mesh(flameOuterGeom, flameOuterMat)
  flameOuter.position.set(x, y - 0.08, z)
  flameOuter.name = `${namePrefix}_outer`
  group.add(flameOuter)
  
  // 点光源
  const flameLight = new THREE.PointLight(0xFFBB44, 2, 4, 2)
  flameLight.position.set(x, y - 0.03, z)
  flameLight.name = `${namePrefix}_light`
  group.add(flameLight)
  
  // 光晕效果
  const glowGeom = new THREE.SphereGeometry(0.3, 12, 12)
  const glowMat = new THREE.MeshBasicMaterial({
    color: 0xFF8822,
    transparent: true,
    opacity: 0.1,
    side: THREE.BackSide
  })
  const glow = new THREE.Mesh(glowGeom, glowMat)
  glow.position.set(x, y - 0.05, z)
  glow.name = `${namePrefix}_glow`
  group.add(glow)
}

const createFallbackLamp = (group) => {
  return createFiveBranchLamp()
}

// 添加发光光晕效果
const addLampGlow = (group) => {
  const glowGeometry = new THREE.SphereGeometry(0.4, 16, 16)
  const glowMaterial = new THREE.MeshBasicMaterial({
    color: 0xFF6600,
    transparent: true,
    opacity: 0.2
  })
  const glow = new THREE.Mesh(glowGeometry, glowMaterial)
  glow.position.set(0, 0.5, 0)
  group.add(glow)
  
  const glowGeometry2 = new THREE.SphereGeometry(0.6, 16, 16)
  const glowMaterial2 = new THREE.MeshBasicMaterial({
    color: 0xFF4400,
    transparent: true,
    opacity: 0.08
  })
  const glow2 = new THREE.Mesh(glowGeometry2, glowMaterial2)
  glow2.position.set(0, 0.5, 0)
  group.add(glow2)
}

const createLampLight = () => {
  pointLight = new THREE.PointLight(0xFF8833, 2.5, 10, 2)
  pointLight.position.set(0, 0.5, 0)
  pointLight.castShadow = true
  pointLight.shadow.mapSize.width = 1024
  pointLight.shadow.mapSize.height = 1024
  scene.add(pointLight)
  
  const lightSphereGeometry = new THREE.SphereGeometry(0.25, 32, 32)
  const lightSphereMaterial = new THREE.MeshBasicMaterial({
    color: 0xFF8833,
    transparent: true,
    opacity: 0.9
  })
  lightSphere = new THREE.Mesh(lightSphereGeometry, lightSphereMaterial)
  lightSphere.position.set(0, 0.5, 0)
  scene.add(lightSphere)
}

const animateFlame = () => {
  if (!lampModel) return
  
  const time = Date.now() * 0.003
  
  lampModel.traverse((child) => {
    // 支持多个火焰动画（主火焰和四个分支火焰）
    if (child.name.includes('_core')) {
      const offset = parseInt(child.name.split('_')[1]) || 0
      child.scale.setScalar(1 + 0.15 * Math.sin(time * 2.5 + offset * 0.3))
      child.material.opacity = 0.9 + 0.1 * Math.sin(time * 3 + offset * 0.2)
    }
    if (child.name.includes('_inner')) {
      const offset = parseInt(child.name.split('_')[1]) || 0
      child.scale.set(
        1 + 0.1 * Math.sin(time * 2.3 + offset * 0.3), 
        1 + 0.15 * Math.sin(time * 2 + 0.5 + offset * 0.3), 
        1 + 0.1 * Math.sin(time * 2.3 + offset * 0.3)
      )
      child.material.opacity = 0.85 + 0.1 * Math.sin(time * 2.8 + offset * 0.2)
    }
    if (child.name.includes('_outer')) {
      const offset = parseInt(child.name.split('_')[1]) || 0
      child.scale.set(
        1 + 0.1 * Math.sin(time * 2 + offset * 0.3), 
        1 + 0.2 * Math.sin(time * 1.8 + 0.5 + offset * 0.3), 
        1 + 0.1 * Math.sin(time * 2.5 + offset * 0.3)
      )
      child.rotation.z = 0.1 * Math.sin(time * 2 + offset * 0.3)
    }
    if (child.name.includes('_mid')) {
      const offset = parseInt(child.name.split('_')[1]) || 0
      child.scale.set(
        1 + 0.12 * Math.sin(time * 2.2 + 1 + offset * 0.3), 
        1 + 0.18 * Math.sin(time * 2 + 0.3 + offset * 0.3), 
        1 + 0.12 * Math.sin(time * 2.2 + 1 + offset * 0.3)
      )
    }
    if (child.name.includes('_light')) {
      const offset = parseInt(child.name.split('_')[1]) || 0
      child.intensity = 2 + 0.6 * Math.sin(time * 2.3 + offset * 0.4)
    }
    if (child.name.includes('_glow')) {
      const offset = parseInt(child.name.split('_')[1]) || 0
      child.scale.setScalar(1 + 0.2 * Math.sin(time * 1.8 + offset * 0.3))
      child.material.opacity = 0.08 + 0.04 * Math.sin(time * 2.1 + offset * 0.2)
    }
  })
  
  requestAnimationFrame(animateFlame)
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
    
    animateFlame()
    
    if (pointLight && lightSphere && isLightingOn.value) {
      const pulse = 1 + 0.3 * Math.sin(Date.now() * 0.003)
      pointLight.intensity = 2.5 * pulse
      lightSphere.material.opacity = 0.6 + 0.3 * Math.sin(Date.now() * 0.003)
      lightSphere.scale.setScalar(1 + 0.15 * Math.sin(Date.now() * 0.003))
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
    camera.position.set(2.5, 2, 2.5)
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