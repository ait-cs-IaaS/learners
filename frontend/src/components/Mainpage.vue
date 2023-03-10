<template>
  <div class="d-flex main-view-container">
    <notification
      v-show="showNotifications && !notificationClosed"
      @hide="notificationClosed = true"
    />

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
import Notification from "@/components/sub-components/Notification.vue";
import { extractNotifications } from "@/helpers";

export default {
  name: "Mainpage",
  components: {
    FramePager,
    AdminArea,
    Notification,
  },
  data() {
    return {
      notificationClosed: false,
      evtSource: EventSource as any,
    };
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
    showNotifications() {
      this.notificationClosed = false;
      return (
        store.getters.getShowNotifications &&
        store.getters.getNotificationsLength > 0 &&
        this.$route.name != "Login"
      );
    },
  },
  methods: {
    initSSE() {
      this.evtSource = new EventSource("http://localhost:5000/stream", {
        withCredentials: true,
      });

      this.evtSource.onopen = function () {
        console.log("Connected to SSE source.");
      };

      this.evtSource.addEventListener("newNotification", (event) => {
        console.log(event);
        console.log(event.data);

        this.notificationClosed = false;
        const newNotification = extractNotifications(event.data);

        console.log(newNotification);

        store.dispatch("appendToNotifications", newNotification);
        store.dispatch("setCurrentNotificationToLast");
      });

      this.evtSource.onerror = function (error) {
        console.error("Connecttion to SSE source lost.");
      };
    },
    closeSSE() {
      console.log("close that shit");
      console.log(this.evtSource);
      this.evtSource.close();
      console.log("closed");
      console.log(this.evtSource);
    },
  },
  mounted() {
    this.initSSE();

    // Get full list of notifications from server
    store.dispatch("getNotificationsFromServer");
  },
  beforeUnmount() {
    this.closeSSE();
  },
};
</script>
