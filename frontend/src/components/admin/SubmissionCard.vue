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
        <template v-for="item in JSON.parse(submission.form_data)">
          <div
            v-for="(input, label) in item"
            :key="label"
            class="details-card-row"
            :class="{
              missing: String(input).length < 1,
            }"
          >
            <div v-if="String(label) == 'drawio-input'">
              <div class="details-card-label">
                {{ unescape(label) }}
              </div>
              <iframe
                class="drawio-preview"
                style="width: 100%; height: 35vw"
                :src="`https://viewer.diagrams.net/${input}`"
                frameborder="0"
              ></iframe>
              <a
                class="open-in-new-tab-link"
                :href="`https://app.diagrams.net/${input}`"
                target="_blank"
              >
                <SvgIcon name="arrow-top-right-on-square" inline />
                open in new tab
              </a>
            </div>
            <div v-else-if="String(label) == 'attachment'">
              <div class="details-card-label">Uploaded file</div>
              <img
                v-if="filetypes.some((s) => input.endsWith(s))"
                :src="`${backend}/uploads/${input}`"
                alt="{{input}}"
                class="file-preview details-card-input"
              />
              <span v-else class="d-block mb-3 details-card-input">
                {{ input }}
              </span>
              <a
                class="open-in-new-tab-link"
                :href="`${backend}/uploads/${input}`"
                target="_blank"
              >
                <SvgIcon name="arrow-top-right-on-square" inline />
                download file
              </a>
            </div>
            <div v-else>
              <div class="details-card-label">
                {{ unescape(label) }}
              </div>
              <div class="details-card-input">
                {{ input }}
              </div>
            </div>
          </div>
        </template>
      </div>
    </v-card-text>
  </v-card>
</template>

<script lang="ts">
import SuccessIcon from "@/components/sub-components/SuccessIcon.vue";
import FailIcon from "@/components/sub-components/FailIcon.vue";
import SvgIcon from "@/components/dynamic-components/SvgIcon.vue";
import Loader from "@/components/sub-components/Loader.vue";
import axios from "axios";

export default {
  name: "SubmissionCard",
  components: {
    SuccessIcon,
    FailIcon,
    Loader,
    SvgIcon,
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
      filetypes: ["png", "jpg", "jpeg", "gif", "json", "svg"],
    };
  },
  computed: {
    backend() {
      return import.meta.env.VITE_BACKEND;
    },
  },
  methods: {
    unescape(_string) {
      return _string.replaceAll("_", " ");
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
    color: rgb(var(--v-theme-secondary));
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
  border-left: 5px solid rgb(var(--v-theme-secondary));
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

.open-in-new-tab-link {
  border: 1px solid rgb(var(--v-theme-secondary));
  border-radius: 4px;
  margin: 10px;
  padding: 4px 10px;
  font-size: 0.85rem;
  display: flex;
  justify-content: center;
  text-decoration: none;
  color: rgb(var(--v-theme-secondary));
  &:hover {
    border: 2px solid rgb(var(--v-theme-secondary));
    margin: 8px;
    margin-top: -1px !important;
    margin-bottom: 9px;
  }
}
.file-preview {
  width: 100%;
  border-radius: 4px;
}
</style>
