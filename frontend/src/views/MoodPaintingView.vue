<template>
  <section id="mood-painting" class="page-container">

    <div class="header-section">
      <h2 class="page-title">{{ $t('views.moodPainting.title') }}</h2>
      <p class="subtitle">{{ $t('views.moodPainting.subtitle') }}</p>
    </div>

    <div class="content-wrapper">
      <el-form label-position="top" @submit.prevent="generate" class="main-form">
      <el-form-item :label="$t('views.moodPainting.selectMood')">
        <el-select
          v-model="mood"
          :placeholder="$t('views.moodPainting.selectMoodPlaceholder')"
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

      <el-form-item :label="$t('views.moodPainting.themeQuestion')">
        <el-input
          v-model="theme"
          :placeholder="$t('views.moodPainting.themePlaceholder')"
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
          {{ $t('views.moodPainting.generateIdea') }}
        </el-button>
      </el-form-item>
      </el-form>

      <el-alert
        v-if="error"
        :title="error"
        type="error"
        show-icon
        :closable="false"
        class="error-alert"
      />

      <div v-if="result?.name" class="result-section">
        <el-card
          shadow="hover"
          :body-style="{ padding: '0px' }"
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
            <p class="elements-text">
              <i class="ph-bold ph-lightbulb"></i>
              {{ $t('views.moodPainting.keyElements') }}: {{ result.elements }}
            </p>
          </div>
        </el-card>
      </div>
    </div>

  </section>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useI18n } from 'vue-i18n';
import { useAIApi } from '../composables/useAIApi.js';
import ImageResult from '../components/ImageResult.vue';
import VoiceInputButton from '../components/VoiceInputButton.vue';

const { t } = useI18n();
const theme = ref('');
const mood = ref('calm'); // 默认心情

// 心情列表
const moods = computed(() => [
  { value: 'happy', label: t('views.moodPainting.moods.happy'), emoji: '😄' },
  { value: 'calm', label: t('views.moodPainting.moods.calm'), emoji: '😌' },
  { value: 'excited', label: t('views.moodPainting.moods.excited'), emoji: '🤩' },
  { value: 'sad', label: t('views.moodPainting.moods.sad'), emoji: '😢' },
  { value: 'anxious', label: t('views.moodPainting.moods.anxious'), emoji: '😟' },
  { value: 'angry', label: t('views.moodPainting.moods.angry'), emoji: '😠' },
]);

// 注意 initialResult: null
const { isLoading, error, result, execute } = useAIApi('/api/mood-painting', { initialResult: null });

async function generate() {
  if (!mood.value) {
    error.value = t('views.moodPainting.selectMoodPlaceholder');
    return;
  }
  if (!theme.value) {
    error.value = t('views.moodPainting.themePlaceholder');
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
/* --- 布局容器 --- */
.page-container {
  max-width: 1000px;
  margin: 0 auto;
}

/* --- 头部区域 --- */
.header-section {
  text-align: center;
  margin-bottom: 40px;
  padding-top: 10px;
}

.page-title {
  font-size: 2rem;
  margin-bottom: 10px;
  border-bottom: none; /* 移除全局 h2 的下划线 */
  font-family: var(--font-serif);
  color: var(--secondary-color);
}

.subtitle {
  color: var(--dark-text);
  font-size: 1rem;
  margin-top: 0;
  font-weight: 500;
  opacity: 0.8;
}

/* --- 内容区域 --- */
.content-wrapper {
  background: white;
  border-radius: 16px;
  box-shadow: var(--card-shadow);
  border: 1px solid var(--border-color);
  padding: 40px;
  margin-bottom: 20px;
}

.main-form {
  max-width: 600px;
  margin: 0 auto;
}

.main-form .el-form-item {
  margin-bottom: 25px;
}

.main-form .el-button {
  font-size: 1.1rem;
  padding: 15px 0;
  border-radius: 8px;
  font-weight: 600;
}

/* --- 错误提示 --- */
.error-alert {
  margin-top: 30px;
  margin-bottom: 20px;
}

/* --- 结果区域 --- */
.result-section {
  margin-top: 40px;
  padding-top: 30px;
  border-top: 1px solid var(--border-color);
}

.mood-result-card {
  animation: result-fade-in 0.5s ease;
  border-radius: 12px;
  overflow: hidden;
}

.idea-content {
  padding: 25px;
}

.idea-content h3 {
  font-family: var(--font-serif);
  color: var(--secondary-color);
  margin-top: 0;
  margin-bottom: 15px;
  font-size: 1.3rem;
}

.idea-content .description {
  line-height: 1.7;
  margin-bottom: 15px;
  color: var(--dark-text);
}

.elements-text {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #fff8e1;
  color: #b8860b;
  padding: 12px 15px;
  border-radius: 8px;
  font-size: 0.9rem;
  margin: 0;
}

.elements-text i {
  font-size: 1rem;
  color: var(--accent-color);
}

/* --- 动画效果 --- */
@keyframes result-fade-in {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

/* --- 移动端适配 --- */
@media (max-width: 768px) {
  .content-wrapper {
    padding: 25px 20px;
    margin: 0 10px 20px 10px;
  }
  
  .page-title {
    font-size: 1.6rem;
  }
  
  .main-form {
    max-width: 100%;
  }
}
</style>