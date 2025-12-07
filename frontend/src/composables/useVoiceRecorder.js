import { ref } from 'vue';
import { useAuthStore } from '../stores/auth';
import { useSettingsStore } from '../stores/settings';
import { ElMessage } from 'element-plus';
import { useI18n } from 'vue-i18n';

export function useVoiceRecorder() {
  const isRecording = ref(false);
  const isProcessing = ref(false);
  const mediaRecorder = ref(null);
  const audioChunks = ref([]);

  const authStore = useAuthStore();
  const settingsStore = useSettingsStore();
  const { t } = useI18n();

  const startRecording = async () => {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      ElMessage.error(t('errors.microphoneNotSupported'));
      return;
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorder.value = new MediaRecorder(stream);
      audioChunks.value = [];

      mediaRecorder.value.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunks.value.push(event.data);
        }
      };

      mediaRecorder.value.start();
      isRecording.value = true;
    } catch (err) {
      console.error("Error accessing microphone:", err);
      ElMessage.error(t('errors.microphoneAccessDenied'));
    }
  };

  const stopRecording = () => {
    return new Promise((resolve, reject) => {
      if (!mediaRecorder.value) return resolve(null);

      mediaRecorder.value.onstop = async () => {
        const audioBlob = new Blob(audioChunks.value, { type: 'audio/webm' });
        // 停止所有轨道以释放麦克风
        mediaRecorder.value.stream.getTracks().forEach(track => track.stop());
        isRecording.value = false;

        // 立即上传
        try {
          const text = await uploadAudio(audioBlob);
          resolve(text);
        } catch (e) {
          reject(e);
        }
      };

      mediaRecorder.value.stop();
    });
  };

  const uploadAudio = async (audioBlob) => {
    isProcessing.value = true;
    const formData = new FormData();
    formData.append('file', audioBlob, 'voice.webm');

    if (settingsStore.aiSettings.bailian_api_key) {
        formData.append('bailian_api_key', settingsStore.aiSettings.bailian_api_key);
    }
    formData.append('api_platform', settingsStore.aiSettings.api_platform);

    try {
      const response = await fetch(`/api/audio-to-text?token=${encodeURIComponent(authStore.token)}`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        if (response.status === 401) {
            authStore.logout(); // 登出，触发重新输入 API Key 的弹窗
            throw new Error(t('errors.authExpired'));
        }

        const data = await response.json();
        throw new Error(data.error || t('errors.voiceRecognitionFailed'));
      }

      const data = await response.json();
      return data.text;
    } catch (e) {
      console.error(e);
      throw e;
    } finally {
      isProcessing.value = false;
    }
  };

  return {
    isRecording,
    isProcessing,
    startRecording,
    stopRecording
  };
}

