<template>
  <el-dialog
    :model-value="true"
    title="欢迎来到 艺启智AI"
    width="500"
    center
    :close-on-click-modal="false"
    :show-close="false"
    :closable="false"
  >
    <p style="text-align: center; margin-top: -10px; margin-bottom: 25px;">
      请输入您的ModelScope API KEY以激活助教功能。
    </p>
    <el-form @submit.prevent="handleSaveApiKey">
      <el-form-item :error="apiError">
        <el-input
          v-model="apiKeyInput"
          type="password"
          placeholder="在此输入您的访问令牌"
          show-password
          size="large"
          @keyup.enter="handleSaveApiKey"
          :disabled="isVerifying"
        />
      </el-form-item>
      <el-form-item>
        <el-button
          type="primary"
          @click="handleSaveApiKey"
          :loading="isVerifying"
          style="width: 100%;"
          size="large"
        >
          {{ isVerifying ? '验证中...' : '进入美术馆' }}
        </el-button>
      </el-form-item>
    </el-form>
    <template #footer>
      <div class="dialog-footer">
        <small>可访问 <a href="https://www.modelscope.cn/my/myaccesstoken" target="_blank">获取访问令牌</a>。密钥将安全保存在本地浏览器中。</small>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref } from 'vue';

const props = defineProps({
  isVerifying: Boolean,
  apiError: String,
});

const apiKeyInput = ref('');

const emit = defineEmits(['save-api-key']);

const handleSaveApiKey = () => {
  if (props.isVerifying) return;
  emit('save-api-key', apiKeyInput.value);
};
</script>

<style scoped>
.dialog-footer {
  text-align: center;
}
</style>
