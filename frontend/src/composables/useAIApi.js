import { ref } from 'vue';
import { useAuthStore } from '../stores/auth';
import { useSettingsStore } from '../stores/settings';
import { useLocaleStore } from '../stores/locale';

import { useI18n } from 'vue-i18n';

export function useAIApi(endpoint, options = {}) {
  const isLoading = ref(false);
  const error = ref('');
  const result = ref(options.initialResult || null);

  const authStore = useAuthStore();
  const settingsStore = useSettingsStore();
  const localeStore = useLocaleStore();
  const { t } = useI18n();

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
      error.value = t('errors.notLoggedIn');
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
        headers: { 
          'Content-Type': 'application/json',
          'Accept-Language': localeStore.locale
        },
        body: JSON.stringify(fullBody),
      });

      if (!response.ok) {
        if (response.status === 401) {
          authStore.logout();
          throw new Error(t('errors.apiKeyInvalid'));
        }
        const errData = await response.json();
        throw new Error(errData.error || `${t('errors.requestFailed')}: ${response.status}`);
      }

      result.value = await response.json();
      return result.value;
    } catch (e) {
      error.value = `${t('errors.generationFailed')}: ${e.message}`;
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
