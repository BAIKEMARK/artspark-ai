<template>
  <section id="art-qa" class="chat-page-container">

    <div class="chat-page-header">
      <h2 class="chat-page-title">艺术小百科</h2>
      <el-button @click="clearHistory" link type="info" size="small" class="clear-btn">
        <el-icon><Delete /></el-icon>
        <span>清空对话</span>
      </el-button>
    </div>

    <el-scrollbar ref="scrollbarRef" class="chat-window">
      <div ref="chatContentRef" class="chat-content-wrapper">
        <div class="chat-message assistant">
          <div class="message-bubble" v-html="marked(welcomeMessage)"></div>
        </div>

        <div v-if="messages.length === 0" class="suggestion-chips">
          <el-card
            shadow="hover"
            v-for="chip in suggestionChips"
            :key="chip"
            class="suggestion-chip"
            @click="askSuggestion(chip)"
          >
            {{ chip }}
          </el-card>
        </div>

        <div
          v-for="(message, index) in messages"
          :key="index"
          class="chat-message"
          :class="message.role"
        >
          <div class="message-bubble" v-html="formatMessage(message.content)"></div>
        </div>

        <div v-if="isLoading" class="chat-message assistant">
          <div class="message-bubble loading-bubble">
            <el-icon class="is-loading"><Loading /></el-icon>
            <span>小艺正在思考...</span>
          </div>
        </div>
      </div>
    </el-scrollbar>

    <el-alert
      v-if="error"
      :title="error"
      type="error"
      show-icon
      :closable="true"
      @close="error = ''"
      class="chat-error-alert"
    />

    <div class="chat-input-area">
      <div class="input-wrapper">
        <el-input
          v-model="currentQuestion"
          placeholder="问小艺任何关于艺术的问题..."
          @keyup.enter="ask"
          :disabled="isLoading"
          size="large"
        >
          <template #append>
            <el-button @click="ask" :loading="isLoading" :icon="Promotion" />
          </template>
        </el-input>
      </div>
    </div>
  </section>
</template>

<script setup>
// <script> 部分与上一步完全相同，无需修改
import { ref, nextTick, watch } from 'vue';
import { useAIApi } from '../composables/useAIApi.js';
import { marked } from 'marked';
import { Promotion, Loading, Delete } from '@element-plus/icons-vue';

const currentQuestion = ref('');
const messages = ref([]);
const welcomeMessage = "你好呀！我是你的艺术老师小艺。你对什么艺术知识感兴趣呢？";
const suggestionChips = ref([
  '什么是印象派？',
  '梵高为什么出名？',
  '水墨画有什么特点？',
]);

const { isLoading, error, result, execute } = useAIApi('/api/ask-question');

const scrollbarRef = ref(null);
const chatContentRef = ref(null);

const scrollToBottom = async () => {
  await nextTick();
  if (scrollbarRef.value && chatContentRef.value) {
    scrollbarRef.value.setScrollTop(chatContentRef.value.scrollHeight);
  }
};

watch([messages, isLoading], scrollToBottom, { deep: true });

const formatMessage = (content) => {
  return marked(content);
};

async function askSuggestion(suggestion) {
  if (isLoading.value) return;
  currentQuestion.value = suggestion;
  await ask();
}

async function ask() {
  if (!currentQuestion.value || isLoading.value) {
    return;
  }
  const userMessage = { role: 'user', content: currentQuestion.value };
  messages.value.push(userMessage);
  const historyToSend = [...messages.value];
  const questionBeingAsked = currentQuestion.value;
  currentQuestion.value = '';
  try {
    const apiResponse = await execute({ messages: historyToSend });
    if (apiResponse && apiResponse.choices && apiResponse.choices[0].message) {
      const assistantMessage = apiResponse.choices[0].message;
      messages.value.push(assistantMessage);
      error.value = '';
    } else {
      throw new Error('AI未能返回有效的回答');
    }
  } catch (e) {
    console.error(e);
    messages.value.pop();
    currentQuestion.value = questionBeingAsked;
  }
}

function clearHistory() {
  messages.value = [];
  error.value = '';
  currentQuestion.value = '';
  if (scrollbarRef.value) {
    scrollbarRef.value.setScrollTop(0);
  }
}
</script>

<style scoped>
/* 1. 根容器：基础玻璃层 */
.chat-page-container {
  display: flex;
  flex-direction: column;
  width: 100%;
  /* 移除了 1000px 的固定最小高度，改为更灵活的视口高度 */
  min-height: 75vh;
  flex-grow: 1; /* 填充可用空间 */

  /* 基础玻璃样式 (更通透) */
  background-color: rgba(44, 62, 80, 0.1); /* 降低不透明度 */
  backdrop-filter: blur(10px); /* 降低模糊度 */
  border: 1px solid rgba(255, 255, 255, 0.1); /* 更微妙的边框 */
  border-radius: 12px;
  overflow: hidden;
}

/* 2. 页面页眉 (保持不变，作为基础层的一部分) */
.chat-page-header {
  flex-shrink: 0;
  width: 100%;
  z-index: 2;
  background: transparent;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  padding: 15px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-sizing: border-box;
}
.chat-page-header .chat-page-title {
  font-family: var(--font-serif);
  color: #FFFFFF;
  text-shadow: 0 1px 3px rgba(0,0,0,0.5);
  margin: 0;
  padding: 0;
  border: none;
  font-size: 1.5rem;
  flex-grow: 1;
}
.chat-page-header .clear-btn {
  color: #FFFFFF;
  opacity: 0.8;
  transition: opacity 0.3s ease;
  margin: 0;
  flex-shrink: 0;
}
.chat-page-header .clear-btn:hover {
  opacity: 1;
}

/* 3. 滚动区域 */
.chat-window {
  flex-grow: 1;
  width: 100%;
  overflow-y: auto;
  z-index: 1;
  background: transparent;
}

/* 4. 聊天内容包装器 */
.chat-content-wrapper {
  max-width: 960px;
  margin: 0 auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 15px;
  box-sizing: border-box;
}

/* 5. 建议卡片 (更新为 "胶囊" 样式) */
.suggestion-chips {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 10px;
  margin-top: 5px;
  margin-bottom: 10px;
}
.suggestion-chip {
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 500;
  transition: all 0.2s ease;

  /* "胶囊" 玻璃样式 */
  background-color: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(5px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: rgba(255, 255, 255, 0.9);
  text-shadow: none;
  border-radius: 16px; /* 更圆润 */
}
.suggestion-chip:hover {
  transform: translateY(-2px);
  background-color: rgba(255, 255, 255, 0.3);
  border-color: rgba(255, 255, 255, 0.4);
}
.suggestion-chip :deep(.el-card__body) {
  padding: 15px;
}

/* 6. 聊天气泡 (核心更新：次级浮动玻璃) */
.chat-message {
  display: flex;
  flex-direction: column;
}
.message-bubble {
  padding: 12px 18px; /* 增加内边距 */
  border-radius: 12px;
  line-height: 1.8; /* 增加行高 */
  max-width: 85%;
  word-wrap: break-word;

  /* 次级玻璃质感 */
  backdrop-filter: blur(5px);
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  /* 使用更亮的边框来模拟高光 */
  border: 1px solid rgba(255, 255, 255, 0.2);
}
/* AI 助手气泡 (半透明亮色) */
.chat-message.assistant .message-bubble {
  background-color: rgba(255, 255, 255, 0.7);
  color: var(--dark-text);
  /* 移除旧边框 */
}
/* 用户气泡 (半透明暗色) */
.chat-message.user .message-bubble {
  background-color: rgba(52, 73, 94, 0.8); /* 基于 --primary-color */
  color: white;
  /* 移除旧边框 */
}
.loading-bubble {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--el-text-color-secondary);
}

/* 7. 错误提示 */
.chat-error-alert {
  max-width: 960px;
  margin: 0 auto 10px auto;
  flex-shrink: 0;
  box-sizing: border-box;
  width: calc(100% - 40px);
  z-index: 2;
  background-color: rgba(245, 108, 108, 0.2);
  border: 1px solid rgba(245, 108, 108, 0.5);
  color: white;
  text-shadow: 0 1px 2px rgba(0,0,0,0.3);
}
.chat-error-alert :deep(.el-alert__title) { color: white; }
.chat-error-alert :deep(.el-alert__icon) { color: white !important; }

/* 8. 输入区域 */
.chat-input-area {
  flex-shrink: 0;
  z-index: 2;
  background: transparent;
  border-top: 1px solid rgba(255, 255, 255, 0.2);
}
.input-wrapper {
  max-width: 960px;
  margin: 0 auto;
  padding: 15px 20px;
  position: relative;
}

/* 9. 输入框样式 */
.input-wrapper :deep(.el-input__wrapper) {
  background-color: rgba(255, 255, 255, 0.9) !important; /* 更不透明 */
  border: 1px solid rgba(255, 255, 255, 0.4) !important;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05) !important; /* 增加阴影 */
}
.input-wrapper :deep(.el-input__inner) {
  color: var(--dark-text) !important;
  font-weight: 500;
}
.input-wrapper :deep(.el-input-group__append) {
  background-color: rgba(255, 255, 255, 0.9) !important; /* 同上 */
  border: 1px solid rgba(255, 255, 255, 0.4) !important;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05) !important; /* 同上 */
  border-left: none;
}
/* 确保发送按钮在悬停时颜色正确 */
.input-wrapper :deep(.el-button) {
  color: var(--el-text-color-regular);
}
.input-wrapper :deep(.el-button:hover) {
  color: var(--el-color-primary);
}


/* 10. Markdown 样式  */
.message-bubble :deep(p) { margin: 0.5em 0; }
.message-bubble :deep(ul),
.message-bubble :deep(ol) { padding-left: 20px; }
.message-bubble :deep(p:first-child) { margin-top: 0; }
.message-bubble :deep(p:last-child) { margin-bottom: 0; }

/* 11. 滚动条 */
.chat-window :deep(.el-scrollbar__thumb) {
  background-color: rgba(255, 255, 255, 0.3);
  border-radius: 4px;
}
.chat-window :deep(.el-scrollbar__thumb:hover) {
  background-color: rgba(255, 255, 255, 0.5);
}
</style>