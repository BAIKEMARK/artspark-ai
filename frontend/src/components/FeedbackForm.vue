<template>
  <el-dialog
    v-model="dialogVisible"
    :title="t('feedback.title')"
    width="600px"
    :before-close="handleClose"
    destroy-on-close
  >
    <p style="margin-bottom: 20px; color: #666;">
      {{ t('feedback.description') }}
    </p>
    <el-form
      :model="feedbackForm"
      ref="feedbackFormRef"
      :rules="rules"
      label-position="top"
      size="large"
    >
      <el-form-item :label="t('feedback.contentLabel')" prop="content">
        <el-input
          v-model="feedbackForm.content"
          type="textarea"
          :rows="5"
          :placeholder="t('feedback.contentPlaceholder')"
          maxlength="500"
          show-word-limit
          resize="none"
        ></el-input>
      </el-form-item>
      <el-form-item :label="t('feedback.contactLabel')" prop="contact">
        <el-input
          v-model="feedbackForm.contact"
          :placeholder="t('feedback.contactPlaceholder')"
          clearable
        >
          <template #prefix>
             <el-icon><i class="ph-bold ph-user"></i></el-icon>
          </template>
        </el-input>
      </el-form-item>
    </el-form>
    <template #footer>
      <div style="text-align: right;">
        <el-button @click="handleCloseDialog">{{ t('feedback.cancel') }}</el-button>
        <el-button type="primary" @click="submitFeedback" :loading="loading">
          {{ t('feedback.submit') }}
        </el-button>
      </div>
    </template>
  </el-dialog>

  <el-tooltip :content="t('feedback.tooltip')" placement="left">
    <div class="feedback-trigger" @click="dialogVisible = true">
      <i class="ph-bold ph-chat-text"></i>
    </div>
  </el-tooltip>
</template>

<script setup>
import { ref, reactive, computed } from 'vue';
import { ElMessage } from 'element-plus';
import axios from 'axios';
import { useI18n } from 'vue-i18n';

const { t } = useI18n();

const dialogVisible = ref(false);
const loading = ref(false);
const feedbackFormRef = ref(null);

const feedbackForm = reactive({
  content: '',
  contact: '',
});

const rules = computed(() => ({
  content: [
    { required: true, message: t('validation.feedbackRequired'), trigger: 'blur' },
    { min: 5, message: t('validation.feedbackTooShort'), trigger: 'blur' },
  ],
}));

const webhookUrl = '/dingtalk-api/robot/send?access_token=' + import.meta.env.VITE_DINGTALK_ACCESS_TOKEN;

const handleCloseDialog = () => {
  dialogVisible.value = false;
};

const handleClose = (done) => {
  done();
};

const submitFeedback = async () => {
  if (!feedbackFormRef.value) return;

  await feedbackFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true;
      try {
        const message = {
          msgtype: 'markdown', // 使用 markdown 格式让消息更美观
          markdown: {
            title: '【艺启智用户反馈】',
            text: `### 📢 用户反馈\n\n**内容：**\n>${feedbackForm.content}\n\n**联系人：** ${feedbackForm.contact || '未填写'}`
          },
        };

        await axios.post(webhookUrl, message);

        ElMessage.success(t('feedback.submitSuccess'));
        dialogVisible.value = false;
      } catch (error) {
        console.error('反馈提交失败:', error);
        ElMessage.success(t('feedback.submitFallback')); // 降级提示
        dialogVisible.value = false;
       } finally {
        loading.value = false;
      }
    }
  });
};
</script>

<style scoped>
/* 浮动按钮样式优化 */
.feedback-trigger {
  position: fixed;
  bottom: 30px;
  right: 30px;
  z-index: 999;

  /* 使用 Flex 居中图标 */
  display: flex;
  align-items: center;
  justify-content: center;

  width: 50px;
  height: 50px;
  /* 使用全局次要颜色作为背景 */
  background-color: #34495E;
  color: darkgray;

  border-radius: 50%; /* 圆形 */
  /* 使用 Element Plus 的全局阴影变量 */
  box-shadow: var(--el-box-shadow-light);
  cursor: pointer;
  /* 简单的过渡动画 */
  transition: all 0.3s ease;

  /* 图标大小 */
  font-size: 26px;
}

/* 悬停效果：轻微上浮和变色 */
.feedback-trigger:hover {
  transform: translateY(-3px);
  box-shadow: var(--el-box-shadow);
  color: var(--accent-color, #ffd700);
}

/* 移动端适配：调整位置和大小 */
@media (max-width: 768px) {
  .feedback-trigger {
    bottom: 20px;
    right: 20px;
    width: 44px;
    height: 44px;
    font-size: 22px;
  }
}
</style>