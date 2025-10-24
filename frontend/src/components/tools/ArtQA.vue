<template>
  <section id="art-qa" class="feature-panel">
    <h2>艺术知识智能问答</h2>
    <div class="form-group">
      <label for="qa-input">提出你的问题:</label>
      <input type="text" id="qa-input" placeholder="例如：什么是水墨画？" v-model="question" @keyup.enter="ask" />
    </div>
    <button id="ask-qa-btn" class="cta-btn" @click="ask" :disabled="isLoading">提问</button>
    <div class="loader" v-if="isLoading"></div>
    <p class="error-message">{{ error }}</p>
    <div id="qa-result" class="result-container" v-if="answer">{{ answer }}</div>
  </section>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useAIApi } from '../../composables/useAIApi.js';

const question = ref('');
const { isLoading, error, result, execute } = useAIApi('/api/ask-question');

const answer = computed(() => result.value?.choices?.[0]?.message?.content || '');

async function ask() {
  if (!question.value) { error.value = '请输入你的问题'; return; }

  try {
    await execute({ question: question.value });
  } catch (e) {
  }
}
</script>
