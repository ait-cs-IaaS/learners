import axios from "axios";
import { Commit } from "vuex";
import { extractNotifications, extractQuestionaires } from "@/helpers";
import { INotificationObject, IQuestionaireObject } from "@/types";

export default {
  // Setup/General Actions
  setLogo: ({ commit }: { commit: Commit }, logo: string) =>
    commit("SET_LOGO", logo),

  setJwt: ({ commit }: { commit: Commit }, jwt: string) =>
    commit("SET_JWT", jwt),

  unsetJwt: ({ commit }: { commit: Commit }) => commit("SET_JWT", ""),

  setError: ({ commit }: { commit: Commit }, error_msg: string) =>
    commit("SET_ERROR", error_msg),

  setCurrentView: ({ commit }: { commit: Commit }, currentView: string) =>
    commit("SET_CURRENT_VIEW", currentView),

  // Tabs
  async getTabsFromServer({ commit }) {
    await axios
      .get("setup/tabs")
      .then((response) => {
        commit("SET_TABS", response.data);
        commit("SET_LOGO", response.data.logo);
      })
      .catch((error) => commit("SET_TABS", []));
  },

  resetTabs: ({ commit }: { commit: Commit }) => commit("SET_TABS", []),

  setOpendInTab: (
    { commit }: { commit: Commit },
    { tabId: string, opened: boolean }
  ) => commit("SET_OPENED_IN_TAB", { tabId: string, opened: boolean }),

  // Notifications
  setCurrentNotification: (
    { commit }: { commit: Commit },
    currentNotificationIndex: number
  ) => commit("SET_CURRENT_NOTIFICATION", currentNotificationIndex),

  setCurrentNotificationToLast: ({ commit }: { commit: Commit }) =>
    commit("SET_CURRENT_NOTIFICATION_INDEX_TO_LAST"),

  decCurrentNotification: ({ commit }: { commit: Commit }) =>
    commit("DEC_CURRENT_NOTIFICATION"),

  incCurrentNotification: ({ commit }: { commit: Commit }) =>
    commit("INC_CURRENT_NOTIFICATION"),

  appendToNotifications: (
    { commit }: { commit: Commit },
    payload: INotificationObject
  ) => commit("APPEND_TO_NOTIFICATIONS", payload),

  async getNotificationsFromServer({ commit }) {
    await axios.get("notifications").then((response) => {
      commit(
        "SET_NOTIFICATIONS",
        extractNotifications(response.data.notifications)
      );
      commit("SET_CURRENT_NOTIFICATION_INDEX_TO_LAST");
    });
  },

  enableNotifications: ({ commit }: { commit: Commit }) =>
    commit("SET_SHOW_NOTIFICATIONS_STATE", true),

  disableNotifications: ({ commit }: { commit: Commit }) =>
    commit("SET_SHOW_NOTIFICATIONS_STATE", false),

  // Questionaires
  appendToQuestionaires: (
    { commit }: { commit: Commit },
    payload: IQuestionaireObject
  ) => commit("APPEND_TO_QUESTIONAIRES", payload),

  setCurrentQuestionaireToLast: ({ commit }: { commit: Commit }) =>
    commit("SET_CURRENT_QUESTIONAIRE_INDEX_TO_LAST"),

  removeQuestionaire: (
    { commit }: { commit: Commit },
    global_question_id: Number
  ) => {
    commit("REMOVE_QUESTIONAIRE", global_question_id);
    commit("SET_CURRENT_QUESTIONAIRE_INDEX_TO_LAST");
  },

  async getQuestionairesFromServer({ commit }) {
    await axios.get("questionaires/questions").then((response) => {
      console.log(
        "------------------------------------------------------------"
      );
      console.log(response);
      console.log(response.data);
      console.log(response.data.questions);
      console.log(extractQuestionaires(response.data.questions));
      commit(
        "SET_QUESTIONAIRES",
        extractQuestionaires(response.data.questions)
      );
      commit("SET_CURRENT_QUESTIONAIRE_INDEX_TO_LAST");
    });
  },

  enableQuestionaire: ({ commit }: { commit: Commit }) =>
    commit("SET_SHOW_QUESTIONAIRE_STATE", true),

  disableQuestionaire: ({ commit }: { commit: Commit }) =>
    commit("SET_SHOW_QUESTIONAIRE_STATE", false),

  // Admin View Actions
  setAdminForceReload: ({ commit }: { commit: Commit }, tab: string) =>
    commit("SET_ADMIN_FORCE_RELOAD", { tab: tab, state: true }),

  unsetAdminForceReload: ({ commit }: { commit: Commit }, tab: string) =>
    commit("SET_ADMIN_FORCE_RELOAD", { tab: tab, state: false }),
};
