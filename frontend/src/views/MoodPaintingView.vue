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
/* 页面特有样式 */
.mood-result-card {
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
</style>