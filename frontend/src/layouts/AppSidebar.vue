<!-- src/components/AppSidebar.vue -->
<script setup>
import { ref } from 'vue'
import {
  Bars3Icon,
  ChartBarIcon,
  ChevronRightIcon,
  Cog6ToothIcon,
  CubeIcon,
  HomeIcon,
  UserGroupIcon,
  XMarkIcon,
} from '@heroicons/vue/24/solid'
import { useAuthStore } from '@/stores/auth.store.js'
import { useUIStore } from '@/stores/ui.store.js'

// Reactive state for collapse (optional – you can also use checkbox hack)
const isCollapsed = ref(false)

const ui = useUIStore()
const auth = useAuthStore()
</script>

<template>
  <aside class="bg-base-200 relative h-screen">
    <!-- Top -->

    <div
      class="flex flex-col h-full transition-all duration-300 overflow-hidden"
      :class="ui.collapsed ? 'w-20' : 'w-64'"
    >
      <div class="flex items-center justify-between mb-1 border-b border-base-300">
        <div class="font-bold text-xl truncate" v-if="!ui.collapsed">⚡ MyPanel</div>

        <!-- collapse button -->
        <button class="btn btn-sm btn-ghost" @click="ui.toggleSidebar">
          <span v-if="ui.collapsed">➡</span>
          <span v-else>⬅</span>
        </button>
      </div>

      <!-- Logo / Header -->
      <div class="flex items-center justify-center h-16 border-b border-base-300">
        <h1 class="text-2xl font-bold" :class="{ hidden: ui.collapsed }">MyApp</h1>
      </div>

      <!-- Menu -->
      <ul class="menu p-4 flex-1 overflow-y-auto text-base-content">
        <!-- Dashboard -->
        <li>
          <a class="active">
            <HomeIcon class="h-5 w-5" />
            <span class="hidden" :class="{ 'md:inline': !ui.collapsed }">Dashboard</span>
          </a>
        </li>

        <!-- Users + Submenu -->
        <li>
          <details open>
            <summary>
              <UserGroupIcon class="h-5 w-5" />
              <span class="hidden" :class="{ 'md:inline': !ui.collapsed }">Users</span>
              <ChevronRightIcon
                class="h-4 w-4 ml-auto transition-transform"
                :class="{ 'rotate-90': $event?.target?.open }"
              />
            </summary>
            <ul>
              <li><a>All Users</a></li>
              <li><a>Add User</a></li>
              <li><a>Roles & Permissions</a></li>
            </ul>
          </details>
        </li>

        <!-- Products + Deep Nested -->
        <li>
          <details>
            <summary>
              <CubeIcon class="h-5 w-5" />
              <span class="hidden" :class="{ 'md:inline': !ui.collapsed }">Products</span>
              <ChevronRightIcon class="h-4 w-4 ml-auto transition-transform" />
            </summary>
            <ul>
              <li><a>All Products</a></li>
              <li>
                <details>
                  <summary>Categories</summary>
                  <ul>
                    <li><a>Electronics</a></li>
                    <li><a>Clothing</a></li>
                    <li><a>Food</a></li>
                  </ul>
                </details>
              </li>
              <li><a>Inventory</a></li>
            </ul>
          </details>
        </li>

        <!-- Analytics -->
        <li>
          <details>
            <summary>
              <ChartBarIcon class="h-5 w-5" />
              <span class="hidden" :class="{ 'md:inline': !ui.collapsed }">Analytics</span>
              <ChevronRightIcon class="h-4 w-4 ml-auto transition-transform" />
            </summary>
            <ul>
              <li><a>Reports</a></li>
              <li><a>Charts</a></li>
            </ul>
          </details>
        </li>

        <!-- Settings -->
        <li>
          <a>
            <Cog6ToothIcon class="h-5 w-5" />
            <span class="hidden" :class="{ 'md:inline': !ui.collapsed }">Settings</span>
          </a>
        </li>
      </ul>

      <!-- User Footer -->
      <div class="p-4 border-t border-base-300">
        <div class="flex items-center gap-3">
          <div class="avatar online">
            <div class="w-10 rounded-full ring ring-primary ring-offset-base-100 ring-offset-2">
              <img src="https://daisyui.com/images/stock/photo-1534528741775-53994a69daeb.jpg" />
            </div>
          </div>
          <div v-show="!ui.collapsed" class="hidden md:block">
            <div class="font-medium">John Doe</div>
            <div class="text-sm opacity-70">Administrator</div>
          </div>
        </div>
      </div>
    </div>
  </aside>
</template>

<style scoped>
/* Rotate chevron when details is open */
details[open] > summary > .rotate-90 {
  transform: rotate(90deg);
}
</style>
