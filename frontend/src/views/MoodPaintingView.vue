<template>
  <section id="mood-painting" class="feature-panel">
    <h2>心情画板</h2>
    <p class="sub-heading">（融合艺术与心理，引导学生用绘画表达情绪）</p>

    <el-form label-position="top" @submit.prevent="generate">
      <el-form-item label="选择你现在的心情:">
        <el-select
          v-model="mood"
          placeholder="请选择一种心情"
          style="width: 100%; max-width: 400px;"
        >
          <el-option
            v-for="item in moods"
            :key="item.value"
            :label="item.label"
            :value="item.value"
          >
            <span>{{ item.emoji }}</span>
            <span style="margin-left: 8px;">{{ item.label }}</span>
          </el-option>
        </el-select>
      </el-form-item>

      <el-form-item label="你想画一个关于什么的主题？">
        <el-input
          v-model="theme"
          placeholder="例如：我的家, 一棵树, 未来的我"
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
          size="large"
        >
          生成专属绘画创意
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

    <el-card
      shadow="hover"
      :body-style="{ padding: '0px' }"
      style="margin-top: 20px;"
      v-if="result?.name"
      class="mood-result-card"
    >
      <ImageResult
        v-if="result.exampleImage"
        :image-url="result.exampleImage"
        :alt-text="result.name"
        :filename="`${result.name}.png`"
      />
      <div class="idea-content">
        <h3>{{ result.name }}</h3>
        <p class="description">{{ result.description }}</p>
        <p><small>关键元素: {{ result.elements }}</small></p>
      </div>
    </el-card>

  </section>
</template>

<script setup>
import { ref } from 'vue';
import { useAIApi } from '../composables/useAIApi.js';
import ImageResult from '../components/ImageResult.vue';
import VoiceInputButton from '../components/VoiceInputButton.vue';

const theme = ref('');
const mood = ref('calm'); // 默认心情

// 心情列表
const moods = ref([
  { value: 'happy', label: '开心', emoji: '😄' },
  { value: 'calm', label: '平静', emoji: '😌' },
  { value: 'excited', label: '激动', emoji: '🤩' },
  { value: 'sad', label: '难过', emoji: '😢' },
  { value: 'anxious', label: '焦虑', emoji: '😟' },
  { value: 'angry', label: '生气', emoji: '😠' },
]);

// 注意 initialResult: null
const { isLoading, error, result, execute } = useAIApi('/api/mood-painting', { initialResult: null });

async function generate() {
  if (!mood.value) {
    error.value = '请选择一种心情';
    return;
  }
  if (!theme.value) {
    error.value = '请输入一个主题';
    return;
  }

  try {
    // result.value 会在 execute 内部被设置
    await execute({ mood: mood.value, theme: theme.value });
  } catch (e) {
    console.error(e);
    // error.value 会在 useAIApi 内部被设置
  }
}

const handleVoiceInput = (text) => {
  theme.value += text;
};
</script>

<style scoped>
.sub-heading {
  color: var(--el-text-color-secondary);
  font-size: 0.9rem;
  margin-top: -20px;
  margin-bottom: 25px;
  text-align: center;
}
.idea-content {
  padding: 20px;
}
.idea-content h3 {
  font-family: var(--font-serif);
  color: var(--secondary-color);
  margin-top: 0;
}
.idea-content .description {
  line-height: 1.7;
}

/* 结果卡片动画 */
.mood-result-card {
  animation: result-fade-in 0.5s ease;
}
@keyframes result-fade-in {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>