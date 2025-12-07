<script setup>
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth.store.js'

const auth = useAuthStore()
const email = ref('')
const password = ref('')

function submit() {
  auth.login(email.value, password.value)
}
</script>

<template>
  <div class="flex flex-col gap-4 rounded-box bg-base-200 p-6 max-w-md">
    <h1 class="text-3xl font-bold self-center">Log in</h1>

    <span class="self-center">
      Don't have an account?
      <a class="link link-secondary">Register</a>
    </span>

    <label class="form-control">
      <div class="label">
        <span class="label-text">Email</span>
      </div>

      <input class="input input-bordered" />
    </label>

    <label class="form-control">
      <div class="label">
        <span class="label-text">Password</span>
        <a class="label-text link link-accent">Forgot password?</a>
      </div>

      <input type="password" class="input input-bordered" />
    </label>

    <div class="form-control">
      <label class="cursor-pointer label self-start gap-2">
        <input type="checkbox" class="checkbox" />
        <span class="label-text">Remember me</span>
      </label>
    </div>

    <button class="btn btn-primary">Log in</button>
  </div>

  <div class="bg-base-200 p-6">
    <h2 class="text-2xl mb-4 font-bold">Login</h2>
    <form @submit.prevent="submit" class="space-y-4">
      <input v-model="email" type="email" placeholder="Email" class="input input-bordered w-full" />
      <input
        v-model="password"
        type="password"
        placeholder="Password"
        class="input input-bordered w-full"
      />

      <button class="btn btn-primary w-full">Login</button>
    </form>
  </div>
</template>
