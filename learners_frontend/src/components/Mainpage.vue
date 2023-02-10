<template>
  <div class="fill-height d-flex main-view-container">
    <frame-pager v-for="tab in tabs" :key="tab.id" :tab="tab" />
  </div>
</template>

<script lang="ts">
import FramePager from "./sub-components/FramePager.vue";
import ITabObject from "@/types";

export default {
  name: "Mainpage",
  components: {
    FramePager,
  },
  props: {
    tabs: Array<ITabObject>,
  },
};
</script>
