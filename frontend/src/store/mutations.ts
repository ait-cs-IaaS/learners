import { generateTabs } from "@/helpers";
import { INotificationObject, IQuestionaireObject } from "@/types";

export default {
  SET_LOGO: (state: { logo: string }, logo: string) => (state.logo = logo),
  SET_JWT: (state: { jwt: string }, jwt: string) => (state.jwt = jwt),
  SET_ERROR: (state: { error: string }, error_msg: string) =>
    (state.error = error_msg),
  SET_TABS: (state: { tabs: any; currentView: string }, response: any) => {
    const { genTabs, genCurrentView } = generateTabs(
      state.tabs || [],
      response
    );
    state.tabs = genTabs;
    state.currentView = genCurrentView;
  },
  SET_CURRENT_VIEW: (state: { currentView: string }, currentView: string) =>
    (state.currentView = currentView),

  SET_OPENED_IN_TAB: (
    state: { tabs: any },
    payload: { tabId: string; opened: boolean }
  ) => {
    const tab = state.tabs.find((tab) => {
      return tab.id === payload.tabId;
    });
    tab.openedInTab = payload.opened;
  },

  SET_CURRENT_NOTIFICATION: (
    state: { currentNotificationIndex: number },
    currentNotificationIndex: number
  ) => (state.currentNotificationIndex = currentNotificationIndex),

  SET_CURRENT_NOTIFICATION_INDEX_TO_LAST: (state: {
    currentNotificationIndex: number;
    notifications: any;
  }) => (state.currentNotificationIndex = state.notifications.length - 1),

  DEC_CURRENT_NOTIFICATION: (state: { currentNotificationIndex: number }) => {
    if (state.currentNotificationIndex > 0) state.currentNotificationIndex -= 1;
  },
  INC_CURRENT_NOTIFICATION: (state: {
    currentNotificationIndex: number;
    notifications: any;
  }) => {
    if (state.currentNotificationIndex < state.notifications.length - 1)
      return (state.currentNotificationIndex += 1);
  },
  SET_NOTIFICATIONS: (state: { notifications: any }, payload: any) =>
    (state.notifications = payload),
  APPEND_TO_NOTIFICATIONS: (
    state: { notifications: any },
    payload: INotificationObject
  ) => state.notifications.push(payload),
  SET_SHOW_NOTIFICATIONS_STATE: (
    state: { showNotifications: boolean },
    newState: boolean
  ) => (state.showNotifications = newState),
  SET_ADMIN_FORCE_RELOAD: (
    state: { adminForceReload: any },
    newState: { tab: string; state: boolean }
  ) => (state.adminForceReload[newState.tab] = newState.state),
  APPEND_TO_QUESTIONAIRES: (
    state: { questionaires: any; showQuestionaires: boolean },
    payload: IQuestionaireObject
  ) => {
    state.questionaires.push(payload);
    if (state.questionaires.length) state.showQuestionaires = true;
  },

  REMOVE_QUESTIONAIRE: (
    state: { questionaires: any },
    global_question_id: Number
  ) =>
    (state.questionaires = state.questionaires.filter(
      (q) => q.global_question_id != global_question_id
    )),

  SET_SHOW_QUESTIONAIRE_STATE: (
    state: { showQuestionaires: boolean },
    newState: boolean
  ) => (state.showQuestionaires = newState),

  SET_CURRENT_QUESTIONAIRE_INDEX_TO_LAST: (state: {
    currentQuestionaireIndex: number;
    questionaires: any;
    showQuestionaires: boolean;
  }) => {
    state.currentQuestionaireIndex = state.questionaires.length - 1;
    if (state.questionaires.length) {
      state.showQuestionaires = true;
    } else {
      state.showQuestionaires = false;
    }
  },

  SET_QUESTIONAIRES: (state: { questionaires: any }, payload: any) =>
    (state.questionaires = payload),

  // DrawIO
  SET_DRAWIO_DATA: (state: { drawioEncodedData: string }, data: string) =>
  (state.drawioEncodedData = data),
};
