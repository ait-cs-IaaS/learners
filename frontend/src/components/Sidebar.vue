<template>
  <div class="d-flex flex-column pb-2" style="height: 100%">
    <!-- eslint-disable vue/no-v-html -->
    <v-tooltip :text="authTooltip" transition="slide-x-transition">
      <template #activator="{ props }">
        <router-link to="/login" custom v-slot="{ navigate }">
          <div
            role="link"
            class="px-2 py-5 my-3"
            @click="navigate"
            v-html="logoSvg"
            v-bind="props"
          ></div>
        </router-link>
      </template>
    </v-tooltip>
    <!--eslint-enable-->
    <div class="pt-5 mb-auto d-flex flex-column">
      <tab-icon v-for="tab in tabs" :key="tab.id" :tab="tab" />
    </div>
    <!-- Footer -->
    <div class="mt-auto">
      <v-tooltip text="notifications" transition="slide-x-transition">
        <template #activator="{ props }">
          <v-btn
            v-ripple="false"
            variant="plain"
            block
            icon
            selected-class="active"
            theme="dark"
            color="white"
            v-bind="props"
            @click="notifications"
          >
            <SvgIcon v-if="notifications_enabled" name="bell-alert" sidebar />
            <SvgIcon v-else name="bell-slash" sidebar />
          </v-btn>
        </template>
      </v-tooltip>
      <v-tooltip text="open in new tab" transition="slide-x-transition">
        <template #activator="{ props }">
          <v-btn
            v-ripple="false"
            variant="plain"
            block
            icon
            selected-class="active"
            theme="dark"
            color="white"
            v-bind="props"
            @click="openNewTab"
          >
            <SvgIcon name="arrow-top-right-on-square" sidebar />
          </v-btn>
        </template>
      </v-tooltip>
    </div>
  </div>
</template>

<script lang="ts">
import SvgIcon from "@/components/dynamic-components/SvgIcon.vue";
import TabIcon from "@/components/sub-components/TabIcon.vue";
import { store } from "@/store";
import { ITabObject } from "@/types";

export default {
  name: "Sidebar",
  components: {
    TabIcon,
    SvgIcon,
  },
  data() {
    return {
      notifications_enabled: true,
    };
  },
  props: {
    tabs: Array<ITabObject>,
  },
  computed: {
    logoSvg: () => store.getters.getLogo,
    authTooltip: () => (store.getters.getJwt ? "logout" : "login"),
  },
  methods: {
    notifications() {
      this.notifications_enabled = !this.notifications_enabled;
    },
    openNewTab() {
      const currentView = store.getters.getCurrentView;
      const activeTab = this.tabs?.find((tab) => {
        return tab.id === currentView;
      });

      if (activeTab) {
        if (activeTab._type === "client") {
          const activeIFrame = document.getElementById(activeTab.id);
          if (activeIFrame) {
            activeIFrame.setAttribute("src", "");
          }
          store.dispatch("setOpendInTab", {
            tabId: activeTab.id,
            opened: true,
          });
        }
        let newTab = window.open(activeTab.url, "_blank");
        if (newTab) newTab.name = `${activeTab.id}_tab`;
      }
    },
  },
};
</script>