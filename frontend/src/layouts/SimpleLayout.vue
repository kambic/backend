<script setup>
import TheNavbar from '@/components/layout/TheNavbar.vue'
import TheFooter from '@/components/layout/TheFooter.vue'
import menuAndSearch from '@/components/sidebar/menuAndSearch.vue'
</script>

<template>
  <TheNavbar />
  <div class="sm:flex container p-5 mx-auto content justify-betweenflex-wrap">
    <menuAndSearch />
    <RouterView class="view main-content w-full order-2"></RouterView>
    <RouterView name="LeftSidebar" class="view order-1 w-full"></RouterView>
    <RouterView name="RightSidebar" class="view order-3 w-full"></RouterView>
  </div>
  <TheFooter />
</template>
