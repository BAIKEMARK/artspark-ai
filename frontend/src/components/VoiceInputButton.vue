<template>
  <el-tooltip
     :content="tooltipContent"
     placement="top"
     :disabled="isRecording"
  >
    <el-button
      class="voice-input-btn"
      :class="{ 'is-recording': isRecording, 'is-processing': isProcessing }"
      @click="handleToggle"
      circle
      :loading="isProcessing"
    >
      <template #icon>
        <div v-if="isRecording" class="recording-wave">
          <span></span><span></span><span></span>
        </div>
        <i v-else class="ph-bold ph-microphone"></i>
      </template>
    </el-button>
  </el-tooltip>
</template>

<script setup>
import { computed } from 'vue';
import { useVoiceRecorder } from '../composables/useVoiceRecorder';
import { ElMessage } from 'element-plus';

const emit = defineEmits(['update:text']);

const { isRecording, isProcessing, startRecording, stopRecording } = useVoiceRecorder();

const tooltipContent = computed(() => {
  if (isProcessing.value) return '正在识别...';
  if (isRecording.value) return '点击停止并识别';
  return '点击开始语音输入';
});

async function handleToggle() {
  if (isProcessing.value) return;

  if (isRecording.value) {
    // 停止录音
    try {
      const text = await stopRecording();
      if (text) {
        emit('update:text', text);
        ElMessage.success('识别成功');
      } else {
        ElMessage.warning('未检测到语音内容');
      }
    } catch (e) {
      ElMessage.error(`识别失败: ${e.message}`);
    }
  } else {
    // 开始录音
    await startRecording();
  }
}
</script>

<style scoped>
.voice-input-btn {
  transition: all 0.3s ease;
  border: none;
  background: transparent;
  color: var(--el-text-color-secondary);
}

.voice-input-btn:hover {
  background: var(--el-fill-color-light);
  color: var(--primary-color);
}

.voice-input-btn.is-recording {
  color: #F56C6C;
  background: #FEF0F0;
  border: 1px solid #FAB6B6;
}

/* 录音波纹动画 */
.recording-wave {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 2px;
  height: 1em;
}

.recording-wave span {
  display: block;
  width: 2px;
  height: 6px;
  background-color: #F56C6C;
  border-radius: 2px;
  animation: wave 1s infinite ease-in-out;
}

.recording-wave span:nth-child(1) { animation-delay: 0s; }
.recording-wave span:nth-child(2) { animation-delay: 0.2s; }
.recording-wave span:nth-child(3) { animation-delay: 0.4s; }

@keyframes wave {
  0%, 100% { height: 4px; opacity: 0.5; }
  50% { height: 12px; opacity: 1; }
}
</style>

