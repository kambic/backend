<template>
  <div class="min-h-screen bg-base-200 p-4 md:p-8">
    <div class="max-w-7xl mx-auto">
      <!-- Header -->
      <div class="mb-8">
        <h1 class="text-4xl font-bold text-primary mb-2">
          DASH.js Player Metrics Dashboard
        </h1>
        <p class="text-base-content/70">
          Real-time streaming metrics visualization
        </p>
      </div>

      <!-- Video Player -->
      <div class="card bg-base-100 shadow-xl mb-6">
        <div class="card-body">
          <h2 class="card-title text-2xl mb-4">Video Player</h2>
          <div class="relative bg-black rounded-lg overflow-hidden">
            <video ref="videoPlayer" class="w-full" controls autoplay></video>
          </div>

          <!-- Player Controls -->
          <div class="flex flex-wrap gap-2 mt-4">
            <button
              class="btn btn-primary btn-sm"
              @click="loadStream"
              :disabled="isPlaying"
            >
              Load Stream
            </button>
            <button class="btn btn-secondary btn-sm" @click="togglePlayPause">
              {{ isPlaying ? "Pause" : "Play" }}
            </button>
            <button class="btn btn-accent btn-sm" @click="resetMetrics">
              Reset Metrics
            </button>
            <select
              class="select select-bordered select-sm"
              v-model="selectedQuality"
              @change="changeQuality"
            >
              <option disabled value="">Quality</option>
              <option
                v-for="quality in availableQualities"
                :key="quality.index"
                :value="quality.index"
              >
                {{ quality.height }}p - {{ quality.bitrate }}kbps
              </option>
            </select>
          </div>
        </div>
      </div>

      <!-- Real-time Stats Cards -->
      <div class="grid grid-cols-1 md:grid-cols-5 gap-4 mb-6">
        <StatsCard
          title="Bitrate"
          :value="currentMetrics.bitrate"
          description="Current quality"
          :icon-path="icons.bitrate"
          color="primary"
        />
        <StatsCard
          title="Buffer Level"
          :value="currentMetrics.bufferLevel"
          description="Seconds buffered"
          :icon-path="icons.buffer"
          color="secondary"
        />
        <StatsCard
          title="Dropped Frames"
          :value="currentMetrics.droppedFrames"
          description="Total dropped"
          :icon-path="icons.frames"
          color="warning"
        />
        <StatsCard
          title="Latency"
          :value="currentMetrics.latency"
          description="Current delay"
          :icon-path="icons.latency"
          color="info"
        />
        <StatsCard
          title="Download Speed"
          :value="currentMetrics.downloadSpeed"
          description="Mbps"
          :icon-path="icons.speed"
          color="success"
        />
      </div>

      <!-- Tab Navigation -->
      <div role="tablist" class="tabs tabs-boxed bg-base-100 mb-6">
        <a
          v-for="tab in tabs"
          :key="tab.id"
          role="tab"
          class="tab"
          :class="{ 'tab-active': activeTab === tab.id }"
          @click="activeTab = tab.id"
        >
          {{ tab.label }}
        </a>
      </div>

      <!-- Charts Grid -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ChartComponent
          v-if="activeTab === 'bitrate' || activeTab === 'all'"
          :config="charts.bitrate"
        />
        <ChartComponent
          v-if="activeTab === 'buffer' || activeTab === 'all'"
          :config="charts.buffer"
        />
        <ChartComponent
          v-if="activeTab === 'latency' || activeTab === 'all'"
          :config="charts.latency"
        />
        <ChartComponent
          v-if="activeTab === 'throughput' || activeTab === 'all'"
          :config="charts.throughput"
        />
      </div>

      <!-- Detailed Metrics Table -->
      <div class="card bg-base-100 shadow-xl mt-6">
        <div class="card-body">
          <h2 class="card-title text-2xl mb-4">Detailed Metrics</h2>
          <div class="overflow-x-auto">
            <table class="table table-zebra">
              <thead>
                <tr>
                  <th>Metric</th>
                  <th>Current Value</th>
                  <th>Average</th>
                  <th>Peak</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>Video Bitrate</td>
                  <td>{{ currentMetrics.bitrate }}</td>
                  <td>{{ averageMetrics.bitrate }}</td>
                  <td>{{ peakMetrics.bitrate }}</td>
                </tr>
                <tr>
                  <td>Buffer Level</td>
                  <td>{{ currentMetrics.bufferLevel }}</td>
                  <td>{{ averageMetrics.bufferLevel }}</td>
                  <td>{{ peakMetrics.bufferLevel }}</td>
                </tr>
                <tr>
                  <td>Latency</td>
                  <td>{{ currentMetrics.latency }}</td>
                  <td>{{ averageMetrics.latency }}</td>
                  <td>{{ peakMetrics.latency }}</td>
                </tr>
                <tr>
                  <td>Download Speed</td>
                  <td>{{ currentMetrics.downloadSpeed }}</td>
                  <td>{{ averageMetrics.downloadSpeed }}</td>
                  <td>{{ peakMetrics.downloadSpeed }}</td>
                </tr>
                <tr>
                  <td>Total Dropped Frames</td>
                  <td>{{ currentMetrics.droppedFrames }}</td>
                  <td>-</td>
                  <td>-</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onBeforeUnmount } from "vue";
import ChartComponent from "../components/charts/ChartComponent.vue";
import StatsCard from "../components/StatsCard.vue";

// Refs
const videoPlayer = ref(null);
const player = ref(null);
const isPlaying = ref(false);
const activeTab = ref("all");
const selectedQuality = ref("");
const availableQualities = ref([]);

// Sample DASH stream URL (Big Buck Bunny)
const streamUrl = "https://dash.akamaized.net/akamai/bbb_30fps/bbb_30fps.mpd";

// Metrics storage
const metricsHistory = reactive({
  bitrate: [],
  buffer: [],
  latency: [],
  throughput: [],
  timestamps: [],
});

const currentMetrics = reactive({
  bitrate: "0 kbps",
  bufferLevel: "0s",
  droppedFrames: "0",
  latency: "0ms",
  downloadSpeed: "0 Mbps",
});

const averageMetrics = reactive({
  bitrate: "0 kbps",
  bufferLevel: "0s",
  latency: "0ms",
  downloadSpeed: "0 Mbps",
});

const peakMetrics = reactive({
  bitrate: "0 kbps",
  bufferLevel: "0s",
  latency: "0ms",
  downloadSpeed: "0 Mbps",
});

// Icons
const icons = {
  bitrate:
    "M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z",
  buffer:
    "M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15",
  frames:
    "M7 4v16M17 4v16M3 8h4m10 0h4M3 12h18M3 16h4m10 0h4M4 20h16a1 1 0 001-1V5a1 1 0 00-1-1H4a1 1 0 00-1 1v14a1 1 0 001 1z",
  latency: "M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z",
  speed: "M13 10V3L4 14h7v7l9-11h-7z",
};

// Tabs
const tabs = ref([
  { id: "all", label: "All Metrics" },
  { id: "bitrate", label: "Bitrate" },
  { id: "buffer", label: "Buffer" },
  { id: "latency", label: "Latency" },
  { id: "throughput", label: "Throughput" },
]);

// Chart configurations
const charts = reactive({
  bitrate: {
    title: "Video Bitrate Over Time",
    type: "line",
    data: {
      labels: [],
      datasets: [
        {
          label: "Bitrate (kbps)",
          borderColor: "#3b82f6",
          backgroundColor: "rgba(59, 130, 246, 0.1)",
          data: [],
          tension: 0.4,
          fill: true,
        },
      ],
    },
  },
  buffer: {
    title: "Buffer Level",
    type: "line",
    data: {
      labels: [],
      datasets: [
        {
          label: "Buffer (seconds)",
          borderColor: "#8b5cf6",
          backgroundColor: "rgba(139, 92, 246, 0.1)",
          data: [],
          tension: 0.4,
          fill: true,
        },
      ],
    },
  },
  latency: {
    title: "Latency",
    type: "line",
    data: {
      labels: [],
      datasets: [
        {
          label: "Latency (ms)",
          borderColor: "#06b6d4",
          backgroundColor: "rgba(6, 182, 212, 0.1)",
          data: [],
          tension: 0.4,
          fill: true,
        },
      ],
    },
  },
  throughput: {
    title: "Download Throughput",
    type: "line",
    data: {
      labels: [],
      datasets: [
        {
          label: "Speed (Mbps)",
          borderColor: "#10b981",
          backgroundColor: "rgba(16, 185, 129, 0.1)",
          data: [],
          tension: 0.4,
          fill: true,
        },
      ],
    },
  },
});

// Methods
const loadStream = () => {
  if (!videoPlayer.value) return;

  // Initialize dash.js player
  if (typeof dashjs !== "undefined") {
    player.value = dashjs.MediaPlayer().create();
    player.value.initialize(videoPlayer.value, streamUrl, true);

    // Setup event listeners
    setupDashListeners();
    isPlaying.value = true;
  } else {
    console.error("dash.js not loaded");
  }
};

const setupDashListeners = () => {
  if (player.value) return;

  // Quality change event
  player.value.on(dashjs.MediaPlayer.events.QUALITY_CHANGE_RENDERED, (e) => {
    updateBitrateMetric(e);
  });

  // Buffer level update
  player.value.on(dashjs.MediaPlayer.events.BUFFER_LEVEL_UPDATED, (e) => {
    updateBufferMetric(e);
  });

  // Fragment loaded
  player.value.on(dashjs.MediaPlayer.events.FRAGMENT_LOADING_COMPLETED, (e) => {
    updateThroughputMetric(e);
  });

  // Stream initialized
  player.value.on(dashjs.MediaPlayer.events.STREAM_INITIALIZED, () => {
    const metrics = player.value.getDashMetrics();
    const bitrateList = metrics?.getBitrateInfoListFor();

    console.log(`[DASH] Available qualities:`);
    availableQualities.value = bitrateList?.map((item, index) => ({
      index,
      height: item.height,
      bitrate: Math.round(item.bitrate / 1000),
    }));
  });

  // Start metrics update interval
  startMetricsUpdate();
};

const updateBitrateMetric = (e) => {
  if (e.mediaType === "video") {
    const bitrate = Math.round(e.newQuality.bitrate / 1000);
    currentMetrics.bitrate = `${bitrate} kbps`;
    addMetricData("bitrate", bitrate);
  }
};

const updateBufferMetric = (e) => {
  if (e.mediaType === "video") {
    const buffer = e.bufferLevel.toFixed(2);
    currentMetrics.bufferLevel = `${buffer}s`;
    addMetricData("buffer", parseFloat(buffer));
  }
};

const updateThroughputMetric = (e) => {
  const request = e.request;
  if (request && request.type === "MediaSegment") {
    const speed = (
      (request.bytesLoaded * 8) /
      (request.requestEndDate.getTime() - request.requestStartDate.getTime()) /
      1000
    ).toFixed(2);
    currentMetrics.downloadSpeed = `${speed} Mbps`;
    addMetricData("throughput", parseFloat(speed));
  }
};

const addMetricData = (metric, value) => {
  const now = new Date().toLocaleTimeString();

  metricsHistory[metric].push(value);
  if (!metricsHistory.timestamps.includes(now)) {
    metricsHistory.timestamps.push(now);
  }

  // Keep only last 30 data points
  if (metricsHistory[metric].length > 30) {
    metricsHistory[metric].shift();
  }
  if (metricsHistory.timestamps.length > 30) {
    metricsHistory.timestamps.shift();
  }

  // Update charts
  updateCharts();
  updateAverageAndPeak();
};

const updateCharts = () => {
  charts.bitrate.data.labels = [...metricsHistory.timestamps];
  charts.bitrate.data.datasets[0].data = [...metricsHistory.bitrate];

  charts.buffer.data.labels = [...metricsHistory.timestamps];
  charts.buffer.data.datasets[0].data = [...metricsHistory.buffer];

  charts.latency.data.labels = [...metricsHistory.timestamps];
  charts.latency.data.datasets[0].data =
    metricsHistory.latency.length > 0
      ? [...metricsHistory.latency]
      : metricsHistory.buffer.map((b) => Math.max(0, 100 - b * 10));

  charts.throughput.data.labels = [...metricsHistory.timestamps];
  charts.throughput.data.datasets[0].data = [...metricsHistory.throughput];
};

const updateAverageAndPeak = () => {
  // Bitrate
  if (metricsHistory.bitrate.length > 0) {
    const avgBitrate = Math.round(
      metricsHistory.bitrate.reduce((a, b) => a + b, 0) /
        metricsHistory.bitrate.length,
    );
    const peakBitrate = Math.max(...metricsHistory.bitrate);
    averageMetrics.bitrate = `${avgBitrate} kbps`;
    peakMetrics.bitrate = `${peakBitrate} kbps`;
  }

  // Buffer
  if (metricsHistory.buffer.length > 0) {
    const avgBuffer = (
      metricsHistory.buffer.reduce((a, b) => a + b, 0) /
      metricsHistory.buffer.length
    ).toFixed(2);
    const peakBuffer = Math.max(...metricsHistory.buffer).toFixed(2);
    averageMetrics.bufferLevel = `${avgBuffer}s`;
    peakMetrics.bufferLevel = `${peakBuffer}s`;
  }

  // Throughput
  if (metricsHistory.throughput.length > 0) {
    const avgSpeed = (
      metricsHistory.throughput.reduce((a, b) => a + b, 0) /
      metricsHistory.throughput.length
    ).toFixed(2);
    const peakSpeed = Math.max(...metricsHistory.throughput).toFixed(2);
    averageMetrics.downloadSpeed = `${avgSpeed} Mbps`;
    peakMetrics.downloadSpeed = `${peakSpeed} Mbps`;
  }
};

const startMetricsUpdate = () => {
  setInterval(() => {
    if (player.value && videoPlayer.value) {
      // Update dropped frames
      const videoElement = videoPlayer.value;
      if (videoElement.getVideoPlaybackQuality) {
        const quality = videoElement.getVideoPlaybackQuality();
        currentMetrics.droppedFrames = quality.droppedVideoFrames.toString();
      }

      // Simulate latency based on buffer
      const bufferValue = parseFloat(currentMetrics.bufferLevel);
      const latency = Math.max(50, 200 - bufferValue * 15);
      currentMetrics.latency = `${Math.round(latency)}ms`;

      if (!metricsHistory.latency) metricsHistory.latency = [];
      metricsHistory.latency.push(Math.round(latency));
      if (metricsHistory.latency.length > 30) {
        metricsHistory.latency.shift();
      }
    }
  }, 1000);
};

const togglePlayPause = () => {
  if (videoPlayer.value) {
    if (isPlaying.value) {
      videoPlayer.value.pause();
      isPlaying.value = false;
    } else {
      videoPlayer.value.play();
      isPlaying.value = true;
    }
  }
};

const changeQuality = () => {
  if (player.value && selectedQuality.value !== "") {
    player.value.setQualityFor("video", selectedQuality.value);
  }
};

const resetMetrics = () => {
  metricsHistory.bitrate = [];
  metricsHistory.buffer = [];
  metricsHistory.latency = [];
  metricsHistory.throughput = [];
  metricsHistory.timestamps = [];

  currentMetrics.bitrate = "0 kbps";
  currentMetrics.bufferLevel = "0s";
  currentMetrics.droppedFrames = "0";
  currentMetrics.latency = "0ms";
  currentMetrics.downloadSpeed = "0 Mbps";

  updateCharts();
};

// Lifecycle
onMounted(() => {
  // Load dash.js library dynamically
  const script = document.createElement("script");
  script.src = "https://cdn.dashjs.org/latest/dash.all.min.js";
  script.onload = () => {
    console.log("dash.js loaded successfully");
  };
  document.head.appendChild(script);
});

onBeforeUnmount(() => {
  if (player.value) {
    player.value.reset();
  }
});
</script>

<style scoped>
video {
  max-height: 500px;
}
</style>
