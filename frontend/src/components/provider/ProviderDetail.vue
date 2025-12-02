<!-- ProviderDetail.vue (Main Component - now uses Pinia) -->
<template>
  <div class="bg-base-200 min-h-screen px-4 py-8">
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
                <span>{{ provider?.vidra_task || "—" }}</span>
              </div>
              <div class="flex justify-between border-b py-3">
                <span class="font-medium">Queue</span>
                <span>{{ provider?.queue || "—" }}</span>
              </div>
            </div>
          </div>
          <div class="space-y-6">
            <div class="bg-base-100 rounded-xl p-6 shadow">
              <h3 class="mb-4 text-xl font-bold">Quick Actions</h3>
              <div class="flex flex-col gap-3">
                <a
                  :href="`/providers/${provider?.id}/edit`"
                  class="btn btn-primary"
                  >Edit Provider</a
                >
                <a
                  :href="`/providers/${provider?.id}/delete`"
                  class="btn btn-error"
                  >Delete Provider</a
                >
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

<script setup>
import { onMounted } from "vue";
import { useRoute } from "vue-router"; // Assuming Vue Router for id
import { useProviderStore } from "@/stores/provider"; // Adjust path
import ProviderHeader from "./ProviderHeader.vue";
import EdgewaresList from "./EdgewaresList.vue";

const route = useRoute();
const store = useProviderStore();

const { provider, edgewares, activeTab, numExpired, setActiveTab } = store;

onMounted(async () => {
  const id = route.params.id; // Assuming route param :id
  await store.fetchProvider(id);
  store.resetCollapses();
});
</script>
