<template>
  <v-tooltip :text="tab.tooltip" transition="slide-x-transition">
    <template #activator="{ props }">
      <v-badge
        location="bottom end"
        color="primary lighten3"
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
          :class="{
            admin: tab._type === 'admin',
            active: tab.id === currentView,
          }"
          block
          icon
          v-bind="props"
          @click="changeView"
        >
          <SvgIcon :name="tab.icon" sidebar />
        </v-btn>
      </v-badge>
    </template>
  </v-tooltip>
</template>

<script lang="ts">
import SvgIcon from "@/components/dynamic-components/SvgIcon.vue";
import ITabObject from "@/types";
import { store } from "@/store";

export default {
  name: "TabIcon",
  components: {
    SvgIcon,
  },
  props: {
    tab: { type: Object as () => ITabObject, default: null },
  },

  computed: {
    currentView() {
      return store.getters.getCurrentView;
    },
  },
  methods: {
    async changeView() {
      this.$router.push("/");
      await store.dispatch("setCurrentView", this.tab.id);
    },
  },
};
</script>
