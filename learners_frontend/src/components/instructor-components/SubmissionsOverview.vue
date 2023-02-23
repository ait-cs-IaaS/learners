<template>
  <div>
    <v-dialog v-model="showLoader" :scrim="false" persistent width="auto">
      <loader />
    </v-dialog>

    <h2>Submissions Overview</h2>
    <v-table class="mt-2">
      <thead>
        <tr>
          <th
            class="text-left"
            v-for="exercise in exercises"
            :key="exercise.id"
          >
            {{ exercise.name }}
          </th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="submission in submissions" :key="submission.user_id">
          <td
            class="text-left"
            v-for="exercise in exercises"
            :key="exercise.id"
          >
            <!-- Success Icon -->
            <success-icon
              class="clickable"
              v-if="submission[exercise.id].completed === 1"
              @click="showDetails(exercise.id, submission['user_id'])"
            />

            <!-- Fail Icon -->
            <fail-icon
              class="clickable"
              v-else-if="
                submission[exercise.id].completed === -1 &&
                submission[exercise.id].executions.len > 0
              "
            />
            <!-- Username -->
            <span v-else-if="exercise.id === 'username'">{{
              submission[exercise.id]
            }}</span>
            <!-- Empty -->
            <span v-else> - </span>
          </td>
        </tr>
      </tbody>
    </v-table>

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
import SubmissionCard from "@/components/sub-components/SubmissionCard.vue";
import SuccessIcon from "@/components/sub-components/SuccessIcon.vue";
import FailIcon from "@/components/sub-components/FailIcon.vue";
import { store } from "@/store";
import axios from "axios";

export default {
  name: "SubmissionsOverview",
  components: {
    SuccessIcon,
    FailIcon,
    SubmissionCard,
  },
  data() {
    return {
      exercises: <any>[{ id: "username", name: "user" }],
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
    showDetails(exerciseId, userId) {
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
          id: exercise.global_exercise_id,
          name: exercise.exercise_name,
        });
      });
    });

    axios.get("submissions").then((res) => {
      const submissions = res.data.submissions;
      submissions.forEach((submission) => {
        this.submissions.push(submission);
      });
    });
  },
};
</script>
