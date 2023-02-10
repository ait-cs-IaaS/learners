<template>
  <div>
    <!-- eslint-disable vue/no-v-html -->
    <v-tooltip :text="authTooltip" transition="slide-x-transition">
      <template #activator="{ props }">
        <router-link to="/login" custom v-slot="{ navigate }">
          <div
            role="link"
            class="px-2 py-5"
            @click="navigate"
            v-html="logoSvg"
            v-bind="props"
          ></div>
        </router-link>
      </template>
    </v-tooltip>
    <!--eslint-enable-->
    <div class="pt-5 mb-auto d-flex flex-column">
      <tab-icon v-for="tab in tabs" :key="tab.id" :tab="tab" />
    </div>
  </div>
</template>

<script lang="ts">
import TabIcon from "./sub-components/TabIcon.vue";
import { store } from "@/store";
import ITabObject from "@/types";

export default {
  name: "Sidebar",
  components: {
    TabIcon,
  },
  props: {
    tabs: Array<ITabObject>,
  },
  computed: {
    logoSvg: () => store.getters.getLogo,
    authTooltip: () => (store.getters.getJwt ? "logout" : "login"),
  },
};
</script>
