<template>
  <section id="art-qa" class="feature-panel">
    <h2>艺术知识智能问答</h2>
    <el-form label-position="top" @submit.prevent="ask">
      <el-form-item label="提出你的问题:">
        <el-input
          v-model="question"
          placeholder="例如：什么是水墨画？"
          clearable
          @keyup.enter="ask"
        />
      </el-form-item>
      <el-form-item>
        <el-button
          type="primary"
          @click="ask"
          :loading="isLoading"
          style="width: 100%;"
        >
          提问
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

    <el-card v-if="answer" class="result-card" shadow="never">
      <div v-html="formattedAnswer"></div>
    </el-card>
  </section>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useAIApi } from '../composables/useAIApi.js';
import { marked } from 'marked';

const question = ref('');
const { isLoading, error, result, execute } = useAIApi('/api/ask-question');

const answer = computed(() => result.value?.choices?.[0]?.message?.content || '');
const formattedAnswer = computed(() => answer.value ? marked(answer.value) : '');


async function ask() {
  if (!question.value) {
    error.value = '请输入你的问题';
    return;
  }

  try {
    await execute({ question: question.value });
  } catch (e) {
    console.error(e);
  }
}
</script>

<style scoped>
.result-card {
  margin-top: 20px;
  white-space: pre-wrap;
  line-height: 1.8;
}
</style>
