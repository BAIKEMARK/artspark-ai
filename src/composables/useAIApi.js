import { ref } from 'vue';

const AUTH_TOKEN_KEY = 'art_spark_auth_token';

export function useAIApi(endpoint, options = {}) {
  const isLoading = ref(false);
  const error = ref('');
  const result = ref(options.initialResult || null);

  const fileToBase64 = (file) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = () => resolve(reader.result);
      reader.onerror = (error) => reject(error);
    });
  };

  const execute = async (body, aiSettings) => {
    isLoading.value = true;
    error.value = '';
    result.value = options.initialResult || null;

    const token = localStorage.getItem(AUTH_TOKEN_KEY);
    if (!token) {
      error.value = '您尚未登录。';
      isLoading.value = false;
      // 在组件中监听此错误并调用 showApiKeyModal
      throw new Error('unauthorized');
    }

    try {
      const fullBody = {
        ...body,
        config_chat_model: aiSettings.chat_model,
        config_vl_model: aiSettings.vl_model,
        config_image_model: aiSettings.image_model,
        config_age_range: aiSettings.age_range,
      };

      const response = await fetch(`${endpoint}?token=${encodeURIComponent(token)}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(fullBody),
      });

      if (!response.ok) {
        const errData = await response.json();
        if (response.status === 401) {
          throw new Error('unauthorized');
        }
        throw new Error(errData.error || `请求失败: ${response.status}`);
      }

      result.value = await response.json();
      return result.value;
    } catch (e) {
      error.value = `生成失败: ${e.message}`;
      if (e.message === 'unauthorized') {
        throw e; // 重新抛出，以便组件可以处理
      }
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

