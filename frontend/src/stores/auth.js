import { defineStore } from 'pinia';
import { ref } from 'vue';

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('art_spark_auth_token') || '');
  const isLoggedIn = ref(!!token.value);

  function login(apiKey) {
    token.value = apiKey;
    isLoggedIn.value = true;
    localStorage.setItem('art_spark_auth_token', apiKey);
  }

  function logout() {
    token.value = '';
    isLoggedIn.value = false;
    localStorage.removeItem('art_spark_auth_token');
  }

  return { token, isLoggedIn, login, logout };
});
