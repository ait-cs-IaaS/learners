<template>
  <div class="d-flex main-view-container">
    <frame-pager v-for="tab in filteredTabs" :key="tab.id" :tab="tab" />
    <instructor-panel v-if="admin" />
  </div>
</template>

<script lang="ts">
import FramePager from "./sub-components/FramePager.vue";
import InstructorPanel from "./sub-components/InstructorPanel.vue";
import ITabObject from "@/types";
import { jwtDecode } from "jwt-js-decode";
import { store } from "@/store";

export default {
  name: "Mainpage",
  components: {
    FramePager,
    InstructorPanel,
  },
  props: {
    tabs: Array<ITabObject>,
  },
  computed: {
    admin() {
      const jwt = jwtDecode(store.getters.getJwt);
      return jwt.payload.admin;
    },
    filteredTabs() {
      const tabsList = this.tabs || [];
      return tabsList.filter((tab) => tab._type != "admin");
    },
  },
};
</script>
