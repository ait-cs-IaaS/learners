/**
 * main.ts
 *
 * Bootstraps Vuetify and other plugins then mounts the App`
 */

// Components
import App from "./App.vue";

// Composables
import { createApp } from "vue";

// Plugins
import { registerPlugins } from "@/plugins";

// Store
import { store } from "@/store";

import "./axios.ts";

import dotenv from 'dotenv';
dotenv.config();

// Import Data Table
import Vue3EasyDataTable from "vue3-easy-data-table";
import "vue3-easy-data-table/dist/style.css";

const app = createApp(App);
registerPlugins(app);
app.component("EasyDataTable", Vue3EasyDataTable);
app.use(store);
app.mount("#app");

console.debug("mounted store", store);
