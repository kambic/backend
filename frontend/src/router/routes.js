import HomeView from "@/views/HomeView.vue";
import MediaView from "@/views/MediaView.vue";
import ChartDashboard from "@/views/ChartDashboard.vue";
import DashDashboard from "@/views/DashDashboard.vue";

import VideoJsPlayerView from "@/views/VideoJsPlayerView.vue";

import ProviderList from "@/views/provider/ProviderList.vue";
import ProviderDetail from "@/views/provider/ProviderDetail.vue";
import JwtDecode from "@/views/JwtDecode.vue";
export default [
  {
    path: "/",
    name: "home",
    component: HomeView,
    meta: { title: "Home" },
  },

  {
    path: "/j",
    name: "jwt-decode",
    component: JwtDecode,
  },

  {
    path: "/v",
    name: "tube-player",
    component: VideoJsPlayerView,
  },

  {
    path: "/providers",
    meta: { title: "Providers" },
    name: "providers",
    component: ProviderList,
  },
  {
    path: "/providers/:id",
    name: "provider-detail",
    component: ProviderDetail,
    props: true,
  },

  {
    path: "/media",
    name: "media",
    component: MediaView,
    meta: { title: "Media" },
  },
  {
    path: "/chart",
    name: "chart",
    component: ChartDashboard,
    meta: { title: "Chart" },
  },

  {
    path: "/dash",
    name: "dash",
    component: DashDashboard,
    meta: { title: "Dash" },
  },

  {
    path: "/dash",
    name: "dash",
    component: DashDashboard,
    meta: { title: "Dash" },
  },

  {
    path: "/preview",
    name: "componentsPreview",
    // Lazy-loaded route
    component: () => import("@/views/PreviewView.vue"),
    meta: { title: "Components Preview" },
  },
  {
    // 404 fallback
    path: "/:pathMatch(.*)*",
    name: "notFound",
    component: () => import("@/views/NotFoundView.vue"),
    meta: { title: "404 Not Found" },
  },
];
