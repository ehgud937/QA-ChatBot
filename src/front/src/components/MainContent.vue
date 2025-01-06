<!-- src/components/MainContent.vue -->
<template>
    <main class="main-content">
      <div class="chat-window">
        <div v-for="(message, index) in messages" :key="index" :class="['message', message.sender]">
          {{ message.text }}
        </div>
      </div>
      <div class="input-area">
        <input v-model="userInput" @keyup.enter="sendMessage" placeholder="메시지를 입력하세요" />
        <button @click="sendMessage">전송</button>
      </div>
    </main>
  </template>
  
  <script>
  // import { ref } from 'vue';
  // import api from '../services/api';
  
  // export default {
  //   name: 'MainContent',
  //   setup() {
  //     const messages = ref([]);
  //     const userInput = ref('');
  
  //     const sendMessage = async () => {
  //       if (userInput.value.trim() === '') return;
  //       // 사용자 메시지 추가
  //       messages.value.push({ text: userInput.value, sender: 'user-message' });
        
  //       // API 요청 보내기
  //       try {
  //         const response = await api.sendMessage(userInput.value);
  //         messages.value.push({ text: response.data.reply, sender: 'bot-message' });
  //       } catch (error) {
  //         console.error('API 요청 에러:', error);
  //         messages.value.push({ text: '에러가 발생했습니다.', sender: 'bot-message' });
  //       }
        
  //       userInput.value = '';
  //     };
  
  //     return {
  //       messages,
  //       userInput,
  //       sendMessage,
  //     };
  //   },
  // };
  </script>
  
  <style scoped>
  .main-content {
    flex: 1;
    padding: 20px;
    background-color: #e3f2fd;
    display: flex;
    flex-direction: column;
    height: 100vh;
  }
  
  .chat-window {
    flex: 1;
    overflow-y: auto;
    margin-bottom: 10px;
    display: flex;
    flex-direction: column;
  }
  
  .message {
    border-radius: 15px;
    padding: 10px;
    margin: 5px 0;
    max-width: 60%;
  }
  
  .user-message {
    background-color: #bbdefb;
    align-self: flex-end;
  }
  
  .bot-message {
    background-color: #c8e6c9;
    align-self: flex-start;
  }
  
  .input-area {
    display: flex;
  }
  
  .input-area input {
    flex: 1;
    padding: 10px;
    border: 1px solid #0d47a1;
    border-radius: 5px 0 0 5px;
  }
  
  .input-area button {
    padding: 10px;
    background-color: #0d47a1;
    color: white;
    border: none;
    border-radius: 0 5px 5px 0;
    cursor: pointer;
  }
  
  .input-area button:hover {
    background-color: #1565c0;
  }
  </style>
  