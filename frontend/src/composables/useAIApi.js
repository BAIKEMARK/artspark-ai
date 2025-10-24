import { ref } from 'vue';
import { useAuthStore } from '../stores/auth';
import { useSettingsStore } from '../stores/settings';

export function useAIApi(endpoint, options = {}) {
  const isLoading = ref(false);
  const error = ref('');
  const result = ref(options.initialResult || null);

  const authStore = useAuthStore();
  const settingsStore = useSettingsStore();

  const fileToBase64 = (file) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = () => resolve(reader.result);
      reader.onerror = (error) => reject(error);
    });
  };

  const execute = async (body) => {
    isLoading.value = true;
    error.value = '';
    result.value = options.initialResult || null;

    if (!authStore.isLoggedIn) {
      error.value = '您尚未登录。';
      isLoading.value = false;
      authStore.logout(); // Ensure state is clean
      return;
    }

    try {
      const fullBody = {
        ...body,
        ...settingsStore.aiSettings,
      };

      const response = await fetch(`${endpoint}?token=${encodeURIComponent(authStore.token)}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(fullBody),
      });

      if (!response.ok) {
        if (response.status === 401) {
          authStore.logout();
          throw new Error('API Key 无效或已过期，请重新登录。');
        }
        const errData = await response.json();
        throw new Error(errData.error || `请求失败: ${response.status}`);
      }

      result.value = await response.json();
      return result.value;
    } catch (e) {
      error.value = `生成失败: ${e.message}`;
    } finally {
      isLoading.value = false;
    }
  };

  return {
    isLoading,
    error,
    result,
    execute,
    fileToBase64,
  };
}
