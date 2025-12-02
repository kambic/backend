<script setup>
import { useProviderStore } from "../../stores/provider.js"; // Adjust path
import ProviderHeader from "../../components/provider/ProviderHeader.vue";
import EdgewaresList from "../../components/provider/EdgewaresList.vue";
import { computed, onMounted, watch } from "vue";
import { useRoute } from "vue-router";

const route = useRoute();
const providerId = route.params.id; // Renamed from postId for clarity

const store = useProviderStore();

// Computed properties to access store state (avoids direct binding, prevents cycles)
const provider = computed(() => store.current);
const numExpired = computed(() => store.numExpired);
const activeTab = computed(() => store.activeTab);
const edgewares = computed(() => store.edgewares);
const loading = computed(() => store.loading);
const error = computed(() => store.error);

const setActiveTab = (tab) => store.setActiveTab(tab);

// Fetch provider on mount
onMounted(async () => {
  await store.fetchProvider(providerId);
  // Load edgewares after provider is fetched
  if (store.currentProvider) {
    await store.loadEdgewares(providerId);
  }
});

// Watch for tab changes to lazy-load if needed (e.g., edgewares on tab switch)
watch(activeTab, (newTab) => {
  if (
    newTab === "edgewares" &&
    store.currentProvider &&
    !edgewares.value.length
  ) {
    store.loadEdgewares(providerId);
  }
});

// Handle loading/error states globally if needed
if (error.value) {
  console.error("Provider error:", error.value);
}
</script>

<template>
  <div v-if="loading" class="flex justify-center items-center min-h-screen">
    <span class="loading loading-spinner loading-lg"></span>
  </div>
  <div v-else-if="error" class="bg-base-200 min-h-screen px-4 py-8">
    <div class="alert alert-error mx-auto max-w-7xl">
      <span>{{ error }}</span>
    </div>
  </div>
  <div v-else-if="!provider" class="bg-base-200 min-h-screen px-4 py-8">
    <p class="text-center text-xl">Provider not found.</p>
  </div>
  <div v-else class="bg-base-200 min-h-screen px-4 py-8">
    <div class="mx-auto max-w-7xl">
      <!-- Header -->
      <ProviderHeader :provider="provider" :num-expired="numExpired" />
      <!-- Tabs -->
      <div class="tabs tabs-bordered mb-8">
        <a
          class="tab tab-lg"
          :class="{ 'tab-active': activeTab === 'overview' }"
          @click="setActiveTab('overview')"
        >
          Overview
        </a>
        <a
          class="tab tab-lg"
          :class="{ 'tab-active': activeTab === 'edgewares' }"
          @click="setActiveTab('edgewares')"
        >
          Edgewares ({{ edgewares.length }})
        </a>
      </div>
      <!-- Overview Tab -->
      <div v-if="activeTab === 'overview'" id="overview-tab">
        <div class="mb-8 grid grid-cols-1 gap-6 lg:grid-cols-3">
          <div class="bg-base-100 rounded-xl p-8 shadow lg:col-span-2">
            <h2 class="mb-6 text-2xl font-bold">Provider Configuration</h2>
            <div class="space-y-4 text-lg">
              <div class="flex justify-between border-b py-3">
                <span class="font-medium">Vidra Task</span>
                <span>{{ provider.vidra_task || "—" }}</span>
              </div>
              <div class="flex justify-between border-b py-3">
                <span class="font-medium">Queue</span>
                <span>{{ provider.queue || "—" }}</span>
              </div>
            </div>
          </div>
          <div class="space-y-6">
            <div class="bg-base-100 rounded-xl p-6 shadow">
              <h3 class="mb-4 text-xl font-bold">Quick Actions</h3>
              <div class="flex flex-col gap-3">
                <router-link
                  :to="`/providers/${provider.id}/edit`"
                  class="btn btn-primary"
                >
                  Edit Provider
                </router-link>
                <router-link
                  :to="`/providers/${provider.id}/delete`"
                  class="btn btn-error"
                >
                  Delete Provider
                </router-link>
              </div>
            </div>
          </div>
        </div>
      </div>
      <!-- Edgewares Tab -->
      <div v-if="activeTab === 'edgewares'" id="edgewares-tab">
        <EdgewaresList :edgewares="edgewares" v-if="edgewares.length > 0" />
        <div v-else class="bg-base-100 rounded-xl py-16 text-center">
          <p class="text-base-content/60 text-xl">
            No edgewares found for this provider.
          </p>
        </div>
      </div>
    </div>
  </div>
</template>
