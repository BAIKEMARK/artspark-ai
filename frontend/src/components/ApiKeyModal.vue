<template>
  <div id="api-key-modal" class="modal-overlay">
    <div class="modal-content">
      <h2 id="modal-title">{{ apiKeyModal.title }}</h2>
      <p id="modal-description">{{ apiKeyModal.description }}</p>
      <div id="api-key-section">
        <input
          type="password"
          id="api-key-input"
          placeholder="在此输入您的访问令牌"
          v-model="apiKeyInput"
          @keyup.enter="handleSaveApiKey"
        />
        <button id="save-key-btn" @click="handleSaveApiKey" :disabled="isVerifyingApiKey">
          {{ isVerifyingApiKey ? '验证中...' : '进入美术馆' }}
        </button>
        <p id="api-error" class="error-message">{{ apiKeyError }}</p>
      </div>
      <small>可访问 <a href="https://www.modelscope.cn/my/myaccesstoken" target="_blank">获取访问令牌</a>。密钥将安全保存在本地浏览器中。</small>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useAuthStore } from '../stores/auth';

const authStore = useAuthStore();

const apiKeyInput = ref('');
const isVerifyingApiKey = ref(false);
const apiKeyError = ref('');

const apiKeyModal = {
  title: '欢迎来到 艺启智AI',
  description: '请输入您的ModelScope API KEY以激活助教功能。'
};

const emit = defineEmits(['save-api-key']);

const handleSaveApiKey = () => {
  emit('save-api-key', apiKeyInput.value);
};
</script>
