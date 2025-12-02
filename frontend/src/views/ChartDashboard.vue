<template>
  <div class="min-h-screen bg-base-200 p-4 md:p-8">
    <div class="max-w-6xl mx-auto">
      <!-- Header -->
      <div class="mb-8">
        <h1 class="text-4xl font-bold text-primary mb-2">
          Vue Chart.js Samples
        </h1>
        <p class="text-base-content/70">Composition API with DaisyUI styling</p>
      </div>

      <!-- Tab Navigation -->
      <div role="tablist" class="tabs tabs-boxed bg-base-100 mb-6">
        <a
          v-for="tab in tabs"
          :key="tab.id"
          role="tab"
          class="tab"
          :class="{ 'tab-active': activeTab === tab.id }"
          @click="activeTab = tab.id"
        >
          {{ tab.label }}
        </a>
      </div>

      <!-- Chart Container -->
      <ChartComponent :config="currentChart" />

      <!-- Stats Cards -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mt-6">
        <StatsCard
          v-for="stat in statsData"
          :key="stat.title"
          :title="stat.title"
          :value="stat.value"
          :description="stat.description"
          :icon-path="stat.iconPath"
          :color="stat.color"
        />
      </div>

      <!-- Code Sample -->
      <div class="mockup-code mt-6 bg-neutral text-neutral-content">
        <pre data-prefix="1"><code>&lt;script setup&gt;</code></pre>
        <pre
          data-prefix="2"
        ><code>import { ref, computed } from 'vue'</code></pre>
        <pre
          data-prefix="3"
        ><code>import { Bar } from 'vue-chartjs'</code></pre>
        <pre data-prefix="4"><code></code></pre>
        <pre data-prefix="5"><code>const chartData = ref({ ... })</code></pre>
        <pre data-prefix="6"><code>&lt;/script&gt;</code></pre>
        <pre data-prefix="7"><code></code></pre>
        <pre data-prefix="8"><code>&lt;template&gt;</code></pre>
        <pre
          data-prefix="9"
        ><code>  &lt;Bar :data="chartData" /&gt;</code></pre>
        <pre data-prefix="10"><code>&lt;/template&gt;</code></pre>
      </div>

      <!-- Theme Switcher -->
      <div class="flex justify-center mt-6">
        <div class="dropdown dropdown-top">
          <div tabindex="0" role="button" class="btn btn-primary m-1">
            <svg
              class="w-5 h-5 mr-2"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01"
              ></path>
            </svg>
            Change Theme
          </div>
          <ul
            tabindex="0"
            class="dropdown-content z-[1] p-2 shadow-2xl bg-base-300 rounded-box w-52 max-h-96 overflow-y-auto"
          >
            <li v-for="theme in themes" :key="theme">
              <button
                class="btn btn-sm btn-block btn-ghost justify-start"
                @click="changeTheme(theme)"
              >
                {{ theme }}
              </button>
            </li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from "vue";
import ChartComponent from "../components/charts/ChartComponent.vue";
import StatsCard from "../components/StatsCard.vue";

// State
const activeTab = ref("bar");

// Data
const tabs = ref([
  { id: "bar", label: "Bar Chart" },
  { id: "line", label: "Line Chart" },
  { id: "pie", label: "Pie Chart" },
  { id: "area", label: "Area Chart" },
  { id: "doughnut", label: "Doughnut Chart" },
]);

const themes = ref([
  "light",
  "dark",
  "cupcake",
  "bumblebee",
  "emerald",
  "corporate",
  "synthwave",
  "retro",
  "cyberpunk",
  "valentine",
  "halloween",
  "garden",
  "forest",
  "aqua",
  "lofi",
  "pastel",
  "fantasy",
  "wireframe",
  "black",
  "luxury",
  "dracula",
]);

const chartConfigs = ref({
  bar: {
    title: "Monthly Sales & Expenses",
    type: "bar",
    data: {
      labels: ["January", "February", "March", "April", "May", "June"],
      datasets: [
        {
          label: "Sales",
          backgroundColor: "#3b82f6",
          data: [4000, 3000, 2000, 2780, 1890, 2390],
        },
        {
          label: "Expenses",
          backgroundColor: "#ef4444",
          data: [2400, 1398, 9800, 3908, 4800, 3800],
        },
      ],
    },
  },
  line: {
    title: "Weekly User Activity",
    type: "line",
    data: {
      labels: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
      datasets: [
        {
          label: "Users",
          borderColor: "#8b5cf6",
          backgroundColor: "rgba(139, 92, 246, 0.1)",
          data: [120, 150, 180, 200, 250, 180, 140],
          tension: 0.4,
        },
        {
          label: "Sessions",
          borderColor: "#10b981",
          backgroundColor: "rgba(16, 185, 129, 0.1)",
          data: [240, 300, 350, 380, 450, 320, 280],
          tension: 0.4,
        },
      ],
    },
  },
  pie: {
    title: "Traffic by Device Type",
    type: "pie",
    data: {
      labels: ["Desktop", "Mobile", "Tablet", "Other"],
      datasets: [
        {
          data: [400, 300, 200, 100],
          backgroundColor: ["#0088FE", "#00C49F", "#FFBB28", "#FF8042"],
        },
      ],
    },
  },
  area: {
    title: "Revenue & Profit Trends",
    type: "line",
    data: {
      labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
      datasets: [
        {
          label: "Revenue",
          borderColor: "#f59e0b",
          backgroundColor: "rgba(245, 158, 11, 0.3)",
          data: [4000, 3000, 5000, 4500, 6000, 5500],
          fill: true,
          tension: 0.4,
        },
        {
          label: "Profit",
          borderColor: "#10b981",
          backgroundColor: "rgba(16, 185, 129, 0.3)",
          data: [2400, 1398, 3800, 3908, 4800, 3800],
          fill: true,
          tension: 0.4,
        },
      ],
    },
  },
  doughnut: {
    title: "Market Share Distribution",
    type: "doughnut",
    data: {
      labels: ["Product A", "Product B", "Product C", "Product D", "Product E"],
      datasets: [
        {
          data: [30, 25, 20, 15, 10],
          backgroundColor: [
            "#8b5cf6",
            "#ec4899",
            "#3b82f6",
            "#10b981",
            "#f59e0b",
          ],
        },
      ],
    },
  },
});

const statsData = ref([
  {
    title: "Total Sales",
    value: "16,060",
    description: "Jan - Jun 2024",
    color: "primary",
    iconPath: "M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z",
  },
  {
    title: "Active Users",
    value: "1,220",
    description: "↗︎ 12% (30 days)",
    color: "secondary",
    iconPath:
      "M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4",
  },
  {
    title: "Revenue",
    value: "$29.5K",
    description: "This month",
    color: "accent",
    iconPath:
      "M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4",
  },
  {
    title: "Growth Rate",
    value: "+24%",
    description: "Year over year",
    color: "info",
    iconPath:
      "M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z",
  },
]);

// Computed
const currentChart = computed(() => chartConfigs.value[activeTab.value]);

// Methods
const changeTheme = (theme) => {
  document.documentElement.setAttribute("data-theme", theme);
};
</script>

<style scoped>
/* Add any component-specific styles here */
</style>
