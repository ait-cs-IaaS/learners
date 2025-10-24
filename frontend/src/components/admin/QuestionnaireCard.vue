<template>
  <v-card
    class="pa-5 questionnaire-card"
    :class="{ 'full-width-card': fullWidth }"
    min-height="450"
  >
    <div v-if="loading" class="loading-container">
      <v-progress-circular
        color="grey"
        indeterminate
        :width="3"
        :size="18"
      ></v-progress-circular>
    </div>

    <!-- Header -->
    <template v-else>
      <v-toolbar-title class="details-card-title">
        <span class="text-grey">Question:</span>
        <h1 v-html="question"></h1>
      </v-toolbar-title>

      <!-- Content -->
      <v-card-text
        class="details-card-text pb-10"
        :class="{ 'full-height-text': fullWidth }"
        :style="cardTextStyle"
      >
        <QuestionnaireChart
          ref="questionnaireChart"
          v-bind:questionnaireId="questionnaireId"
        />
      </v-card-text>
    </template>
  </v-card>
</template>

<script lang="ts">
import QuestionnaireChart from "@/components/sub-components/QuestionnaireChart.vue";
import axios from "axios";

export default {
  name: "QuestionnaireCard",
  components: {
    QuestionnaireChart,
  },
  props: {
    questionnaireId: { type: String, require: true },
    fullWidth: { type: Boolean, default: false },
  },
  data() {
    return {
      question: "",
      loading: false,
    };
  },
  computed: {
    cardTextStyle(): Record<string, string> | undefined {
      return this.fullWidth ? undefined : { height: "70vh" };
    },
  },
  async beforeMount() {
    this.loading = true;
    const url = `questionnaires/questions/${this.questionnaireId}`;
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

<style scoped lang="scss">
.details-card-title {
  flex: 0 0;
}

.questionnaire-card {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.loading-container {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.full-width-card {
  max-width: none;
  justify-content: flex-start;
  align-items: stretch;
  border-radius: 4px !important;
  height: calc(100% - 60px - 60px);
  width: calc(100vw - 60px - 60px);
  min-width: calc(100vw - 60px - 60px) !important;
  margin: auto;
}

.full-height-text {
  flex: 1;
  height: 100%;
}

.full-height-text :deep(.questionnaireChart) {
  height: 100%;
}
</style>
