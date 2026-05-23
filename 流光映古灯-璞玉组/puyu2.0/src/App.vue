
<template>
  <div class="app-container">
    <router-view v-slot="{ Component, route }">
      <transition :name="route.meta.transitionName || 'fade'" mode="out-in">
        <component :is="Component" :key="route.path" />
      </transition>
    </router-view>
    <!-- 全局悬浮球组件 -->
    <AncientLampFloatingBall />
  </div>
</template>

<script setup>
import AncientLampFloatingBall from './components/AncientLampFloatingBall.vue'
</script>

<style>
/* 全局样式重置和基础设置 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body {
  width: 100%;
  height: 100%;
  font-family: 'Noto Serif SC', 'Microsoft YaHei', serif;
  color: #5d4037;
  background-color: #f8f5f0;
  line-height: 1.6;
  overflow-x: hidden;
}

#app {
  width: 100%;
  height: 100%;
}

.app-container {
  width: 100%;
  height: 100%;
}

/* 基础淡入淡出过渡 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 淡入滑入过渡效果 */
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}

/* 页面加载时的淡入效果 */
.app-container > .router-view {
  animation: pageLoad 0.6s ease-out;
}

@keyframes pageLoad {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

/* 全局链接样式 */
a {
  color: #5d4037;
  text-decoration: none;
  transition: color 0.3s ease;
}

a:hover {
  color: #8b6b46;
}

/* 全局标题样式 */
h1, h2, h3, h4, h5, h6 {
  font-weight: 600;
  color: #5d4037;
  margin-bottom: 1rem;
  line-height: 1.3;
}

/* 全局按钮样式 */
button {
  font-family: inherit;
  cursor: pointer;
  border: none;
  outline: none;
  transition: all 0.3s ease;
}

/* 全局图片样式 */
img {
  max-width: 100%;
  height: auto;
  display: block;
}

/* 滚动条美化 */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: rgba(139, 107, 70, 0.1);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb {
  background: rgba(139, 107, 70, 0.3);
  border-radius: 4px;
  transition: background 0.3s ease;
}

::-webkit-scrollbar-thumb:hover {
  background: rgba(139, 107, 70, 0.5);
}
</style>
