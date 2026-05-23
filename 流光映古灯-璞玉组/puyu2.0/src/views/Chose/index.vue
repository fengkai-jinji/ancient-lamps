
<template>
  <div class="box">
    <!-- 收缩/展开按钮 -->
    <button 
      class="toggle-sidebar-btn" 
      @click="toggleSidebar"
      :class="{ 'collapsed': isSidebarCollapsed }"
      aria-label="切换导航栏显示"
    >
      <span class="toggle-icon">
        {{ isSidebarCollapsed ? '▶' : '◀' }}
      </span>
    </button>
    
    <div class="banner" :class="{ 'collapsed': isSidebarCollapsed }">
      <!-- Logo 区域恢复美观效果 -->
      <div class="bantop">
        <img :src="Logo" class="logo" />
        <div class="logo-text-container">
          <p class="main-logo-text">流光映古灯</p>
          <p class="sub-logo-text">循光溯源·与古为新</p>
        </div>
      </div>
      <div class="banner1">
        <p :class="{ active: activePath === '/home' }">
          <router-link to="/home">首页</router-link>
        </p>
        <p :class="{ active: activePath === '/history' }">
          <router-link to="/history">灯史长河</router-link>
        </p>
        <p :class="{ active: activePath === '/card' }">
          <router-link to="/card">灯具鉴赏</router-link>
        </p>
        <p :class="{ active: activePath === '/culture' }">
          <router-link to="/culture">灯影诗话</router-link>
        </p>
        <p :class="{ active: activePath === '/map' }">
          <router-link to="/map">地域灯踪</router-link>
        </p>
        <p :class="{ active: activePath === '/modern' }">
          <router-link to="/modern">今昔共赏</router-link>
        </p>
      </div>
    </div>
    <div class="right">
      <router-view></router-view>
    </div>
    
    <!-- 右下角跳转按钮 - 仅在非今昔共赏相关页面显示 -->
    <router-link 
      v-if="!$route.path.startsWith('/modern')"
      to="/modern" 
      class="modern-jump-btn"
    >
      今昔共赏 →
    </router-link>
  </div>
</template>
<script setup>
import { ref, watch, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import logoImage from '@/assets/images/logo.jpg'

const route = useRoute()
const Logo = logoImage
const activePath = ref(route.path)
const isSidebarCollapsed = ref(true)

watch(
  () => route.path,
  (newPath) => {
    activePath.value = newPath
  }
)

onMounted(() => {
  activePath.value = route.path
})

const toggleSidebar = () => {
  isSidebarCollapsed.value = !isSidebarCollapsed.value
}
</script>

<style scoped>
/* 引入字体（确保美观效果） */
@import url('https://fonts.googleapis.com/css2?family=Ma+Shan+Zheng&family=Noto+Serif+SC:wght@400;500;600&display=swap');

.box {
  display: flex;
  width: 100%;
  height: 100vh;
}

/* 导航栏主体 - 优化渐变背景和阴影效果 */
.banner {
  flex: 0 0 320px;
  background: linear-gradient(135deg, #f8f5f0 0%, #f0ede8 50%, #e8e5e0 100%);
  height: 100vh;
  padding: 30px 25px;
  /* box-shadow: 5px 0 25px rgba(0, 0, 0, 0.08); */
  /* border-radius: 0 20px 20px 0; */
  overflow-y: auto;
  transition: all 0.3s ease;
  position: relative;
  z-index: 10;
}

/* 导航栏收缩状态 - 完全收缩只保留按钮 */
.banner.collapsed {
  flex: 0 0 0;
  padding: 0;
  width: 0;
  overflow: hidden;
}

/* 导航栏收缩时隐藏所有内容 */
.banner.collapsed * {
  display: none !important;
}

/* 收缩/展开按钮样式 */
.toggle-sidebar-btn {
  position: fixed;
  top: 50%;
  left: 0;
  transform: translateY(-50%);
  width: 30px;
  height: 80px;
  background: linear-gradient(135deg, #f8f5f0 0%, #e8e5e0 100%);
  border: 1px solid rgba(139, 107, 70, 0.2);
  border-left: none;
  border-radius: 0 10px 10px 0;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 3px 0 10px rgba(0, 0, 0, 0.08);
  z-index: 20;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 按钮悬停效果 */
.toggle-sidebar-btn:hover {
  background: linear-gradient(135deg, #e8e5e0 0%, #f0ede8 100%);
  box-shadow: 3px 0 15px rgba(0, 0, 0, 0.1);
}

/* 按钮收缩状态位置调整 */
.toggle-sidebar-btn.collapsed {
  left: 0;
  z-index: 100;
}

/* 按钮图标样式 */
.toggle-icon {
  color: #8b6b46;
  font-size: 16px;
  font-weight: bold;
  transition: transform 0.3s ease;
  transform: rotate(180deg);
  /* 应用跳动和闪烁动画 */
  animation: bounce 1.5s infinite ease-in-out, blink 2s infinite alternate;
}

/* 跳动动画 */
@keyframes bounce {
  0%, 20%, 50%, 80%, 100% {
    transform: rotate(180deg) translateY(0);
  }
  40% {
    transform: rotate(180deg) translateY(-5px);
  }
  60% {
    transform: rotate(180deg) translateY(-3px);
  }
}

/* 闪烁动画 */
@keyframes blink {
  0%, 50% {
    opacity: 1;
    color: #8b6b46;
  }
  100% {
    opacity: 0.5;
    color: #d4b88c;
  }
}

/* 收缩状态下的按钮图标旋转 */
.toggle-sidebar-btn.collapsed .toggle-icon {
  transform: rotate(180deg);
  /* 确保收缩状态下动画继续工作 */
  animation: bounce 1.5s infinite ease-in-out, blink 2s infinite alternate;
}

/* 优化导航栏在不同屏幕尺寸下的响应式表现 */
@media (max-width: 768px) {
  .banner {
    flex: 0 0 260px;
    padding: 20px 20px;
  }
  
  /* 移动设备下的按钮位置调整 */
  .toggle-sidebar-btn {
    left: 0;
    width: 25px;
    height: 60px;
  }
  
  .toggle-sidebar-btn.collapsed {
    left: 0;
    z-index: 100;
  }
  
  /* 移动设备下的导航栏收缩状态 - 完全收缩 */
  .banner.collapsed {
    flex: 0 0 0;
    padding: 0;
    width: 0;
    overflow: hidden;
  }
}

/* Logo 区域 - 增强视觉效果 */
.bantop {
  display: flex;
  align-items: center;
  padding-bottom: 25px;
  border-bottom: 2px solid rgba(139, 107, 70, 0.15);
  margin-bottom: 30px;
  position: relative;
}

/* 添加Logo区域装饰效果 */
.bantop::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  width: 60px;
  
  background: #8b6b46;
}

.logo {
  height: 70px;
  width: 70px;
  border-radius: 50%;
  margin: 0 15px 0 5px;
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.12);
  object-fit: cover;
  border: 2px solid #d4b88c;
  flex-shrink: 0;
  background: white;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  transition: transform 0.3s ease;
}

.logo:hover {
  transform: scale(1.05);
}

.logo img {
  max-height: 100%;
  max-width: 100%;
}

.logo-text-container {
  display: flex;
  flex-direction: column;
  flex: 1;
  overflow: visible;
}

.main-logo-text {
	font-size: 1.8rem;
	color: #5d4037;
	font-weight: bold;
	letter-spacing: 2px;
	font-family: "Ma Shan Zheng", cursive;
	margin: 0;
	text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.05);
	white-space: nowrap;
	overflow: visible;
}

.sub-logo-text {
  font-size: 1rem;
  color: #8b6b46;
  font-style: italic;
  margin: 5px 0 0 0;
  font-weight: 300;
  letter-spacing: 0.5px;
  font-family: "Ma Shan Zheng", cursive;
}

/* 导航链接 - 增强交互体验 */
.banner1 {
  margin: 0 -5px;
  padding-top: 10px;
}

.banner1 p {
  margin: 12px 5px;
  padding: 15px 20px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.85);
  border: 1px solid rgba(139, 107, 70, 0.08);
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  text-align: left;
  overflow: hidden;
  font-family: 'STXihei', '华文细黑', serif;
}

/* 添加链接背景装饰效果 */
.banner1 p::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(139, 107, 70, 0.05), transparent);
  transition: left 0.5s ease;
}

.banner1 p:hover::before {
  left: 100%;
}

/* 激活状态样式增强 */
.banner1 p.active {
  background: rgba(139, 107, 70, 0.15);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  transform: translateX(5px);
}

.banner1 p.active::after {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  height: 100%;
  width: 4px;
  background: #8b6b46;
  border-radius: 0 2px 2px 0;
}

/* 链接样式 - 增强可读性和美观度 */
.banner1 p a {
  color: #5d4037;
  text-decoration: none;
  font-size: 1.15rem;
  font-weight: 500;
  letter-spacing: 1px;
  font-family: 'STXihei', '华文细黑', serif;
  display: block;
  transition: all 0.3s ease;
}

/* 悬停效果增强 */
.banner1 p:hover {
  background: rgba(139, 107, 70, 0.08);
  transform: translateX(5px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.banner1 p:hover a {
  color: #a07d55;
  letter-spacing: 1.2px;
}

/* 右边页面 - 优化内容区域 */
.right {
  flex: 1;
  background-color: #fcfaf7;
  min-height: 100vh;
  overflow-y: auto;
  transition: all 0.3s ease;
  position: relative;
}

/* 响应式优化 */
@media (max-width: 768px) {
  .right {
    padding: 20px 15px;
  }
}

/* 右下角跳转按钮样式 */
.modern-jump-btn {
  position: fixed;
  bottom: 30px;
  right: 30px;
  background: white;
  color: #5d4037;
  padding: 12px 20px;
  border-radius: 25px;
  text-decoration: none;
  font-family: 'STXihei', '华文细黑', serif;
  font-size: 1rem;
  font-weight: 500;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  border: none;
  transition: all 0.3s ease;
  z-index: 100;
  letter-spacing: 0.5px;
  min-width: 120px;
  text-align: center;
}

/* 按钮悬停效果 */
.modern-jump-btn:hover {
  background: #f8f5f0;
  transform: translateY(-1px);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15);
}

/* 按钮点击效果 */
.modern-jump-btn:active {
  transform: translateY(0);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

/* 移动设备响应式调整 */
@media (max-width: 768px) {
  .modern-jump-btn {
    bottom: 20px;
    right: 20px;
    padding: 10px 16px;
    font-size: 0.9rem;
    min-width: 100px;
  }
}
</style>