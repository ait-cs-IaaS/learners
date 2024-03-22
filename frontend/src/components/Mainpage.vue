<template>
  <div class="d-flex main-view-container">
    <transition name="fade">
      <notification
        v-show="showNotifications && !notificationClosed"
        @hide="notificationClosed = true"
      />
    </transition>

    <questionnaire
      v-show="showQuestionnaires"
      :currentQuestionnaire="currentQuestionnaire"
    />

    <frame-pager
      v-for="tab in filteredTabs"
      :key="tab.id"
      :tab="tab"
      :currentView="currentView"
      @loaded="iframeLoaded"
    />
    <admin-area
      v-if="admin"
      :currentView="currentView"
      :sse_error="sse_error"
    />
    <!-- <user-area /> -->
  </div>
</template>

<script lang="ts">
import FramePager from "@/components/general/FramePager.vue";
import AdminArea from "@/components/admin/AdminArea.vue";
// import UserArea from "@/components/user/UserArea.vue";
import Notification from "@/components/sub-components/Notification.vue";
import Questionnaire from "@/components/sub-components/Questionnaire.vue";
import { ITabObject } from "@/types";
import { jwtDecode } from "jwt-js-decode";
import { store } from "@/store";
import { setStyles, initSSE, initVisibility } from "@/helpers";
import axios from "axios";
import { VueCookies } from "vue-cookies";
import { inject } from "vue";

// TODO: Add UserArea
export default {
  name: "Mainpage",
  components: {
    FramePager,
    AdminArea,
    Notification,
    Questionnaire,
  },
  data() {
    return {
      notificationClosed: false,
      questionnaireClosed: false,
      sse_error: false,
      evtSource: EventSource as any,
      serverEvent: Object as any,
      iframes: [] as any,
      intervalTracker: null as any | null,
    };
  },
  props: {
    tabs: { type: Array<ITabObject>, require: true },
    currentView: {
      type: String,
      require: false,
      default: store.getters.getCurrentView,
    },
  },
  computed: {
    admin() {
      if (store.getters.getJwt) {
        const jwt = jwtDecode(store.getters.getJwt);
        return jwt.payload.admin;
      } else {
        return false;
      }
    },
    filteredTabs() {
      const tabsList = this.tabs || [];
      return tabsList.filter((tab) => tab._type != "admin");
    },
    toggleNotifications() {
      return store.getters.getShowNotifications;
    },
    currentNotificationIndex() {
      const index = store.getters.getCurrentNotificationIndex;
      if (index) this.notificationClosed = false;
    },
    showNotifications() {
      return (
        store.getters.getShowNotifications &&
        store.getters.getNotifications.length > 0 &&
        this.$route.name != "Login"
      );
    },
    showQuestionnaires() {
      return (
        store.getters.getShowQuestionnaires &&
        store.getters.getQuestionnairesLength > 0
      );
    },
    currentQuestionnaire() {
      let questionnaires = store.getters.getQuestionnaires;
      if (questionnaires) {
        let index = store.getters.getCurrentQuestionnaireIndex;
        return questionnaires[index];
      }
    },
  },
  methods: {
    startSseSession(ctx) {
      let attemptCount = 1;

      const connectToStream = (context) => {
        if (attemptCount > 2) {
          console.log(
            "Unable to establish SSE connection. Using fallback polling function."
          );
          this.streamFallbackMethod();
        } else {
          const jwt = store.getters.getJwt;

          const backend = store.getters.getBackendUrl;
          context.evtSource = new EventSource(`${backend}/stream?jwt=${jwt}`);

          context.evtSource.onopen = function () {
            console.log("Connected to SSE source.");
            context.sse_error = false;
            initSSE(context);
          };

          context.evtSource.onerror = function () {
            console.log("Unable to establish SSE connection.");
            context.sse_error = true;
            this.intervalTracker = setTimeout(() => {
              attemptCount++;
              connectToStream(context);
            }, 5000);
          };
        }
      };

      connectToStream(ctx);
    },
    closeSSE() {
      this.evtSource.close();
    },
    iframeLoaded() {
      initVisibility(this.iFramesGather());
    },
    iFrameHandle(event) {
      // Receiving function for calls from iframe
    },
    iFramesGather() {
      const contentContainers = document.querySelectorAll(".content-container");
      let iframes_list = [] as any;
      contentContainers.forEach((container) => {
        const iframesInContainer = Array.from(
          container.querySelectorAll("iframe")
        );
        iframes_list.push(...iframesInContainer);
      });
      this.iframes = iframes_list;
      return iframes_list;
    },
    streamFallbackMethod() {
      const gatherUpdates = () => {
        // Get full list of notifications from server
        store.dispatch("getNotificationsFromServer");

        // Get full list of questionnaires from server
        store.dispatch("getQuestionnairesFromServer");

        // Trigger visibility control
        initVisibility(this.iFramesGather());

        // Call setTimeout again to repeat after 10 seconds
        this.intervalTracker = setTimeout(gatherUpdates, 15000);
      };

      clearInterval(this.intervalTracker);

      // Initial call to start the loop
      gatherUpdates();
    },
  },
  async beforeMount() {
    setStyles(this);
    clearInterval(this.intervalTracker);
  },
  mounted() {
    // Verify local jwt token
    if (!store.getters.getJwt) {
      const $cookies = inject<VueCookies>("$cookies");
      $cookies?.remove("jwt_cookie");
      store.dispatch("resetTabs");
      store.dispatch("unsetJwt");
      axios.defaults.headers.common["Authorization"] = "";
      this.$router.push("/login");
    }

    this.startSseSession(this);

    // Get full list of notifications from server
    store.dispatch("getNotificationsFromServer");

    // Get full list of questionnaires from server
    store.dispatch("getQuestionnairesFromServer");

    // Allow call to wrapper
    window.addEventListener("message", this.iFrameHandle);

    // Get a list of all iFrames
    this.iFramesGather();
  },
  beforeUnmount() {
    this.closeSSE();
    clearInterval(this.intervalTracker);
  },
  beforeDestroy() {
    window.removeEventListener("message", this.iFrameHandle);
  },
  watch: {
    toggleNotifications: {
      handler(new_state, old_state) {
        if (new_state === true || old_state === undefined) {
          this.notificationClosed = false;
        }
      },
      immediate: true,
    },
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
