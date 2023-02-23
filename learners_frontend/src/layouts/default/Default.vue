<template>
  <v-container fluid class="pa-0">
    <v-navigation-drawer
      model-value
      rail
      permanent
      color="primary"
      rail-width="60"
      style="border: none"
    >
      <sidebar :tabs="tabs" />
    </v-navigation-drawer>

    <v-main>
      <router-view :tabs="tabs" />
    </v-main>
  </v-container>
</template>

<script lang="ts">
import Sidebar from "@/components/Sidebar.vue";
import { store } from "@/store";

export default {
  name: "DefaultLayout",
  components: {
    Sidebar,
  },
  computed: {
    tabs: () => store.getters.getTabs,
  },
};
</script>
