<template>
  <section id="idea-generator" class="feature-panel">
    <h2>创意灵感生成器</h2>
    <el-form label-position="top" @submit.prevent="generate">
      <el-form-item label="灵感主题:">
        <el-input
          v-model="theme"
          placeholder="例如：春天, 节日"
          clearable
          @keyup.enter="generate"
        >
          <template #suffix>
            <VoiceInputButton @update:text="handleVoiceInput" />
          </template>
        </el-input>
      </el-form-item>
      <el-form-item>
        <el-button
          type="primary"
          @click="generate"
          :loading="isLoading"
          style="width: 100%;"
        >
          生成灵感
        </el-button>
      </el-form-item>
    </el-form>

    <el-alert
      v-if="error"
      :title="error"
      type="error"
      show-icon
      :closable="false"
      style="margin-top: 20px;"
    />

    <el-row :gutter="20" style="margin-top: 20px;" v-if="result?.length > 0">
      <el-col
        :xs="24"
        :sm="12"
        :md="8"
        v-for="(idea, index) in result"
        :key="index"
        style="margin-bottom: 20px;"
      >
        <el-card shadow="hover" :body-style="{ padding: '0px' }">
          <ImageResult v-if="idea.exampleImage" :image-url="idea.exampleImage" :alt-text="idea.name" :filename="`${idea.name}.png`" />
          <div class="idea-content">
            <h3>{{ idea.name }}</h3>
            <p>{{ idea.description }}</p>
            <p><small>关键元素: {{ idea.elements }}</small></p>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </section>
</template>

<script setup>
import { ref } from 'vue';
import { useAIApi } from '../composables/useAIApi.js';
import ImageResult from '../components/ImageResult.vue';
import VoiceInputButton from '../components/VoiceInputButton.vue';

const theme = ref('');
const { isLoading, error, result, execute } = useAIApi('/api/generate-ideas', { initialResult: [] });

const handleVoiceInput = (text) => {
  theme.value += text; // 追加到主题输入框
};

async function generate() {
  if (!theme.value) {
    error.value = '请输入灵感主题';
    return;
  }
  try {
    await execute({ theme: theme.value });
  } catch (e) {
    console.error(e);
  }
}
</script>

<style scoped>
.idea-content {
  padding: 14px;
}
.image-slot {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 100%;
  background: #f5f7fa;
  color: #909399;
  font-size: 30px;
}
</style>
