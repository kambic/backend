<template>
  <div class="file-manager p-4">
    <div class="flex gap-2 mb-4">
      <button
        @click="goBack"
        :disabled="!canGoBack"
        class="btn btn-sm btn-outline">
        Back
      </button>
      <button
        @click="goForward"
        :disabled="!canGoForward"
        class="btn btn-sm btn-outline">
        Forward
      </button>
      <button @click="refresh" class="btn btn-sm btn-primary">Refresh</button>
      <input
        v-model="pathInput"
        @keyup.enter="goToPath"
        class="input input-sm input-bordered ml-4 flex-1"
      />
    </div>
    <div class="text-sm text-gray-500 mb-2">
      Current Path: {{ currentPath }}
    </div>
    <vue-finder
      :driver="driver"
      style="height: 70vh"
      @path-change="onPathChange"
    />
  </div>
</template>

<script setup>
import { ref, watch } from "vue";
import { useVueFinder } from "@/composables/useVueFinder";
import { VueFinder } from "vuefinder";

const finder = useVueFinder({
  baseURL: "/api",
  initialPath: "local://public/documents",
});
const {
  driver,
  currentPath,
  canGoBack,
  canGoForward,
  goBack,
  goForward,
  goTo,
  refresh,
} = finder;

const pathInput = ref(currentPath.value);
watch(currentPath, (newPath) => {
  pathInput.value = newPath;
});
function goToPath() {
  if (pathInput.value) goTo(pathInput.value);
}
function onPathChange(newPath) {
  goTo(newPath);
}
</script>

<style>
.file-manager .vf-item:hover {
  background-color: #f0f9ff;
}
</style>
