<template>
  <div class="app-container">
    <div class="header">
      <div class="logo">
        <span class="icon">💡</span>
        <h1>SSAFY 학사규정 도우미</h1>
      </div>
    </div>
 
    <div class="chat-container">
      <div class="chat-messages" ref="chatContainer">
        <div v-if="messages.length === 0" class="welcome-message">
          <div class="welcome-card">
            <h2>무엇이든 물어보세요!</h2>
            <p>SSAFY 학사규정과 관련된 질문에 답변해드립니다.</p>
            <div class="example-questions">
              <button @click="setExample('출석체크는 몇 시까지 해야 하나요?')">
                출석체크 시간
              </button>
              <button @click="setExample('배우자 출산 시 휴가는 며칠인가요?')">
                경조사 휴가
              </button>
              <button @click="setExample('점심시간은 언제인가요?')">
                점심시간
              </button>
            </div>
          </div>
        </div>
        
        <div v-for="(message, index) in messages" 
             :key="index" 
             :class="['message', message.type]">
          <div class="avatar" :class="message.type">
            {{ message.type === 'user' ? '👤' : '🤖' }}
          </div>
          <div class="message-content">{{ message.content }}</div>
        </div>
      </div>
 
      <div class="input-container">
        <input 
          v-model="userInput" 
          placeholder="무엇이 궁금하신가요?" 
          @keyup.enter="sendMessage"
          :disabled="isLoading"
        />
        <button 
          class="send-button" 
          @click="sendMessage" 
          :disabled="isLoading || !userInput.trim()"
        >
          <span v-if="!isLoading">전송</span>
          <span v-else class="loading">
            <span class="dot"></span>
            <span class="dot"></span>
            <span class="dot"></span>
          </span>
        </button>
        <button @click="resetChat" class="reset-button">
          초기화
        </button>
      </div>
    </div>
  </div>
 </template>
 
 <script setup>
 import { ref, watch, nextTick } from 'vue'
 import axios from 'axios'
 
 const userInput = ref('')
 const messages = ref([])
 const isLoading = ref(false)
 const chatContainer = ref(null)
 const chatId = 'default'
 
 const setExample = (question) => {
  userInput.value = question
 }
 
 const scrollToBottom = async () => {
  await nextTick()
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight
  }
 }
 
 watch(messages, () => {
  scrollToBottom()
 }, { deep: true })
 
 const sendMessage = async () => {
  if (!userInput.value.trim() || isLoading.value) return
 
  const userMessage = userInput.value
  messages.value.push({ type: 'user', content: userMessage })
  userInput.value = ''
  isLoading.value = true
 
  try {
    const response = await axios.post('https://ssafychat.kro.kr/api/chat', {
      text: userMessage,
      chat_id: chatId
    })
    
    messages.value.push({ type: 'assistant', content: response.data.response })
  } catch (error) {
    messages.value.push({ 
      type: 'assistant', 
      content: '오류가 발생했습니다: ' + error.message 
    })
  } finally {
    isLoading.value = false
  }
 }
 
 const resetChat = async () => {
  try {
    await axios.post('https://ssafychat.kro.kr/api/reset-chat', {
      chat_id: chatId
    })
    messages.value = []
  } catch (error) {
    messages.value.push({ 
      type: 'assistant', 
      content: '대화 초기화 중 오류가 발생했습니다.' 
    })
  }
 }
 </script>
 
 <style>
 @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
 
 :root {
  --primary-color: #4A90E2;
  --primary-light: #5C9CE5;
  --primary-dark: #357ABD;
  --background-light: #F5F7FA;
  --text-dark: #2C3E50;
  --text-light: #FFFFFF;
  --danger-color: #E74C3C;
  --success-color: #2ECC71;
  --border-color: #E1E8ED;
  --max-width: 1200px;
  --header-height: 70px;
  --shadow-sm: 0 2px 4px rgba(0,0,0,0.1);
  --shadow-md: 0 4px 6px rgba(0,0,0,0.1);
  --shadow-lg: 0 10px 15px rgba(0,0,0,0.1);
 }
 
 * {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
  font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, Roboto, sans-serif;
 }
 
 .app-container {
  min-height: 100vh;
  background: var(--background-light);
  color: var(--text-dark);
  display: flex;
  flex-direction: column;
 }
 
 .header {
  height: var(--header-height);
  background: var(--text-light);
  border-bottom: 1px solid var(--border-color);
  position: fixed;
  top: 0;
  width: 100%;
  z-index: 100;
  box-shadow: var(--shadow-sm);
 }
 
 .logo {
  max-width: var(--max-width);
  margin: 0 auto;
  padding: 0 20px;
  height: 100%;
  display: flex;
  align-items: center;
  gap: 12px;
 }
 
 .logo h1 {
  font-size: 24px;
  color: var(--text-dark);
  font-weight: 600;
 }
 
 .chat-container {
  max-width: var(--max-width);
  width: 100%;
  margin: var(--header-height) auto 0;
  flex: 1;
  display: flex;
  flex-direction: column;
  position: relative;
  padding: 20px;
 }
 
 .chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px 0;
  display: flex;
  flex-direction: column;
  gap: 20px;
 }
 
 .welcome-card {
  background: var(--text-light);
  border-radius: 16px;
  padding: 30px;
  text-align: center;
  box-shadow: var(--shadow-md);
  margin: 20px auto;
  max-width: 600px;
  width: 90%;
 }
 
 .welcome-card h2 {
  font-size: 28px;
  color: var(--primary-color);
  margin-bottom: 12px;
  font-weight: 700;
 }
 
 .welcome-card p {
  color: var(--text-dark);
  margin-bottom: 24px;
  font-size: 16px;
 }
 
 .example-questions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  justify-content: center;
 }
 
 .example-questions button {
  background: var(--primary-light);
  color: var(--text-light);
  padding: 12px 20px;
  border-radius: 25px;
  border: none;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 14px;
  font-weight: 500;
 }
 
 .example-questions button:hover {
  background: var(--primary-dark);
  transform: translateY(-2px);
 }
 
 .message {
  display: flex;
  gap: 12px;
  max-width: 70%;
  animation: slideIn 0.3s ease-out;
  padding: 0 20px;
 }
 
 .message.user {
  margin-left: auto;
  flex-direction: row-reverse;
 }
 
 .avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  flex-shrink: 0;
  background: var(--primary-light);
 }
 
 .avatar.user {
  background: var(--success-color);
 }
 
 .message-content {
  padding: 15px 20px;
  border-radius: 15px;
  background: var(--text-light);
  box-shadow: var(--shadow-sm);
  line-height: 1.5;
  font-size: 15px;
 }
 
 .user .message-content {
  background: var(--primary-color);
  color: var(--text-light);
 }
 
 .input-container {
  margin-top: 20px;
  padding: 20px;
  background: var(--text-light);
  border-radius: 12px;
  box-shadow: var(--shadow-lg);
  display: flex;
  gap: 12px;
 }
 
 input {
  flex: 1;
  padding: 12px 20px;
  border: 2px solid var(--border-color);
  border-radius: 8px;
  font-size: 16px;
  transition: all 0.3s ease;
  color: var(--text-dark);
 }
 
 input:focus {
  border-color: var(--primary-color);
  outline: none;
 }
 
 .send-button, .reset-button {
  padding: 12px 24px;
  border-radius: 8px;
  border: none;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
 }
 
 .send-button {
  background: var(--primary-color);
  color: var(--text-light);
 }
 
 .send-button:hover:not(:disabled) {
  background: var(--primary-dark);
 }
 
 .reset-button {
  background: var(--danger-color);
  color: var(--text-light);
 }
 
 .reset-button:hover {
  background: #c0392b;
 }
 
 .loading {
  display: flex;
  gap: 4px;
 }
 
 .dot {
  width: 6px;
  height: 6px;
  background: var(--text-light);
  border-radius: 50%;
  animation: bounce 1s infinite;
 }
 
 .dot:nth-child(2) {
  animation-delay: 0.2s;
 }
 
 .dot:nth-child(3) {
  animation-delay: 0.4s;
 }
 
 @keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
 }
 
 @keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-5px); }
 }
 
 /* 반응형 디자인 */
 @media (max-width: 1200px) {
  .chat-container {
    padding: 10px;
  }
  
  .message {
    max-width: 85%;
  }
 }
 
 @media (max-width: 768px) {
  .logo h1 {
    font-size: 20px;
  }
  
  .welcome-card {
    padding: 20px;
  }
  
  .welcome-card h2 {
    font-size: 24px;
  }
  
  .message {
    max-width: 90%;
    padding: 0 10px;
  }
  
  .input-container {
    padding: 15px;
    flex-wrap: wrap;
  }
  
  input {
    width: 100%;
  }
  
  .send-button, .reset-button {
    flex: 1;
    padding: 10px 15px;
  }
 }
 
 @media (max-width: 480px) {
  .header {
    height: 60px;
  }
  
  .logo {
    padding: 0 15px;
  }
  
  .logo h1 {
    font-size: 18px;
  }
  
  .welcome-card h2 {
    font-size: 20px;
  }
  
  .message {
    max-width: 95%;
  }
  
  .message-content {
    font-size: 14px;
    padding: 12px 15px;
  }
  
  .avatar {
    width: 35px;
    height: 35px;
    font-size: 18px;
  }
 }
 </style>