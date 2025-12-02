<template>
  <div class="max-w-4xl mx-auto p-6">
    <div class="stats shadow w-full bg-base-200">
      <div class="stat place-items-center">
        <div class="stat-title">Total Users</div>
        <div class="stat-value text-primary">89K</div>
        <div class="stat-desc">+23% from last month</div>
      </div>
    </div>

    <div class="mt-8 card bg-base-100 shadow-lg">
      <div class="card-body">
        <h2 class="card-title">User Growth by Region</h2>
        <div class="h-80">
          <Bar :data="chartData" :options="chartOptions" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Bar } from 'vue-chartjs'
import { Chart as ChartJS, Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale } from 'chart.js'

ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale)

const chartData = {
  labels: ['North America', 'Europe', 'Asia', 'South America', 'Africa'],
  datasets: [{
    label: 'Users (K)',
    data: [45, 32, 28, 18, 12],
    backgroundColor: [
      'rgb(239, 68, 68)',   // red-500
      'rgb(249, 115, 22)',  // orange-500
      'rgb(234, 179, 8)',   // yellow-500
      'rgb(34, 197, 94)',   // green-500
      'rgb(99, 102, 241)'   // indigo-500
    ],
    borderRadius: 6
  }]
}

const chartOptions = {
  indexAxis: 'y',
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false }
  },
  scales: {
    x: { grid: { display: false } },
    y: { grid: { display: false } }
  }
}
</script>
