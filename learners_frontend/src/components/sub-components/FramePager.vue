<template>
  <iframe
    :class="{ invisible: !(currentView === tab.id) }"
    :src="iframeSrc"
    frameborder="0"
    class="content-container pager exercises"
    noresize="noresize"
    width="100%"
    height="100%"
  ></iframe>
</template>

<script lang="ts">
import TabObject from "@/types";
import { store } from "@/store";

export default {
  name: "FramePager",
  props: {
    tab: { type: Object as () => TabObject, default: null },
  },
  computed: {
    currentView() {
      return store.state.currentView;
    },
    iframeSrc() {
      const jwt = store.getters.getJwt;
      return jwt ? `${this.tab.url}?jwt=${jwt}` : `${this.tab.url}`;
    },
  },
};
</script>
