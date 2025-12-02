<template>
  <div class="stat bg-base-100 shadow rounded-box">
    <div class="stat-figure" :class="`text-${color}`">
      <svg
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 24 24"
        class="inline-block w-8 h-8 stroke-current"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          :d="iconPath"
        />
      </svg>
    </div>
    <div class="stat-title">{{ title }}</div>
    <div class="stat-value" :class="`text-${color}`">{{ value }}</div>
    <div class="stat-desc">{{ description }}</div>
  </div>
</template>

<script setup>
// Props
defineProps({
  title: {
    type: String,
    required: true
  },
  value: {
    type: String,
    required: true
  },
  description: {
    type: String,
    required: true
  },
  iconPath: {
    type: String,
    required: true
  },
  color: {
    type: String,
    default: 'primary'
  }
})
</script>

<style scoped>
/* Add any component-specific styles here */
</style>
