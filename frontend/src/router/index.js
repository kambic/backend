import { createRouter, createWebHistory } from "vue-router";

import authRoutes from "./auth.router.js";
import MainLayout from "../layouts/MainLayout.vue";
import DashDashboard from "@/views/DashDashboard.vue";
const routes = [
  authRoutes,

  {
    path: "/",
    component: MainLayout,
    children: [
      {
        path: "dashboard",
        name: "dashboard",
        component: DashDashboard,
      },
    ],
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
