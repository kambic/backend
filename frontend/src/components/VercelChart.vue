<template>
  <div class="mx-auto max-w-4xl p-6">
    <!-- Headless UI style card -->
    <div class="overflow-hidden rounded-xl border border-gray-200 bg-white dark:border-gray-800 dark:bg-gray-900">
      <div class="border-b border-gray-200 dark:border-gray-800 px-6 py-4">
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
          Monthly Active Users
        </h3>
        <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
          Jan – Jun 2025
        </p>
      </div>

      <div class="p-6">
        <div class="h-96 w-full">
          <Bar :data="chartData" :options="chartOptions" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Bar } from 'vue-chartjs'
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale
} from 'chart.js'

ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale)

const chartData = {
  labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
  datasets: [
    {
      label: 'MAU',
      data: [32000, 41000, 48000, 55000, 68000, 79000],
      backgroundColor: 'rgb(79, 70, 229)', // indigo-600
      borderRadius: 6,
      borderSkipped: false,
      barThickness: 20
    }
  ]
}

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
    tooltip: {
      backgroundColor: 'rgba(0, 0, 0, 0.8)',
      cornerRadius: 8,
      padding: 12
    }
  },
  scales: {
    x: { grid: { display: false }, ticks: { color: '#6b7280' } },
    y: {
      grid: { color: '#e5e7eb', drawBorder: false },
      ticks: { color: '#6b7280', callback: (v) => `${v / 1000}k` }
    }
  }
}
</script>
