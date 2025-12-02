<template>
  <div class="card bg-base-100 shadow-xl">
    <div class="card-body">
      <h2 class="card-title text-2xl mb-4">{{ config.title }}</h2>
      <canvas ref="chartCanvas" class="w-full" style="max-height: 400px;"></canvas>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, nextTick } from 'vue'
import { Chart, registerables } from 'chart.js'

Chart.register(...registerables)

// Props
const props = defineProps({
  config: {
    type: Object,
    required: true
  }
})

// Refs
const chartCanvas = ref(null)
const chartInstance = ref(null)

// Methods
const renderChart = () => {
  nextTick(() => {
    if (!chartCanvas.value) return

    // Destroy existing chart
    if (chartInstance.value) {
      chartInstance.value.destroy()
    }

    // Create new chart
    const ctx = chartCanvas.value.getContext('2d')
    chartInstance.value = new Chart(ctx, {
      type: props.config.type,
      data: props.config.data,
      options: {
        responsive: true,
        maintainAspectRatio: true,
        plugins: {
          legend: {
            position: 'top',
          }
        }
      }
    })
  })
}

// Watch for config changes
watch(() => props.config, renderChart, { deep: true })

// Lifecycle
onMounted(renderChart)
</script>

<style scoped>
/* Add any component-specific styles here */
</style>
