<template>
  <div class="card bg-base-100 shadow-xl">
    <div class="card-body">
      <!-- Filters and Stats -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-4">
        <!-- Stats -->
        <div class="stats shadow col-span-1 md:col-span-2 lg:col-span-1">
          <div class="stat">
            <div class="stat-title">Total Providers</div>
            <div class="stat-value">{{ count }}</div>
            <div v-if="!loading && count > 0" class="stat-desc">
              Showing {{ Math.max((currentPage - 1) * pageSize + 1, 1) }} to
              {{ Math.min(currentPage * pageSize, count) }} results
            </div>
          </div>
        </div>

        <!-- Search -->
        <div class="form-control w-full">
          <div class="input-group">
            <input
              v-model="search"
              @keyup.enter="handleSearch"
              type="text"
              placeholder="Search by name or description..."
              class="input input-bordered flex-grow"
            />
            <button class="btn btn-square" @click="handleSearch">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                class="h-4 w-4"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                />
              </svg>
            </button>
          </div>
        </div>

        <!-- Date Range Filters -->
        <div class="form-control w-full">
          <label class="label">
            <span class="label-text">Date Range (Created)</span>
          </label>
          <div class="join w-full">
            <input
              v-model="startDate"
              type="date"
              class="input input-bordered join-item flex-1"
              @change="handleFilter"
            />
            <span class="join-item flex items-center px-4">to</span>
            <input
              v-model="endDate"
              type="date"
              class="input input-bordered join-item flex-1"
              @change="handleFilter"
            />
          </div>
        </div>
      </div>

      <!-- Clear Filters Button -->
      <div class="flex justify-end mb-4">
        <button
          v-if="hasActiveFilters"
          class="btn btn-outline btn-sm"
          @click="clearFilters"
        >
          Clear Filters
        </button>
      </div>

      <!-- Table -->
      <div class="overflow-x-auto">
        <table class="table table-zebra table-pin-rows w-full">
          <thead>
            <tr>
              <th
                @click="handleSort('id')"
                class="cursor-pointer hover:bg-base-200 transition-colors"
              >
                ID
                <span v-if="ordering === 'id'" class="ml-1">↑</span>
                <span v-if="ordering === '-id'" class="ml-1">↓</span>
              </th>
              <th
                @click="handleSort('name')"
                class="cursor-pointer hover:bg-base-200 transition-colors"
              >
                Name
                <span v-if="ordering === 'name'" class="ml-1">↑</span>
                <span v-if="ordering === '-name'" class="ml-1">↓</span>
              </th>
              <th
                @click="handleSort('description')"
                class="cursor-pointer hover:bg-base-200 transition-colors"
              >
                Description
                <span v-if="ordering === 'description'" class="ml-1">↑</span>
                <span v-if="ordering === '-description'" class="ml-1">↓</span>
              </th>
              <th>Created At</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in items" :key="item.id">
              <td>{{ item.id }}</td>
              <td>{{ item.name }}</td>
              <td class="max-w-xs truncate" title="{{ item.description }}">
                {{ item.description }}
              </td>
              <td>{{ formatDate(item.created_at) }}</td>
              <td>
                <div class="flex gap-2">
                  <button
                    class="btn btn-sm btn-primary"
                    @click="handleEdit(item.id)"
                  >
                    Edit
                  </button>
                  <button
                    class="btn btn-sm btn-error"
                    @click="handleDelete(item.id)"
                  >
                    Delete
                  </button>
                </div>
              </td>
            </tr>
            <tr v-if="loading">
              <td colspan="5" class="text-center py-8">
                <span class="loading loading-spinner loading-lg"></span>
                <p class="mt-2">Loading...</p>
              </td>
            </tr>
            <tr v-if="error && items.length === 0">
              <td
                colspan="5"
                class="bg-error text-error-content text-center p-4 rounded"
              >
                {{ error }}
              </td>
            </tr>
            <tr v-if="!loading && items.length === 0 && !error">
              <td colspan="5" class="text-center py-8">No data available.</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Enhanced Pagination -->
      <div v-if="totalPages > 1" class="flex justify-center mt-6">
        <div class="join">
          <button
            class="join-item btn"
            @click="previousPage"
            :disabled="currentPage === 1"
          >
            « Previous
          </button>
          <button
            v-for="page in visiblePages"
            :key="page"
            class="join-item btn"
            :class="{ 'btn-active': page === currentPage }"
            @click="goToPage(page)"
          >
            {{ page }}
          </button>
          <button
            class="join-item btn"
            @click="nextPage"
            :disabled="currentPage === totalPages"
          >
            Next »
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from "vue";

const items = ref([]);
const currentPage = ref(1);
const totalPages = ref(0);
const count = ref(0);
const pageSize = 10; // Match your DRF pagination page_size
const loading = ref(true);
const error = ref(null);
const search = ref("");
const ordering = ref(""); // e.g., 'name', '-name', 'id', etc.
const startDate = ref("");
const endDate = ref("");

const visiblePages = computed(() => {
  const pages = [];
  const maxVisible = 5;
  let start = Math.max(1, currentPage.value - Math.floor(maxVisible / 2));
  let end = Math.min(totalPages.value, start + maxVisible - 1);

  if (end - start + 1 < maxVisible) {
    start = Math.max(1, end - maxVisible + 1);
  }

  for (let i = start; i <= end; i++) {
    pages.push(i);
  }

  // Add ellipsis if needed
  if (start > 1) {
    pages.unshift("...");
    pages.unshift(1);
  }
  if (end < totalPages.value) {
    pages.push("...");
    pages.push(totalPages.value);
  }

  // Filter out non-numbers for button rendering
  return pages.filter((p) => typeof p === "number");
});

const hasActiveFilters = computed(() => {
  return search.value || ordering.value || startDate.value || endDate.value;
});

const buildUrl = (page, searchVal, orderVal, startDateVal, endDateVal) => {
  let url = `/api/providers/?page=${page}`;
  if (searchVal) {
    url += `&search=${encodeURIComponent(searchVal)}`;
  }
  if (orderVal) {
    url += `&ordering=${orderVal}`;
  }
  if (startDateVal) {
    url += `&created__gte=${startDateVal}`;
  }
  if (endDateVal) {
    url += `&created__lte=${endDateVal}`;
  }
  return url;
};

const fetchData = async (
  page = 1,
  searchVal = "",
  orderVal = "",
  startDateVal = "",
  endDateVal = "",
) => {
  loading.value = true;
  error.value = null;
  try {
    const url = buildUrl(page, searchVal, orderVal, startDateVal, endDateVal);
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    items.value = data.results || data;
    count.value = data.count || items.value.length;
    totalPages.value = Math.ceil(count.value / pageSize);
    currentPage.value = page;
    search.value = searchVal;
    ordering.value = orderVal;
    startDate.value = startDateVal;
    endDate.value = endDateVal;
    console.log("Data successfully loaded:", items.value);
  } catch (err) {
    console.error("Data fetching error:", err);
    error.value = "Failed to fetch data: " + err.message;
    items.value = [];
  } finally {
    loading.value = false;
  }
};

const goToPage = (page) => {
  if (page >= 1 && page <= totalPages.value && page !== currentPage.value) {
    fetchData(
      page,
      search.value,
      ordering.value,
      startDate.value,
      endDate.value,
    );
  }
};

const previousPage = () => {
  if (currentPage.value > 1) {
    fetchData(
      currentPage.value - 1,
      search.value,
      ordering.value,
      startDate.value,
      endDate.value,
    );
  }
};

const nextPage = () => {
  if (currentPage.value < totalPages.value) {
    fetchData(
      currentPage.value + 1,
      search.value,
      ordering.value,
      startDate.value,
      endDate.value,
    );
  }
};

const handleSearch = () => {
  fetchData(1, search.value, ordering.value, startDate.value, endDate.value);
};

const handleFilter = () => {
  fetchData(1, search.value, ordering.value, startDate.value, endDate.value);
};

const handleSort = (field) => {
  let newOrdering = field;
  if (ordering.value === field) {
    newOrdering = "-" + field;
  }
  ordering.value = newOrdering;
  fetchData(1, search.value, newOrdering, startDate.value, endDate.value);
};

const clearFilters = () => {
  search.value = "";
  ordering.value = "";
  startDate.value = "";
  endDate.value = "";
  fetchData(1, "", "", "", "");
};

const formatDate = (dateString) => {
  if (!dateString) return "";
  return new Date(dateString).toLocaleDateString();
};

const handleEdit = (id) => {
  console.log("Edit item:", id);
  // Implement edit logic, e.g., navigate to edit page
};

const handleDelete = (id) => {
  if (confirm("Are you sure you want to delete this item?")) {
    console.log("Delete item:", id);
    // Implement delete logic, then refetch
    fetchData(
      currentPage.value,
      search.value,
      ordering.value,
      startDate.value,
      endDate.value,
    );
  }
};

onMounted(() => fetchData(1, "", "", "", ""));
</script>
