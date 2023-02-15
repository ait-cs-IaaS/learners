<template>
  <v-tooltip :text="tab.tooltip" transition="slide-x-transition">
    <template #activator="{ props }">
      <v-badge
        location="bottom end"
        color="white"
        text-color="primary"
        bordered
        rounded
        :model-value="Boolean(tab.index)"
        :content="tab.index"
        offset-x="12"
        offset-y="10"
        max="9"
      >
        <v-btn
          v-ripple="false"
          variant="plain"
          :class="{ admin: tab._type === 'admin' }"
          block
          icon
          selected-class="active"
          :theme="tab._type === 'admin' ? 'light' : 'dark'"
          :color="tab._type === 'admin' ? 'primary' : 'white'"
          v-bind="props"
          @click="changeView"
        >
          <v-icon>{{ tab.icon }}</v-icon>
        </v-btn>
      </v-badge>
    </template>
  </v-tooltip>
</template>

<script lang="ts">
import ITabObject from "@/types";
import { store } from "@/store";

export default {
  name: "TabIcon",
  props: {
    tab: { type: Object as () => ITabObject, default: null },
  },
  methods: {
    async changeView() {
      this.$router.push("/");
      await store.dispatch("setCurrentView", this.tab.id);
    },
  },
};
</script>
