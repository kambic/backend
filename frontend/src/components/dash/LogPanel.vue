<!-- ================================================== -->
<!-- LogPanel.vue -->
<!-- ================================================== -->
<template>
  <div class="card bg-base-200">
    <div class="card-body">
      <h2 class="card-title text-lg">Event Log</h2>
      <div class="mockup-code max-h-64 overflow-auto">
        <pre
          v-for="(l, i) in logs"
          :key="i"
        ><code>[{{l.t}}] {{l.m}}</code></pre>
      </div>
    </div>
  </div>
</template>
<script>
export default {
  props: ["logs"],
};
</script>
