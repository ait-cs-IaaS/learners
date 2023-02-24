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
          <v-row class="text-grey">
            <v-col class="type-col">Type</v-col>
            <v-col cols="5">Name</v-col>
            <v-col>Page</v-col>
            <v-col cols="2">Progress</v-col>
            <v-col class="type-col"></v-col>
          </v-row>

          <v-row
            v-for="exercise in exerciseGroup.childExercises"
            :key="exercise"
            class="py-0 mt-0 exercise-row"
          >
            <v-col class="type-col">
              <SvgIcon
                v-if="exercise.exercise_type === 'script'"
                name="command-line"
              />
              <SvgIcon
                v-if="exercise.exercise_type === 'form'"
                name="book-open"
              />
            </v-col>
            <v-col cols="5">
              <h3>
                {{ exercise.exercise_name }}
              </h3>
            </v-col>
            <v-col>
              {{ exercise.page_title }}
            </v-col>
            <v-col cols="2">
              <v-progress-linear
                v-model="exercise.completion_percentage"
                color="success"
                height="25"
              >
                {{ exercise.completion_percentage }}
              </v-progress-linear>
            </v-col>
            <v-col class="type-col">
              <v-badge :content="14" color="error">
                <SvgIcon name="chat-bubble-left" />
              </v-badge>
            </v-col>
          </v-row>
        </v-container>
      </v-card>
    </div>
  </div>
</template>

<script lang="ts">
import SuccessIcon from "@/components/sub-components/SuccessIcon.vue";
import FailIcon from "@/components/sub-components/FailIcon.vue";
import Loader from "@/components/sub-components/Loader.vue";
import SvgIcon from "@/components/dynamic-components/SvgIcon.vue";
import axios from "axios";
import { store } from "@/store";

export default {
  name: "ExercisesOverview",
  components: {
    SuccessIcon,
    FailIcon,
    SvgIcon,
    Loader,
  },
  data() {
    return {
      tabledata: { cols: <any>[], rows: <any>[] },
      submissions: [],
      cols: <any>[{ id: "username", name: "user" }],
      rows: <any>[],
      exerciseGroups: <any>[],
      loading: false,
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
  methods: {},
  async beforeMount() {
    this.loading = true;
    axios
      .get("exercises")
      .then((res) => {
        console.log(res.data);
        const exercises = res.data.exercises;

        // const exerciseGroups = exercises.reduce((exerciseGroups, item) => {
        //   const exerciseGroup = exerciseGroups[item.parent_page_title] || [];
        //   exerciseGroup.push(item);
        //   exerciseGroups[item.parent_page_title] = exerciseGroup;
        //   return exerciseGroups;
        // }, {});

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

        // exercises.sort((a, b) => (a.order_weight > b.order_weight ? 1 : -1));
        // exercises.forEach((exercise) => {
        //   console.log(exercise);
        //   this.cols.push({
        //     id: exercise.global_exercise_id,
        //     name: exercise.exercise_name,
        //   });
        // });
      })
      .finally(() => (this.loading = false));

    axios.get("submissions").then((res) => {
      const submissions = res.data.submissions;
      console.log(submissions);
      submissions.forEach((submission) => {
        this.rows.push(submission);
      });
    });
  },
};
</script>
