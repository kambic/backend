<script setup>
import { MoonIcon } from '@heroicons/vue/24/solid'
import { SunIcon } from '@heroicons/vue/24/solid'
import { onMounted, ref } from 'vue'

const theme = ref()

onMounted(() => {
  const currentTheme = document
    .querySelector('html')
    .attributes.getNamedItem('data-theme').nodeValue
  theme.value = currentTheme
  console.info(`Theme: ${currentTheme}`)
})

function onThemeToggle() {
  const previousTheme = document
    .querySelector('html')
    .attributes.getNamedItem('data-theme').nodeValue
  console.info(`Changing theme from: ${previousTheme}`)

  theme.value = previousTheme == 'dark' ? 'light' : 'dark'
}
</script>

<!-- https://github.com/saadeghi/theme-change -->
<template>
  <button
    @click="onThemeToggle()"
    class="btn gap-2 btn-ghost"
    data-toggle-theme="dark,light"
    data-act-class="ACTIVECLASS"
  >
    <MoonIcon v-if="theme == 'light'" class="flex-1 w-5" />
    <SunIcon v-if="theme == 'dark'" class="flex-1 w-5" />
  </button>
</template>
