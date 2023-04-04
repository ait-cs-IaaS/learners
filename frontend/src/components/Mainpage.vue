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

    <frame-pager v-for="tab in filteredTabs" :key="tab.id" :tab="tab" />
    <admin-area v-if="admin" />
    <user-area />
  </div>
</template>

<script lang="ts">
import FramePager from "@/components/general/FramePager.vue";
import AdminArea from "@/components/admin/AdminArea.vue";
import UserArea from "@/components/user/UserArea.vue";
import Notification from "@/components/sub-components/Notification.vue";
import Questionaire from "@/components/sub-components/Questionaire.vue";
import { ITabObject } from "@/types";
import { jwtDecode } from "jwt-js-decode";
import { store } from "@/store";
import { extractNotifications, extractQuestionaires } from "@/helpers";

export default {
  name: "Mainpage",
  components: {
    FramePager,
    AdminArea,
    UserArea,
    Notification,
    Questionaire,
  },
  data() {
    return {
      notificationClosed: false,
      questionaireClosed: false,
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
    showQuestionaires() {
      return (
        store.getters.getShowQuestionaires &&
        store.getters.getQuestionairesLength > 0 &&
        store.getters.getCurrentView === "presentations"
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
    initSSE() {
      this.evtSource = new EventSource("http://localhost:5000/stream", {
        withCredentials: true,
      });

      this.evtSource.onopen = function () {
        console.log("Connected to SSE source.");
      };

      this.evtSource.addEventListener("newNotification", (event) => {
        this.notificationClosed = false;
        const newNotification = extractNotifications(event.data);
        newNotification.event = "newNotification";
        // Store actions
        store.dispatch("appendToNotifications", newNotification);
        store.dispatch("setCurrentNotificationToLast");
      });

      this.evtSource.addEventListener("newSubmission", (event) => {
        this.notificationClosed = false;
        const newNotification = extractNotifications(event.data);
        newNotification.event = "newSubmission";
        // Store actions
        store.dispatch("appendToNotifications", newNotification);
        store.dispatch("setCurrentNotificationToLast");
        store.dispatch("setAdminForceReload", "submissions");
      });

      this.evtSource.addEventListener("newComment", (event) => {
        this.notificationClosed = false;
        const newNotification = extractNotifications(event.data);
        newNotification.event = "newComment";
        // Store actions
        store.dispatch("appendToNotifications", newNotification);
        store.dispatch("setCurrentNotificationToLast");
        store.dispatch("setAdminForceReload", "feedback");
      });

      this.evtSource.addEventListener("newQuestionaire", (event) => {
        this.questionaireClosed = false;
        console.log("NEW QUESTIONAIRE");
        console.log(event);
        console.log(event.data);
        console.log(JSON.parse(event.data));
        console.log(JSON.parse(event.data)?.question);
        const newQuestionaire = extractQuestionaires(event.data);
        newQuestionaire.event = "newQuestionaire";
        console.log(newQuestionaire);
        // Store actions
        store.dispatch("appendToQuestionaires", newQuestionaire);
        store.dispatch("setCurrentQuestionaireToLast");
        store.dispatch("setAdminForceReload", "questionaire");
      });

      this.evtSource.onerror = function (error) {
        console.error("Connecttion to SSE source lost.");
      };
    },
    closeSSE() {
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

    // Get full list of questionaires from server
    store.dispatch("getQuestionairesFromServer");
  },
  beforeUnmount() {
    this.closeSSE();
  },
};
</script>

<style lang="scss">
.fade-leave-active {
  transition: opacity 1s;
}
.fade-leave-to {
  opacity: 0;
}
</style>
