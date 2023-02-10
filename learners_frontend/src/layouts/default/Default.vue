<template>
  <v-container fluid class="pa-0 fill-height">
    <v-navigation-drawer model-value rail permanent color="primary">
      <sidebar :tabs="tabs" />
    </v-navigation-drawer>

    <v-main class="fill-height">
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
