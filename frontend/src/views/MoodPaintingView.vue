<template>
  <section id="mood-painting" class="feature-panel">
    <h2>{{ $t('views.moodPainting.title') }}</h2>
    <p class="sub-heading">{{ $t('views.moodPainting.subtitle') }}</p>

    <el-form label-position="top" @submit.prevent="generate">
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
        <p><small>{{ $t('views.moodPainting.keyElements') }}: {{ result.elements }}</small></p>
      </div>
    </el-card>

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