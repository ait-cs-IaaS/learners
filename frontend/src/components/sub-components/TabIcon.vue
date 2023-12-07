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
          :class="{
            highlight: tab._type === 'admin' || tab._type === 'user',
            active: tab.id === currentView,
          }"
          block
          icon
          v-bind="props"
          :to="`#${tab.id}`"
        >
          <SvgIcon :name="tab.icon" sidebar />
        </v-btn>
      </v-badge>
    </template>
  </v-tooltip>
</template>

<script lang="ts">
import SvgIcon from "@/components/dynamic-components/SvgIcon.vue";
import { ITabObject } from "@/types";
import type { PropType } from "vue";
import { store } from "@/store";

export default {
  name: "TabIcon",
  components: {
    SvgIcon,
  },
  props: {
    tab: { type: Object as PropType<ITabObject>, require: true, default: null },
    currentView: { type: String, require: false, default: "" },
  },
};
</script>
