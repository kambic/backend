<script setup lang="ts">
import { onMounted } from "vue";
import { useRouter } from "vue-router";
import { useProviderStore } from "../../stores/provider";
import ProvidersTable from "@/components/provider/ProvidersTable.vue";

const router = useRouter();
const store = useProviderStore();

onMounted(() => {
  store.fetchProviders();
});

function goToProvider(id: string) {
  router.push({ name: "provider-detail", params: { id } });
}
</script>

<template>
  <div class="p-6 max-w-5xl mx-auto">
    <h1 class="text-2xl font-bold mb-6">Providers</h1>

    <div v-if="store.loading" class="flex justify-center">
      <span class="loading loading-spinner loading-lg" />
    </div>

    <div v-else-if="store.error" class="alert alert-error">
      {{ store.error }}
    </div>

    <div v-else class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div
        v-for="p in store.items"
        :key="p.id"
        class="card bg-base-100 shadow hover:shadow-lg cursor-pointer"
        @click="goToProvider(p.slug)"
      >
        <div class="card-body">
          <h2 class="card-title">{{ p.name }}</h2>
          <p class="text-sm opacity-70">{{ p.description }}</p>

          <div class="card-actions justify-end">
            <button class="btn btn-primary btn-sm">View details</button>
          </div>
        </div>
      </div>
    </div>
    <ProvidersTable />
  </div>
</template>
