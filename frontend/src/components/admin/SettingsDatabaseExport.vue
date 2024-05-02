<template>
  <v-card class="pa-5 d-flex justify-center align-content-center">
    <!-- Header -->
    <v-toolbar-title v-if="!loading" class="details-card-title">
      <span class="text-grey">overline:</span>
      <h1>Database Export</h1>
    </v-toolbar-title>

    <!-- Content -->
  </v-card>
</template>

<script lang="ts">
import type { PropType } from "vue";
import { IExerciseObject } from "@/types";

export default {
  name: "SettingsDatabaseExport",
  props: {
    exercise: {
      type: Object as PropType<IExerciseObject>,
      require: true,
      default: null,
    },
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
};
</script>

<style lang="scss">
.details-card-label {
  font-size: 0.85rem;
  align-self: center;
}

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

.details-card-exercise-header {
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
</style>
