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
      <span class="text-grey">Question:</span>
      <h1 v-html="question"></h1>
    </v-toolbar-title>

    <!-- Content -->
    <v-card-text
      v-if="!loading"
      class="details-card-text pb-10"
      style="height: 70vh"
    >
      <QuestionaireChart
        ref="questionaireChart"
        v-bind:questionaireId="questionaireId"
      />
    </v-card-text>
  </v-card>
</template>

<script lang="ts">
import Loader from "@/components/sub-components/Loader.vue";
import QuestionaireChart from "@/components/sub-components/QuestionaireChart.vue";
import axios from "axios";

export default {
  name: "QuestionaireCard",
  components: {
    Loader,
    QuestionaireChart,
  },
  props: {
    questionaireId: { type: String, require: true },
  },
  data() {
    return {
      question: "",
      loading: false,
    };
  },
  async beforeMount() {
    this.loading = true;
    const url = `questionaires/questions/${this.questionaireId}`;
    axios
      .get(url)
      .then((res) => {
        const response = res.data;
        this.question = response.question;
      })
      .finally(() => {
        this.loading = false;
      });
  },
};
</script>
