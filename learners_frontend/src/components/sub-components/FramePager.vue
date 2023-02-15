<template>
  <div
    class="content-container pager exercises d-flex justify-center flex-wrap align-content-center"
    :class="{ invisible: !(currentView === tab.id) }"
  >
    <v-card
      v-if="tab.openedInTab"
      title="Resume VNC Client here"
      variant="outlined"
      max-width="500"
      max-height="200"
      class="pa-4"
      style="margin-left: -56px"
    >
      <v-card-text>
        The VNC Client is currently opened in a different browser-tab. <br />
        Only one instance can be run simultaneously.
      </v-card-text>
      <v-card-actions>
        <v-btn
          class="ma-2 px-3 resume-btn"
          variant="flat"
          color="primary"
          v-ripple="false"
          @click="resumeHere"
        >
          Resume here
        </v-btn>
      </v-card-actions>
    </v-card>
    <iframe
      v-else
      :id="tab.id"
      :src="iframeSrc"
      frameborder="0"
      noresize="noresize"
      width="100%"
      height="100%"
    ></iframe>
  </div>
</template>

<script lang="ts">
import TabObject from "@/types";
import { store } from "@/store";

export default {
  name: "FramePager",
  props: {
    tab: { type: Object as () => TabObject, default: null },
  },
  computed: {
    currentView() {
      return store.state.currentView;
    },
    iframeSrc() {
      const jwt = store.getters.getJwt;
      return this.tab._type !== "client" && jwt
        ? `${this.tab.url}?jwt=${jwt}`
        : this.tab.url;
    },
  },
  methods: {
    resumeHere() {
      const respIFrame = document.getElementById(this.tab.id);

      if (respIFrame) {
        respIFrame.setAttribute("src", this.tab.url);
      }
      store.dispatch("setOpendInTab", {
        tabId: this.tab.id,
        opened: false,
      });

      const referTab = window.open("", `${this.tab.id}_tab`);
      if (referTab) referTab.close();
    },
  },
};
</script>
