<template>
  <div class="virtual-lamp-container">
    <div ref="loaderRef" id="loader">
      <div id="loader-text" style="color:var(--fire-glow); font-family:'Orbitron', sans-serif; letter-spacing: 6px; font-size: 12px;">
        LOADING HISTORY...
      </div>
    </div>

    <div id="vignette"></div>

    <div class="nav-back-btn" @click="goHome">
      <svg viewBox="0 0 24 24" width="16" height="16" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round">
        <line x1="19" y1="12" x2="5" y2="12"></line>
        <polyline points="12 19 5 12 12 5"></polyline>
      </svg>
      <span>RETURN</span>
    </div>

    <div id="status-bar">
      <div><span style="color:var(--fire-glow)">COLLECTION: HAN DYNASTY</span></div>
      <div><span ref="gestureStateRef" style="color:#666">WAITING</span></div>
    </div>

    <div id="cinema-layer">
      <div id="countdown-container" style="position:relative; display:flex; justify-content:center; align-items:center;">
        <div ref="ringElementRef" class="charge-ring"></div>
        <div ref="countLabelRef" id="countdown-num">-</div>
      </div>
      <div ref="subtitleRef" id="subtitle"></div>
      <div ref="guideHintRef" id="guide-hint">☝️ 食指 · 错银铜牛 | ✌️ 剪刀手 · 长信宫灯</div>
    </div>

    <div ref="danmuContainerRef" id="danmu-container"></div>

    <canvas ref="camPreviewRef" id="cam-preview"></canvas>
    <canvas ref="canvasRef" id="gl-canvas"></canvas>

    <div ref="crosshairRef" id="crosshair">
      <svg width="60" height="60" viewBox="0 0 60 60" class="crosshair-svg">
        <circle class="center-dot" cx="30" cy="30" r="2" fill="white" />
        <circle class="outer-ring" cx="30" cy="30" r="15" fill="none" stroke="white" stroke-width="1" opacity="0.3"/>
      </svg>
    </div>

    <video ref="videoRef" id="webcam" style="display:none;" autoplay playsinline></video>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue';
import { useRouter } from 'vue-router'; 
import * as THREE from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { FilesetResolver, HandLandmarker } from '@mediapipe/tasks-vision';

// --- Router ---
const router = useRouter();
const goHome = () => {
  // 🔥 跳转回 modern index 页面
  // 请确保你的 router 配置中，src/views/modern/index.vue 对应的路径是 '/modern'
  router.push('/modern');
};

// --- Refs (DOM 绑定) ---
const canvasRef = ref(null);
const videoRef = ref(null);
const camPreviewRef = ref(null);
const loaderRef = ref(null);
const gestureStateRef = ref(null);
const ringElementRef = ref(null);
const countLabelRef = ref(null);
const subtitleRef = ref(null);
const guideHintRef = ref(null);
const danmuContainerRef = ref(null);
const crosshairRef = ref(null);

// --- 核心变量 ---
let scene, camera, renderer, particleGroup, geometry;
let handLandmarker = null;
let animationId = null;
let danmuInterval = null;
let visionReady = false;

// --- 配置与状态 ---
const CONFIG = {
  particleCount: 120000,    
  pixelRatio: Math.min(window.devicePixelRatio, 1.5),
  cameraFov: 45,
  modelScale: 5.5,
  modelYOffset: 0.5
};

const STAGE = { INTRO: 0, LAMP1: 1, LAMP2: 2, CHAOS: 3 };

const STATE = {
  currentStage: STAGE.INTRO,
  currentShape: 'AncientEmbers',
  handPos: { x: 0, y: 0 },
  fingerCount: 0,
  stableFingerCount: 0,
  debounceTimer: 0,
  summonTimer: 0,
  time: 0,
  rotationVelocity: { x: 0, y: 0 },
  pinchStart: { x: 0, y: 0 },
  modelLoaded: false
};

// --- 数据资源 ---
const MEMORIES_OX = [
  "错银云纹，璀璨如星", "腹中蓄水，烟火无痕", "汉代黑科技，环保之光",
  "神牛负灯，气吞山河", "扬州广陵，吉金铸史", "精工细作，错彩镂金",
  "两千年前的凝视", "灯火阑珊，牛背流光", "大汉威仪，永恒守望"
];
const MEMORIES_CHANGXIN = [
  "长信宫中，长乐未央", "青铜鎏金，光耀千秋", "虚怀若谷，袖纳烟尘",
  "中华第一灯，举世无双", "宫女执灯，温婉如玉", "以此轮月，照君前行",
  "金辉流转，岁月静好", "见字如面，一眼千年", "唯愿长明，伴君左右"
];
const MEMORIES_INTRO = [
  "唤醒沉睡的文物...", "穿越两千年的光...", 
  "星河滚滚，吉金永存", "伸手，触碰历史的温度"
];

let pointsOx = []; 
let targetPositions, colors, randoms, positions;

// --- 形状逻辑 (Shapes) ---
const Shapes = {
  AncientEmbers: () => {
    const r = Math.sqrt(Math.random()) * 28;
    const theta = Math.random() * Math.PI * 2;
    const y = (Math.random() - 0.5) * 45;
    const noiseX = (Math.random() - 0.5) * 5;
    const noiseZ = (Math.random() - 0.5) * 5;
    return { x: r * Math.cos(theta) + noiseX, y, z: r * Math.sin(theta) + noiseZ };
  },
  ChaosNebula: () => {
    const r = 10 + Math.random() * 8;
    const theta = Math.random() * Math.PI * 2;
    const phi = Math.acos(2 * Math.random() - 1);
    return { x: r * Math.sin(phi) * Math.cos(theta), y: r * Math.sin(phi) * Math.sin(theta), z: r * Math.cos(phi) };
  },
  OxModel: (i) => {
    if (pointsOx.length > 0) {
      const p = pointsOx[i % pointsOx.length];
      return { x: p.x, y: p.y, z: p.z };
    }
    return { x: 0, y: 0, z: 0 };
  },
  ChangxinLamp: (i, count) => {
    const pBody = 0.3, pHead = 0.4, pArm = 0.55, pLamp = 0.80;
    const tGlobal = i / count;
    
    const scale = 1.5;   
    const yOff = -1.7;   

    if (tGlobal < pBody) {
      const t = tGlobal / pBody;
      const h = t * 2.5;
      const r = 0.8 * (1.2 - t * 0.4);
      const theta = Math.random() * Math.PI * 2;
      return { x: r * Math.cos(theta) * scale, y: (h - 1.2 + yOff) * scale, z: r * Math.sin(theta) * scale };
    } else if (tGlobal < pHead) {
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos(2 * Math.random() - 1);
      const r = 0.45;
      return { x: r * Math.sin(phi) * Math.cos(theta) * scale, y: (1.8 + r * Math.sin(phi) * Math.sin(theta) + yOff) * scale, z: r * Math.cos(phi) * scale };
    } else if (tGlobal < pArm) {
      const t = (tGlobal - pHead) / (pArm - pHead);
      const lx = -0.5 + t * 1.5;
      const r = 0.2;
      const theta = Math.random() * Math.PI * 2;
      return { x: (lx + r * Math.cos(theta)) * scale, y: (1.0 + r * Math.sin(theta) + yOff) * scale, z: 0.5 * Math.sin(t * Math.PI) * scale };
    } else if (tGlobal < pLamp) {
      const t = (tGlobal - pArm) / (pLamp - pArm);
      const h = t * 1.8;
      const r = 0.6;
      const theta = Math.random() * Math.PI * 2;
      return { x: (1.2 + r * Math.cos(theta)) * scale, y: (1.2 + h + yOff) * scale, z: r * Math.sin(theta) * scale };
    } else {
      const t = (tGlobal - pLamp) / (1 - pLamp);
      const p0 = { x: 1.2, y: 3.0 }, p1 = { x: 1.0, y: 4.5 }, p2 = { x: 0.0, y: 4.0 }, p3 = { x: 0.0, y: 2.2 };
      const u = 1 - t;
      const bx = u * u * u * p0.x + 3 * u * u * t * p1.x + 3 * u * t * t * p2.x + t * t * t * p3.x;
      const by = u * u * u * p0.y + 3 * u * u * t * p1.y + 3 * u * t * t * p2.y + t * t * t * p3.y;
      const r = 0.25;
      const theta = Math.random() * Math.PI * 2;
      return { x: (bx + r * Math.cos(theta)) * scale, y: (by + r * Math.sin(theta) + yOff) * scale, z: r * Math.sin(theta) * scale };
    }
  }
};

// --- Lifecycle ---

onMounted(() => {
  initThree();
  loadModel();
  setupVision();
  animate();
  
  danmuInterval = setInterval(() => {
    updateSlots(300);
    spawnDanmu();
  }, 400);

  window.addEventListener('resize', onResize);
});

onBeforeUnmount(() => {
  cleanup();
});

// --- Three.js Initialization ---

function initThree() {
  scene = new THREE.Scene();
  scene.fog = new THREE.FogExp2(0x050302, 0.025);

  camera = new THREE.PerspectiveCamera(CONFIG.cameraFov, window.innerWidth / window.innerHeight, 0.1, 100);
  camera.position.set(0, 0, 14);

  renderer = new THREE.WebGLRenderer({
    canvas: canvasRef.value,
    powerPreference: "high-performance",
    antialias: false,
    alpha: false
  });
  renderer.setPixelRatio(CONFIG.pixelRatio);
  renderer.setSize(window.innerWidth, window.innerHeight);

  initParticles();
}

function createParticleTexture() {
  const size = 64;
  const cvs = document.createElement('canvas');
  cvs.width = size;
  cvs.height = size;
  const ctx = cvs.getContext('2d');
  const grad = ctx.createRadialGradient(size / 2, size / 2, 0, size / 2, size / 2, size / 2);
  grad.addColorStop(0, 'rgba(255, 255, 255, 1)');
  grad.addColorStop(0.3, 'rgba(255, 255, 255, 0.6)');
  grad.addColorStop(1, 'rgba(0, 0, 0, 0)');
  ctx.fillStyle = grad;
  ctx.fillRect(0, 0, size, size);
  return new THREE.CanvasTexture(cvs);
}

function initParticles() {
  geometry = new THREE.BufferGeometry();
  positions = new Float32Array(CONFIG.particleCount * 3);
  targetPositions = new Float32Array(CONFIG.particleCount * 3);
  colors = new Float32Array(CONFIG.particleCount * 3);
  randoms = new Float32Array(CONFIG.particleCount);

  for (let i = 0; i < CONFIG.particleCount; i++) {
    const i3 = i * 3;
    const r = Math.random() * 25;
    const theta = Math.random() * Math.PI * 2;
    const y = (Math.random() - 0.5) * 30;
    
    positions[i3] = r * Math.cos(theta);
    positions[i3 + 1] = y;
    positions[i3 + 2] = r * Math.sin(theta);
    
    randoms[i] = Math.random();
  }

  geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
  geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));

  const particlesMesh = new THREE.Points(geometry, new THREE.PointsMaterial({
    size: 0.08,
    map: createParticleTexture(),
    vertexColors: true,
    blending: THREE.AdditiveBlending,
    depthWrite: false,
    transparent: true,
    opacity: 0.9
  }));

  particleGroup = new THREE.Group();
  particleGroup.add(particlesMesh);
  scene.add(particleGroup);
  
  // 初始形状
  setTargetShape('AncientEmbers');
}

// --- Logic Functions ---

function setTargetShape(name) {
  const func = Shapes[name];
  for (let i = 0; i < CONFIG.particleCount; i++) {
    const pos = func(i, CONFIG.particleCount);
    targetPositions[i * 3] = pos.x;
    targetPositions[i * 3 + 1] = pos.y;
    targetPositions[i * 3 + 2] = pos.z;
  }
  STATE.currentShape = name;
}

function loadModel() {
  const loader = new GLTFLoader();
  loader.load('/models/scene.gltf', (gltf) => {
    const meshes = [];
    gltf.scene.traverse((child) => {
      if (child.isMesh) meshes.push(child);
    });
    if (meshes.length === 0) return;

    let totalArea = 0;
    const meshAreas = [];
    
    meshes.forEach(mesh => {
      let area = 0;
      const geo = mesh.geometry.toNonIndexed();
      const pos = geo.attributes.position;
      for (let i = 0; i < pos.count; i += 3) {
        const a = new THREE.Vector3().fromBufferAttribute(pos, i).applyMatrix4(mesh.matrixWorld);
        const b = new THREE.Vector3().fromBufferAttribute(pos, i + 1).applyMatrix4(mesh.matrixWorld);
        const c = new THREE.Vector3().fromBufferAttribute(pos, i + 2).applyMatrix4(mesh.matrixWorld);
        area += new THREE.Vector3().crossVectors(new THREE.Vector3().subVectors(b, a), new THREE.Vector3().subVectors(c, a)).length() * 0.5;
      }
      totalArea += area;
      meshAreas.push({ mesh, area, geo });
    });

    const tempVec = new THREE.Vector3();
    let pIndex = 0;

    meshAreas.forEach(item => {
      const count = Math.floor((item.area / totalArea) * CONFIG.particleCount);
      const pos = item.geo.attributes.position;
      for (let k = 0; k < count && pIndex < CONFIG.particleCount; k++) {
        const triIndex = Math.floor(Math.random() * (pos.count / 3)) * 3;
        const a = new THREE.Vector3().fromBufferAttribute(pos, triIndex).applyMatrix4(item.mesh.matrixWorld);
        const b = new THREE.Vector3().fromBufferAttribute(pos, triIndex + 1).applyMatrix4(item.mesh.matrixWorld);
        const c = new THREE.Vector3().fromBufferAttribute(pos, triIndex + 2).applyMatrix4(item.mesh.matrixWorld);
        
        let r1 = Math.random(), r2 = Math.random();
        if (r1 + r2 > 1) { r1 = 1 - r1; r2 = 1 - r2; }
        
        tempVec.set(0, 0, 0).addScaledVector(a, r1).addScaledVector(b, r2).addScaledVector(c, 1 - r1 - r2);
        pointsOx.push({ x: tempVec.x, y: tempVec.y, z: tempVec.z });
        pIndex++;
      }
    });

    while (pointsOx.length < CONFIG.particleCount && pointsOx.length > 0) {
        pointsOx.push(pointsOx[Math.floor(Math.random() * pointsOx.length)]);
    }

    // Centering and Scaling
    let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity, minZ = Infinity, maxZ = -Infinity;
    pointsOx.forEach(p => {
      if (p.x < minX) minX = p.x; if (p.x > maxX) maxX = p.x;
      if (p.y < minY) minY = p.y; if (p.y > maxY) maxY = p.y;
      if (p.z < minZ) minZ = p.z; if (p.z > maxZ) maxZ = p.z;
    });

    const cx = (minX + maxX) / 2, cy = (minY + maxY) / 2, cz = (minZ + maxZ) / 2;
    const scale = CONFIG.modelScale / Math.max(maxX - minX, maxY - minY, maxZ - minZ);
    
    pointsOx.forEach(p => {
      p.x = (p.x - cx) * scale;
      p.y = (p.y - cy) * scale + CONFIG.modelYOffset;
      p.z = (p.z - cz) * scale;
    });

    STATE.modelLoaded = true;
    checkLoadingComplete();

  }, undefined, (err) => {
    console.error(err);
    if(loaderRef.value) loaderRef.value.textContent = "ERROR: LOAD FAILED";
  });
}

// --- Danmu (Floating Text) ---
const SLOTS_COUNT = 15;
const leftSlots = new Array(SLOTS_COUNT).fill(0);
const rightSlots = new Array(SLOTS_COUNT).fill(0);

function updateSlots(dt) {
  for (let i = 0; i < SLOTS_COUNT; i++) {
    if (leftSlots[i] > 0) leftSlots[i] -= dt;
    if (rightSlots[i] > 0) rightSlots[i] -= dt;
  }
}

function spawnDanmu() {
  let sourceArray = [];
  if (STATE.currentStage === STAGE.LAMP1) sourceArray = MEMORIES_OX;
  else if (STATE.currentStage === STAGE.LAMP2) sourceArray = MEMORIES_CHANGXIN;
  else if (STATE.currentStage === STAGE.INTRO) sourceArray = MEMORIES_INTRO;
  else return;

  const isLeft = Math.random() > 0.5;
  const slots = isLeft ? leftSlots : rightSlots;
  const validIndices = [];
  for (let i = 2; i < SLOTS_COUNT - 3; i++) {
    if (slots[i] <= 0) validIndices.push(i);
  }
  if (validIndices.length === 0) return;

  const slotIndex = validIndices[Math.floor(Math.random() * validIndices.length)];
  slots[slotIndex] = 5500;

  const text = document.createElement('div');
  text.className = 'memory-text';
  text.textContent = sourceArray[Math.floor(Math.random() * sourceArray.length)];

  const xPos = isLeft ? (5 + Math.random() * 20) : (75 + Math.random() * 20);
  const yPos = (slotIndex / SLOTS_COUNT) * 100 + (Math.random() - 0.5) * 4;

  text.style.left = xPos + '%';
  text.style.top = yPos + '%';
  const depth = Math.random();
  text.style.fontSize = (13 + depth * 10) + 'px';
  text.style.filter = `blur(${(1 - depth) * 1.5}px)`;
  text.style.zIndex = Math.floor(depth * 50);

  const duration = 15 + (1 - depth) * 10;
  text.style.animationDuration = duration + 's';
  text.style.animationName = 'deepDrift';

  if(danmuContainerRef.value) {
    danmuContainerRef.value.appendChild(text);
    setTimeout(() => {
      if (text.parentNode) text.remove();
    }, duration * 1000);
  }
}

// --- UI Logic ---
function updateUI() {
  if(!countLabelRef.value) return;

  countLabelRef.value.style.opacity = 0;
  ringElementRef.value.classList.remove('active');
  subtitleRef.value.className = '';
  subtitleRef.value.textContent = '';

  if (STATE.currentStage === STAGE.INTRO) {
    guideHintRef.value.style.opacity = 1;
    guideHintRef.value.textContent = "☝️ 食指 · 错银铜牛 | ✌️ 剪刀手 · 长信宫灯";
  } else if (STATE.currentStage === STAGE.LAMP1) {
    subtitleRef.value.textContent = "【错银铜牛灯】";
    subtitleRef.value.classList.add('visible');
    guideHintRef.value.style.opacity = 0;
  } else if (STATE.currentStage === STAGE.LAMP2) {
    subtitleRef.value.textContent = "【长信宫灯】";
    subtitleRef.value.classList.add('visible');
    guideHintRef.value.style.opacity = 0;
  } else if (STATE.currentStage === STAGE.CHAOS) {
    subtitleRef.value.classList.remove('visible');
    guideHintRef.value.textContent = "🖐️ 五指张开 · 散作星尘";
    guideHintRef.value.style.opacity = 1;
  }
}

// --- Vision / MediaPipe ---

function checkLoadingComplete() {
  if (STATE.modelLoaded && visionReady) {
    if(loaderRef.value) {
        loaderRef.value.style.opacity = 0;
        setTimeout(() => loaderRef.value.style.display = 'none', 500);
    }
    predict();
  }
}

async function setupVision() {
    try {
      const vision = await FilesetResolver.forVisionTasks("/wasm");
    handLandmarker = await HandLandmarker.createFromOptions(vision, {
      baseOptions: {
        modelAssetPath: `https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task`,
        delegate: "GPU"
      },
      runningMode: "VIDEO",
      numHands: 1
    });

    const stream = await navigator.mediaDevices.getUserMedia({ video: { width: 320, height: 240 } });
    if(videoRef.value) {
        videoRef.value.srcObject = stream;
        videoRef.value.addEventListener("loadeddata", () => {
        visionReady = true;
        checkLoadingComplete();
        });
    }
  } catch (err) {
    console.error(err);
    // 即使模型加载失败，也让页面正常显示
    visionReady = true;
    checkLoadingComplete();
    if(loaderRef.value) loaderRef.value.innerHTML = `提示: 手势识别功能不可用，可能是网络问题`;
    setTimeout(() => {
      if(loaderRef.value) {
        loaderRef.value.style.opacity = 0;
        setTimeout(() => loaderRef.value.style.display = 'none', 500);
      }
    }, 2000);
  }
}

function countFingers(lm) {
  const wrist = lm[0];
  let count = 0;
  [[8, 6], [12, 10], [16, 14], [20, 18]].forEach(indices => {
    const tip = lm[indices[0]];
    const pip = lm[indices[1]];
    if (Math.hypot(tip.x - wrist.x, tip.y - wrist.y) > Math.hypot(pip.x - wrist.x, pip.y - wrist.y) * 1.02) count++;
  });
  const thumbTip = lm[4];
  const pinkyMCP = lm[17];
  const thumbIP = lm[3];
  if (Math.hypot(thumbTip.x - pinkyMCP.x, thumbTip.y - pinkyMCP.y) > Math.hypot(thumbIP.x - pinkyMCP.x, thumbIP.y - pinkyMCP.y) * 1.05) count++;
  return count;
}

let lastVideoTime = -1;

function predict() {
  if (!handLandmarker || !videoRef.value || !camPreviewRef.value) return;

  if (lastVideoTime !== videoRef.value.currentTime) {
    lastVideoTime = videoRef.value.currentTime;
    const ctx = camPreviewRef.value.getContext('2d');
    ctx.drawImage(videoRef.value, 0, 0, 300, 150);
    
    const res = handLandmarker.detectForVideo(videoRef.value, performance.now());

    if (res.landmarks.length > 0) {
      const lm = res.landmarks[0];
      const cx = (lm[5].x + lm[9].x) / 2, cy = (lm[5].y + lm[9].y) / 2;
      STATE.handPos.x = (1 - cx) * window.innerWidth;
      STATE.handPos.y = cy * window.innerHeight;

      if(crosshairRef.value) {
          crosshairRef.value.style.left = STATE.handPos.x + 'px';
          crosshairRef.value.style.top = STATE.handPos.y + 'px';
          crosshairRef.value.style.opacity = 1;
      }

      const fingers = countFingers(lm);
      if (fingers === STATE.fingerCount) {
        STATE.debounceTimer++;
        if (STATE.debounceTimer > 5) STATE.stableFingerCount = fingers;
      } else {
        STATE.fingerCount = fingers;
        STATE.debounceTimer = 0;
      }

      let targetStage = null;

      if (STATE.currentStage === STAGE.INTRO || STATE.currentStage === STAGE.CHAOS) {
        if (STATE.stableFingerCount === 1) {
          targetStage = STAGE.LAMP1;
          if(countLabelRef.value) countLabelRef.value.textContent = "1";
          if(ringElementRef.value) ringElementRef.value.className = 'charge-ring active';
        } else if (STATE.stableFingerCount === 2) {
          targetStage = STAGE.LAMP2;
          if(countLabelRef.value) countLabelRef.value.textContent = "2";
          if(ringElementRef.value) ringElementRef.value.className = 'charge-ring type-2 active';
        }
      } else {
        if (STATE.stableFingerCount === 5) {
          STATE.summonTimer = 0;
          STATE.currentStage = STAGE.CHAOS;
          setTargetShape('AncientEmbers');
          updateUI();
        }
      }

      if (targetStage !== null) {
        if(countLabelRef.value) countLabelRef.value.style.opacity = 1;
        STATE.summonTimer += 0.03;
        if (STATE.summonTimer > 1.2) {
          STATE.currentStage = targetStage;
          if (targetStage === STAGE.LAMP1) setTargetShape('OxModel');
          else setTargetShape('ChangxinLamp');
          
          particleGroup.rotation.set(0, 0, 0);
          STATE.rotationVelocity = { x: 0, y: 0 };
          updateUI();
          STATE.summonTimer = 0;
        }
      } else {
        if (STATE.currentStage === STAGE.INTRO || STATE.currentStage === STAGE.CHAOS) {
          STATE.summonTimer = 0;
          if(ringElementRef.value) ringElementRef.value.classList.remove('active');
          if(countLabelRef.value) countLabelRef.value.style.opacity = 0;
        }
      }

      if (STATE.currentStage === STAGE.LAMP1 || STATE.currentStage === STAGE.LAMP2) {
        const pinch = Math.hypot(lm[4].x - lm[8].x, lm[4].y - lm[8].y, lm[4].z - lm[8].z);
        if (pinch < 0.08) {
          const sensitivity = 0.0008;
          STATE.rotationVelocity.x += (STATE.handPos.y - STATE.pinchStart.y) * sensitivity;
          STATE.rotationVelocity.y += (STATE.handPos.x - STATE.pinchStart.x) * sensitivity;
          STATE.pinchStart = { ...STATE.handPos };
        } else {
          STATE.pinchStart = { ...STATE.handPos };
        }
      }

      if(gestureStateRef.value) gestureStateRef.value.textContent = `MODE: ${STATE.currentStage} | FINGERS: ${STATE.stableFingerCount}`;
    } else {
      if(crosshairRef.value) crosshairRef.value.style.opacity = 0;
      STATE.summonTimer = 0;
      if(ringElementRef.value) ringElementRef.value.classList.remove('active');
      if(countLabelRef.value) countLabelRef.value.style.opacity = 0;
    }
  }
  animationId = requestAnimationFrame(predict);
}

const clock = new THREE.Clock();

function animate() {
    requestAnimationFrame(animate);

    if(!scene || !camera || !renderer || !geometry) return;

    const delta = clock.getDelta();
    STATE.time += delta;

    camera.position.x += (Math.sin(STATE.time * 0.5) * 0.3 - camera.position.x) * 0.05;
    camera.position.y += (Math.cos(STATE.time * 0.3) * 0.2 - camera.position.y) * 0.05;
    camera.lookAt(0, 0, 0);

    if (STATE.summonTimer > 0 && (STATE.currentStage === STAGE.INTRO || STATE.currentStage === STAGE.CHAOS)) {
        particleGroup.rotation.y += 0.05;
        particleGroup.rotation.z += 0.02;
    } else if (STATE.currentStage === STAGE.LAMP1 || STATE.currentStage === STAGE.LAMP2) {
        STATE.rotationVelocity.x *= 0.92;
        STATE.rotationVelocity.y *= 0.92;
        particleGroup.rotation.x += STATE.rotationVelocity.x;
        particleGroup.rotation.y += STATE.rotationVelocity.y;
    } else {
        particleGroup.rotation.y += 0.002;
    }

    const posAttr = geometry.attributes.position;
    const colAttr = geometry.attributes.color;

    for (let i = 0; i < CONFIG.particleCount; i++) {
        const i3 = i * 3;
        let tx = targetPositions[i3], ty = targetPositions[i3 + 1], tz = targetPositions[i3 + 2];

        if (STATE.summonTimer > 0 && (STATE.currentStage === STAGE.INTRO || STATE.currentStage === STAGE.CHAOS)) {
            const shake = STATE.summonTimer * 0.05;
            posAttr.array[i3] += (Math.random() - 0.5) * shake;
            posAttr.array[i3 + 1] += (Math.random() - 0.5) * shake;
            posAttr.array[i3 + 2] += (Math.random() - 0.5) * shake;
        } else if (STATE.currentStage === STAGE.LAMP1 || STATE.currentStage === STAGE.LAMP2) {
            const dx = tx - posAttr.array[i3], dy = ty - posAttr.array[i3 + 1], dz = tz - posAttr.array[i3 + 2];
            const breathe = Math.sin(STATE.time * 2 + randoms[i] * 6.28) * 0.01;
            posAttr.array[i3] += dx * 0.1 + breathe;
            posAttr.array[i3 + 1] += dy * 0.1 + breathe;
            posAttr.array[i3 + 2] += dz * 0.1 + breathe;

            let r, g, b;
            const py = posAttr.array[i3 + 1];

            if (STATE.currentStage === STAGE.LAMP1) {
                // 铜牛颜色
                r = 0.25; g = 0.35; b = 0.30;
                if (randoms[i] > 0.6) { r = 0.1; g = 0.45; b = 0.35; }
                if (randoms[i] > 0.92) {
                    const shine = Math.sin(STATE.time * 3 + i) * 0.2;
                    r = 0.9 + shine; g = 0.9 + shine; b = 0.95 + shine;
                }
            } else {
                // 长信宫灯颜色
                r = 0.45; g = 0.40; b = 0.25;
                if (randoms[i] > 0.65) { r = 0.2; g = 0.25; b = 0.2; }
                if (randoms[i] > 0.88) {
                    const shine = Math.sin(STATE.time * 4 + i) * 0.3;
                    r = 0.2 + shine; g = 0.9 + shine; b = 0.8 + shine;
                }
            }

            // 火苗效果
            if (py > 2.0 && py < 4.0 && Math.random() > 0.96 && Math.abs(posAttr.array[i3]) < 1.0) {
                const flicker = Math.sin(STATE.time * 20);
                r = 1.0; g = 0.5 + flicker * 0.1; b = 0.05;
            }
            colAttr.array[i3] = r;
            colAttr.array[i3 + 1] = g;
            colAttr.array[i3 + 2] = b;
        } else {
            // 散开状态
            posAttr.array[i3] += (tx - posAttr.array[i3]) * 0.015;
            posAttr.array[i3 + 1] += (ty - posAttr.array[i3 + 1]) * 0.015;
            posAttr.array[i3 + 2] += (tz - posAttr.array[i3 + 2]) * 0.015;

            posAttr.array[i3 + 1] += 0.008 + randoms[i] * 0.01;
            if (posAttr.array[i3 + 1] > 20) posAttr.array[i3 + 1] = -20;

            const pulse = Math.sin(STATE.time * 1.5 + randoms[i] * 5);
            const brightness = 0.6 + pulse * 0.4;
            colAttr.array[i3] = 1.0 * brightness;
            colAttr.array[i3 + 1] = 0.5 * brightness;
            colAttr.array[i3 + 2] = 0.1 * brightness;
        }
    }
    posAttr.needsUpdate = true;
    colAttr.needsUpdate = true;
    renderer.render(scene, camera);
}

function onResize() {
  if (camera && renderer) {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
  }
}

function cleanup() {
  window.removeEventListener('resize', onResize);
  if (animationId) cancelAnimationFrame(animationId);
  if (danmuInterval) clearInterval(danmuInterval);
  
  if (videoRef.value && videoRef.value.srcObject) {
    const tracks = videoRef.value.srcObject.getTracks();
    tracks.forEach(track => track.stop());
  }

  if (renderer) renderer.dispose();
  if (geometry) geometry.dispose();
  if (handLandmarker) handLandmarker.close();
}
</script>

<style>
/* 全局样式引入字体 */
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;900&family=Noto+Serif+SC:wght@300;500;700&display=swap');

:root {
  --bronze-main: #4a5d50;
  --fire-glow: #ff9d00;
  --jade-cyan: #2affd6;
}

.virtual-lamp-container {
  position: relative;
  width: 100vw;
  height: 100vh;
  margin: 0;
  overflow: hidden;
  background-color: #020305;
  font-family: 'Noto Serif SC', serif;
  color: white;
  user-select: none;
}

/* 🔙 右上角返回按钮 */
.nav-back-btn {
  position: absolute;
  top: 0;
  right: 0; /* Changed to right */
  left: auto;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 30px;
  cursor: pointer;
  z-index: 100;
  color: rgba(255, 255, 255, 0.6);
  font-family: 'Orbitron', sans-serif;
  font-size: 12px;
  letter-spacing: 2px;
  transition: all 0.3s ease;
  /* 调整背景渐变方向和边框位置 */
  background: linear-gradient(-90deg, rgba(0,0,0,0.8) 0%, rgba(0,0,0,0) 100%);
  border-left: 1px solid rgba(255, 255, 255, 0.05);
  border-right: none;
}

.nav-back-btn svg {
  margin-right: 8px;
  transition: transform 0.3s ease;
}

.nav-back-btn:hover {
  color: var(--fire-glow);
  background: linear-gradient(-90deg, rgba(255, 157, 0, 0.1) 0%, rgba(0,0,0,0) 100%);
  border-left: 1px solid rgba(255, 157, 0, 0.3);
  text-shadow: 0 0 10px rgba(255, 157, 0, 0.5);
}

.nav-back-btn:hover svg {
  transform: translateX(-4px);
  stroke: var(--fire-glow);
}

.nav-back-btn:active {
  transform: scale(0.98);
}

#gl-canvas { position: absolute; top: 0; left: 0; z-index: 1; }

#vignette {
  position: absolute; top: 0; left: 0; width: 100%; height: 100%;
  background: radial-gradient(circle at center, transparent 20%, rgba(0,0,0,0.6) 60%, #000000 100%);
  z-index: 5; pointer-events: none; mix-blend-mode: multiply;
}

#status-bar {
  position: absolute; top: 0; left: 0; width: 100%; height: 60px;
  display: flex; justify-content: space-between; align-items: center;
  /* 🔥 修改 Padding: 翻转左右内边距 */
  padding: 0 160px 0 40px; 
  box-sizing: border-box; z-index: 50;
  font-family: 'Orbitron', sans-serif; font-size: 12px; pointer-events: none;
  letter-spacing: 2px; color: rgba(255,255,255,0.3);
  border-bottom: 1px solid rgba(255,255,255,0.05);
}

#cinema-layer {
  position: absolute; top: 0; left: 0; width: 100%; height: 100%;
  display: flex; flex-direction: column; justify-content: center; align-items: center;
  z-index: 40; pointer-events: none;
}

#countdown-num {
  font-family: 'Orbitron', sans-serif; font-size: 260px; font-weight: 100;
  color: rgba(255,255,255,0.9); text-shadow: 0 0 100px var(--bronze-main);
  letter-spacing: 20px; transition: opacity 0.2s; opacity: 0; mix-blend-mode: screen;
}

#subtitle {
  position: absolute; bottom: 10%; 
  font-family: 'Noto Serif SC', serif; font-size: 36px; font-weight: 700;
  color: #dcdcdc;
  letter-spacing: 12px; text-align: center;
  opacity: 0; transform: translateY(20px);
  transition: all 1.2s cubic-bezier(0.19, 1, 0.22, 1);
  z-index: 60; width: 100%;
  text-shadow: 0 0 30px rgba(255, 160, 50, 0.4);
}
#subtitle.visible { opacity: 1; transform: translateY(0); }

#danmu-container {
  position: absolute; top: 0; left: 0; width: 100%; height: 100%;
  pointer-events: none; overflow: hidden; z-index: 20; 
}

.memory-text {
  position: absolute; font-family: 'Noto Serif SC', serif;
  color: rgba(240, 240, 230, 0.95); font-weight: 500; white-space: nowrap;
  opacity: 0; border-left: 2px solid rgba(200, 160, 80, 0.6); padding-left: 12px;
  text-shadow: 0 2px 5px rgba(0,0,0,0.8); letter-spacing: 2px;
  mix-blend-mode: normal; will-change: transform, opacity, filter;
}

@keyframes deepDrift {
  0% { opacity: 0; transform: translateY(40px) translateX(0); filter: blur(6px); }
  15% { opacity: 1; transform: translateY(0) translateX(5px); filter: blur(0px); }
  85% { opacity: 0.8; transform: translateY(-20px) translateX(10px); filter: blur(1px); }
  100% { opacity: 0; transform: translateY(-50px) translateX(15px); filter: blur(10px); }
}

#guide-hint {
  position: absolute; bottom: 4%; font-family: 'Noto Serif SC', serif;
  font-size: 14px; color: rgba(255,255,255,0.4); letter-spacing: 6px;
  text-transform: uppercase; transition: opacity 0.5s;
}

#cam-preview {
  position: absolute; bottom: 20px; right: 20px; width: 120px; height: 90px;
  background: #000; border: 1px solid rgba(255,255,255,0.1); opacity: 0.2; 
  z-index: 10; transform: scaleX(-1); border-radius: 2px;
}

#crosshair {
  position: absolute; top: 50%; left: 50%; width: 40px; height: 40px;
  transform: translate(-50%, -50%); pointer-events: none; z-index: 30;
  transition: opacity 0.3s; opacity: 0;
}
.crosshair-svg circle { transition: all 0.3s; }

#loader {
  position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: #000;
  display: flex; flex-direction: column; justify-content: center; align-items: center; z-index: 999;
  transition: opacity 0.5s;
}

.charge-ring {
  position: absolute; width: 350px; height: 350px;
  border: 1px solid rgba(255,255,255,0.02);
  border-top: 2px solid var(--fire-glow);
  border-bottom: 2px solid rgba(255,255,255,0.5);
  border-radius: 50%; opacity: 0; visibility: hidden; 
  transition: opacity 0.2s;
}
.charge-ring.type-2 {
  border-top: 2px solid var(--jade-cyan);
  border-bottom: 2px solid rgba(255,255,255,0.8);
  box-shadow: 0 0 30px rgba(42, 255, 214, 0.2);
}
.charge-ring.active { visibility: visible; opacity: 1; animation: spin 1.2s cubic-bezier(0.4, 0, 0.2, 1) infinite; }
@keyframes spin { 100% { transform: rotate(360deg); } }
</style>