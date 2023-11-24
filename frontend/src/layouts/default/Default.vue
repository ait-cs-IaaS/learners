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
      <sidebar :tabs="tabs" :currentView="currentView" :loaded="loaded" />
    </v-navigation-drawer>

    <v-main>
      <router-view :tabs="tabs" :currentView="currentView" />
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
  data() {
    return {
      currentView: "",
      loaded: false,
    };
  },
  computed: {
    tabs: () => store.getters.getTabs,
  },
  mounted() {
    this.loaded = true;
  },
  watch: {
    "$route.hash": {
      handler(new_state, old_state) {
        if (new_state != undefined) {
          const view_id = new_state.substring(1);
          const tabs = store.getters.getTabs;
          console.log(tabs);
          if (tabs.length) {
            if (tabs.some((tab) => tab.id === view_id)) {
              this.currentView = view_id;
              store.dispatch("setCurrentView", view_id);
            } else {
              this.currentView = tabs[0].id;
              store.dispatch("setCurrentView", tabs[0].id);
            }
          }
        }
      },
      immediate: true,
    },
  },
};
</script>
