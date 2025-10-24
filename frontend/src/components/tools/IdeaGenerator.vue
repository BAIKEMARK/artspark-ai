<template>
  <section id="idea-generator" class="feature-panel">
    <h2>创意灵感生成器</h2>
    <div class="form-group">
      <label for="idea-theme-input">灵感主题:</label>
      <input type="text" id="idea-theme-input" placeholder="例如：春天, 节日" v-model="theme" @keyup.enter="generate" />
    </div>
    <button id="generate-ideas-btn" class="cta-btn" @click="generate" :disabled="isLoading">生成灵感</button>
    <div class="loader" v-if="isLoading"></div>
    <p class="error-message">{{ error }}</p>
    <div id="ideas-result" class="result-container" v-if="result?.length > 0">
      <div class="idea-card" v-for="(idea, index) in result" :key="index">
        <img :src="idea.exampleImage || 'https://via.placeholder.com/256x256?text=Image'" :alt="idea.name" />
        <h3>{{ idea.name }}</h3>
        <p>{{ idea.description }}</p>
        <small>关键元素: {{ idea.elements }}</small>
        <a v-if="idea.exampleImage" :href="getDownloadUrl(idea.exampleImage)" class="download-btn" :download="`${idea.name.replace(/\s/g, '_')}.png`" target="_blank" rel="noopener noreferrer">
          <i class="icon ph-bold ph-download-simple"></i> 下载图片
        </a>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref } from 'vue';
import { useAIApi } from '../../composables/useAIApi.js';

const props = defineProps({ aiSettings: Object });
const emit = defineEmits(['show-api-key-modal']);

const theme = ref('');
const { isLoading, error, result, execute } = useAIApi('/api/generate-ideas', { initialResult: [] });

function getDownloadUrl(imageUrl) {
    return `/api/proxy-download?url=${encodeURIComponent(imageUrl)}`;
}

async function generate() {
  if (!theme.value) { error.value = '请输入灵感主题'; return; }

  try {
    await execute({ theme: theme.value }, props.aiSettings);
  } catch (e) {
    if (e.message === 'unauthorized') {
      emit('show-api-key-modal', 'expired');
    }
  }
}
</script>

