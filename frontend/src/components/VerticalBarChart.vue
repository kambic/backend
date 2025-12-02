<template>
  <div class="card w-full max-w-2xl mx-auto bg-base-100 shadow-xl">
    <div class="card-body">
      <h2 class="card-title text-primary">Monthly Revenue 2025</h2>
      <div class="h-96">
        <Bar :data="chartData" :options="chartOptions" />
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
      label: 'Revenue ($K)',
      data: [65, 78, 92, 88, 105, 120],
      backgroundColor: 'rgba(99, 102, 241, 0.7)', // indigo-500 with opacity
      borderColor: '#6366f1',
      borderWidth: 2,
      borderRadius: 8,
      borderSkipped: false
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
      titleColor: '#fff',
      bodyColor: '#fff',
      cornerRadius: 8
    }
  },
  scales: {
    y: {
      beginAtZero: true,
      grid: { display: false },
      ticks: { color: '#94a3b8' }
    },
    x: {
      grid: { display: false },
      ticks: { color: '#94a3b8' }
    }
  }
}
</script>

<style scoped>
/* Optional: make chart canvas background match DaisyUI card */
canvas {
  background-color: transparent;
}
</style>
