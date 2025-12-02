<template>
  <div class="min-h-screen bg-base-200 p-4">
    <div class="max-w-7xl mx-auto space-y-4">
      <HeaderControls
        :manifest-url="manifestUrl"
        @load="initPlayer"
        @reset="clearData"
      />

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <PlayerPanel
          ref="playerPanel"
          :manifest-url="manifestUrl"
          @buffer="onBuffer"
          @quality="onQuality"
          @event="log"
        />

        <ChartsPanel ref="chartsPanel" />
      </div>

      <LogPanel :logs="logs" />

      <div class="alert">
        <span class="font-semibold">Related tools:</span>
        <span
          >dash.js, Shaka Player, Video.js, DevTools HAR, MPD validators</span
        >
      </div>
    </div>
  </div>
</template>

<script setup>
// === Root Demo Page ===
import { ref } from "vue";
import HeaderControls from "./dash/HeaderControls.vue";
import PlayerPanel from "./dash/PlayerPanel.vue";
import ChartsPanel from "./dash/ChartsPanel.vue";
import LogPanel from "./dash/LogPanel.vue";

const manifestUrl = ref("");
const logs = ref([]);

const chartsPanel = ref();

function log(msg) {
  logs.value.unshift({ t: new Date().toLocaleTimeString(), m: msg });
  if (logs.value.length > 200) logs.value.pop();
}

function onBuffer(val) {
  chartsPanel.value?.pushBuffer(val);
}
function onQuality(kbps) {
  chartsPanel.value?.pushBitrate(kbps);
}

function initPlayer(url) {
  manifestUrl.value = url;
  log("Load MPD");
}
function clearData() {
  logs.value = [];
  chartsPanel.value?.reset();
}
</script>
