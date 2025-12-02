<!-- ================================================== -->
<!-- PlayerPanel.vue -->
<!-- ================================================== -->
<template>
  <div class="card bg-base-200">
    <div class="card-body">
      <video ref="video" controls class="w-full bg-black"></video>
      <div class="stats shadow mt-3">
        <div class="stat">
          <div class="stat-title">Buffer</div>
          <div class="stat-value text-sm">{{ buffer.toFixed(2) }} s</div>
        </div>
        <div class="stat">
          <div class="stat-title">Quality</div>
          <div class="stat-value text-sm">{{ quality }}</div>
        </div>
        <div class="stat">
          <div class="stat-title">Bitrate</div>
          <div class="stat-value text-sm">{{ bitrate }}</div>
        </div>
      </div>
    </div>
  </div>
</template>
<script>
import dashjs from "dashjs";

export default {
  props: ["manifestUrl"],
  emits: ["buffer", "quality", "event"],
  data: () => ({ player: null, buffer: 0, quality: "-", bitrate: "-" }),
  watch: {
    manifestUrl(url) {
      if (url) this.init(url);
    },
  },
  methods: {
    init(url) {
      if (this.player) this.player.reset();
      this.player = dashjs.MediaPlayer().create();
      this.player.initialize(this.$refs.video, url, true);

      const E = dashjs.MediaPlayer.events;
      this.player.on(E.BUFFER_LEVEL_UPDATED, (e) => {
        this.buffer = e.bufferLevel;
        this.$emit("buffer", e.bufferLevel);
      });

      this.player.on(E.QUALITY_CHANGE_RENDERED, (e) => {
        const info = this.player.getBitrateInfoListFor("video")[e.newQuality];
        const kbps = info ? Math.round(info.bitrate / 1000) : 0;
        this.quality = e.newQuality;
        this.bitrate = kbps + " kbps";
        this.$emit("quality", kbps);
      });

      this.player.on(E.ERROR, (e) => this.$emit("event", "ERROR " + e.error));
    },
  },
};
</script>
