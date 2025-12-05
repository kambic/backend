<script setup>
import { ref } from "vue";
import { useAuthStore } from "@/stores/auth.store.js";

const auth = useAuthStore();
const email = ref("");
const password = ref("");

function submit() {
  auth.login(email.value, password.value);
}
</script>

<template>
  <h2 class="text-2xl mb-4 font-bold">Login</h2>

  <form @submit.prevent="submit" class="space-y-4">
    <input
      v-model="email"
      type="email"
      placeholder="Email"
      class="input input-bordered w-full"
    />
    <input
      v-model="password"
      type="password"
      placeholder="Password"
      class="input input-bordered w-full"
    />

    <button class="btn btn-primary w-full">Login</button>
  </form>
</template>
