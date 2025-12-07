<!-- src/components/ThemeToggle.vue -->
<script setup>
import { onMounted, ref, watch } from 'vue'
import { MoonIcon, SunIcon } from '@heroicons/vue/24/solid' // optional icons

const currentTheme = ref('light')

// List of your favorite DaisyUI themes here
const themes = [
  'light',
  'dark',
  'cupcake',
  'bumblebee',
  'emerald',
  'corporate',
  'synthwave',
  'retro',
  'cyberpunk',
  'valentine',
  'halloween',
  'garden',
  'forest',
  'aqua',
  'lofi',
  'pastel',
  'fantasy',
  'dracula',
  'cmyk',
  'autumn',
  'business',
  'night',
  'coffee',
  'winter',
]

let themeIndex = 0

// Load saved theme or default to light
const loadTheme = () => {
  const saved = localStorage.getItem('theme')
  if (saved && themes.includes(saved)) {
    currentTheme.value = saved
  } else {
    // Optional: respect OS preference
    if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
      currentTheme.value = 'dark'
    }
  }
  applyTheme(currentTheme.value)
}

// Apply theme to <html data-theme="...">
const applyTheme = (theme) => {
  document.documentElement.setAttribute('data-theme', theme)
  document.documentElement.classList.toggle('dark', theme === 'dark')
}

// Cycle through themes or just toggle light/dark
const toggleTheme = () => {
  themeIndex = (themeIndex + 1) % themes.length
  currentTheme.value = themes[themeIndex]
  applyTheme(currentTheme.value)
  localStorage.setItem('theme', currentTheme.value)
}

// Optional: simple light/dark only toggle
const toggleLightDark = () => {
  currentTheme.value = currentTheme.value === 'dark' ? 'light' : 'dark'
  applyTheme(currentTheme.value)
  localStorage.setItem('theme', currentTheme.value)
}

onMounted(() => {
  loadTheme()

  // Listen to OS theme changes
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
    if (!localStorage.getItem('theme')) {
      currentTheme.value = e.matches ? 'dark' : 'light'
      applyTheme(currentTheme.value)
    }
  })
})
</script>

<template>
  <!-- Option 1: Cycle through all themes (fun!) -->
  <button
    @click="toggleTheme"
    class="btn btn-circle btn-ghost tooltip tooltip-bottom"
    data-tip="Change theme"
  >
    <SunIcon v-if="currentTheme === 'dark'" class="h-6 w-6" />
    <MoonIcon v-else class="h-6 w-6" />
  </button>

  <!-- Option 2: Simple light/dark toggle (cleaner) -->
  <!--
  <button @click="toggleLightDark" class="btn btn-circle btn-ghost">
    <SunIcon v-if="currentTheme === 'dark'" class="h-6 w-6" />
    <MoonIcon v-else class="h-6 w-6" />
  </button>
  -->
</template>
