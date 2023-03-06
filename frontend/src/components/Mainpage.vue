<template>
  <div class="d-flex main-view-container">
    <frame-pager v-for="tab in filteredTabs" :key="tab.id" :tab="tab" />
    <admin-area v-if="admin" />
  </div>
</template>

<script lang="ts">
import FramePager from "@/components/general/FramePager.vue";
import AdminArea from "@/components/admin/AdminArea.vue";
import { ITabObject } from "@/types";
import { jwtDecode } from "jwt-js-decode";
import { store } from "@/store";

export default {
  name: "Mainpage",
  components: {
    FramePager,
    AdminArea,
  },
  props: {
    tabs: { type: Array<ITabObject>, require: true },
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
