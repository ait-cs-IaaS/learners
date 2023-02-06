<template>
  <div>
    <v-tooltip text="Tooltip" transition="slide-x-transition">
      <template #activator="{ props }">
        <v-btn
          v-ripple="false"
          variant="plain"
          class="rounded-0"
          block
          fab
          icon
          plain
          tile
          color="white"
          depressed
          v-bind="props"
        >
          <v-icon>mdi-format-list-bulleted-square</v-icon>
        </v-btn>
      </template>
    </v-tooltip>
  </div>
</template>

<script lang="ts">
export default {
  name: "Sidebar",
  methods: {
    changeView() {
      this.$store.commit("changeCurrentView");
      console.log(this.$store.state.currentView);
    },
  },
};
</script>
