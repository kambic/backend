<!-- ProviderHeader.vue (Updated to use computed numExpired) -->
<template>
  <div class="bg-base-100 mb-8 rounded-xl p-8 shadow-lg">
    <div class="flex flex-col items-start justify-between gap-6 sm:flex-row">
      <div>
        <h1 class="text-primary text-4xl font-bold">
          {{ provider?.user?.username }}
        </h1>
        <p class="mt-2 text-xl opacity-80">{{ provider?.user?.email }}</p>
        <div class="mt-4 flex flex-wrap items-center gap-3">
          <span class="badge badge-lg badge-ghost">ID: {{ provider?.id }}</span>
          <span class="badge badge-lg badge-warning">
            {{ numExpired }} Expired Edgeware{{ numExpired === 1 ? "" : "s" }}
          </span>
        </div>
      </div>
      <router-link :to="{ name: 'providers' }" class="btn btn-ghost btn-lg">
        ← Back to Providers
      </router-link>
    </div>
  </div>
</template>

<script setup>
defineProps({
  provider: {
    type: Object,
    required: true,
  },
  numExpired: {
    type: Number,
    default: 0,
  },
});
</script>
