import { defineStore } from "pinia";
import { ref } from "vue";
export const useUIStore = defineStore("ui", () => {
  const collapsed = ref(false);
  function toggleSidebar() {
    collapsed.value = !collapsed.value;
  }
  return { collapsed, toggleSidebar };
});
