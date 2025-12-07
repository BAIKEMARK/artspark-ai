<template>
  <el-dialog
    :model-value="true"
    :title="t('apiKeyModal.title')"
    width="500"
    center
    :close-on-click-modal="false"
    :show-close="false"
    :closable="false"
  >
    <p style="text-align: center; margin-top: -10px; margin-bottom: 25px;">
      {{ t('apiKeyModal.description') }}
    </p>
    <el-form @submit.prevent="handleSaveApiKey">
      <el-form-item :error="apiError">
        <el-input
          v-model="apiKeyInput"
          type="password"
          placeholder="{{ t('apiKeyModal.placeholder') }}"
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
          {{ isVerifying ? t('apiKeyModal.verifying') : t('apiKeyModal.enter') }}
        </el-button>
      </el-form-item>
    </el-form>
    <template #footer>
      <div class="dialog-footer">
        <small>{{ t('apiKeyModal.footerText') }} <a href="https://www.modelscope.cn/my/myaccesstoken" target="_blank">{{ t('apiKeyModal.getToken') }}</a>{{ t('apiKeyModal.securityNote') }}</small>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { useI18n } from 'vue-i18n';
const { t } = useI18n();

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
