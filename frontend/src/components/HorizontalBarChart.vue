<template>
  <div class="rounded-lg border border-gray-200 bg-white p-8 dark:border-gray-700 dark:bg-gray-900">
    <div class="mb-6">
      <h3 class="text-xl font-medium text-gray-900 dark:text-white">Top Pages</h3>
    </div>

    <div class="h-96">
      <Bar :data="chartData" :options="chartOptions" />
    </div>
  </div>
</template>

<script setup>
import { Bar } from 'vue-chartjs'
import { Chart as ChartJS, Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale } from 'chart.js'

ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale)

const chartData = {
  labels: [
    '/dashboard',
    '/settings',
    '/projects',
    '/analytics',
    '/profile',
    '/billing'
  ],
  datasets: [{
    label: 'Page Views',
    data: [12500, 9800, 8700, 7200, 5100, 4200],
    backgroundColor: '#10b981', // emerald-500
    borderRadius: 8,
    borderSkipped: false
  }]
}

const chartOptions = {
  indexAxis: 'y',
  responsive: true,
  maintainAspectRatio: false,
  plugins: { legend: { display: false } },
  scales: {
    x: { grid: { display: false }, ticks: { color: '#9ca3af' } },
    y: { grid: { display: false }, ticks: { color: '#9ca3af' } }
  }
}
</script>
