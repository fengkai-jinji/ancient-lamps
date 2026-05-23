<template>
  <div class="ancient-lamp-floating-root">
    <!-- 遮罩层 -->
    <transition name="fade">
      <div
        v-if="isOpen"
        class="modal-overlay"
        @click="closePanel"
        @wheel.prevent
        @touchmove.prevent
      ></div>
    </transition>

    <!-- 悬浮球 -->
    <transition name="scale-fade">
      <div
        v-show="!isOpen"
        class="floating-ball"
        ref="ballRef"
        :style="ballStyle"
        @mousedown="startDrag"
        @touchstart.passive="startDrag"
        @click="openPanel"
      >
        <div class="ball-content">
          <span class="lamp-icon">🏮</span>
        </div>
        <div class="pulse-ring"></div>
      </div>
    </transition>

    <!-- 主面板 -->
    <transition name="modal-pop">
      <div v-if="isOpen" class="main-panel" @wheel.stop>
        <!-- 顶部导航栏 -->
        <div class="panel-header">
          <div class="header-left">
            <span class="lamp-logo">🏮</span>
            <span class="title">智慧古灯助手</span>
            <span class="status-badge" :class="{ online: isBackendOnline }">
              {{ isBackendOnline ? '已连接' : '离线' }}
            </span>
          </div>

          <div class="tab-center">
            <button
              :class="['tab-btn', { active: activeTab === 'chat' }]"
              @click="activeTab = 'chat'"
            >
              💬 古灯问答
            </button>
            <button
              :class="['tab-btn', { active: activeTab === 'design' }]"
              @click="activeTab = 'design'"
            >
              🎨 设计建议
            </button>
          </div>

          <button class="close-btn" @click="closePanel" title="关闭">×</button>
        </div>

        <!-- 内容区域 -->
        <div class="panel-body">
          <!-- 聊天标签页 -->
          <div v-show="activeTab === 'chat'" class="tab-content chat-mode">
            <div class="messages-area" ref="msgContainer">
              <div v-if="messages.length === 0" class="empty-placeholder">
                <div class="welcome-icon">🏮</div>
                <p>欢迎来到智慧古灯世界！</p>
                <p>关于古灯的历史、文化、制作工艺等问题，我都很乐意解答。</p>
              </div>

              <div
                v-for="(msg, index) in messages"
                :key="index"
                :class="['message-row', msg.role]"
              >
                <div class="avatar">
                  <template v-if="msg.role === 'user'">
                    <span class="default-icon">👤</span>
                  </template>
                  <template v-else>
                    <span class="icon">🏮</span>
                  </template>
                </div>
                <div class="bubble markdown-body" v-html="renderContent(msg.content)"></div>
              </div>

              <div v-if="isLoading" class="message-row assistant">
                <div class="avatar">🏮</div>
                <div class="bubble loading-bubble">
                  <span class="dot"></span><span class="dot"></span><span class="dot"></span>
                </div>
              </div>
            </div>

            <div class="quick-questions" ref="quickQScroll" @wheel.prevent="handleHorizontalScroll">
              <button
                v-for="(q, index) in suggestionQuestions"
                :key="index"
                class="quick-chip"
                @click="handleQuickAsk(q)"
              >
                {{ q }}
              </button>
            </div>

            <div class="input-bar">
              <input
                v-model="chatInput"
                @keyup.enter="handleSendMessage"
                :disabled="isLoading"
                placeholder="请输入关于古灯的问题..."
                type="text"
                autocomplete="off"
              />
              <button
                class="send-btn"
                @click="handleSendMessage"
                :disabled="!chatInput.trim() || isLoading"
              >
                ➤
              </button>
            </div>
          </div>

          <!-- 设计建议标签页 -->
          <div v-show="activeTab === 'design'" class="tab-content design-mode">
            <div class="design-scroll-area">
              <div class="section-label">✨ 设计参考</div>
              <div class="preset-scroll">
                <span
                  v-for="(preset, index) in designPresets"
                  :key="index"
                  class="preset-chip"
                  @click="designPrompt = preset"
                >
                  {{ preset }}
                </span>
              </div>

              <div class="section-label" style="margin-top: 20px;">📐 风格选择</div>
              <div class="style-grid">
                <div
                  v-for="style in styleOptions"
                  :key="style.val"
                  :class="['style-card', { active: selectedStyle === style.val }]"
                  @click="selectedStyle = style.val"
                >
                  <span class="style-icon">{{ style.icon }}</span>
                  <span class="style-name">{{ style.name }}</span>
                  <span class="style-detail">{{ style.detail }}</span>
                </div>
              </div>

              <div class="result-display">
                <div v-if="designResult" class="design-result">
                  <h4>💡 设计建议</h4>
                  <p>{{ designResult }}</p>
                </div>
                <div v-else-if="isGenerating" class="generating-state">
                  <div class="spinner"></div>
                  <p>正在为您生成设计建议...</p>
                </div>
                <div v-else class="empty-state">
                  <p>选择风格和描述需求，获取专业的古灯设计建议</p>
                </div>
                <p v-if="designError" class="error-text">❌ {{ designError }}</p>
              </div>
            </div>

            <div class="input-bar design-input-bar">
              <textarea
                v-model="designPrompt"
                placeholder="描述您想要的古灯设计..."
                rows="2"
              ></textarea>
              <button
                class="magic-btn"
                @click="handleGenerateDesign"
                :disabled="isGenerating || !designPrompt.trim()"
              >
                🎨 获取建议
              </button>
            </div>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, nextTick, onMounted, onUnmounted } from 'vue';

// 状态管理
const isOpen = ref(false);
const activeTab = ref('chat');
const isBackendOnline = ref(false);

// 拖拽逻辑
const ballRef = ref(null);
const ballPos = ref({ x: 0, y: 0 });
const isDragging = ref(false);
let startPos = { x: 0, y: 0 };
let initialBallPos = { x: 0, y: 0 };
let moveHandler = null;
let upHandler = null;

const ballStyle = computed(() => ({
  transform: `translate3d(${ballPos.value.x}px, ${ballPos.value.y}px, 0)`,
}));

// 聊天数据
const chatInput = ref('');
const messages = ref([]);
const isLoading = ref(false);
const msgContainer = ref(null);
const quickQScroll = ref(null);

const suggestionQuestions = [
  '🏮 长信宫灯的历史背景是什么？',
  '🪔 古灯的制作材料有哪些？',
  '🎭 不同朝代的古灯有什么特点？',
  '💎 如何收藏和保养古灯？',
  '🎨 请推荐一些现代古灯设计风格',
];

// 设计数据
const designPrompt = ref('');
const selectedStyle = ref('traditional');
const isGenerating = ref(false);
const designError = ref('');
const designResult = ref('');

const designPresets = [
  '一款简约典雅的台灯，适合书房使用',
  '复古风格的吊灯，用于客厅装饰',
  '具有中国风元素的现代设计',
  '小巧精致的床头柜灯',
  '融合传统与现代的创意设计',
];

const styleOptions = [
  { name: '传统古典', detail: '明清宫廷风格', val: 'traditional', icon: '🏛️' },
  { name: '简约现代', detail: '简洁优雅线条', val: 'modern', icon: '✨' },
  { name: '自然田园', detail: '木质自然风格', val: 'pastoral', icon: '🌿' },
];

// 功能函数
const openPanel = () => {
  if (isDragging.value) return;
  isOpen.value = true;
  document.body.classList.add('lock-scroll');
  document.documentElement.classList.add('lock-scroll');
};

const closePanel = () => {
  isOpen.value = false;
  document.body.classList.remove('lock-scroll');
  document.documentElement.classList.remove('lock-scroll');
};

const renderContent = (text) => {
  if (!text) return '';
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/`(.*?)`/g, '<code>$1</code>')
    .replace(/\n/g, '<br>');
};

// 后端API调用
const API_BASE_URL = 'http://localhost:5000/api';

const checkBackendStatus = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/lamps`);
    isBackendOnline.value = response.ok;
    return isBackendOnline.value;
  } catch (err) {
    isBackendOnline.value = false;
    return false;
  }
};

const sendMessage = async (message) => {
  try {
    const response = await fetch(`${API_BASE_URL}/ai/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ message }),
    });

    if (!response.ok) {
      throw new Error('API请求失败');
    }

    const data = await response.json();
    return { answer: data.response || data.answer || '抱歉，我无法回答这个问题。' };
  } catch (err) {
    return {
      answer: '古灯文化博大精深，让我为您简单介绍一下：\n\n中国古灯历史悠久，最早可追溯到新石器时代。从最初的陶灯，到青铜灯、瓷灯，每一种都承载着时代的记忆。\n\n您想了解哪个朝代的古灯呢？',
    };
  }
};

const handleSendMessage = async () => {
  const text = chatInput.value.trim();
  if (!text || isLoading.value) return;

  messages.value.push({ role: 'user', content: text });
  chatInput.value = '';
  isLoading.value = true;
  render();
  scrollToBottom();

  try {
    const res = await sendMessage(text);
    messages.value.push({ role: 'assistant', content: res.answer });
  } catch (err) {
    messages.value.push({ role: 'assistant', content: '抱歉，网络连接异常，请稍后再试。' });
  } finally {
    isLoading.value = false;
    render();
    scrollToBottom();
  }
};

const handleQuickAsk = (text) => {
  chatInput.value = text;
  handleSendMessage();
};

const handleHorizontalScroll = (e) => {
  if (quickQScroll.value) {
    quickQScroll.value.scrollLeft += e.deltaY;
  }
};

const scrollToBottom = () => {
  nextTick(() => {
    if (msgContainer.value) {
      msgContainer.value.scrollTop = msgContainer.value.scrollHeight;
    }
  });
};

const handleGenerateDesign = async () => {
  if (!designPrompt.value || isGenerating.value) return;

  isGenerating.value = true;
  designError.value = '';
  designResult.value = '';

  try {
    await new Promise((resolve) => setTimeout(resolve, 1500));
    designResult.value = generateDesignSuggestion(designPrompt.value, selectedStyle.value);
  } catch (err) {
    designError.value = '生成建议失败，请稍后再试';
  } finally {
    isGenerating.value = false;
  }
};

const generateDesignSuggestion = (prompt, style) => {
  const styleDescriptions = {
    traditional: '采用传统古典风格，建议使用红木或紫檀等名贵木材，配以精致的雕刻花纹，如祥云纹、回纹等，体现庄重典雅的气质。',
    modern: '现代简约风格，强调线条简洁，可使用金属与玻璃的组合，色彩以素雅为主，营造时尚而不失文化底蕴的氛围。',
    pastoral: '自然田园风格，选用原木材料，保留天然纹理，搭配棉麻布艺灯罩，营造温馨舒适的家居氛围。',
  };

  return `根据您的需求"${prompt}"，为您提供以下设计建议：\n\n${styleDescriptions[style]}\n\n💡 小贴士：在设计时，可以参考长信宫灯的环保理念，考虑使用LED光源，既节能又能更好地展现设计的美感。`;
};

// 拖拽功能
const startDrag = (e) => {
  if (e.type === 'mousedown') {
    e.preventDefault();
    if (e.button !== 0) return;
  }

  isDragging.value = false;
  document.body.style.userSelect = 'none';

  const clientX = e.type.startsWith('touch') ? e.touches[0].clientX : e.clientX;
  const clientY = e.type.startsWith('touch') ? e.touches[0].clientY : e.clientY;

  startPos = { x: clientX, y: clientY };
  initialBallPos = { ...ballPos.value };

  moveHandler = (ev) => {
    isDragging.value = true;
    const cx = ev.type.startsWith('touch') ? ev.touches[0].clientX : ev.clientX;
    const cy = ev.type.startsWith('touch') ? ev.touches[0].clientY : ev.clientY;

    let newX = initialBallPos.x + (cx - startPos.x);
    let newY = initialBallPos.y + (cy - startPos.y);

    newX = Math.min(Math.max(0, newX), window.innerWidth - 64);
    newY = Math.min(Math.max(0, newY), window.innerHeight - 64);

    ballPos.value = { x: newX, y: newY };
  };

  upHandler = () => {
    document.removeEventListener('mousemove', moveHandler);
    document.removeEventListener('mouseup', upHandler);
    document.removeEventListener('touchmove', moveHandler);
    document.removeEventListener('touchend', upHandler);

    document.body.style.userSelect = '';

    if (isDragging.value) {
      snapToEdge();
      setTimeout(() => (isDragging.value = false), 100);
    }
  };

  document.addEventListener('mousemove', moveHandler);
  document.addEventListener('mouseup', upHandler);
  document.addEventListener('touchmove', moveHandler, { passive: false });
  document.addEventListener('touchend', upHandler);
};

const snapToEdge = () => {
  const midX = window.innerWidth / 2;
  const targetX = ballPos.value.x < midX ? 20 : window.innerWidth - 80;
  ballPos.value = { x: targetX, y: ballPos.value.y };
};

const handleResize = () => {
  snapToEdge();
};

// 生命周期
onMounted(async () => {
  ballPos.value = {
    x: window.innerWidth - 90,
    y: window.innerHeight - 120,
  };
  await checkBackendStatus();
  window.addEventListener('resize', handleResize);
});

onUnmounted(() => {
  window.removeEventListener('resize', handleResize);
  document.body.classList.remove('lock-scroll');
  document.documentElement.classList.remove('lock-scroll');
});
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@400;500;600;700&display=swap');

.ancient-lamp-floating-root {
  position: fixed;
  top: 0;
  left: 0;
  width: 0;
  height: 0;
  z-index: 99999;
  font-family: 'Noto Serif SC', 'Microsoft YaHei', serif;
}

/* 遮罩层 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-color: rgba(93, 64, 55, 0.4);
  backdrop-filter: blur(4px);
  z-index: 10000;
}

/* 悬浮球 */
.floating-ball {
  position: fixed;
  width: 64px;
  height: 64px;
  cursor: pointer;
  pointer-events: auto;
  touch-action: none;
  z-index: 10001;
  left: 0;
  top: 0;
  transition: transform 0.1s linear;
  user-select: none;
}

.ball-content {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: linear-gradient(135deg, #d4a574 0%, #8b5a2b 100%);
  box-shadow: 0 8px 25px rgba(139, 90, 43, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 32px;
}

.pulse-ring {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  border: 2px solid rgba(212, 165, 116, 0.6);
  animation: pulse 2s infinite;
  pointer-events: none;
}

@keyframes pulse {
  0% { transform: scale(1); opacity: 0.8; }
  100% { transform: scale(1.6); opacity: 0; }
}

/* 主面板 */
.main-panel {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 900px;
  height: 720px;
  max-width: 92vw;
  max-height: 90vh;
  background: #f8f5f0;
  border-radius: 24px;
  box-shadow: 0 40px 80px rgba(93, 64, 55, 0.3);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  z-index: 10002;
  border: 2px solid #d4a574;
}

/* 头部 */
.panel-header {
  padding: 0 24px;
  height: 70px;
  background: linear-gradient(135deg, #f8f5f0 0%, #e8dcc8 100%);
  border-bottom: 2px solid #d4a574;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
}

.header-left .title {
  font-size: 18px;
  font-weight: 700;
  color: #5d4037;
}

.status-badge {
  font-size: 12px;
  padding: 4px 10px;
  border-radius: 12px;
  background: #fee2e2;
  color: #ef4444;
  font-weight: 500;
}

.status-badge.online {
  background: #dcfce7;
  color: #166534;
}

.tab-center {
  background: #e8dcc8;
  padding: 4px;
  border-radius: 24px;
  display: flex;
  gap: 4px;
}

.tab-btn {
  padding: 8px 20px;
  border: none;
  background: transparent;
  border-radius: 20px;
  font-size: 15px;
  color: #6b5b4f;
  cursor: pointer;
  transition: all 0.3s;
  font-weight: 500;
  font-family: inherit;
}

.tab-btn:hover {
  background: rgba(255, 255, 255, 0.5);
}

.tab-btn.active {
  background: white;
  color: #8b5a2b;
  font-weight: 700;
  box-shadow: 0 2px 8px rgba(93, 64, 55, 0.1);
}

.close-btn {
  width: 36px;
  height: 36px;
  border: none;
  background: #e8dcc8;
  border-radius: 50%;
  font-size: 24px;
  color: #8b7355;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
  font-family: inherit;
}

.close-btn:hover {
  background: #d4a574;
  color: white;
}

/* 内容区 */
.panel-body {
  flex: 1;
  overflow: hidden;
  position: relative;
  background: #f8f5f0;
}

.tab-content {
  height: 100%;
  display: flex;
  flex-direction: column;
}

/* 聊天 */
.messages-area {
  flex: 1;
  overflow-y: auto;
  padding: 30px;
  display: flex;
  flex-direction: column;
  gap: 24px;
  padding-bottom: 10px;
}

.empty-placeholder {
  text-align: center;
  color: #8b7355;
  margin-top: 80px;
}

.welcome-icon {
  font-size: 60px;
  margin-bottom: 20px;
}

.message-row {
  display: flex;
  gap: 16px;
  max-width: 80%;
}

.message-row.user {
  align-self: flex-end;
  flex-direction: row-reverse;
}

.avatar {
  width: 42px;
  height: 42px;
  border-radius: 12px;
  background: #e8dcc8;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  flex-shrink: 0;
}

.bubble {
  padding: 16px 20px;
  border-radius: 20px;
  font-size: 16px;
  line-height: 1.6;
  background: white;
  border: 1px solid #e8dcc8;
  color: #5d4037;
  box-shadow: 0 2px 4px rgba(93, 64, 55, 0.05);
}

.user .bubble {
  background: linear-gradient(135deg, #d4a574 0%, #8b5a2b 100%);
  color: white;
  border: none;
  border-bottom-right-radius: 4px;
  box-shadow: 0 4px 10px rgba(139, 90, 43, 0.3);
}

.assistant .bubble {
  border-bottom-left-radius: 4px;
}

/* 快捷提问 */
.quick-questions {
  padding: 10px 24px;
  display: flex;
  gap: 10px;
  overflow-x: auto;
  white-space: nowrap;
  background: #f8f5f0;
  border-top: 1px solid #e8dcc8;
  flex-shrink: 0;
  scrollbar-width: none;
  -ms-overflow-style: none;
}

.quick-questions::-webkit-scrollbar {
  display: none;
}

.quick-chip {
  background: white;
  border: 1px solid #e8dcc8;
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 13px;
  color: #6b5b4f;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 2px 6px rgba(93, 64, 55, 0.05);
  flex-shrink: 0;
  display: flex;
  align-items: center;
  font-family: inherit;
}

.quick-chip:hover {
  border-color: #d4a574;
  color: #8b5a2b;
  background: #fff8f0;
  transform: translateY(-2px);
  box-shadow: 0 4px 10px rgba(139, 90, 43, 0.15);
}

/* 输入区 */
.input-bar {
  padding: 24px;
  background: white;
  border-top: 1px solid #e8dcc8;
  display: flex;
  gap: 16px;
  align-items: flex-end;
}

.input-bar input,
.input-bar textarea {
  flex: 1;
  border: 2px solid #e8dcc8;
  border-radius: 28px;
  padding: 14px 24px;
  outline: none;
  transition: border 0.3s;
  font-size: 16px;
  font-family: inherit;
  resize: none;
  background: #f8f5f0;
  color: #5d4037;
}

.input-bar input:focus,
.input-bar textarea:focus {
  border-color: #d4a574;
  background: white;
}

.send-btn,
.magic-btn {
  width: 52px;
  height: 52px;
  border-radius: 50%;
  background: linear-gradient(135deg, #d4a574 0%, #8b5a2b 100%);
  color: white;
  border: none;
  cursor: pointer;
  flex-shrink: 0;
  font-size: 20px;
  transition: all 0.3s;
  font-family: inherit;
}

.send-btn:hover,
.magic-btn:hover {
  transform: scale(1.05);
  box-shadow: 0 4px 15px rgba(139, 90, 43, 0.4);
}

.send-btn:active,
.magic-btn:active {
  transform: scale(0.95);
}

.send-btn:disabled,
.magic-btn:disabled {
  background: #d4c4b0;
  cursor: not-allowed;
  box-shadow: none;
}

.magic-btn {
  width: auto;
  padding: 0 32px;
  border-radius: 28px;
  font-weight: 600;
}

/* 设计模式 */
.design-scroll-area {
  flex: 1;
  overflow-y: auto;
  padding: 24px 30px;
  overscroll-behavior: contain;
}

.section-label {
  font-size: 15px;
  font-weight: 700;
  color: #5d4037;
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.preset-scroll {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 24px;
  overflow-x: visible;
}

.preset-chip {
  background: #e8dcc8;
  border: 1px solid transparent;
  padding: 8px 16px;
  border-radius: 12px;
  font-size: 13px;
  color: #6b5b4f;
  cursor: pointer;
  line-height: 1.5;
  transition: all 0.3s ease;
  max-width: 100%;
  text-align: left;
  white-space: normal;
  font-family: inherit;
}

.preset-chip:hover {
  border-color: #d4a574;
  color: #8b5a2b;
  background: #fff8f0;
  transform: translateY(-1px);
  box-shadow: 0 2px 6px rgba(139, 90, 43, 0.15);
}

.style-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin-bottom: 24px;
}

.style-card {
  border: 2px solid #e8dcc8;
  padding: 16px;
  border-radius: 12px;
  text-align: center;
  cursor: pointer;
  background: white;
  transition: all 0.3s;
  position: relative;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.style-card:hover {
  border-color: #d4a574;
  background: #fff8f0;
}

.style-card.active {
  border-color: #8b5a2b;
  background: #fff8f0;
  box-shadow: inset 0 0 0 2px #8b5a2b;
}

.style-icon {
  font-size: 32px;
  display: block;
}

.style-name {
  font-weight: 700;
  font-size: 14px;
  display: block;
  color: #5d4037;
}

.style-detail {
  font-size: 12px;
  color: #8b7355;
}

.result-display {
  background: white;
  border-radius: 16px;
  min-height: 200px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border: 2px dashed #e8dcc8;
  position: relative;
  margin-bottom: 10px;
  padding: 24px;
}

.design-result {
  width: 100%;
  text-align: left;
}

.design-result h4 {
  color: #8b5a2b;
  margin-bottom: 12px;
}

.design-result p {
  color: #5d4037;
  line-height: 1.8;
}

.empty-state {
  color: #8b7355;
  text-align: center;
}

.generating-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  color: #6b5b4f;
}

.error-text {
  color: #ef4444;
  font-size: 14px;
}

/* Loading */
.loading-bubble .dot {
  display: inline-block;
  width: 6px;
  height: 6px;
  background: #8b7355;
  border-radius: 50%;
  margin: 0 3px;
  animation: bounce 1.4s infinite ease-in-out both;
}

.loading-bubble .dot:nth-child(1) { animation-delay: -0.32s; }
.loading-bubble .dot:nth-child(2) { animation-delay: -0.16s; }

@keyframes bounce { 0%, 80%, 100% { transform: scale(0); } 40% { transform: scale(1); } }

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #e8dcc8;
  border-top-color: #8b5a2b;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }

/* 动画 */
.fade-enter-active, .fade-leave-active { transition: opacity 0.3s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

.modal-pop-enter-active { transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1); }
.modal-pop-leave-active { transition: all 0.2s ease-in; }
.modal-pop-enter-from { opacity: 0; transform: translate(-50%, -45%) scale(0.95); }

.scale-fade-enter-active, .scale-fade-leave-active { transition: all 0.3s; }
.scale-fade-enter-from, .scale-fade-leave-to { opacity: 0; transform: scale(0); }

/* 滚动条美化 */
.messages-area::-webkit-scrollbar,
.design-scroll-area::-webkit-scrollbar {
  width: 6px;
}

.messages-area::-webkit-scrollbar-track,
.design-scroll-area::-webkit-scrollbar-track {
  background: #e8dcc8;
  border-radius: 3px;
}

.messages-area::-webkit-scrollbar-thumb,
.design-scroll-area::-webkit-scrollbar-thumb {
  background: #d4a574;
  border-radius: 3px;
}

/* 响应式 */
@media (max-width: 768px) {
  .main-panel {
    width: 95vw;
    height: 85vh;
    border-radius: 16px;
  }

  .panel-header {
    padding: 0 16px;
    height: 60px;
  }

  .header-left .title {
    font-size: 16px;
  }

  .tab-btn {
    padding: 6px 14px;
    font-size: 14px;
  }

  .style-grid {
    grid-template-columns: 1fr;
  }
}
</style>

<style>
.lock-scroll {
  overflow: hidden !important;
  height: 100vh !important;
}
</style>
