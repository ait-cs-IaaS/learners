<template>
  <div
    class="content-container pager exercises justify-center flex-wrap align-content-center"
    :class="{ invisible: !(currentView === tab.id) }"
    v-show="currentView === tab.id"
  >
    <iframe
      v-if="!tab.openedInTab && (iframeLoaded || lazyLoad)"
      :id="tab.id"
      :src="iframeSrc"
      loading="lazy"
      frameborder="0"
      noresize="noresize"
      style="height: 100vh"
      width="100%"
      @load="onIframeLoad"
      ref="iframeElement"
    ></iframe>

    <div class="fullscreen-center" v-else>
      <div class="resume-info">
        <h3>
          Resume VNC Client <i>{{ tab.id }}</i> here
        </h3>
        <p>
          The VNC Client is currently opened in a different browser-tab. <br />
          Only one instance can be run simultaneously.
        </p>
        <v-btn
          class="mt-5 px-3 resume-btn"
          variant="flat"
          color="secondary"
          v-ripple="false"
          @click="resumeHere"
        >
          Resume here
        </v-btn>
      </div>
    </div>

    <transition name="fade">
      <div class="fullscreen-center" v-if="!iframeLoaded && !tab.openedInTab">
        <loader width="20%" class="mx-auto" :loadingTxt="iframeLoadingText" />
      </div>
    </transition>
  </div>
</template>

<script lang="ts">
import { ITabObject } from "@/types";
import { store } from "@/store";
import { PropType } from "vue";
import Loader from "@/components/sub-components/Loader.vue";

export default {
  name: "FramePager",
  props: {
    tab: {
      type: Object as PropType<ITabObject>,
      required: true,
      default: null,
    },
    currentView: { type: String, required: false, default: "" },
    lazyLoad: { type: Boolean, required: false, default: false },
  },
  components: {
    Loader,
  },
  data() {
    return {
      iframeLoaded: false,
      iframeLoadingText: "",
    };
  },
  computed: {
    iframeSrc() {
      const jwt = store.getters.getJwt;
      let src =
        this.tab._type !== "client" && jwt
          ? `${this.tab.url}?jwt=${jwt}`
          : this.tab.url;

      // Add backend prefix
      if (!src.startsWith("http")) {
        src = `${store.getters.getBackendUrl}/${src}`;
      }
      return src;
    },
  },
  methods: {
    onIframeLoad() {
      this.iframeLoaded = true;
      this.$emit("loaded");

      // Delay loading other iframes
      setTimeout(() => (this.lazyLoad = true), 1000);
    },
  },
  resumeHere() {
    if (this.$refs.iframeElement) {
      (this.$refs.iframeElement as HTMLIFrameElement).src = this.tab.url;
    }

    store.dispatch("setOpendInTab", {
      tabId: this.tab.id,
      opened: false,
    });

    const referTab = window.open("", `${this.tab.id}_tab`);
    if (referTab) referTab.close();
  },
  beforeMount() {
    if (this.tab._type === "client") {
      this.iframeLoadingText = "connecting to client ... ";
    } else {
      this.iframeLoadingText = "loading content ... ";
    }
  },
};
</script>

<style lang="scss">
.fullscreen-center {
  display: flex;
  height: 100%;
  width: 100%;
  background-color: #f6f6f6;
  position: absolute;
  top: 0px;
  left: 0px;
  flex-direction: column;
}

.resume-info {
  margin: auto auto;
  max-width: 30%;

  & h1,
  h2,
  h3,
  h4,
  h5 {
    color: rgb(var(--v-theme-secondary));
    margin-bottom: 0.8rem;
  }
}

.fade-leave-active {
  transition: opacity 1s;
}

.fade-leave-to {
  opacity: 0;
}
</style>
