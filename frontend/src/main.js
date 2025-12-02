import { createApp } from "vue";
import router from "@/router/index.js";
import App from "./App.vue";
import "./assets/styles/main.scss";
import VueFinder from 'vuefinder';

import { createPinia } from "pinia";

const pinia = createPinia();
const app = createApp(App);

app.use(router);
app.use(pinia);
app.use(VueFinder);
app.mount("#app");
