<template>
  <div class="ai-chat-container">
    <!-- 返回按钮 -->
    <div class="back-button-container">
      <button type="button" @click="goBack" class="back-button">
        <span class="back-icon">←</span>
        <span class="back-text">返回</span>
      </button>
    </div>
    
    <!-- 页面加载动画 -->
    <div v-if="isLoadingPage" class="page-loader">
      <div class="loader-content">
        <div class="loader-spinner">
          <div class="spinner"></div>
        </div>
        <h3>智能古灯助手</h3>
        <p>正在加载中...</p>
      </div>
    </div>
    
    <!-- 主聊天窗口 -->
    <div class="chat-window" v-show="!isLoadingPage">
      <!-- 聊天头部 -->
      <div class="chat-header">
        <div class="header-left">
          <div class="avatar-container">
            <div class="ai-avatar">
              <span class="icon">💬</span>
            </div>
            <div class="header-info">
              <h2 class="chat-title">智慧古灯助手</h2>
              <p class="chat-status">在线</p>
            </div>
          </div>
        </div>
        <div class="header-right">
          <button 
            @click="clearChat"
            class="header-btn"
            title="清空聊天"
          >
            <span class="icon">🗑️</span>
          </button>
          <button 
            @click="toggleTheme"
            class="header-btn"
            :title="isDarkTheme ? '切换到浅色模式' : '切换到深色模式'"
          >
            <span class="icon" v-if="isDarkTheme">☀️</span>
            <span class="icon" v-else>🌙</span>
          </button>
        </div>
      </div>
      
      <!-- 聊天消息区域 -->
      <div class="chat-messages" ref="messagesContainer">
        <!-- 欢迎消息 -->
        <div v-if="messages.length === 0" class="welcome-message">
          <div class="welcome-bubble">
            <h3>欢迎使用智慧古灯助手</h3>
            <p>我可以为您解答关于古灯的历史、文化、设计和3D打印等方面的问题。</p>
            <div class="welcome-suggestions">
              <el-button 
                v-for="question in quickQuestions.slice(0, 4)" 
                :key="question" 
                size="small" 
                @click="sendQuickQuestion(question)"
                class="suggestion-btn"
              >
                {{ question }}
              </el-button>
            </div>
          </div>
        </div>
        
        <!-- 聊天消息 -->
        <div 
          v-for="message in messages" 
          :key="message.id" 
          class="message-wrapper"
          :class="message.role"
        >
          <!-- 用户消息 -->
          <div v-if="message.role === 'user'" class="message-container user">
            <div class="message-bubble user-bubble">
              <div class="message-content">{{ message.content }}</div>
              <div class="message-time">{{ formatTime(message.timestamp) }}</div>
            </div>
            <div class="message-avatar user-avatar">
              <el-icon><User /></el-icon>
            </div>
          </div>
          
          <!-- AI消息 -->
          <div v-else class="message-container ai">
            <div class="message-avatar ai-avatar">
              <el-icon><ChatDotRound /></el-icon>
            </div>
            <div class="message-bubble ai-bubble">
              <div class="message-content">{{ message.content }}</div>
              <div class="message-time">{{ formatTime(message.timestamp) }}</div>
            </div>
          </div>
        </div>
        
        <!-- 加载状态 -->
        <div v-if="isLoading" class="loading-container">
          <div class="loading-bubble">
            <div class="loading-spinner">
              <span class="icon loading-icon">⏳</span>
            </div>
            <p>正在思考...</p>
          </div>
        </div>
      </div>
      
      <!-- 输入区域 -->
      <div class="chat-input-area">
        <!-- 工具栏 -->
        <div class="input-toolbar">
          <button 
            @click="toggleEmojiPicker"
            class="toolbar-btn"
            title="表情"
          >
            😊
          </button>
          <button 
            @click="toggleVoiceInput"
            class="toolbar-btn"
            title="语音输入"
          >
            <span class="icon">🎤</span>
          </button>
        </div>
        
        <!-- 表情选择器 -->
        <div v-if="showEmojiPicker" class="emoji-picker">
          <div class="emoji-grid">
            <div 
              v-for="emoji in commonEmojis" 
              :key="emoji" 
              class="emoji-item"
              @click="insertEmoji(emoji)"
            >
              {{ emoji }}
            </div>
          </div>
        </div>
        
        <!-- 语音输入提示 -->
        <div v-if="isVoiceInput" class="voice-input-hint">
          <div class="voice-animation">
            <div class="voice-wave" v-for="i in 5" :key="i" :style="{ '--i': i }"></div>
          </div>
          <p>点击麦克风开始语音输入</p>
        </div>
        
        <!-- 输入框 -->
        <div class="input-container">
          <textarea
            v-model="inputMessage"
            placeholder="输入您的问题..."
            @keyup.enter.exact="sendMessage"
            class="message-input"
            :disabled="isVoiceInput"
            style="z-index: 100;"
          ></textarea>
          <button
            @click="sendMessage"
            :disabled="!inputMessage.trim() || isLoading"
            class="send-button"
            style="z-index: 101;"
            title="发送"
          >
            <span class="icon">➤</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { replyDatabase } from './utils/chatUtils.js'

const router = useRouter()
const goBack = () => router.push('/modern')

// 聊天记录
const messages = ref([])

// 输入消息
const inputMessage = ref('')

// 加载状态
const isLoading = ref(false)

// 页面加载状态
const isLoadingPage = ref(true)

// 消息容器引用
const messagesContainer = ref(null)

// 主题状态
const isDarkTheme = ref(false)

// 表情选择器状态
const showEmojiPicker = ref(false)

// 语音输入状态
const isVoiceInput = ref(false)

// 快速问题
const quickQuestions = [
  '古灯的历史起源是什么？',
  '如何设计一个传统风格的古灯？',
  '3D打印古灯需要注意什么？',
  '古灯在古代的用途有哪些？',
  '不同朝代古灯的特点是什么？',
  '古灯的材料有哪些种类？'
]

// 常用表情
const commonEmojis = [
  '😊', '😃', '😄', '😁', '😆', '😅', '🤣', '😂',
  '🙂', '🙃', '😉', '😇', '😍', '🤩', '😘', '😗',
  '😙', '😚', '😋', '😛', '😝', '😜', '🤪', '🤨',
  '🧐', '🤓', '😎', '🤩', '🥳', '😏', '😒', '😞'
]

// 模拟页面加载
setTimeout(() => {
  isLoadingPage.value = false
}, 1500)

// 发送消息
const sendMessage = async () => {
  const content = inputMessage.value.trim()
  if (!content || isLoading.value) return
  
  // 添加用户消息
  const userMessage = {
    id: Date.now(),
    role: 'user',
    content,
    timestamp: Date.now()
  }
  messages.value.push(userMessage)
  inputMessage.value = ''
  showEmojiPicker.value = false
  
  // 滚动到底部
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
  
  // 显示加载状态
  isLoading.value = true
  
  try {
    // 模拟AI思考时间
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // 调用DeepSeek API获取AI回复
    const aiResponse = await fetchAIResponse(content)
    
    // 添加AI回复
    const aiMessage = {
      id: Date.now() + 1,
      role: 'ai',
      content: aiResponse,
      timestamp: Date.now()
    }
    messages.value.push(aiMessage)
    
    // 滚动到底部
    nextTick(() => {
      if (messagesContainer.value) {
        messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
      }
    })
  } catch (error) {
    console.error('Error fetching AI response:', error)
    
    // 添加错误消息
    const errorMessage = {
      id: Date.now() + 1,
      role: 'ai',
      content: '抱歉，我暂时无法回答您的问题，请稍后再试。',
      timestamp: Date.now()
    }
    messages.value.push(errorMessage)
    
    // 滚动到底部
    nextTick(() => {
      if (messagesContainer.value) {
        messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
      }
    })
  } finally {
    // 隐藏加载状态
    isLoading.value = false
  }
}

// 发送快速问题
const sendQuickQuestion = (question) => {
  inputMessage.value = question
  sendMessage()
}

// 清空对话
const clearChat = () => {
  messages.value = []
}

// 切换主题
const toggleTheme = () => {
  isDarkTheme.value = !isDarkTheme.value
  // 这里可以添加主题切换逻辑
}

// 切换表情选择器
const toggleEmojiPicker = () => {
  showEmojiPicker.value = !showEmojiPicker.value
  isVoiceInput.value = false
}

// 切换语音输入
const toggleVoiceInput = () => {
  isVoiceInput.value = !isVoiceInput.value
  showEmojiPicker.value = false
}

// 插入表情
const insertEmoji = (emoji) => {
  inputMessage.value += emoji
}

// 格式化时间
const formatTime = (timestamp) => {
  const date = new Date(timestamp)
  return date.toLocaleTimeString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 调用后端API获取AI回复
const fetchAIResponse = async (message) => {
  try {
    // 调用后端API
    const response = await fetch('/api/ai/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        message: message
      })
    })
    
    if (!response.ok) {
      throw new Error(`API error: ${response.status}`)
    }
    
    const data = await response.json()
    return data.response
  } catch (error) {
    console.error('Error fetching AI response:', error)
    
    // 错误时使用预设回复
    const responses = replyDatabase.default
    const randomIndex = Math.floor(Math.random() * responses.length)
    return responses[randomIndex]
  }
}
</script>

<style scoped>
.ai-chat-container {
  min-height: 100vh;
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #faf9f5;
  padding: 20px;
  position: relative;
  overflow: hidden;
}

/* 返回按钮 */
.back-button-container {
  position: absolute;
  top: 40px;
  left: 40px;
  z-index: 1000;
}

.back-button {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  background: linear-gradient(135deg, rgba(139, 107, 70, 0.2), rgba(150, 123, 86, 0.2));
  border: 2px solid rgba(139, 107, 70, 0.3);
  border-radius: 24px;
  color: #8b6b46;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(139, 107, 70, 0.2);
  font-family: "SimSun", serif;
}

.back-button:hover {
  background: linear-gradient(135deg, rgba(139, 107, 70, 0.3), rgba(150, 123, 86, 0.3));
  border-color: #8b6b46;
  box-shadow: 0 6px 20px rgba(139, 107, 70, 0.4);
  transform: translateY(-2px);
}

.back-button:active {
  transform: translateY(0);
  box-shadow: 0 2px 10px rgba(139, 107, 70, 0.3);
}

.back-icon {
  font-size: 1.2rem;
  font-weight: bold;
}

.back-text {
  font-size: 0.9rem;
}

.ai-chat-container::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(139, 107, 70, 0.1) 0%, transparent 50%);
  animation: rotate 20s linear infinite;
  pointer-events: none;
}

@keyframes gradientShift {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 页面加载动画 */
.page-loader {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(250, 249, 245, 0.98);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
  backdrop-filter: blur(10px);
}

.loader-content {
  text-align: center;
}

.loader-spinner {
  width: 80px;
  height: 80px;
  margin: 0 auto 20px;
  position: relative;
}

.spinner {
  width: 100%;
  height: 100%;
  border: 4px solid rgba(139, 107, 70, 0.1);
  border-radius: 50%;
  border-top: 4px solid #8b6b46;
  animation: spin 1s linear infinite;
  box-shadow: 0 0 20px rgba(139, 107, 70, 0.3);
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 聊天窗口 */
.chat-window {
  width: 100%;
  max-width: 900px;
  height: 85vh;
  max-height: 800px;
  background: rgba(248, 245, 240, 0.9);
  border: 1px solid rgba(139, 107, 70, 0.3);
  border-radius: 24px;
  box-shadow: 
    0 20px 60px rgba(0, 0, 0, 0.5),
    0 0 40px rgba(139, 107, 70, 0.1),
    inset 0 1px 0 rgba(255, 255, 255, 0.05);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  backdrop-filter: blur(20px);
  position: relative;
}

.chat-window::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(139, 107, 70, 0.5), transparent);
}

/* 聊天头部 */
.chat-header {
  background: linear-gradient(135deg, rgba(139, 107, 70, 0.15), rgba(150, 123, 86, 0.15));
  color: #5d4037;
  padding: 20px 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  border-bottom: 1px solid rgba(139, 107, 70, 0.2);
  position: relative;
  z-index: 10;
}

.chat-header::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(139, 107, 70, 0.4), transparent);
}

.avatar-container {
  display: flex;
  align-items: center;
  gap: 16px;
}

.ai-avatar {
  width: 52px;
  height: 52px;
  border-radius: 50%;
  background: linear-gradient(135deg, rgba(139, 107, 70, 0.3), rgba(150, 123, 86, 0.3));
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 1.6rem;
  color: #8b6b46;
  box-shadow: 
    0 4px 12px rgba(139, 107, 70, 0.3),
    inset 0 1px 0 rgba(255, 255, 255, 0.2);
  border: 2px solid rgba(139, 107, 70, 0.4);
  position: relative;
  overflow: hidden;
}

.ai-avatar::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: linear-gradient(45deg, transparent, rgba(255, 255, 255, 0.1), transparent);
  animation: shimmer 3s infinite;
}

@keyframes shimmer {
  0% { transform: translateX(-100%) rotate(45deg); }
  100% { transform: translateX(100%) rotate(45deg); }
}

.header-info {
  display: flex;
  flex-direction: column;
}

.chat-title {
  font-size: 1.2rem;
  font-weight: 600;
  margin: 0;
  color: #5d4037;
}

.chat-status {
  font-size: 0.8rem;
  opacity: 0.8;
  margin: 0;
  color: #8b6b46;
}

.header-right {
  display: flex;
  gap: 8px;
}

.header-btn {
  color: #8b6b46;
  border-color: rgba(139, 107, 70, 0.3);
  background: rgba(248, 245, 240, 0.6);
}

.header-btn:hover {
  border-color: #8b6b46;
  color: #8b6b46;
  background: rgba(248, 245, 240, 0.8);
}

/* 聊天消息区域 */
.chat-messages {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
  background: rgba(248, 245, 240, 0.7);
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.chat-messages::-webkit-scrollbar {
  width: 8px;
}

.chat-messages::-webkit-scrollbar-track {
  background: rgba(248, 245, 240, 0.6);
  border-radius: 4px;
}

.chat-messages::-webkit-scrollbar-thumb {
  background: linear-gradient(180deg, rgba(139, 107, 70, 0.4), rgba(150, 123, 86, 0.4));
  border-radius: 4px;
  border: 1px solid rgba(139, 107, 70, 0.3);
}

.chat-messages::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(180deg, rgba(139, 107, 70, 0.6), rgba(150, 123, 86, 0.6));
}

/* 欢迎消息 */
.welcome-message {
  display: flex;
  justify-content: center;
  padding: 40px 20px;
}

.welcome-bubble {
  background: linear-gradient(135deg, rgba(248, 245, 240, 0.9), rgba(232, 224, 213, 0.9));
  border: 1px solid rgba(139, 107, 70, 0.3);
  border-radius: 24px;
  padding: 32px;
  max-width: 80%;
  text-align: center;
  box-shadow: 
    0 8px 24px rgba(0, 0, 0, 0.3),
    0 0 40px rgba(139, 107, 70, 0.1);
  position: relative;
  overflow: hidden;
}

.welcome-bubble::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(139, 107, 70, 0.05) 0%, transparent 50%);
  animation: pulse 4s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 0.5; transform: scale(1); }
  50% { opacity: 1; transform: scale(1.1); }
}

.welcome-bubble h3 {
  margin: 0 0 16px;
  color: #8b6b46;
  font-size: 1.4rem;
  font-weight: 700;
  text-shadow: 0 0 20px rgba(139, 107, 70, 0.3);
  position: relative;
}

.welcome-bubble p {
  margin: 0 0 24px;
  color: #8b6b46;
  line-height: 1.6;
  font-size: 1rem;
  position: relative;
}

.welcome-suggestions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: center;
  position: relative;
}

.suggestion-btn {
  font-size: 0.85rem;
  padding: 8px 16px;
  border-radius: 20px;
  background: linear-gradient(135deg, rgba(248, 245, 240, 0.8), rgba(232, 224, 213, 0.8));
  border-color: rgba(139, 107, 70, 0.4);
  color: #8b6b46;
  border: 1px solid rgba(139, 107, 70, 0.3);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.suggestion-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(139, 107, 70, 0.2), transparent);
  transition: left 0.5s;
}

.suggestion-btn:hover::before {
  left: 100%;
}

.suggestion-btn:hover {
  background: linear-gradient(135deg, rgba(139, 107, 70, 0.2), rgba(150, 123, 86, 0.2));
  border-color: #8b6b46;
  box-shadow: 
    0 4px 16px rgba(139, 107, 70, 0.4),
    0 0 20px rgba(139, 107, 70, 0.2);
  transform: translateY(-2px);
}

/* 消息样式 */
.message-wrapper {
  display: flex;
  animation: messageSlideIn 0.3s ease;
}

.message-wrapper.user {
  justify-content: flex-end;
}

.message-wrapper.ai {
  justify-content: flex-start;
}

@keyframes messageSlideIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message-container {
  display: flex;
  max-width: 75%;
  gap: 14px;
  align-items: flex-end;
}

.message-container.user {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 1.3rem;
  flex-shrink: 0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.user-avatar {
  background: linear-gradient(135deg, rgba(139, 107, 70, 0.3), rgba(150, 123, 86, 0.3));
  color: #8b6b46;
  border: 2px solid rgba(139, 107, 70, 0.4);
}

.ai-avatar {
  background: linear-gradient(135deg, rgba(139, 107, 70, 0.2), rgba(150, 123, 86, 0.2));
  color: #8b6b46;
  border: 2px solid rgba(139, 107, 70, 0.3);
}

.message-bubble {
  background: linear-gradient(135deg, rgba(248, 245, 240, 0.9), rgba(232, 224, 213, 0.9));
  border: 1px solid rgba(139, 107, 70, 0.25);
  border-radius: 20px;
  padding: 14px 18px;
  box-shadow: 
    0 4px 16px rgba(0, 0, 0, 0.3),
    0 0 30px rgba(139, 107, 70, 0.05);
  position: relative;
  max-width: 100%;
  transition: all 0.3s ease;
}

.message-bubble:hover {
  box-shadow: 
    0 6px 20px rgba(0, 0, 0, 0.4),
    0 0 40px rgba(139, 107, 70, 0.1);
}

.user-bubble {
  background: linear-gradient(135deg, rgba(139, 107, 70, 0.25), rgba(150, 123, 86, 0.25));
  color: #5d4037;
  border-bottom-right-radius: 6px;
  border-color: rgba(139, 107, 70, 0.4);
  box-shadow: 
    0 4px 16px rgba(139, 107, 70, 0.2),
    0 0 30px rgba(139, 107, 70, 0.1);
}

.ai-bubble {
  color: #5d4037;
  border-bottom-left-radius: 6px;
}

.message-content {
  font-size: 0.95rem;
  line-height: 1.4;
  margin-bottom: 8px;
  word-break: break-word;
  color: #5d4037;
}

.message-time {
  font-size: 0.7rem;
  opacity: 0.7;
  text-align: right;
  color: #8b6b46;
}

/* 加载状态 */
.loading-container {
  display: flex;
  justify-content: flex-start;
  padding: 10px 0;
}

.loading-bubble {
  background: linear-gradient(135deg, rgba(248, 245, 240, 0.9), rgba(232, 224, 213, 0.9));
  border: 1px solid rgba(139, 107, 70, 0.25);
  border-radius: 20px;
  padding: 14px 18px;
  box-shadow: 
    0 4px 16px rgba(0, 0, 0, 0.3),
    0 0 30px rgba(139, 107, 70, 0.05);
  display: flex;
  align-items: center;
  gap: 10px;
  border-bottom-left-radius: 6px;
}

.loading-spinner {
  font-size: 1.1rem;
  color: #8b6b46;
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 0.6; }
  50% { opacity: 1; }
}

/* 输入区域 */
.chat-input-area {
  background: linear-gradient(135deg, rgba(248, 245, 240, 0.9), rgba(232, 224, 213, 0.9));
  border-top: 1px solid rgba(139, 107, 70, 0.3);
  padding: 16px 24px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  position: relative;
}

.chat-input-area::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(139, 107, 70, 0.4), transparent);
}

.input-toolbar {
  display: flex;
  gap: 10px;
}

.toolbar-btn {
  border-color: rgba(139, 107, 70, 0.3);
  background: linear-gradient(135deg, rgba(248, 245, 240, 0.8), rgba(232, 224, 213, 0.8));
  color: #8b6b46;
  border: 1px solid rgba(139, 107, 70, 0.25);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.toolbar-btn:hover {
  border-color: #8b6b46;
  color: #8b6b46;
  background: linear-gradient(135deg, rgba(139, 107, 70, 0.15), rgba(150, 123, 86, 0.15));
  box-shadow: 
    0 4px 12px rgba(139, 107, 70, 0.3),
    0 0 20px rgba(139, 107, 70, 0.15);
  transform: translateY(-2px);
}

/* 表情选择器 */
.emoji-picker {
  background: linear-gradient(135deg, rgba(248, 245, 240, 0.95), rgba(232, 224, 213, 0.95));
  border: 1px solid rgba(139, 107, 70, 0.3);
  border-radius: 16px;
  padding: 16px;
  box-shadow: 
    0 8px 24px rgba(0, 0, 0, 0.4),
    0 0 40px rgba(139, 107, 70, 0.1);
  backdrop-filter: blur(10px);
}

.emoji-grid {
  display: grid;
  grid-template-columns: repeat(8, 1fr);
  gap: 10px;
}

.emoji-item {
  font-size: 1.3rem;
  text-align: center;
  padding: 10px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  background: linear-gradient(135deg, rgba(248, 245, 240, 0.8), rgba(232, 224, 213, 0.8));
  border: 1px solid rgba(139, 107, 70, 0.2);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.emoji-item:hover {
  background: linear-gradient(135deg, rgba(139, 107, 70, 0.2), rgba(150, 123, 86, 0.2));
  border-color: rgba(139, 107, 70, 0.5);
  transform: translateY(-3px) scale(1.1);
  box-shadow: 
    0 6px 16px rgba(139, 107, 70, 0.3),
    0 0 20px rgba(139, 107, 70, 0.2);
}

/* 语音输入提示 */
.voice-input-hint {
  text-align: center;
  padding: 16px;
  background: rgba(248, 245, 240, 0.6);
  border: 1px solid rgba(139, 107, 70, 0.2);
  border-radius: 12px;
}

.voice-animation {
  display: flex;
  justify-content: center;
  gap: 6px;
  margin-bottom: 8px;
}

.voice-wave {
  width: 4px;
  height: 20px;
  background: #8b6b46;
  border-radius: 2px;
  animation: voiceWave 1.5s ease-in-out infinite;
  animation-delay: calc(var(--i) * 0.1s);
}

@keyframes voiceWave {
  0%, 100% {
    transform: scaleY(0.3);
    opacity: 0.5;
  }
  50% {
    transform: scaleY(1);
    opacity: 1;
  }
}

/* 输入框容器 */
.input-container {
  display: flex;
  gap: 12px;
  align-items: center;
}

.message-input {
  flex: 1;
  border-radius: 24px;
  border: 1px solid rgba(139, 107, 70, 0.3);
  background: linear-gradient(135deg, rgba(248, 245, 240, 0.8), rgba(232, 224, 213, 0.8));
  color: #5d4037;
  padding: 12px 20px;
  font-size: 0.95rem;
  resize: none;
  min-height: 48px;
  max-height: 120px;
  overflow-y: auto;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.message-input:focus {
  border-color: #8b6b46;
  box-shadow: 
    0 0 0 3px rgba(139, 107, 70, 0.2),
    0 4px 12px rgba(139, 107, 70, 0.3);
  outline: none;
  background: linear-gradient(135deg, rgba(248, 245, 240, 0.9), rgba(232, 224, 213, 0.9));
}

.message-input::placeholder {
  color: #8b6b46;
}

.send-button {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: linear-gradient(135deg, #8b6b46, #967b56);
  border: none;
  color: white;
  flex-shrink: 0;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
  box-shadow: 
    0 4px 12px rgba(139, 107, 70, 0.4),
    0 0 20px rgba(139, 107, 70, 0.2);
}

.send-button::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: linear-gradient(45deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  transform: rotate(45deg);
  transition: all 0.6s ease;
  opacity: 0;
}

.send-button:hover::before {
  left: 130%;
  opacity: 1;
}

.send-button:hover {
  transform: translateY(-3px) scale(1.05);
  box-shadow: 
    0 8px 24px rgba(139, 107, 70, 0.5),
    0 0 40px rgba(139, 107, 70, 0.3);
}

.send-button:active {
  transform: translateY(-1px) scale(1.02);
}

.send-button:disabled {
  background: linear-gradient(135deg, rgba(248, 245, 240, 0.8), rgba(232, 224, 213, 0.8));
  border: 1px solid rgba(139, 107, 70, 0.2);
  color: #8b6b46;
  cursor: not-allowed;
  box-shadow: none;
}

.send-button:disabled:hover {
  transform: none;
  box-shadow: none;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .ai-chat-container {
    padding: 0;
    min-height: 100vh;
  }
  
  .chat-window {
    width: 100%;
    height: 100vh;
    max-height: none;
    border-radius: 0;
    border: none;
  }
  
  .chat-messages {
    padding: 16px;
  }
  
  .message-container {
    max-width: 85%;
  }
  
  .chat-input-area {
    padding: 10px 16px;
  }
}

@media (max-width: 480px) {
  .chat-header {
    padding: 12px 16px;
  }
  
  .ai-avatar {
    width: 40px;
    height: 40px;
  }
  
  .chat-title {
    font-size: 1rem;
  }
  
  .chat-messages {
    padding: 12px;
  }
  
  .message-content {
    font-size: 0.9rem;
  }
  
  .welcome-bubble {
    max-width: 95%;
    padding: 16px;
  }
  
  .welcome-suggestions {
    flex-direction: column;
    align-items: center;
  }
  
  .suggestion-btn {
    width: 100%;
    max-width: 200px;
  }
}
</style>