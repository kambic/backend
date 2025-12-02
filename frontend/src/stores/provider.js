// stores/provider.js (Fixed Pinia Store)
import { defineStore } from "pinia";
import { mande } from "mande";

const api = mande("/api/providers");
const edgewareApi = mande("/api/edgewares");

export const useProviderStore = defineStore("provider", {
  state: () => ({
    items: [],
    currentProvider: null,
    loading: false,
    error: null,
    activeTab: "overview", // Default to overview
    edgewares: [],
  }),
  getters: {
    byId: (state) => (id) => state.items.find((p) => p.id === id),
    current: (state) => state.currentProvider,
    numExpired: (state) => {
      // Placeholder: Assuming providers have an 'expiry_date' field.
      // Compare with new Date(). Adjust field name/logic as per your schema.
      // For now, returns 0 if no expiry; implement real logic here.
      if (!state.currentProvider?.expiry_date) return 0;
      const now = new Date();
      const expiry = new Date(state.currentProvider.expiry_date);
      return now > expiry ? 1 : 0;
    },
  },
  actions: {
    async fetchProviders() {
      if (this.loading || this.items.length) return;
      this.loading = true;
      this.error = null;
      try {
        const res = await api.get();
        this.items = res.results || [];
        console.log("Providers loaded:", this.items);
      } catch (err) {
        this.error = err?.message || "Unknown error";
      } finally {
        this.loading = false;
      }
    },
    async fetchProvider(id) {
      if (this.loading && this.currentProvider?.id === id) return;
      this.loading = true;
      this.error = null;
      try {
        const res = await api.get(`/${id}`); // Assuming API endpoint is /api/v1/providers/{id}
        this.currentProvider = res; // Single object, not array
        if (!this.items.find((p) => p.id === id)) {
          this.items.push(res); // Cache for list views
        }
        console.log("Provider loaded:", this.currentProvider);
      } catch (err) {
        this.error = err?.message || "Unknown error";
      } finally {
        this.loading = false;
      }
    },
    async loadEdgewares(providerId) {
      console.log("Loading edgewares for provider:", providerId);
      this.edgewares = []; // Reset
      try {
        // Assuming API: /api/v1/providers/{id}/edgewares or filter by provider_id
        const res = await edgewareApi.get({ provider_id: providerId }); // Adjust query/endpoint as needed
        this.edgewares = res.results || res; // Handle array or direct response
        console.log("Edgewares loaded:", this.edgewares);
      } catch (err) {
        console.error("Failed to load edgewares:", err);
        this.error = err?.message || "Failed to load edgewares";
      }
    },
    setActiveTab(tab) {
      this.activeTab = tab;
    },
  },
});
