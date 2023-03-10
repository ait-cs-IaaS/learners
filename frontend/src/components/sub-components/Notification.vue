<template>
  <div class="notification-container" :class="{ animating: animate }">
    <div
      class="notification-content"
      v-html="currentNotifications?.message"
    ></div>
    <div class="notification-controls">
      <v-tooltip location="top" text="previous" transition="fade-transition">
        <template #activator="{ props }">
          <v-btn
            class="notification-actions"
            fab
            tile
            icon
            x-small
            elevation="0"
            theme="dark"
            v-ripple="false"
            v-bind="props"
            @click="showPreviousNotification()"
          >
            <SvgIcon name="chevron-left"
          /></v-btn>
        </template>
      </v-tooltip>

      <v-tooltip location="top" text="next" transition="fade-transition">
        <template #activator="{ props }">
          <v-btn
            class="notification-actions"
            fab
            tile
            icon
            x-small
            elevation="0"
            theme="dark"
            v-ripple="false"
            v-bind="props"
            @click="showNextNotification()"
          >
            <SvgIcon name="chevron-right"
          /></v-btn>
        </template>
      </v-tooltip>
      <v-tooltip location="top" text="hide" transition="fade-transition">
        <template #activator="{ props }">
          <v-btn
            class="notification-actions"
            fab
            tile
            icon
            x-small
            elevation="0"
            theme="dark"
            v-ripple="false"
            v-bind="props"
            @click="$emit('hide')"
          >
            <SvgIcon name="x-mark"
          /></v-btn>
        </template>
      </v-tooltip>
    </div>
  </div>
</template>

<script lang="ts">
import SvgIcon from "@/components/dynamic-components/SvgIcon.vue";
import { store } from "@/store";

export default {
  name: "Notification",
  components: {
    SvgIcon,
  },
  props: {
    message: {
      type: String,
      require: false,
      default: "Requesting data ...",
    },
  },
  data() {
    return {
      contentChanging: false,
    };
  },
  computed: {
    currentNotifications() {
      let notifications = store.getters.getNotifications;
      console.log("notifications: ", notifications);
      if (notifications) {
        let index = store.getters.getCurrentNotification;
        console.log(notifications);
        console.log(index);
        console.log(notifications[index]);
        this.triggerAnimation();
        return notifications[index];
      }
    },
    animate() {
      return this.contentChanging;
    },
  },
  methods: {
    showPreviousNotification() {
      store.dispatch("decCurrentNotification");
    },
    showNextNotification() {
      store.dispatch("incCurrentNotification");
    },
    triggerAnimation() {
      this.contentChanging = true;
      setTimeout(() => {
        this.contentChanging = false;
      }, 600);
    },
  },
};
</script>

<style lang="scss">
.notification-container {
  position: absolute !important;
  background-color: rgba(0, 0, 0, 0.75);
  display: block;
  z-index: 99 !important;
  bottom: 14px !important;
  left: 74px !important;
  // pointer-events: none;
  padding: 24px;
  border-radius: 4px;
  min-width: 340px;
  max-width: 40%;

  &.animating {
    animation: fade-in 600ms ease;
  }
  h1,
  h2,
  h3,
  h4,
  h5,
  p {
    color: white;
  }
}

@keyframes fade-in {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.v-btn.notification-actions {
  pointer-events: all;
  height: calc(var(--v-btn-height) + 0px);
  width: calc(var(--v-btn-height) + 6px);
  background: none;
}
.notification-content {
  color: white;
}
.notification-controls {
  display: block;
  // background-color: green;
  position: absolute;
  top: 0;
  right: 0;
  float: right;
  clear: both;
  height: 34px;
  padding: 8px;
  border-radius: 4px;
}
</style>
