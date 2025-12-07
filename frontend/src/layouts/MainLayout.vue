<script setup>
import { useAuthStore } from '@/stores/auth.store.js'
import { useUIStore } from '@/stores/ui.store.js'
import AppSidebar from '@//layouts/AppSidebar.vue'

const ui = useUIStore()
const auth = useAuthStore()
</script>

<template>
  <div class="flex min-h-screen">
    <AppSidebar />
    <main class="flex-1 p-8 bg-base-100">
      <slot />
      <!-- Page content -->
    </main>
  </div>
</template>
