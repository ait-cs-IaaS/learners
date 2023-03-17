<template>
  <v-card
    class="pa-5 d-flex justify-center align-content-center"
    min-height="450"
  >
    <v-progress-circular
      class="ma-auto"
      color="grey"
      indeterminate
      :width="3"
      :size="18"
      v-show="loading"
    ></v-progress-circular>

    <!-- Header -->
    <v-toolbar-title v-if="!loading" class="details-card-title">
      <span class="text-grey">Exercise:</span>
      <h1>{{ exerciseName }}</h1>
      <span class="text-grey">User:</span>
      <h2>{{ userName }}</h2>
    </v-toolbar-title>

    <!-- Content -->
    <v-card-text v-if="!loading" class="details-card-text">
      <div
        v-for="(submission, index) in submissions"
        :key="submission"
        class="details-card-submission-row"
        :class="{ 'previous-submission': index > 0 }"
      >
        <!-- Submission Header -->
        <v-container class="details-card-submission-header mb-4">
          <v-row>
            <v-col cols="1">
              <success-icon v-if="submission.completed === 1" />
              <fail-icon v-else-if="submission.completed === -1" />
            </v-col>
            <v-col cols="11">
              <h2>Submission #{{ submissions.length - index }}</h2>
              <span class="text-grey">
                Executed on: {{ submission.execution_timestamp }}
              </span>
            </v-col>
          </v-row>
        </v-container>
        <!-- Submission's fields -->
        <div
          v-for="(input, label) in extractFormData(submission)"
          :key="label"
          class="details-card-row"
          :class="{
            missing: String(input).length < 1,
          }"
        >
          <div class="details-card-label">
            {{ unescape(label) }}
          </div>
          <div class="details-card-input">
            {{ input }}
          </div>
        </div>
      </div>
    </v-card-text>
  </v-card>
</template>

<script lang="ts">
import SuccessIcon from "@/components/sub-components/SuccessIcon.vue";
import FailIcon from "@/components/sub-components/FailIcon.vue";
import Loader from "@/components/sub-components/Loader.vue";
import axios from "axios";

export default {
  name: "SubmissionCard",
  components: {
    SuccessIcon,
    FailIcon,
    Loader,
  },
  props: {
    userId: { type: Number, require: true },
    exerciseId: { type: String, require: true },
  },
  data() {
    return {
      exerciseName: "",
      userName: "",
      submissions: <any>[],
      loading: false,
    };
  },
  methods: {
    unescape(_string) {
      return _string.replaceAll("_", " ");
    },
    extractFormData(submission) {
      const form_data = JSON.parse(submission.form_data);
      return Object.values(form_data)[0];
    },
  },
  async beforeMount() {
    this.loading = true;
    const url = `submissions/${this.userId}/${this.exerciseId}`;

    axios
      .get(url)
      .then((res) => {
        const submissions = res.data.submissions;
        this.exerciseName = res.data.exercise_name;
        this.userName = res.data.user_name;
        submissions.forEach((submission) => {
          this.submissions.push(submission);
        });
      })
      .finally(() => (this.loading = false));
  },
};
</script>

<style lang="scss">
.details-card-title {
  padding: 10px 24px;
  span {
    font-size: 0.85rem;
    display: block;
    margin-top: 5px;
  }
  h1 {
    font-size: 1.6rem;
  }
  h2 {
    font-size: 1.2rem;
  }
}

.details-card-submission-row {
  margin-bottom: 40px;
}

.details-card-submission-header {
  display: flex;
  h2 {
    font-size: 1.2rem;
    color: rgb(var(--v-theme-primary));
  }
  .success-checkmark {
    display: inline-flex;
    margin-bottom: -6px;
    margin-left: 0 4px;
  }
  span {
    font-size: 0.85rem;
    display: block;
    margin-top: 5px;
  }
}

.details-card-text {
  flex-grow: 1;
  overflow-y: auto;
}

.details-card-row {
  display: block;
  margin-bottom: 10px;
  padding: 10px;
  border-radius: 4px;
  box-shadow: 1px 1px 4px #c1c1c1;
  border-left: 5px solid rgb(var(--v-theme-primary));
  &.missing {
    border-left: 5px solid #9e9e9e;
    background-color: #ececec;
  }
}

.details-card-label {
  text-transform: capitalize;
  font-size: 0.95rem;
  padding: 4px 10px;
  color: #9e9e9e !important;
}
.details-card-input {
  font-size: 0.95rem;
  display: block;
  padding: 4px 10px;
}
</style>
