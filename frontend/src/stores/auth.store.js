import { defineStore } from "pinia";
import { computed, ref } from "vue";
import router from "../router";

export const useAuthStore = defineStore("auth", () => {
  const user = ref(null);

  // Fake login
  function login(email, password) {
    user.value = { email };
    router.push("/dashboard");
  }

  function logout() {
    user.value = null;
    router.push("/auth/login");
  }

  const isLoggedIn = computed(() => user.value !== null);

  return { user, login, logout, isLoggedIn };
});
