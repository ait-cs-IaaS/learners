<template>
  <div>
    <v-dialog v-model="showLoader" :scrim="false" persistent width="auto">
      <loader />
    </v-dialog>

    <div
      v-for="(exerciseGroup, exerciseGroupName, index) in exerciseGroups"
      class="mb-12"
    >
      <h2>
        {{ exerciseGroupName }}
      </h2>

      <v-card variant="flat" class="pa-0 mt-2 mb-5">
        <v-progress-linear
          v-model="exerciseGroup.completionPercentage"
          color="success"
          height="5"
        >
        </v-progress-linear>

        <v-container class="pa-5">
          <v-row class="text-grey d-none d-sm-flex">
            <v-col sm="1" class="d-none d-lg-flex">Type</v-col>
            <v-col sm="4" lg="5">Name</v-col>
            <v-col sm="3">Page</v-col>
            <v-col sm="2">Progress</v-col>
            <v-col sm="2" lg="1" class="action-col">Actions</v-col>
          </v-row>

          <v-row
            v-for="exercise in exerciseGroup.childExercises"
            :key="exercise"
            class="py-0 mt-0 exercise-row"
            @click="showDetails(exercise)"
          >
            <v-col sm="1" class="d-none d-lg-flex">
              <SvgIcon
                v-if="exercise.exercise_type === 'script'"
                name="command-line"
              />
              <SvgIcon
                v-if="exercise.exercise_type === 'form'"
                name="book-open"
              />
            </v-col>
            <v-col cols="12" sm="4" lg="5">
              <h3 v-html="exercise.exercise_name"></h3>
            </v-col>
            <v-col cols="12" sm="3">
              <span v-html="exercise.page_title"> </span>
            </v-col>
            <v-col cols="8" sm="2" class="process">
              <v-progress-linear
                v-model="exercise.completion_percentage"
                color="success"
                height="25"
              >
                {{ exercise.completion_percentage }}
              </v-progress-linear>
            </v-col>
            <v-col cols="4" sm="2" lg="1" class="action-col">
              <!-- <v-badge :content="14" color="error" class="mx-2">
                <SvgIcon name="chat-bubble-left" />
              </v-badge> -->
              <SvgIcon
                name="user-group"
                class="mx-2"
                clickable
                @click.stop="manageGroups(exercise)"
              />
              <SvgIcon
                name="eye"
                class="mx-2"
                clickable
                @click.stop="manageVisibility(exercise)"
              />
            </v-col>
          </v-row>
        </v-container>
      </v-card>
    </div>

    <!-- Dialog -->
    <v-dialog v-model="dialog" width="60%">
      <exercise-card :exercise="selectedExercise" />
    </v-dialog>
  </div>
</template>

<script lang="ts">
import ExerciseCard from "@/components/admin/ExerciseCard.vue";
import SuccessIcon from "@/components/sub-components/SuccessIcon.vue";
import FailIcon from "@/components/sub-components/FailIcon.vue";
import Loader from "@/components/sub-components/Loader.vue";
import SvgIcon from "@/components/dynamic-components/SvgIcon.vue";
import axios from "axios";
import { store } from "@/store";
import { IExerciseObject } from "@/types";

export default {
  name: "ExercisesOverview",
  components: {
    SuccessIcon,
    FailIcon,
    SvgIcon,
    Loader,
    ExerciseCard,
  },
  data() {
    return {
      tabledata: { cols: <any>[], rows: <any>[] },
      submissions: [],
      exerciseGroups: <any>[],
      detailsIdentifier: { exerciseId: "" },
      loading: false,
      dialog: false,
      selectedExercise: Object as () => IExerciseObject,
    };
  },
  props: {
    currentTab: { type: String, require: false },
  },
  computed: {
    showLoader() {
      const viewCondition = store.getters.getCurrentView === "admin";
      const tabCondition = this.currentTab === "Exercises";
      const eventCondition = this.loading;
      return viewCondition && tabCondition && eventCondition;
    },
  },
  methods: {
    showDetails(exercise) {
      this.selectedExercise = exercise;
      this.dialog = true;
    },
    manageGroups(exercise) {
      console.log("Manage Group: Not implemented yet.");
      console.log(exercise);
    },
    manageVisibility(exercise) {
      console.log("Manage Visibility: Not implemented yet.");
      console.log(exercise);
    },
  },
  async beforeMount() {
    this.loading = true;
    axios
      .get("exercises")
      .then((res) => {
        console.log(res.data);
        const exercises = res.data.exercises;

        this.exerciseGroups = exercises.reduce((exerciseGroups, item) => {
          const exerciseGroup = exerciseGroups[item.parent_page_title] || {
            childExercises: [],
            completionPercentage: 0,
          };
          exerciseGroup.childExercises.push(item);
          exerciseGroup.completionPercentage += item.completion_percentage;
          exerciseGroups[item.parent_page_title] = exerciseGroup;
          return exerciseGroups;
        }, {});

        console.log(this.exerciseGroups);
      })
      .finally(() => (this.loading = false));
  },
};
</script>
