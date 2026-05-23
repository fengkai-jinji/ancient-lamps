<template>
  <div class="container">
    <header>
      <h1>古灯历史时间轴</h1>
    </header>
    
    <!-- 时间轴 -->
    <div class="timeline-container" ref="timelineRef">
      <div class="timeline">
        <!-- 流动光效 -->
        <div class="timeline-glow"></div>
        
        <div 
          v-for="(item, index) in timelineData" 
          :key="index" 
          class="timeline-point"
          :class="{ active: currentIndex === index }"
          @click="goToSlide(index)"
        >
          <div class="point">
            <div class="point-inner"></div>
          </div>
          <div class="timeline-year">{{ item.year }}</div>
          <div class="timeline-dynasty">{{ item.dynasty }}</div>
          
          <!-- 悬停信息卡片 -->
          <div class="hover-card">
            <h3>{{ item.year }}灯具</h3>
            <p>{{ item.description.substring(0, 50) }}...</p>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 轮播图 -->
    <div class="carousel-container" @mouseenter="handleMouseEnter" @mouseleave="handleMouseLeave">
      <div class="carousel-hint">点击图片探索地域灯踪</div>
      <div class="carousel" :style="{ transform: `translateX(-${currentIndex * 100}%)` }">
        <div 
          v-for="(item, index) in timelineData" 
          :key="index" 
          class="carousel-item"
          :class="{ active: currentIndex === index }"
          @click="goToMap"
        >
          <div class="carousel-item-inner">
            <div class="carousel-image-container">
              <img :src="getImageUrl(item.image)" :alt="item.name" class="lantern-image" @error="handleImageError($event)">
              <div class="image-overlay">
                <div class="overlay-content">
                  <h3>{{ item.year }}</h3>
                  <p>{{ item.dynasty }}</p>
                </div>
              </div>
            </div>
            <div class="lantern-info">
              <h2 class="lantern-name">{{ item.name }}</h2>
              <p class="lantern-description">{{ item.description }}</p>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 导航按钮 -->
      <button class="nav-btn prev" @click="prevSlide" :disabled="currentIndex === 0">
        <span class="nav-icon">‹</span>
      </button>
      <button class="nav-btn next" @click="nextSlide" :disabled="currentIndex === timelineData.length - 1">
        <span class="nav-icon">›</span>
      </button>
    </div>
    

  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';

const router = useRouter();

const currentIndex = ref(0);
const hoveredIndex = ref(-1);
const timelineRef = ref(null);
const autoplayTimer = ref(null);
const autoplayInterval = 1000; // 自动播放间隔时间（毫秒），恢复为原来的1秒间隔
const timelineData = ref([]);

// 获取图片URL
const getImageUrl = (imagePath) => {
  if (!imagePath) return '';
  // 直接使用后端静态文件服务
  if (typeof imagePath === 'string') {
    if (imagePath.startsWith('/static/')) {
      return `http://localhost:5000${imagePath}`;
    } else {
      return `http://localhost:5000/static/images/${imagePath}`;
    }
  }
  return imagePath;
};

// 从后端获取历史数据
const fetchHistory = async () => {
  try {
    const res = await axios.get('http://localhost:5000/api/history');
    timelineData.value = res.data;
  } catch (error) {
    // 静默处理错误，避免控制台日志影响性能
  }
};

const prevSlide = () => {
  if (currentIndex.value > 0) {
    currentIndex.value--;
    resetAutoplay(); // 用户交互后重置自动播放
  }
};

const nextSlide = () => {
  if (currentIndex.value < timelineData.value.length - 1) {
    currentIndex.value++;
  } else {
    // 最后一张时回到第一张
    currentIndex.value = 0;
  }
  resetAutoplay(); // 用户交互后重置自动播放
};

const goToSlide = (index) => {
  currentIndex.value = index;
  resetAutoplay(); // 用户交互后重置自动播放
};

// 自动播放下一张
const autoplayNextSlide = () => {
  nextSlide();
};

// 启动自动播放
const startAutoplay = () => {
  if (autoplayTimer.value) return;
  autoplayTimer.value = setInterval(autoplayNextSlide, autoplayInterval);
};

// 停止自动播放
const stopAutoplay = () => {
  if (autoplayTimer.value) {
    clearInterval(autoplayTimer.value);
    autoplayTimer.value = null;
  }
};

// 重置自动播放
const resetAutoplay = () => {
  stopAutoplay();
  startAutoplay();
};

// 鼠标悬停时暂停自动播放
const handleMouseEnter = () => {
  stopAutoplay();
};

// 鼠标离开时恢复自动播放
const handleMouseLeave = () => {
  startAutoplay();
};

// 滚动触发动画
onMounted(() => {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('animate-in');
      }
    });
  }, { threshold: 0.1 });
  
  if (timelineRef.value) {
    observer.observe(timelineRef.value);
  }
  
  // 从后端获取历史数据
  fetchHistory();
  
  // 启动自动播放
  startAutoplay();
});

// 跳转到地域灯踪
const goToMap = () => {
  router.push('/map');
};

const handleImageError = (e) => {
  e.target.src = 'http://localhost:5000/static/images/logo.jpg';
  console.warn('图片加载失败，已使用默认图片替代');
};

// 组件卸载时清除定时器
onUnmounted(() => {
  stopAutoplay();
});
</script>

<style scoped>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
  font-family: "Microsoft YaHei", "宋体", sans-serif;
}

body {
  background-color: #f8f5f0;
  color: #5d4037;
  line-height: 1.6;
}

.container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 30px;
}

header {
  text-align: center;
  padding: 30px 0 10px 0;
  margin-bottom: 0;
}

h1 {
  font-size: 3.5rem;
  color: #5d4037;
  letter-spacing: 4px;
  font-family: "Ma Shan Zheng", cursive;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
  position: relative;
  display: inline-block;
  margin: 0;
  white-space: nowrap;
  overflow: visible;
  text-overflow: unset;
}

/* h1:after {
  content: "";
  position: absolute;
  bottom: -10px;
  left: 10%;
  width: 80%;
  height: 3px;
  background: linear-gradient(to right, transparent, #8d6e63, transparent);
} */

.subtitle {
  font-size: 1.2rem;
  color: #8d6e63;
  font-style: italic;
  text-align: center;
  display: block;
  margin: 0 auto;
  max-width: 80%;
}

/* 时间轴样式 */
.timeline-container {
  position: relative;
  margin: 0 0;
  padding: 5px 0;
  opacity: 0;
  transform: translateY(20px);
  transition: all 0.8s ease;
}

.timeline-container.animate-in {
  opacity: 1;
  transform: translateY(0);
}

.timeline {
  display: flex;
  justify-content: space-between;
  position: relative;
  padding: 5px 50px;
  overflow: hidden;
}

.timeline:before {
    content: "";
    position: absolute;
    top: 15px;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(to right, rgba(215, 204, 200, 0.6), rgba(141, 110, 99, 0.6), rgba(215, 204, 200, 0.6));
    border-radius: 1.5px;
}

/* 时间轴流动光效 */
.timeline-glow {
  position: absolute;
  top: 15px;
  left: -100px;
  width: 100px;
  height: 3px;
  background: linear-gradient(90deg, transparent, rgba(139, 107, 70, 0.4), transparent);
  border-radius: 1.5px;
  animation: timelineFlow 3s infinite linear;
  z-index: 1;
}

@keyframes timelineFlow {
  0% {
    left: -100px;
  }
  100% {
    left: calc(100% + 100px);
  }
}

.timeline-point {
  position: relative;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  z-index: 2;
  padding: 5px 0;
}

.timeline-point:hover {
  transform: translateY(-5px);
}

.timeline-point.active .point {
  transform: scale(1.3);
}

.timeline-point.active .point-inner {
  background-color: rgba(93, 64, 55, 0.8);
  box-shadow: 0 0 20px rgba(93, 64, 55, 0.4);
  animation: activePulse 2s infinite;
}

@keyframes activePulse {
  0%, 100% {
    box-shadow: 0 0 0 0 rgba(93, 64, 55, 0.7);
  }
  50% {
    box-shadow: 0 0 0 10px rgba(93, 64, 55, 0);
  }
}

/* 跳动动画效果 */
@keyframes pulse {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.2);
  }
}

.point {
  width: 26px;
  height: 26px;
  margin: 0 auto 8px;
  transition: all 0.3s ease;
  animation: pulse 1.5s infinite;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  top: -5px;
}

.point-inner {
  width: 16px;
  height: 16px;
  background-color: rgba(141, 110, 99, 0.7);
  border-radius: 50%;
  transition: all 0.3s ease;
  box-shadow: 0 0 8px rgba(139, 107, 70, 0.3);
}

/* 悬停信息卡片 */
.hover-card {
  position: absolute;
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%);
  background-color: rgba(255, 255, 255, 0.98);
  padding: 15px;
  border-radius: 8px;
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.15);
  width: 220px;
  margin-bottom: 10px;
  z-index: 100;
  animation: slideUp 0.3s ease;
  pointer-events: none; /* 避免干扰鼠标事件 */
  opacity: 0;
  transition: opacity 0.3s ease;
}

.timeline-point:hover .hover-card {
  opacity: 1;
}

.hover-card h3 {
  font-size: 1rem;
  margin-bottom: 5px;
  color: #5d4037;
}

.hover-card p {
  font-size: 0.9rem;
  color: #795548;
  margin: 0;
  line-height: 1.4;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateX(-50%) translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateX(-50%) translateY(0);
  }
}

/* 三角形指示器 */
.hover-card::after {
  content: "";
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  border-width: 8px;
  border-style: solid;
  border-color: rgba(255, 255, 255, 0.95) transparent transparent transparent;
}

.timeline-year {
  font-weight: bold;
  margin-bottom: 5px;
  font-size: 1.1rem;
}

.timeline-dynasty {
  font-size: 0.85rem;
  color: #795548;
}

/* 轮播图样式 */
.carousel-container {
  position: relative;
  margin: 30px 0;
  overflow: hidden;
  border-radius: 15px;
  padding: 30px;
}

.carousel-hint {
  text-align: center;
  margin-bottom: 15px;
  color: #8b6b46;
  font-size: 0.95rem;
  font-family: "Ma Shan Zheng", cursive;
  opacity: 0.8;
  animation: hintPulse 2s ease-in-out infinite;
}

@keyframes hintPulse {
  0%, 100% { opacity: 0.6; }
  50% { opacity: 1; }
}

.carousel {
  display: flex;
  transition: transform 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}

.carousel-item {
  min-width: 100%;
  padding: 20px;
  transition: all 0.6s ease;
  opacity: 0.6;
  transform: scale(0.9);
  cursor: pointer;
}

.carousel-item.active {
  opacity: 1;
  transform: scale(1);
}

.carousel-item.active:hover {
  transform: scale(1.02);
}

.carousel-item.active:hover .carousel-image-container {
  box-shadow: 0 15px 40px rgba(139, 107, 70, 0.3);
}

.carousel-item-inner {
  display: flex;
  flex-direction: column;
  align-items: center;
  perspective: 1000px;
  background: transparent;
}

.carousel-image-container {
  position: relative;
  margin-bottom: 20px;
  border-radius: 8px;
  overflow: hidden;
  /* box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15); */
  transition: transform 0.6s ease;
}

.carousel-item.active .carousel-image-container {
  transform: rotateY(0deg);
}

.lantern-image {
  width: 100%;
  max-width: 550px;
  height: 280px;
  object-fit: cover;
  transition: transform 0.6s ease;
}

.carousel-image-container:hover .lantern-image {
  transform: scale(1.05);
}

/* 图片叠加层 */
.image-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(to top, rgba(0, 0, 0, 0.6), transparent);
  display: flex;
  align-items: flex-end;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.carousel-image-container:hover .image-overlay {
  opacity: 1;
}

.overlay-content {
  color: white;
  text-align: center;
  padding: 20px;
}

.overlay-content h3 {
  margin: 0 0 5px 0;
  font-size: 1.5rem;
}

.overlay-content p {
  margin: 0;
  font-size: 1rem;
  opacity: 0.9;
}

.lantern-info {
  text-align: center;
  max-width: 800px;
  padding: 0 20px;
}

.lantern-name {
  font-size: 2rem;
  color: #5d4037;
  margin-bottom: 15px;
  position: relative;
  display: inline-block;
}

.lantern-name::after {
  content: "";
  position: absolute;
  bottom: -5px;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(to right, transparent, #8d6e63, transparent);
}

.lantern-description {
  color: #795548;
  line-height: 1.8;
  text-align: left;
  font-size: 1.05rem;
}

.nav-btn {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  background: rgba(139, 107, 70, 0.8);
  color: white;
  border: none;
  width: 50px;
  height: 50px;
  border-radius: 50%;
  cursor: pointer;
  font-size: 1.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  z-index: 10;
}

.nav-btn.prev {
  left: 15px;
}

.nav-btn.next {
  right: 15px;
}

.nav-btn:hover:not(:disabled) {
  background: linear-gradient(135deg, #8d6e63, #6d4c41);
  transform: translateY(-50%) scale(1.1);
  box-shadow: 0 6px 20px rgba(139, 107, 70, 0.4);
}

.nav-btn:disabled {
  background: rgba(139, 107, 70, 0.3);
  cursor: not-allowed;
  transform: translateY(-50%) scale(1);
}

.nav-icon {
  font-size: 1.5rem;
  font-weight: bold;
}



/* 页脚 */
footer {
  text-align: center;
  padding: 20px 0;
  margin-top: 40px;
  border-top: 1px solid #d7ccc8;
  color: #8d6e63;
  font-size: 0.9rem;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .timeline {
    padding: 0 30px;
  }
  
  .hover-card {
    width: 160px;
    padding: 10px;
  }
  
  .hover-card h3 {
    font-size: 0.9rem;
  }
  
  .hover-card p {
    font-size: 0.8rem;
  }
}

@media (max-width: 768px) {
  .timeline {
    padding: 0 20px;
  }
  
  .timeline-point {
    padding: 5px 0;
  }
  
  .timeline-year {
    font-size: 0.9rem;
  }
  
  .timeline-dynasty {
    font-size: 0.8rem;
  }
  
  .point {
    width: 24px;
    height: 24px;
  }
  
  .point-inner {
    width: 14px;
    height: 14px;
  }
  
  .hover-card {
    display: none;
  }
  
  .lantern-image {
    height: 250px;
  }
  
  .lantern-name {
    font-size: 1.5rem;
  }
  
  .lantern-description {
    font-size: 0.95rem;
  }
  
  .nav-btn {
    padding: 10px 18px;
    font-size: 1rem;
  }
  
  .carousel-container {
    padding: 20px;
  }
}

@media (max-width: 480px) {
  .timeline {
    padding: 0 10px;
  }
  
  .timeline-year {
    font-size: 0.8rem;
  }
  
  .timeline-dynasty {
    font-size: 0.7rem;
  }
  
  .lantern-image {
    height: 200px;
  }
  
  .carousel-nav {
    flex-direction: column;
    gap: 10px;
  }
  
  .nav-btn {
    justify-content: center;
  }
}
</style>