<template>
  <div>
    <h2 class="mb-4">
      Visibility Overview
      <v-progress-circular
        class="mx-2 mb-1"
        color="grey"
        indeterminate
        :width="3"
        :size="18"
        v-show="loading"
      ></v-progress-circular>
    </h2>

    <v-snackbar
      content-class="ma-0 mb-n1 pa-0 pb-1"
      v-model="showTimer"
      width="fit-content"
      min-width="auto"
      rounded="rounded-0"
      timeout="-1"
      style="border-radius: 0"
      color="primary"
    >
      <scenario-timer />
    </v-snackbar>
    <v-btn
      @click="notify = !notify"
      :ripple="false"
      color="primary"
      class="mb-4 pr-5"
    >
      <SvgIcon
        :name="notify ? 'bell-alert' : 'bell-slash'"
        inline
        clickable
        class="ml-4 mr-4"
      />
      <span class="pr-3">
        Notify users on new content: {{ notify.toString() }}
      </span>
    </v-btn>

    <div style="position: relative">
      <page-tree
        :pageTree="pageTree"
        :topLevel="true"
        @togglePage="updateTree"
      />
    </div>
  </div>
</template>

<script lang="ts">
import SuccessIcon from "@/components/sub-components/SuccessIcon.vue";
import FailIcon from "@/components/sub-components/FailIcon.vue";
import Loader from "@/components/sub-components/Loader.vue";
import SvgIcon from "@/components/dynamic-components/SvgIcon.vue";
import PageTree from "@/components/general/PageTree.vue";
import ScenarioTimer from "@/components/sub-components/ScenarioTimer.vue";
import axios from "axios";
import { store } from "@/store";
import { sortTree } from "@/helpers";

export default {
  name: "VisibilityOverview",
  components: {
    SuccessIcon,
    FailIcon,
    SvgIcon,
    Loader,
    PageTree,
    ScenarioTimer,
  },
  data() {
    return {
      notify: true,
      loading: false,
      dialog: false,
      pageTree: {},
    };
  },
  props: {
    currentTab: { type: String, require: false },
    sse_error: { type: Boolean, default: false },
  },
  computed: {
    showTimer() {
      return this.currentTab === "Visibility" && !this.sse_error;
    },
    showLoader() {
      const viewCondition = store.getters.getCurrentView === "admin";
      const tabCondition = this.currentTab === "Visibility";
      const eventCondition = this.loading;
      return viewCondition && tabCondition && eventCondition;
    },
    forceReload() {
      return store.getters.getAdminForceReload("visibility");
    },
  },
  methods: {
    async getDataFromServer() {
      this.loading = true;
      axios
        .get("pages")
        .then((res) => {
          this.pageTree = sortTree(res.data.pages);
        })
        .finally(() => {
          this.loading = false;
          store.dispatch("unsetAdminForceReload", "visibility");
        });
    },
    async updateTree(pageId) {
      await axios
        .put(`/pages/${pageId}/hidden`, { notify: this.notify })
        .then(() => {
          this.updateObjectById(this.pageTree, pageId);
        });
    },
    updateObjectById(obj, page_id) {
      for (const key in obj) {
        if (obj[key].page_id === page_id) {
          obj[key].hidden = !obj[key].hidden;
          return true;
        }
        if (obj[key].childs) {
          if (this.updateObjectById(obj[key].childs, page_id)) {
            return true;
          }
        }
      }
      return false;
    },
  },
  watch: {
    forceReload: {
      handler(new_state, old_state) {
        if (new_state === true || old_state === undefined) {
          this.getDataFromServer();
        }
      },
      immediate: true,
    },
  },
};
</script>
