<script setup>
import { useAuthStore } from '@/stores/auth.store.js'
import { useUIStore } from '@/stores/ui.store.js'

const ui = useUIStore()
const auth = useAuthStore()
</script>

<template>
  <div class="flex min-h-screen bg-base-200">
    <!-- SIDEBAR -->
    <aside
      :class="[
        'bg-base-100 border-r h-screen p-4 transition-all duration-300 flex flex-col',
        ui.collapsed ? 'w-20' : 'w-64',
      ]"
    >
      <!-- Top -->
      <div class="flex items-center justify-between mb-6">
        <div class="font-bold text-xl truncate" v-if="!ui.collapsed">⚡ MyPanel</div>

        <!-- collapse button -->
        <button class="btn btn-sm btn-ghost" @click="ui.toggleSidebar">
          <span v-if="ui.collapsed">➡</span>
          <span v-else>⬅</span>
        </button>
      </div>

      <!-- NAV LINKS -->
      <ul class="menu flex-grow">
        <li>
          <router-link to="/dashboard">
            <span>🏠</span>
            <span v-if="!ui.collapsed">Dashboard</span>
          </router-link>
        </li>

        <li>
          <router-link to="/settings">
            <span>⚙️</span>
            <span v-if="!ui.collapsed">Settings</span>
          </router-link>
        </li>
      </ul>

      <!-- FOOTER -->
      <div class="mt-auto">
        <button @click="auth.logout" class="btn btn-error btn-sm w-full">
          <span>🚪</span>
          <span v-if="!ui.collapsed">Logout</span>
        </button>
      </div>
    </aside>

    <!-- CONTENT AREA -->
    <main class="flex-grow p-6">
      <router-view />
    </main>
  </div>
</template>
