<template>
  <div
    class="content-container pager exercises d-flex flex-wrap"
    :class="{ invisible: !(currentView === 'admin') }"
    style="overflow-y: scroll"
  >
    <v-container class="pa-5 mt-5">
      <v-row>
        <v-col cols="12">
          <h1>Admin Area</h1>
        </v-col>
        <v-col>
          <v-tabs v-model="adminTabs" bg-color="#f1f1f1" :mandatory="true">
            <v-tab value="Submissions">Submissions Overview</v-tab>
            <v-tab value="Exercises">Exercises</v-tab>
            <v-tab value="Notifications">Notifications</v-tab>
          </v-tabs>

          <v-card-text>
            <v-window v-model="adminTabs">
              <v-window-item value="Submissions">
                <submissions-overview class="tab-container" />
              </v-window-item>
              <v-window-item value="Exercises">
                <exercises-overview class="tab-container" />
              </v-window-item>
              <v-window-item value="Notifications">
                Notifications
              </v-window-item>
            </v-window>
          </v-card-text>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script lang="ts">
import SubmissionsOverview from "../instructor-components/SubmissionsOverview.vue";
import ExercisesOverview from "../instructor-components/ExercisesOverview.vue";
import { store } from "@/store";

export default {
  name: "InstructorPanel",
  components: {
    SubmissionsOverview,
    ExercisesOverview,
  },
  computed: {
    currentView() {
      return store.state.currentView;
    },
  },
  data() {
    return {
      adminTabs: null,
    };
  },
};
</script>
