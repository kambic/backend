<template>
  <div class="stat bg-base-100 shadow rounded-box">
    <div class="stat-figure" :class="`text-${color}`">
      <component :is="iconComponent" class="w-8 h-8" />
    </div>
    <div class="stat-title">{{ title }}</div>
    <div class="stat-value" :class="`text-${color}`">{{ value }}</div>
    <div class="stat-desc">{{ desc }}</div>
  </div>
</template>

<script setup>
defineProps({
  title: String,
  value: String,
  desc: String,
  color: { type: String, default: 'primary' }
})

const icons = {
  chart: () => import('vue-tabler-icons').then(m => m.IconChartBar),
  users: () => import('vue-tabler-icons').then(m => m.IconUsers),
  dollar: () => import('vue-tabler-icons').then(m => m.IconCurrencyDollar),
  trend: () => import('vue-tabler-icons').then(m => m.IconTrendingUp)
}

const iconComponent = defineAsyncComponent(() => icons[props.icon] || icons.chart)
</script>
