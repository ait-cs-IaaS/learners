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


const app = createApp(App);
registerPlugins(app);
app.use(store);
app.mount("#app");

console.debug("mounted store", store);
