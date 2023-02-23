<template>
  <div>
    <v-dialog v-model="showLoader" :scrim="false" persistent width="auto">
      <h5>Requesting data</h5>
      <v-progress-linear
        class="mt-3"
        color="primary"
        indeterminate
        rounded
        height="6"
      ></v-progress-linear>
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
                name="list-bullet"
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
    <!-- <v-table>
      <thead>
        <tr>
          <th class="text-left" v-for="col in cols" :key="col.id">
            {{ col.name }}
          </th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="row in rows" :key="row.user_id">
          <td class="text-left" v-for="col in cols" :key="col.id">
            <success-icon v-if="row[col.id] === 1" />
            <fail-icon v-else-if="row[col.id] === -1" />
            <span v-else>{{ row[col.id] }}</span>
          </td>
        </tr>
      </tbody>
    </v-table> -->
  </div>
</template>

<script lang="ts">
import SuccessIcon from "../sub-components/SuccessIcon.vue";
import FailIcon from "../sub-components/FailIcon.vue";
import axios from "axios";
import SvgIcon from "@/components/dynamic-components/SvgIcon.vue";

export default {
  name: "ExercisesOverview",
  components: {
    SuccessIcon,
    FailIcon,
    SvgIcon,
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
      return this.loading && this.currentTab === "Exercises";
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
