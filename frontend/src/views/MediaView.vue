<script setup>
import DashPlayer from "@/components/DashPlayer.vue";
import BarChart from "@/components/charts/BarChart.vue";
import VerticalBarChart from "@/components/charts/VerticalBarChart.vue";
import HorizontalBarChart from "@/components/charts/HorizontalBarChart.vue";
import VercelChart from "@/components/charts/VercelChart.vue";
</script>

<template>
  <div>
    Media View
    <BarChart />
    <VerticalBarChart />
    <HorizontalBarChart />
    <VercelChart />
    <VercelChart />
    <!--  <DashPlayer/>-->
  </div>
</template>

<style scoped lang="scss"></style>
