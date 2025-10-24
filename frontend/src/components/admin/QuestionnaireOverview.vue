<template>
  <div>
    <h2 class="mb-5">
      Questionnaire Overview
      <v-progress-circular
        class="mx-2 mb-1"
        color="grey"
        indeterminate
        :width="3"
        :size="18"
        v-show="loading"
      />
    </h2>

    <v-card class="pa-5">
      <h3>Create a new Question</h3>

      <div class="mt-5">
        <v-alert
          v-if="successMessage"
          type="success"
          variant="tonal"
          class="mb-4"
          closable
          @click:close="successMessage = ''"
        >
          {{ successMessage }}
        </v-alert>

        <!-- SINGLE v-form -->
        <v-form
          ref="formRef"
          v-model="valid"
          validate-on="submit"
          @submit.prevent="submit"
        >
          <v-container>
            <v-row>
              <v-col class="py-0 px-0" cols="12">
                <v-select
                  v-model="selectedQuestionnaireId"
                  :items="questionnaireItems"
                  item-title="label"
                  item-value="id"
                  label="Select questionnaire"
                  :rules="[req]"
                  variant="outlined"
                  :return-object="false"
                  clearable
                />
              </v-col>

              <v-col class="py-0 px-0" lg="10" cols="12">
                <v-text-field
                  v-model="question"
                  label="Question"
                  :rules="[req]"
                  variant="outlined"
                  class="mb-2"
                />
              </v-col>

              <v-col class="py-0" lg="2" cols="12">
                <v-switch
                  v-model="multiple"
                  label="Multiple answers"
                  density="compact"
                  color="secondary"
                  class="my-2 mx-5"
                />
              </v-col>

              <v-col class="pt-0 pb-5 px-0" cols="12">
                <div class="mb-2 text-subtitle-2">Answer options</div>

                <v-slide-y-transition group tag="div">
                  <div
                    v-for="(val, i) in answers"
                    :key="`answer-${i}`"
                    class="d-flex align-center mb-2"
                  >
                    <v-text-field
                      v-model="answers[i]"
                      :label="`Answer ${i + 1}`"
                      variant="outlined"
                      density="comfortable"
                      hide-details="auto"
                      class="flex-1"
                      @update:model-value="onAnswerChange(i)"
                      :rules="[i === answers.length - 1 ? () => true : req]"
                    />
                    <v-btn
                      variant="text"
                      class="ml-2 text-secondary"
                      :disabled="answers.length <= 1 && !answers[0].trim()"
                      @click="remove(i)"
                      icon
                      aria-label="Remove answer"
                    >
                      <v-icon>mdi-close</v-icon>
                    </v-btn>
                  </div>
                </v-slide-y-transition>
              </v-col>

              <v-col cols="12" class="pa-0 d-flex justify-end">
                <v-btn
                  class="mx-5 my-auto text-secondary"
                  variant="text"
                  @click="reset"
                  >Reset</v-btn
                >
                <v-btn
                  color="success"
                  size="large"
                  type="submit"
                  variant="elevated"
                  :disabled="!canSubmit"
                >
                  submit
                </v-btn>
              </v-col>
            </v-row>
          </v-container>
        </v-form>
      </div>
    </v-card>

    <v-expansion-panels class="mt-5">
      <v-expansion-panel
        v-for="questionnaire in questionnaires"
        :key="questionnaire.page_title"
      >
        <v-expansion-panel-title>
          <span v-html="questionnaire.page_title" />
        </v-expansion-panel-title>
        <v-expansion-panel-text>
          <v-container class="px-3">
            <v-row
              v-for="(question, index) in extractRows(questionnaire.questions)"
              :key="question.id"
              class="questionnaire-row"
            >
              <v-col cols="4">
                <span class="question-id">{{ index + 1 }}</span>
                <span v-html="question.question"></span>
              </v-col>

              <v-col cols="6">
                <ol class="answers">
                  <li
                    v-for="answer in JSON.parse(question.answer_options)"
                    :key="answer"
                  >
                    {{ answer }}
                  </li>
                </ol>
              </v-col>

              <v-col class="d-flex justify-end">
                {{ question.language }}
              </v-col>

              <v-col cols="1" class="d-flex justify-end btn-col">
                <v-btn
                  v-if="!question.active"
                  @click="activateQuestion(question)"
                  color="success"
                >
                  send
                </v-btn>
                <v-btn
                  v-else
                  @click="viewQuestion(question.id)"
                  color="success"
                  variant="outlined"
                >
                  <SvgIcon name="eye" class="mr-2" />
                  view
                </v-btn>
              </v-col>
            </v-row>
          </v-container>
        </v-expansion-panel-text>
      </v-expansion-panel>
    </v-expansion-panels>

    <div v-if="Object.keys(questionnaires).length === 0" class="no-data">
      No data.
    </div>

    <!-- Dialog -->
    <v-dialog
      v-model="dialog"
      :width="dialogFullscreen ? '100%' : '60%'"
      :fullscreen="dialogFullscreen"
    >
      <div class="dialog-header-actions">
        <v-btn
          icon
          rounded
          size="x-small"
          variant="text"
          color="white"
          @click="toggleDialogFullscreen"
        >
          <v-icon v-if="dialogFullscreen">mdi-fullscreen-exit</v-icon>
          <v-icon v-else>mdi-fullscreen</v-icon>
        </v-btn>
        <v-btn
          icon
          rounded
          size="x-small"
          class="ml-auto"
          color="white"
          variant="text"
          @click="closeDialog"
        >
          <SvgIcon name="x-mark" clickable />
        </v-btn>
      </div>
      <questionnaire-card
        :questionnaireId="selectedQuestionnaire"
        :fullWidth="dialogFullscreen"
      />
    </v-dialog>
  </div>
</template>

<script lang="ts">
interface Question {
  id: string;
  question: string;
  answer_options: string; // backend stores JSON string
  language: string;
  active: boolean;
  options: string[];
}

interface NewQuestionPayload {
  question: string;
  multiple: boolean;
  answers: string[]; // for preview / emit
  // If your backend needs a stringified version:
  answer_options?: string; // JSON.stringify(answers)
}

import axios from "axios";

import QuestionnaireCard from "@/components/admin/QuestionnaireCard.vue";
import Loader from "@/components/sub-components/Loader.vue";
import SvgIcon from "@/components/dynamic-components/SvgIcon.vue";
import { store } from "@/store";
import { IQuestionnaireQuestionObject } from "@/types";

export default {
  name: "QuestionnaireOverview",
  components: {
    QuestionnaireCard,
    Loader,
    SvgIcon,
  },
  props: {
    currentTab: { type: String, require: false },
  },
  data() {
    return {
      questionnaires: [] as any[],
      successMessage: "" as string,

      // Loader conditions
      questionnaireLoading: false,

      // Dialog & misc
      form: false,
      dialog: false,
      dialogFullscreen: false,
      selectedQuestionnaire: "",

      // ===== Question builder state =====
      valid: true, // v-form
      question: "" as string,
      multiple: false as boolean,
      answers: [""] as string[], // always keep a trailing empty input
      selectedQuestionnaireId: "" as string,
    };
  },
  computed: {
    questionnaireItems(): Array<{ id: string; label: string }> {
      return (this.questionnaires || []).map((q: any) => ({
        id: q.id, // ensure backend expects this id
        label: q.page_title || q.id,
      }));
    },

    loading() {
      return this.questionnaireLoading;
    },
    forceReload() {
      return store.getters.getAdminForceReload("questionnaire");
    },

    // Build the clean payload you preview / send
    payload(): NewQuestionPayload {
      const unique = (arr: string[]) => Array.from(new Set(arr));
      const cleanAnswers = unique(
        this.answers.map((s) => s.trim()).filter((s) => s.length > 0)
      );

      return {
        question: this.question.trim(),
        multiple: this.multiple,
        answers: cleanAnswers,
        // If your backend expects a JSON string instead of array, you can use:
        // answer_options: JSON.stringify(cleanAnswers),
      };
    },

    // Enable submit only when the form is actually valid
    canSubmit(): boolean {
      return (
        this.payload.question.length > 0 &&
        this.payload.answers.length >= 1 &&
        // all non-last filled fields must be non-empty
        this.answers.slice(0, -1).every((s) => s.trim().length > 0)
      );
    },
  },
  methods: {
    // ===== Question builder methods & rules =====
    req(v: string): true | string {
      return !!v?.trim() || "Required";
    },

    onAnswerChange(i: number) {
      // When typing into the last field, append a new empty one
      if (i === this.answers.length - 1 && this.answers[i].trim() !== "") {
        this.answers.push("");
      }
    },

    remove(i: number) {
      this.answers.splice(i, 1);
      // Keep at least one input visible
      if (this.answers.length === 0) this.answers.push("");
    },

    reset() {
      this.question = "";
      this.multiple = false;
      this.answers = [""];
    },

    async submit() {
      if (!this.canSubmit) return;

      const body = {
        question: this.payload.question,
        multiple: this.payload.multiple,
        answer_options: JSON.stringify(this.payload.answers),
        questionnaire_id: this.selectedQuestionnaireId || undefined,
        language: "en",
      };

      try {
        await axios.post("questionnaires/questions", body);
        await this.getDataFromServer();

        // show success
        this.successMessage = "Question created successfully.";

        // clear your model
        this.reset();
        this.selectedQuestionnaireId = "";

        // clear Vuetify validation state
        const form = this.$refs.formRef as any;
        form?.resetValidation(); // removes error state
        // optional: form?.reset(); // resets v-models bound directly to inputs
      } catch (e) {
        console.error("Failed to create question", e);
      }
    },

    // ===== Existing page logic (unchanged) =====
    extractRows(questions: Question[]) {
      let updatedRows = [] as Question[];
      questions.forEach((question) => {
        let found_index = updatedRows.findIndex((q) => q.id === question.id);
        if (found_index > -1) {
          const current_language = updatedRows[found_index]["language"];
          if (!current_language.includes(question.language))
            updatedRows[found_index]["language"] =
              current_language + ", " + question.language;
        } else updatedRows.push(question);
      });
      return updatedRows;
    },

    async activateQuestion(question: Question) {
      await axios
        .put(`questionnaires/questions/${question.id}`)
        .then(() => (question.active = true));
    },

    async viewQuestion(question_id: string) {
      this.selectedQuestionnaire = question_id;
      this.dialogFullscreen = false;
      this.dialog = true;
    },

    toggleDialogFullscreen() {
      this.dialogFullscreen = !this.dialogFullscreen;
    },

    closeDialog() {
      this.dialog = false;
      this.dialogFullscreen = false;
    },

    async getDataFromServer() {
      this.questionnaireLoading = true;
      axios
        .get("questionnaires")
        .then((res) => {
          this.questionnaires = res.data.questionnaires;
        })
        .finally(() => {
          this.questionnaireLoading = false;
          store.dispatch("unsetAdminForceReload", "questionnaire");
        });
    },
  },
  watch: {
    dialog(value: boolean) {
      if (!value) {
        this.dialogFullscreen = false;
      }
    },
    forceReload: {
      handler(new_state, old_state) {
        if (new_state === true || old_state === undefined) {
          this.getDataFromServer();
        }
      },
      immediate: true,
    },
  },
};
</script>

<style lang="scss">
.answers {
  list-style: lower-alpha;
  margin-left: 1rem;

  & li {
    padding-left: 10px;
    &::marker {
      color: rgba(var(--v-theme-secondary), 1);
    }
  }
}

.question-id {
  font-weight: bold;
  color: rgba(var(--v-theme-secondary), 1);
  padding-right: 15px;
  height: 100%;
  float: left;
}

.drop-down-group-title {
  font-weight: bold;
}

.questionnaire-row {
  transition: all 100ms ease;
  padding: 16px 24px 16px 16px;
  cursor: pointer;

  &:not(:last-child) {
    border-bottom: 1px solid #919191;
  }

  &:hover {
    background-color: rgba(var(--v-theme-secondary), 0.05);
  }
}

.v-list-item {
  padding-top: 0px !important;
  padding-bottom: 0px !important;
}
.v-list-item__content {
  display: flex;
  flex-direction: row-reverse;
  justify-content: start;
  align-content: center;
}

.v-list-item-title {
  flex: 1;
  align-self: center;
  height: 100%;
  width: 100%;
}
.v-list-item-subtitle {
  flex: 1;
  align-self: center;
}

.v-list-item-action {
  align-content: center;
  justify-content: center;
  display: flex;
  height: 45px;
  max-width: 20%;
}

.v-input.v-checkbox {
  display: flex;
}

.initial-notifications-list-item {
  position: relative;
  background-color: #f6f6f6;
  margin-top: 0px;
  border-radius: 4px;
}

.dialog-header-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  padding: 8px 12px 0;
}

.list-hover-container {
  display: flex;
  position: absolute;
  background-color: rgba(var(--v-theme-secondary), 0);
  width: 100%;
  height: 100%;
  transition: all 150ms ease;
  border-radius: 4px;

  &:hover {
    background-color: rgba(var(--v-theme-secondary), 0.1);
  }

  button.v-btn {
    background-color: white;
    border: solid 1px #555;
  }
}

.autocomplete-inputs .v-input__control {
  min-height: 60px;
}

.btn-col {
  min-width: fit-content;
}

.v-overlay--active.v-dialog--fullscreen {
  background: #000;
  margin-left: 60px;
}
</style>
