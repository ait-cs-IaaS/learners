<template>
  <div class="d-flex main-view-container">
    <transition name="fade">
      <notification
        v-show="showNotifications && !notificationClosed"
        @hide="notificationClosed = true"
      />
    </transition>

    <questionaire
      v-show="showQuestionaires"
      :currentQuestionaire="currentQuestionaire"
    />

    <frame-pager
      v-for="tab in filteredTabs"
      :key="tab.id"
      :tab="tab"
      :currentView="currentView"
    />
    <admin-area v-if="admin" :currentView="currentView" />
    <!-- <user-area /> -->
  </div>
</template>

<script lang="ts">
import FramePager from "@/components/general/FramePager.vue";
import AdminArea from "@/components/admin/AdminArea.vue";
// import UserArea from "@/components/user/UserArea.vue";
import Notification from "@/components/sub-components/Notification.vue";
import Questionaire from "@/components/sub-components/Questionaire.vue";
import { ITabObject } from "@/types";
import { jwtDecode } from "jwt-js-decode";
import { store } from "@/store";
import { setStyles, initSSE } from "@/helpers";

// TODO: Add UserArea
export default {
  name: "Mainpage",
  components: {
    FramePager,
    AdminArea,
    Notification,
    Questionaire,
  },
  data() {
    return {
      notificationClosed: false,
      questionaireClosed: false,
      sse_error: true,
      evtSource: EventSource as any,
      serverEvent: Object as any,
      iframes: [] as any,
    };
  },
  props: {
    tabs: { type: Array<ITabObject>, require: true },
    currentView: { type: String, require: false, default: "" },
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
        store.getters.getNotifications.length > 0 &&
        this.$route.name != "Login"
      );
    },
    showQuestionaires() {
      return (
        store.getters.getShowQuestionaires &&
        store.getters.getQuestionairesLength > 0 &&
        this.currentView === "presentations"
      );
    },
    currentQuestionaire() {
      let questionaires = store.getters.getQuestionaires;
      if (questionaires) {
        let index = store.getters.getCurrentQuestionaireIndex;
        return questionaires[index];
      }
    },
  },
  methods: {
    startSseSession(ctx) {
      let attemptCount = 1;

      const connectToStream = (context) => {
        const jwt = store.getters.getJwt;
        context.evtSource = new EventSource(
          `${import.meta.env.VITE_BACKEND}/stream?jwt=${jwt}`
        );

        context.evtSource.onopen = function () {
          console.log("Connected to SSE source.");
          context.sse_error = false;
          initSSE(context);
        };

        context.evtSource.onerror = function () {
          console.log("Unable to establish SSE connection.");
          context.sse_error = true;
          setTimeout(() => {
            attemptCount++;
            console.log(attemptCount);
            connectToStream(context);
          }, 5000);
        };
      };

      connectToStream(ctx);
    },
    closeSSE() {
      this.evtSource.close();
    },
    setDrawIO(event) {
      // Set url of iframe
      store.dispatch("setDrawioData", event.data.message);
      // switch view
      store.dispatch("setCurrentView", "drawio");
    },
  },
  async beforeMount() {
    setStyles(this);
  },
  mounted() {
    this.startSseSession(this);

    // Get full list of notifications from server
    store.dispatch("getNotificationsFromServer");

    // Get full list of questionaires from server
    store.dispatch("getQuestionairesFromServer");

    // Allow call to change drawio url
    window.addEventListener("message", this.setDrawIO);

    const contentContainers = document.querySelectorAll(".content-container");
    contentContainers.forEach((container) => {
      const iframesInContainer = Array.from(
        container.querySelectorAll("iframe")
      );
      this.iframes.push(...iframesInContainer);
    });

    // const pParam = this.$route.query.p;
    // if (pParam) store.dispatch("setCurrentView", pParam);
  },
  beforeUnmount() {
    this.closeSSE();
  },
  beforeDestroy() {
    window.removeEventListener("message", this.setDrawIO);
  },
};
</script>

<style lang="scss">
.fade-leave-active {
  transition: opacity 500ms;
}
.fade-leave-to {
  opacity: 0;
}
</style>
