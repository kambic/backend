<!-- EdgewareCard.vue (Unchanged) -->
<template>
  <div class="bg-base-100 overflow-hidden rounded-xl shadow-lg">
    <div class="collapse-arrow border-base-300 collapse border">
      <input type="checkbox" />
      <div
        class="collapse-title flex items-center justify-between pr-8 text-xl font-bold"
      >
        <div class="flex items-center gap-4">
          <span class="max-w-md truncate">{{ edge.title || "Untitled" }}</span>
          <span v-if="edge.expired" class="badge badge-error badge-sm"
            >EXPIRED</span
          >
        </div>
        <div class="flex items-center gap-3 text-sm">
          <span
            :class="[
              'badge',
              edge.status === 'done'
                ? 'badge-success'
                : edge.status === 'ew_error' || edge.status === 'ftp_error'
                  ? 'badge-error'
                  : edge.status === 'ew_pending'
                    ? 'badge-warning'
                    : 'badge-ghost',
            ]"
          >
            {{ getStatusDisplay(edge.status) }}
          </span>
          <span class="text-base-content/70" v-if="edge.content_duration_ms">
            ⏱ {{ formatDuration(edge.content_duration_ms) }}
          </span>
        </div>
      </div>
      <div class="collapse-content">
        <div class="bg-base-200 grid grid-cols-1 gap-6 p-6 md:grid-cols-2">
          <div class="space-y-3">
            <div>
              <strong>EW ID:</strong>
              <code class="text-xs">{{ edge.ew_id || "—" }}</code>
            </div>
            <div><strong>Offer ID:</strong> {{ edge.offer_id || "—" }}</div>
            <div>
              <strong>Encoder:</strong>
              <span class="badge badge-outline">{{
                getEncoderDisplay(edge.encoder)
              }}</span>
            </div>
            <div>
              <strong>Ingested:</strong> {{ formatDate(edge.ingested) || "—" }}
            </div>
            <div>
              <strong>Expired:</strong> {{ formatDate(edge.expired) || "—" }}
            </div>
          </div>
          <div class="space-y-3">
            <div><strong>Host:</strong> {{ edge.host || "—" }}</div>
            <div>
              <strong>FTP Dir:</strong>
              <code class="text-xs break-all">{{ edge.ftp_dir || "—" }}</code>
            </div>
            <div>
              <strong>Playable:</strong> {{ edge.playable ? "Yes" : "No" }}
            </div>
          </div>
        </div>

        <!-- Streams Table -->
        <div
          v-if="edge.stream_set && edge.stream_set.length > 0"
          class="border-base-300 border-t p-6"
        >
          <h4 class="mb-4 text-lg font-bold">Streams</h4>
          <div class="overflow-x-auto">
            <table class="table-sm table-zebra table">
              <thead>
                <tr>
                  <th>Type</th>
                  <th>URI</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="stream in edge.stream_set" :key="stream.id">
                  <td>
                    <span class="badge badge-primary badge-sm">{{
                      stream.type.toUpperCase()
                    }}</span>
                  </td>
                  <td class="max-w-xs font-mono text-xs break-all">
                    {{ stream.uri }}
                  </td>
                  <td>
                    <button
                      @click="$emit('copy-uri', stream.uri)"
                      class="btn btn-xs btn-ghost"
                      title="Copy"
                    >
                      Copy
                    </button>
                    <a
                      :href="stream.uri"
                      target="_blank"
                      class="btn btn-xs btn-ghost"
                      title="Open"
                    >
                      Open
                    </a>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        <div
          v-else-if="edge.stream_set"
          class="border-base-300 text-base-content/60 border-t p-6 text-center"
        >
          No streams available
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits } from "vue";

defineProps({
  edge: {
    type: Object,
    required: true,
  },
});

defineEmits(["copy-uri"]);

const getStatusDisplay = (status) => {
  const statusMap = {
    done: "Done",
    ew_error: "EW Error",
    ftp_error: "FTP Error",
    ew_pending: "Pending",
    // Add more as needed
  };
  return statusMap[status] || status;
};

const getEncoderDisplay = (encoder) => {
  const encoderMap = {
    // e.g., 'h264': 'H.264', etc.
  };
  return encoderMap[encoder] || encoder || "—";
};

const formatDate = (dateStr) => {
  if (!dateStr) return null;
  return new Date(dateStr).toLocaleString("en-GB", {
    day: "numeric",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
};

const formatDuration = (ms) => {
  if (!ms) return "";
  const seconds = Math.floor(ms / 1000);
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);
  if (hours > 0) return `${hours}h ${minutes % 60}m`;
  if (minutes > 0) return `${minutes}m ${seconds % 60}s`;
  return `${seconds}s`;
};
</script>
