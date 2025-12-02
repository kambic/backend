<script setup>
import TemplatePackages from "@/components/Home/TemplatePackages.vue";
import ThemeController from "@/components/Home/ThemeController.vue";
import Guide from "@/components/Home/Guide.vue";
// import FileManager from "@/components/FileManager.vue";
</script>

<template>
  <!-- Title -->

  <!-- Banner -->

  <!-- Packages -->
  <div class="bg-base-300 text-base-content text-center mb-10">
    <div class="container-center pb-4">
      <TemplatePackages />
    </div>
  </div>

  <!-- Theme Controller -->
  <div class="container-center text-center">
    <ThemeController class="mb-10" />
  </div>

  <!-- Components Preview -->
  <div class="bg-base-300 text-base-content mb-10">
    <div class="container-center py-10">
      <!--      <FileManager />-->
    </div>
  </div>

  <!-- Guide -->
  <div class="container-center">
    <Guide />
  </div>
</template>

<style scoped lang="scss"></style>
