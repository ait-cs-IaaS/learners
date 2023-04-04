<template>
  <div
    class="questionaire-container"
    :class="{
      animating: animate,
    }"
  >
    <v-container>
      <v-form @submit.prevent="submitHandler">
        <v-row>
          <v-col>
            <h2>Q{{ currentQuestionaire?.id }}</h2>
          </v-col>
        </v-row>
        <v-row>
          <v-col>{{ currentQuestionaire?.question }} </v-col>
        </v-row>
        <v-row>
          <v-item-group
            v-model="selectedAnswers"
            :multiple="currentQuestionaire?.multiple"
          >
            <v-col
              v-for="answer in currentQuestionaire?.answers"
              :key="answer"
              cols="12"
              class="py-1"
            >
              <v-item v-slot="{ isSelected, toggle }">
                <v-card
                  :color="isSelected ? 'primary' : ''"
                  class="d-flex align-center px-3 py-2"
                  dark
                  @click="toggle"
                >
                  <v-scroll-y-transition>
                    <div class="flex-grow-1">
                      {{ answer }}
                    </div>
                  </v-scroll-y-transition>
                </v-card>
              </v-item>
            </v-col>
          </v-item-group>
        </v-row>
        <v-row>
          <v-col cols="12" class="py-2 d-flex justify-end">
            <v-btn
              :disabled="selectedAnswers === undefined"
              color="success"
              size="large"
              type="submit"
              variant="elevated"
            >
              submit
            </v-btn>
          </v-col>
        </v-row>
      </v-form>
    </v-container>
  </div>
</template>

<script lang="ts">
import SvgIcon from "@/components/dynamic-components/SvgIcon.vue";
import { store } from "@/store";
import { IQuestionaireObject } from "@/types";
import axios from "axios";
import { PropType } from "vue";

export default {
  name: "Questionaire",
  components: {
    SvgIcon,
  },
  data() {
    return {
      contentChanging: false,
      selectedAnswers: undefined,
    };
  },
  props: {
    currentQuestionaire: {
      type: Object as PropType<IQuestionaireObject>,
      require: true,
    },
  },
  computed: {
    animate() {
      return this.contentChanging;
    },
  },
  methods: {
    async submitHandler() {
      if (this.selectedAnswers === undefined) return;
      const response = await axios.post(`questionaires/questions/${this.currentQuestionaire?.global_question_id}`, {
        answers: this.selectedAnswers,
      });
      store.dispatch("removeQuestionaire", this.currentQuestionaire?.global_question_id);
    },
    triggerAnimation() {
      this.contentChanging = true;
      setTimeout(() => {
        this.contentChanging = false;
      }, 600);
    },
  },
  watch: {
    currentQuestionaire: function (newVal, oldVal) {
      this.selectedAnswers = undefined;
      this.triggerAnimation();
    },
  },
};
</script>

<style lang="scss">
.questionaire-container {
  position: absolute !important;
  background-color: #f6f6f6;
  display: block;
  z-index: 99 !important;
  top: 0px !important;
  right: 16px !important;
  padding: 24px 8px 24px 24px;
  border-radius: 0px;
  width: 364px;
  height: 100vh;
  overflow-x: hidden;
  overflow-y: auto;
  border-left: 3px solid white;

  &.animating {
    animation: fade-in 600ms ease;
  }

  &.submission {
    background-color: rgba(75, 138, 102, 0.9);
  }
}

@keyframes fade-in {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.questionaire-grid {
  display: flex;
}
</style>
