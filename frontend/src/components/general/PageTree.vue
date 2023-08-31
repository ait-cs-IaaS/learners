<template>
  <v-expansion-panels
    variant="accordion"
    :class="{ 'sub-level': !topLevel }"
    multiple
  >
    <v-expansion-panel
      v-for="(details, title) in pageTree"
      :key="details.page_id"
      :class="{
        'active-page': !details.hidden,
        'inactive-page': details.hidden || inactiveChild,
      }"
    >
      <v-expansion-panel-title :class="{ 'top-level': topLevel }">
        <v-btn
          @click.stop="toggleVisibility(details.page_id)"
          variant="text"
          :ripple="false"
          :icon="true"
        >
          <SvgIcon
            :name="details.hidden ? 'eye-slash' : 'eye'"
            inline
            clickable
          />
        </v-btn>

        <span v-html="title"></span>

        <template v-slot:actions="{ expanded }">
          <SvgIcon
            v-if="
              typeof details.childs === 'object' &&
              Object.keys(details.childs).length
            "
            :name="expanded ? 'chevron-up' : 'chevron-down'"
            inline
            class="ml-5"
          />
        </template>
      </v-expansion-panel-title>

      <v-expansion-panel-text class="ma-0 pa-0">
        <page-tree
          v-if="
            typeof details.childs === 'object' &&
            Object.keys(details.childs).length
          "
          :pageTree="details.childs"
          :inactiveChild="Boolean(details.hidden)"
          @togglePage="emitChange"
        />
      </v-expansion-panel-text>
    </v-expansion-panel>
  </v-expansion-panels>

  <div v-if="Object.keys(pageTree).length === 0" class="no-data">No data.</div>
</template>
<script lang="ts">
import SvgIcon from "@/components/dynamic-components/SvgIcon.vue";

export default {
  name: "PageTree",
  components: {
    SvgIcon,
  },
  props: {
    pageTree: { type: Object, required: true },
    topLevel: { type: Boolean, requierd: false, default: false },
    depth: { type: Number, requierd: false, default: 0 },
    inactiveChild: { type: Boolean, requierd: false, default: false },
  },
  methods: {
    toggleVisibility(pageId) {
      console.log("clicked");
      console.log(pageId);
      this.emitChange(pageId);
    },
    emitChange(pageId) {
      this.$emit("togglePage", pageId);
    },
  },
  emits: ["togglePage"],
};
</script>

<style>
.top-level {
  color: white;
  background-color: rgb(var(--v-theme-secondary));
}

.inactive-page .top-level {
  filter: brightness(0.8);
}

.sub-level {
  padding-left: 40px !important;
}
.sub-level .v-expansion-panel__shadow {
  display: none;
}

.inactive-page {
  color: #b6b6b6 !important;
}

.v-expansion-panel-title {
  min-height: auto !important;
  max-height: 64px;
}
.v-expansion-panel::after {
  border-top-style: solid;
  border-top-width: thin;
  border-top-color: #e0e0e0;
  content: "";
  left: 0;
  position: absolute;
  right: 0;
  top: 0;
  opacity: 1;
}

.v-expansion-panel-title--active .v-expansion-panel-title__overlay {
  opacity: 0 !important;
}

.v-expansion-panel .v-btn:hover > .v-btn__overlay {
  opacity: 0;
}
</style>
