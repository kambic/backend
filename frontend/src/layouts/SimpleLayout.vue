<script setup>
import TheNavbar from '@/components/layout/TheNavbar.vue'
import TheFooter from '@/components/layout/TheFooter.vue'
import menuAndSearch from '@/components/sidebar/menuAndSearch.vue'
</script>

<template>
  <!-- 3. Dashboard sidebar + main (perfect for DashWind style) -->

  <!-- Main Grid Layout -->
  <div class="grid grid-cols-1 md:grid-cols-[auto_1fr] min-h-screen">
    <!-- Sidebar -->
    <aside class="bg-base-200 relative">
      <!-- Hidden checkbox controls collapse -->
      <input type="checkbox" id="sidebar-toggle" class="peer hidden" />

      <!-- Sidebar Content -->
      <div
        class="flex flex-col h-screen transition-all duration-300 w-64 peer-checked:w-20 md:w-64 md:peer-checked:w-20"
      >
        <!-- Header + Toggle Button -->
        <div class="flex items-center justify-between p-4 border-b border-base-300">
          <h1 class="text-xl font-bold truncate">MyApp</h1>
          <label for="sidebar-toggle" class="btn btn-square btn-ghost swap swap-rotate md:hidden">
            <input type="checkbox" />
            <svg
              class="swap-off fill-current"
              xmlns="http://www.w3.org/2000/svg"
              width="32"
              height="32"
              viewBox="0 0 512 512"
            >
              <path d="M64,384H448V341.33H64Zm0-106.67H448V234.67H64ZM64,128v42.67H448V128Z" />
            </svg>
            <svg
              class="swap-on fill-current"
              xmlns="http://www.w3.org/2000/svg"
              width="32"
              height="32"
              viewBox="0 0 512 512"
            >
              <polygon
                points="400 145.49 366.51 112 256 222.51 145.49 112 112 145.49 222.51 256 112 366.51 145.49 400 256 289.49 366.51 400 400 366.51 289.49 256 400 145.49"
              />
            </svg>
          </label>
        </div>

        <!-- Menu Items -->
        <ul class="menu p-4 flex-1 overflow-y-auto">
          <li>
            <a class="flex items-center gap-3"
              ><svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M3 12l2-2m0 0l7-7 7-7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"
                /></svg
              ><span class="hidden peer-checked:hidden md:inline">Dashboard</span></a
            >
          </li>
          <li>
            <a class="flex items-center gap-3"
              ><svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"
                /></svg
              ><span class="hidden peer-checked:hidden md:inline">Users</span></a
            >
          </li>
          <li>
            <a class="flex items-center gap-3"
              ><svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                /></svg
              ><span class="hidden peer-checked:hidden md:inline">Analytics</span></a
            >
          </li>
          <li>
            <a class="flex items-center gap-3"
              ><svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M10.325 4.317c.426-1.756 2.924-2.892 4.679-2.892 1.756 0 3.254 1.136 3.679 2.892"
                ></path></svg
              ><span class="hidden peer-checked:hidden md:inline">Settings</span></a
            >
          </li>
        </ul>

        <!-- Footer -->
        <div class="p-4 border-t border-base-300">
          <div class="avatar online">
            <div class="w-10 rounded-full">
              <img src="https://daisyui.com/images/stock/photo-1534528741775-53994a69daeb.jpg" />
            </div>
          </div>
        </div>
      </div>

      <!-- Hover-to-expand trigger (desktop only) -->
      <label
        for="sidebar-toggle"
        class="absolute inset-y-0 left-full w-4 cursor-col-resize opacity-0 hover:opacity-100 transition-opacity bg-base-300 hidden md:block"
      ></label>
    </aside>

    <!-- Main Content Area -->
    <main class="p-8">
      <h1 class="text-4xl font-bold mb-8">Dashboard Content</h1>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div class="card bg-base-200 shadow-xl">
          <div class="card-body">
            <h2 class="card-title">Card 1</h2>
            <p>Content goes here...</p>
          </div>
        </div>
        <!-- Repeat cards -->
        <div class="card bg-base-200 shadow-xl">
          <div class="card-body">
            <h2 class="card-title">Card 2</h2>
            <p>Content goes here...</p>
          </div>
        </div>
        <div class="card bg-base-200 shadow-xl">
          <div class="card-body">
            <h2 class="card-title">Card 3</h2>
            <p>Content goes here...</p>
          </div>
        </div>
      </div>
      <div class="sm:flex container p-5 mx-auto content justify-betweenflex-wrap">
        <RouterView class="view main-content w-full order-2"></RouterView>
        <RouterView name="LeftSidebar" class="view order-1 w-full"></RouterView>
        <RouterView name="RightSidebar" class="view order-3 w-full"></RouterView>
      </div>
    </main>
  </div>

  <div class="flex flex-col min-h-screen bg-base-400">
    <TheNavbar />
    <!--    <menuAndSearch />-->
    <div class="sm:flex container p-5 mx-auto content justify-betweenflex-wrap">
      <RouterView class="view main-content w-full order-2"></RouterView>
      <RouterView name="LeftSidebar" class="view order-1 w-full"></RouterView>
      <RouterView name="RightSidebar" class="view order-3 w-full"></RouterView>
    </div>
    <TheFooter />
  </div>
</template>
