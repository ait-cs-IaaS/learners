<template>
  <div
    :class="{
      'sidebar-hero-icon': sidebar,
      'content-hero-icon': !sidebar,
      'clickable-icon': clickable,
    }"
    class="hero-icon"
  >
    <component :is="dynamicComponent" />
  </div>
</template>

<script lang="ts">
import { defineAsyncComponent } from "vue";

export default {
  props: {
    name: {
      type: String,
      required: true,
    },
    clickable: {
      type: Boolean,
      required: false,
      default: false,
    },
    sidebar: {
      type: Boolean,
      required: false,
      default: false,
    },
  },

  computed: {
    dynamicComponent() {
      const name = this.name;
      return defineAsyncComponent(() => import(`./icons/${name}.svg`));
    },
  },
};
</script>

<style>
.hero-icon {
  display: flex;
  justify-content: center;
  align-content: center;
}

.hero-icon.clickable-icon {
  cursor: pointer;
}

.hero-icon.sidebar-hero-icon {
  width: 24px;
}

.hero-icon.content-hero-icon {
  width: 22px;
}
</style>
