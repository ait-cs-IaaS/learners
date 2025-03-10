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
              <fail-icon
                v-else-if="
                  submission.completed === 0 && submission.executed === 0
                "
              />
              <partial-icon v-else-if="submission.executed === 1" />
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
        <template v-for="(inputgroup, groupIndex) in parsedFormData" :key="groupIndex">
          <template v-for="(inputgroupDetails, index) in inputgroup" :key="index">
            <h4 v-if="hasData(inputgroupDetails.data)" class="mb-3 details-card-label">
              {{ unescape(inputgroup[0].section) }}
              <span v-if="inputgroup.length > 1">: #{{ index + 1 }}</span>
            </h4>

            <template v-for="(input, label) in inputgroupDetails.data" :key="label">
              <hr v-if="input === '--divider--'" class="divider" />
              <div
                v-else
                class="details-card-row"
                :class="{ missing: !String(input).trim() }"
              >
                <div class="details-card-label">
                  {{ unescape(label) }}
                </div>

                <template v-if="input.type === 'drawio'">
                  <object :data="input.value" type="image/svg+xml"></object>
                  <a class="open-in-new-tab-link" @click="openInNewTab(input.value)">
                    <SvgIcon name="arrow-top-right-on-square" inline />
                    open in new tab
                  </a>
                </template>

                <template v-else-if="input.type === 'checkbox'">
                  <div v-for="item in input.value" :key="item" class="details-card-input">
                    <SvgIcon name="checkbox-checked" class="text-secondary" inline left />
                    {{ item }}
                  </div>
                </template>

                <template v-else-if="['radio', 'select-one'].includes(input.type)">
                  <div class="details-card-input">
                    <SvgIcon name="radio-checked" class="text-secondary" inline left />
                    {{ input.value }}
                  </div>
                </template>

                <template v-else-if="input.type === 'file'">
                  <img
                    v-if="isImage(input.value)"
                    :src="`${backend}/uploads/${input.value}`"
                    :alt="input.value"
                    class="file-preview details-card-input"
                  />
                  <span v-else class="d-block mb-3 details-card-input">
                    {{ input.value }}
                  </span>
                  <a class="open-in-new-tab-link" :href="`${backend}/uploads/${input.value}`" target="_blank">
                    <SvgIcon name="arrow-top-right-on-square" inline />
                    download file
                  </a>
                </template>

                <template v-else>
                  <div class="details-card-input" v-html="input.value"></div>
                </template>
              </div>
            </template>

            <hr v-if="hasData(inputgroupDetails.data)" class="divider" />
          </template>
        </template>

      </div>
    </v-card-text>
  </v-card>
</template>

<script lang="ts">
import SuccessIcon from "@/components/sub-components/SuccessIcon.vue";
import FailIcon from "@/components/sub-components/FailIcon.vue";
import PartialIcon from "@/components/sub-components/PartialIcon.vue";
import SvgIcon from "@/components/dynamic-components/SvgIcon.vue";
import Loader from "@/components/sub-components/Loader.vue";
import axios from "axios";
import { store } from "@/store";

export default {
  name: "SubmissionCard",
  components: {
    SuccessIcon,
    FailIcon,
    PartialIcon,
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
      backend: "",
    };
  },
  computed: {
    parsedFormData() {
      if (this.submissions.length > 0 && this.submissions[0].form_data) {
        return JSON.parse(this.submissions[0].form_data);
      }
      return []; 
    },
  },
  methods: {
    hasData(data) {
      return Object.keys(data).length > 0;
    },
    isImage(fileName) {
      return this.filetypes.some((ext) => fileName.endsWith(ext));
    },
    unescape(_string) {
      if (_string) return _string.replaceAll("_", " ");
      else return _string
    },
    openInNewTab(object_data) {
      const newTab = window.open();
      newTab?.document.write(
        '<html><body style="margin: 0;"><img src="' +
          object_data +
          '" alt="SVG Image"></body></html>'
      );
      newTab?.document.close();
    },
  },
  async beforeMount() {
    this.backend = store.getters.getBackendUrl;
    this.loading = true;
    const url = `submissions/${this.userId}/${this.exerciseId}`;

    axios
      .get(url)
      .then((res) => {
        console.log(res.data)
        const submissions = res.data.submissions;
        this.exerciseName = res.data.exercise_name;
        this.userName = res.data.user_name;
        submissions.forEach((submission) => {
          console.log(submission.form_data)
          // console.log(JSON.parse(JSON.parse(submission.form_data)))
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
  object {
    background-color: #fff;
    padding: 30px;
    margin: 30px auto;
    width: 90%;
    display: block;
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
  transition: 200ms ease;
  cursor: pointer;

  &:hover {
    background-color: rgba(var(--v-theme-secondary), 0.07);
  }
}
.file-preview {
  width: 100%;
  border-radius: 4px;
}
.divider {
  opacity: 0;
  margin: 1.6rem 0;
}

.details-card-input table {
  width: 100%;
  text-align: left;
  border: 0px !important;
  border-spacing: 0;

  & tbody th {
    font-size: 80%;
    border-bottom: 2px solid #dddddd;
    font-weight: 400;
    background-color: #f6f6f6;
    padding: 0.7rem 0.5rem;
  }
  & tbody tr td {
    padding: 0.7rem 0.5rem;
    margin: 0px !important;
    background-color: #f6f6f6;
    border-bottom: 1px solid #dddddd !important;
  }
}
</style>
