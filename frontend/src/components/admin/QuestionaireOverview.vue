<template>
  <div>
    <h2 class="mb-3">
      Questionaire Overview

      <v-progress-circular
        class="mx-2 mb-1"
        color="grey"
        indeterminate
        :width="3"
        :size="18"
        v-show="loading"
      ></v-progress-circular>
    </h2>

    <div>
      <v-expansion-panels class="pb-3 my-5">
        <v-expansion-panel
          v-for="questionaire in questionaires"
          :key="questionaire.page_title"
        >
          <v-expansion-panel-title>
            {{ questionaire.page_title }}
          </v-expansion-panel-title>
          <v-expansion-panel-text>
            <v-container class="px-0">
              <v-row
                v-for="question in extractRows(questionaire.questions)"
                :key="question"
                class="questionaire-row"
              >
                <v-col cols="4">
                  <span class="question-id">
                    {{ question.id }}
                  </span>
                  <span>
                    {{ question.question }}
                  </span>
                </v-col>
                <v-col cols="6">
                  <ol class="answers">
                    <li v-for="answer in JSON.parse(question.answers)">
                      {{ answer }}
                    </li>
                  </ol>
                </v-col>
                <v-col cols="1">
                  {{ question.language }}
                </v-col>
                <v-col cols="1" class="d-flex justify-end">
                  <v-btn
                    v-if="!question.active"
                    @click="activateQuestion(question.global_question_id)"
                    color="success"
                  >
                    send
                  </v-btn>
                  <v-btn
                    v-else
                    @click="viewQuestion(question.global_question_id)"
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
    </div>

    <div v-if="Object.keys(questionaires).length === 0" class="no-data">
      No data.
    </div>
  </div>
</template>

<script lang="ts">
import axios from "axios";

import Loader from "@/components/sub-components/Loader.vue";
import SvgIcon from "@/components/dynamic-components/SvgIcon.vue";
import { store } from "@/store";

export default {
  name: "QuestionaireOverview",
  components: {
    Loader,
    SvgIcon,
  },
  data() {
    return {
      questionaires: <any>[],
      // Loader conditions
      questionaireLoading: false,
      // Form
      form: false,
    };
  },
  props: {
    currentTab: { type: String, require: false },
  },
  computed: {
    loading() {
      return this.questionaireLoading;
    },
    forceReload() {
      return store.getters.getAdminForceReload("questionaire");
    },
  },
  methods: {
    extractRows(questions) {
      let updatedRows = <any>[];
      questions.forEach((question) => {
        let found_index = updatedRows.findIndex(
          (q) => q.global_question_id === question.global_question_id
        );
        if (found_index > -1) {
          const current_language = updatedRows[found_index]["language"];
          if (!current_language.includes(question.language))
            updatedRows[found_index]["language"] =
              current_language + ", " + question.language;
        } else updatedRows.push(question);
      });
      return updatedRows;
    },
    async activateQuestion(global_question_id) {
      await axios.put(`questionaires/questions/${global_question_id}`);
    },
    async viewQuestion(global_question_id) {
      console.log("not implemented yet.");
    },
    async getDataFromServer() {
      this.questionaireLoading = true;
      store.dispatch("unsetAdminForceReload", "questionaire");
      axios
        .get("questionaires")
        .then((res) => {
          this.questionaires = res.data.questionaires;
        })
        .finally(() => {
          this.questionaireLoading = false;
        });
    },
  },
  watch: {
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
      color: rgba(var(--v-theme-primary), 1);
    }
  }
}

.question-id {
  font-weight: bold;
  color: rgba(var(--v-theme-primary), 1);
  padding-right: 15px;
  height: 100%;
  float: left;
}

.drop-down-group-title {
  font-weight: bold;
}

.questionaire-row {
  transition: all 100ms ease;
  padding: 16px 6px;
  cursor: pointer;

  &:not(:last-child) {
    border-bottom: 1px solid #919191;
  }

  &:hover {
    background-color: rgba(var(--v-theme-primary), 0.05);
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

.list-hover-container {
  display: flex;
  position: absolute;
  background-color: rgba(var(--v-theme-primary), 0);
  width: 100%;
  height: 100%;
  transition: all 150ms ease;
  border-radius: 4px;

  &:hover {
    background-color: rgba(var(--v-theme-primary), 0.1);
  }

  button.v-btn {
    background-color: white;
    border: solid 1px #555;
  }
}

.autocomplete-inputs .v-input__control {
  min-height: 60px;
}
</style>
