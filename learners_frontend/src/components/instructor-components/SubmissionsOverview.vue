<template>
  <div>
    <h2>Submissions Overview</h2>
    <v-table>
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
    </v-table>
  </div>
</template>

<script lang="ts">
import SuccessIcon from "../sub-components/SuccessIcon.vue";
import FailIcon from "../sub-components/FailIcon.vue";
import axios from "axios";

export default {
  name: "SubmissionsOverview",
  components: {
    SuccessIcon,
    FailIcon,
  },
  data() {
    return {
      tabledata: { cols: <any>[], rows: <any>[] },
      submissions: [],
      cols: <any>[{ id: "username", name: "user" }],
      rows: <any>[],
    };
  },
  computed: {},
  methods: {},
  async beforeMount() {
    axios.get("exercises").then((res) => {
      const exercises = res.data.exercises;
      exercises.sort((a, b) => (a.order_weight > b.order_weight ? 1 : -1));
      exercises.forEach((exercise) => {
        console.log(exercise);
        this.cols.push({
          id: exercise.global_exercise_id,
          name: exercise.exercise_name,
        });
      });
    });

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
