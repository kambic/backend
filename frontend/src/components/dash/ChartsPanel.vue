<!-- ================================================== -->
<!-- ChartsPanel.vue -->
<!-- ================================================== -->
<template>

<div class="card bg-base-200">
<div class="card-body">
<h2 class="card-title text-lg">Playback Metrics</h2>
<canvas ref="buf"></canvas>
<canvas ref="br" class="mt-4"></canvas>
</div>
</div>
</template>
<script>
import Chart from "chart.js/auto";

export default {
  data: () => ({ bufferChart: null, bitrateChart: null }),
  mounted() {
    this.init();
  },
  methods: {
    init() {
      this.bufferChart = this.make(this.$refs.buf, "Buffer (s)");
      this.bitrateChart = this.make(this.$refs.br, "Bitrate (kbps)");
    },
    make(ref, label) {
      return new Chart(ref.getContext("2d"), {
        type: "line",
        data: { labels: [], datasets: [{ label, data: [], tension: 0.3 }] },
        options: { animation: false, scales: { x: { display: false } } },
      });
    },
    pushBuffer(v) {
      this.push(this.bufferChart, v);
    },
    pushBitrate(v) {
      this.push(this.bitrateChart, v);
    },
    push(c, v) {
      c.data.labels.push("");
      c.data.datasets[0].data.push(v);
      if (c.data.labels.length > 60) {
        c.data.labels.shift();
        c.data.datasets[0].data.shift();
      }
      c.update("none");
    },
    reset() {
      this.bufferChart.destroy();
      this.bitrateChart.destroy();
      this.init();
    },
  },
};
</script>
