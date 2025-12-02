<!-- ================================================== -->
<!-- HeaderControls.vue -->
<!-- ================================================== -->
<template>
  <div class="card bg-base-100 shadow">
    <div class="card-body flex gap-2">
      <input
        v-model="url"
        class="input input-bordered flex-1"
        placeholder="DASH MPD URL"
      />
      <button class="btn btn-primary" @click="$emit('load', url)">Load</button>
      <button class="btn" @click="$emit('reset')">Reset</button>
    </div>
  </div>
</template>

<script>
export default {
  props: ["manifestUrl"],
  emits: ["load", "reset"],
  data: () => ({ url: "https://dash.akamaized.net/akamai/bbb_30fps/bbb_30fps.mpd" }),
};
</script>
