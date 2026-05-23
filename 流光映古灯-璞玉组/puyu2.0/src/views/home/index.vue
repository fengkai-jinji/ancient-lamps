<template>
	<div id="app">
		<div class="main-content">
			<canvas ref="particleCanvas" class="particle-background"></canvas>

			<header>
				<div class="title-container">
					<h1 class="main-title">流光映古灯</h1>
					<button class="title-button" id="title-button" @click="openKnowledgeGraph">
						<i class="fas fa-search"></i> 探索知识图谱
					</button>
				</div>
				<p class="subtitle">循光溯源·与古为新</p>
			</header>

			<div class="hexagon-container">
				<div class="hexagon-track" id="hexagon-track" ref="hexagonTrack">
				</div>
			</div>

			<div class="knowledge-graph" id="knowledge-graph" ref="knowledgeGraph">
				<div class="graph-container">
					<div class="graph-header">
						<h2 class="graph-title">灯具脉络图</h2>
						<button class="close-btn" id="close-graph" @click="closeKnowledgeGraph">×</button>
					</div>

					<div class="echarts-container">
						<Echarts />
					</div>

				</div>
			</div>

			<footer>
				<p>流光映古灯数字文物展示系统</p>
				<div class="footer-links">
					<a href="#"> 承古灯之韵</a>
					<a href="#">映今世之华</a>
					<a href="#">「流光映古灯」/匠心呈现 - 璞玉组 |</a>
				</div>
			</footer>
		</div>
	</div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue';
import Echarts from '@/components/echarts.vue';
import axios from 'axios';

const HEXAGON_CONFIG = {
  rows: 3,
  cols: 12,
  particleCount: 80
};

const particleCanvas = ref(null);
const hexagonTrack = ref(null);
const knowledgeGraph = ref(null);
const animationFrameId = ref(null);
const resizeHandler = ref(null);
const hexagonData = ref([]);

// 从后端获取图片路径
const getImageUrl = (imagePath) => {
  if (!imagePath) return '';
  if (typeof imagePath === 'string') {
    if (imagePath.startsWith('/static/')) {
      return `http://localhost:5000${imagePath}`;
    } else {
      return `http://localhost:5000/static/images/${imagePath}`;
    }
  }
  return imagePath;
};

// 从后端获取首页灯具数据
const fetchHomeData = async () => {
  try {
    const res = await axios.get('http://localhost:5000/api/home');
    hexagonData.value = res.data.map(item => ({
      ...item,
      image: getImageUrl(item.image)
    }));
  } catch (error) {
    // 静默处理错误，避免控制台日志影响性能
  }
};

// 【恢复打乱数组功能】保留原有的随机打乱逻辑
const shuffleArray = (array) => {
  const newArray = [...array];
  for (let i = newArray.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [newArray[i], newArray[j]] = [newArray[j], newArray[i]];
  }
  return newArray;
};

class Particle {
  constructor(canvasWidth, canvasHeight) {
    this.x = Math.random() * canvasWidth;
    this.y = Math.random() * canvasHeight;
    this.vx = (Math.random() - 0.5) * 0.8;
    this.vy = (Math.random() - 0.5) * 0.5 - 0.8;
    this.size = Math.random() * 3 + 1;
    this.opacity = Math.random() * 0.5 + 0.3;
    this.fadeSpeed = Math.random() * 0.005 + 0.002;
    this.color = `218, 165, 32`;
  }

  update(canvasWidth, canvasHeight) {
    this.x += this.vx;
    this.y += this.vy;
    this.opacity -= this.fadeSpeed;

    if (this.y < -10 || this.opacity <= 0) {
      this.x = Math.random() * canvasWidth;
      this.y = canvasHeight + 10;
      this.opacity = Math.random() * 0.5 + 0.4;
      this.vy = (Math.random() - 0.5) * 0.5 - 0.8;
    }

    if (this.x < -10) this.x = canvasWidth + 10;
    if (this.x > canvasWidth + 10) this.x = -10;
  }

  draw(ctx) {
    ctx.beginPath();
    ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
    const gradient = ctx.createRadialGradient(
      this.x, this.y, 0,
      this.x, this.y, this.size * 2.5
    );
    gradient.addColorStop(0, `rgba(${this.color}, ${this.opacity})`);
    gradient.addColorStop(1, `rgba(${this.color}, 0)`);
    ctx.fillStyle = gradient;
    ctx.fill();
  }
}

const initParticles = () => {
  try {
    const canvas = particleCanvas.value;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    let canvasWidth, canvasHeight;
    let particles = [];

    const resizeCanvas = () => {
      try {
        if (canvas) {
          canvasWidth = canvas.width = window.innerWidth;
          canvasHeight = canvas.height = window.innerHeight;
        }
      } catch (error) {
        console.warn('Error resizing canvas:', error);
      }
    };

    resizeHandler.value = resizeCanvas;
    window.addEventListener('resize', resizeHandler.value);
    resizeCanvas();

    for (let i = 0; i < HEXAGON_CONFIG.particleCount; i++) {
      particles.push(new Particle(canvasWidth, canvasHeight));
    }

    const animateParticles = () => {
      try {
        if (ctx && canvasWidth && canvasHeight) {
          ctx.clearRect(0, 0, canvasWidth, canvasHeight);
          particles.forEach(p => {
            p.update(canvasWidth, canvasHeight);
            p.draw(ctx);
          });
          animationFrameId.value = requestAnimationFrame(animateParticles);
        }
      } catch (error) {
        console.warn('Error animating particles:', error);
      }
    };
    animateParticles();
  } catch (error) {
    console.warn('Error initializing particles:', error);
  }
};

const openKnowledgeGraph = () => {
  try {
    if (knowledgeGraph.value) {
      knowledgeGraph.value.style.display = 'flex';
      // 延迟触发 resize，确保 ECharts 容器已经完全渲染
      setTimeout(() => {
        nextTick(() => {
          try {
            window.dispatchEvent(new Event('resize'));
          } catch (error) {
            console.warn('Error dispatching resize event:', error);
          }
        });
      }, 100);
    }
  } catch (error) {
    console.warn('Error opening knowledge graph:', error);
  }
};

const closeKnowledgeGraph = () => {
  try {
    if (knowledgeGraph.value) {
      knowledgeGraph.value.style.display = 'none';
    }
  } catch (error) {
    console.warn('Error closing knowledge graph:', error);
  }
};

const createHexagon = (data) => {
  const hex = document.createElement('div');
  hex.className = 'hexagon';
  const inner = document.createElement('div');
  inner.className = 'hexagon-inner';
  const front = document.createElement('div');
  front.className = 'hexagon-front';
  const img = document.createElement('img');
  img.src = data.image;
  img.alt = data.title;
  img.onerror = function() {
    this.src = 'http://localhost:5000/static/images/logo.jpg';
  };
  const back = document.createElement('div');
  back.className = 'hexagon-back';

  if (!data.blank) {
    const title = document.createElement('div');
    title.className = 'hexagon-title';
    title.textContent = data.title;
    back.appendChild(title);
  }

  front.appendChild(img);
  inner.appendChild(front);
  inner.appendChild(back);
  hex.appendChild(inner);
  return hex;
};

// 【核心修复】恢复每行图片打乱 + 水平无缝滚动
const initializeHexagons = () => {
  const track = hexagonTrack.value;
  if (!track) return;

  // 清空现有内容
  track.innerHTML = '';

  // 每行都单独打乱，保持随机性
  for (let row = 0; row < HEXAGON_CONFIG.rows; row++) {
    const rowEl = document.createElement('div');
    rowEl.className = 'hexagon-row';
    
    // 【关键】每行都重新打乱数组，恢复原有随机效果
    const shuffledHexagons = shuffleArray(hexagonData.value);
    // 拼接多份，保证无缝滚动不空白
    const longList = [...shuffledHexagons, ...shuffledHexagons, ...shuffledHexagons];

    // 按列数创建（也可以用longList的长度，保证足够长）
    for (let col = 0; col < longList.length; col++) {
      const hex = createHexagon(longList[col]);
      rowEl.appendChild(hex);
    }

    track.appendChild(rowEl);
  }
};

const pageLoadAnimation = () => {
  document.body.style.opacity = 0;
  document.body.style.transition = 'opacity 0.5s ease';
  setTimeout(() => {
    document.body.style.opacity = 1;
  }, 100);
};

onMounted(async () => {
  await fetchHomeData();
  initializeHexagons();
  pageLoadAnimation();
  nextTick(() => initParticles());
});

onUnmounted(() => {
  if (animationFrameId.value) cancelAnimationFrame(animationFrameId.value);
  if (resizeHandler.value) window.removeEventListener('resize', resizeHandler.value);
});
</script>

<style>
.particle-background {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
  background: transparent;
}

header,
.hexagon-container,
.knowledge-graph,
footer {
  position: relative;
  z-index: 1;
}

.main-content {
  width: 100%;
  padding: 20px 0;
  background: #f8f5f0;
  display: flex;
  flex-direction: column;
  align-items: center;
  min-height: 100vh;
  position: relative;
}

header {
  text-align: center;
  padding: 15px 0;
  margin-bottom: 15px;
  width: 100%;
}

.title-container {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 20px;
  margin-bottom: 10px;
  white-space: nowrap;
}

.main-title {
  font-size: 3rem;
  color: #5d4037;
  letter-spacing: 3px;
  font-family: "Ma Shan Zheng", cursive;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
  margin: 0;
}

.title-button {
  background: linear-gradient(135deg, #8b6b46, #d4b88c);
  color: white;
  border: none;
  padding: 8px 18px;
  border-radius: 30px;
  cursor: pointer;
  font-family: "Ma Shan Zheng", cursive;
  font-size: 0.9rem;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15);
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
}

.title-button:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2);
  background: linear-gradient(135deg, #9a7b56, #e3c9a1);
}

.subtitle {
  font-size: 1.3rem;
  color: #8b6b46;
  max-width: 700px;
  margin: 0 auto;
  font-family: "Ma Shan Zheng", cursive;
  letter-spacing: 1px;
}

/* 水平滚动核心 - 【调慢速度】把60s改成180s，速度慢3倍 */
.hexagon-container {
  width: 100%;
  overflow: hidden;
  position: relative;
  height: 480px;
  margin: 10px 0 25px;
}

.hexagon-track {
  display: flex;
  flex-direction: column;
  position: absolute;
  /* 【关键】60s → 180s，滚动速度慢3倍，你可以根据需要调整（数值越大越慢） */
  animation: scroll 180s linear infinite;
  will-change: transform;
  top: 0;
  left: 0;
}

/* 纯水平滚动 */
@keyframes scroll {
  0% {
    transform: translateX(0);
  }
  100% {
    transform: translateX(-50%);
  }
}

.hexagon-row {
  display: flex;
  margin-bottom: -40px;
  width: fit-content;
}

.hexagon-row:nth-child(even) {
  margin-left: 90px;
}

.hexagon {
  width: 160px;
  height: 187px;
  position: relative;
  margin: 0 6px;
  cursor: pointer;
  transition: transform 0.3s;
  perspective: 1000px;
  flex-shrink: 0;
}

.hexagon-inner {
  position: relative;
  width: 100%;
  height: 100%;
  transition: transform 0.6s;
  transform-style: preserve-3d;
  clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%);
}

.hexagon:hover .hexagon-inner {
  transform: rotateY(180deg);
}

.hexagon-front,
.hexagon-back {
  position: absolute;
  width: 100%;
  height: 100%;
  backface-visibility: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border: 2px solid #8b6b46;
}

.hexagon-front {
  background: #B5A381;
}

.hexagon-back {
  background: #e8e0d5;
  color: #5d4037;
  transform: rotateY(180deg);
  padding: 8px;
  text-align: center;
}

.hexagon img {
  width: 90%;
  height: 90%;
  object-fit: cover;
  clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%);
}

.hexagon-title {
  font-size: 1.1rem;
  font-weight: bold;
  color: #5d4037;
  font-family: "Ma Shan Zheng", cursive;
}

.knowledge-graph {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(248, 245, 240, 0.95);
  display: none;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.graph-container {
  width: 95%;
  height: 90%;
  background: rgba(248, 245, 240, 0.9);
  border-radius: 15px;
  padding: 20px;
  position: relative;
  box-shadow: 0 0 50px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  border: 1px solid rgba(139, 107, 70, 0.3);
  backdrop-filter: blur(10px);
}

.echarts-container {
  flex: 1;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 10px;
  padding: 0;
  border: 1px solid rgba(139, 107, 70, 0.3);
  box-shadow: 0 2px 10px rgba(139, 107, 70, 0.1);
  margin-top: 15px;
  display: flex;
  justify-content: center;
  align-items: center;
  min-width: 300px;
  min-height: 400px;
}

.graph-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid rgba(139, 107, 70, 0.3);
}

.graph-title {
  font-size: 1.8rem;
  color: #5d4037;
  font-family: "Ma Shan Zheng", cursive;
}

.close-btn {
  background: none;
  border: none;
  color: #8b6b46;
  font-size: 1.8rem;
  cursor: pointer;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.graph-canvas {
  flex: 2;
  position: relative;
  background: linear-gradient(135deg, #f8f5f0 0%, #e8e0d5 100%);
  border-radius: 10px;
  border: 2px solid rgba(139, 107, 70, 0.2);
  overflow: hidden;
  width: 100%;
  background-image:
    radial-gradient(circle at 2px 2px, rgba(139, 107, 70, 0.08) 1px, transparent 0),
    repeating-linear-gradient(0deg, transparent, transparent 40px, rgba(139, 107, 70, 0.05) 40px, rgba(139, 107, 70, 0.05) 41px),
    repeating-linear-gradient(90deg, transparent, transparent 40px, rgba(139, 107, 70, 0.05) 40px, rgba(139, 107, 70, 0.05) 41px);
  background-size: 40px 40px, 40px 40px, 40px 40px;
  box-shadow: inset 0 0 100px rgba(139, 107, 70, 0.1);
}

footer {
  text-align: center;
  margin-top: 20px;
  padding: 15px 10px;
  border-top: 1px solid rgba(139, 107, 70, 0.2);
  color: #8b6b46;
  width: 100%;
  font-size: 0.9rem;
}

.footer-links {
  display: flex;
  justify-content: center;
  gap: 12px;
  margin-top: 10px;
}

.footer-links a {
  color: #8b6b46;
  text-decoration: none;
  font-family: "Ma Shan Zheng", cursive;
}

@media (max-width: 900px) {
  .main-title {
    font-size: 2.5rem;
  }
  .hexagon {
    width: 120px;
    height: 138px;
  }
  .hexagon-row:nth-child(even) {
    margin-left: 60px;
  }
}
</style>