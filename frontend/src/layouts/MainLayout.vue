<script setup>
import { useAuthStore } from "@/stores/auth.store.js";

const auth = useAuthStore();
</script>

<template>
  <div class="drawer lg:drawer-open">
    <input id="main-drawer" type="checkbox" class="drawer-toggle" />

    <!-- MAIN CONTENT -->
    <div class="drawer-content p-6 bg-base-200 min-h-screen">
      <label
        for="main-drawer"
        class="btn btn-primary drawer-button lg:hidden mb-4"
      >
        ☰ Menu
      </label>

      <slot />
    </div>

    <!-- SIDEBAR -->
    <div class="drawer-side">
      <label for="main-drawer" class="drawer-overlay"></label>

      <aside class="menu p-4 w-80 min-h-full bg-base-100 border-r">
        <!-- Brand -->
        <div class="text-2xl font-bold mb-6 flex items-center gap-3">
          <span class="text-primary">⚡</span>
          <span>MyPanel</span>
        </div>

        <ul>
          <li>
            <router-link to="/dashboard" class="font-medium">
              🏠 Dashboard
            </router-link>
          </li>

          <li>
            <router-link to="/settings" class="font-medium">
              ⚙ Settings
            </router-link>
          </li>
        </ul>

        <!-- Divider -->
        <div class="divider"></div>

        <!-- Account section -->
        <ul>
          <li>
            <button @click="auth.logout" class="text-red-500 font-medium">
              🚪 Logout
            </button>
          </li>
        </ul>
      </aside>
    </div>
  </div>
</template>
