<template>
  <div>
    <v-dialog v-model="showLoader" :scrim="false" persistent width="auto">
      <loader />
    </v-dialog>

    <h2>Submissions Overview</h2>
    <data-table
      class="mt-3"
      :headers="exercises"
      :items="submissions"
      @showDetails="showDetails"
    />

    <!-- Dialog -->
    <v-dialog v-model="dialog" width="60%">
      <submission-card
        :userId="detailsIdentifier.userId"
        :exerciseId="detailsIdentifier.exerciseId"
      />
    </v-dialog>
  </div>
</template>

<script lang="ts">
import SubmissionCard from "@/components/admin/SubmissionCard.vue";
import Loader from "@/components/sub-components/Loader.vue";
import DataTable from "@/components/sub-components/DataTable.vue";
import { store } from "@/store";
import axios from "axios";

export default {
  name: "SubmissionsOverview",
  components: {
    SubmissionCard,
    Loader,
    DataTable,
  },
  data() {
    return {
      exercises: <any>[
        {
          value: "username",
          text: "user",
          parent: "user",
          fixed: true,
          sortable: true,
        },
      ],
      submissions: <any>[],
      dialog: false,
      detailsIdentifier: { userId: 0, exerciseId: "" },
      loading: false,
    };
  },
  props: {
    currentTab: { type: String, require: false },
  },
  computed: {
    showLoader() {
      const viewCondition = store.getters.getCurrentView === "admin";
      const tabCondition = this.currentTab === "Submissions";
      const eventCondition = this.loading;
      return viewCondition && tabCondition && eventCondition;
    },
  },
  methods: {
    showDetails({ exerciseId, userId }) {
      this.dialog = true;
      this.detailsIdentifier = { userId: userId, exerciseId: exerciseId };
    },
  },
  async beforeMount() {
    axios.get("exercises").then((res) => {
      const exercises = res.data.exercises;
      exercises.sort((a, b) => (a.order_weight > b.order_weight ? 1 : -1));
      exercises.forEach((exercise) => {
        this.exercises.push({
          value: exercise.global_exercise_id,
          text: exercise.exercise_name,
          parent: exercise.parent_page_title,
        });
      });
    });

    axios.get("submissions").then((res) => {
      const submissions = res.data.submissions;
      submissions.forEach((submission) => {
        this.submissions.push(submission);
      });
      console.log(this.submissions);
    });
  },
};
</script>
