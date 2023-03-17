import { Commit, createStore } from "vuex";
import VuexPersister from "vuex-persister";
import { extractNotifications, generateTabs } from "@/helpers";
import { ITabObject, INotificationObject } from "@/types";
import axios from "axios";

const vuexPersister = new VuexPersister({
  overwrite: true,
  storage: sessionStorage,
});

export const store = createStore({
  state: {
    logo: "",
    jwt: "",
    currentView: "",
    tabs: new Array<ITabObject>(),
    error: "",
    notifications: new Array<INotificationObject>(),
    currentNotification: 0,
    showNotifications: true,
    adminForceReload: {
      submissions: false,
      exercises: false,
      notifications: false,
      feedback: false,
    },
  },
  mutations: {
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
      state: { currentNotification: number },
      currentNotification: number
    ) => (state.currentNotification = currentNotification),

    SET_CURRENT_NOTIFICATION_TO_LAST: (state: {
      currentNotification: number;
      notifications: any;
    }) => (state.currentNotification = state.notifications.length - 1),
    DEC_CURRENT_NOTIFICATION: (state: { currentNotification: number }) => {
      if (state.currentNotification > 0) state.currentNotification -= 1;
    },
    INC_CURRENT_NOTIFICATION: (state: {
      currentNotification: number;
      notifications: any;
    }) => {
      if (state.currentNotification < state.notifications.length - 1)
        return (state.currentNotification += 1);
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
  },
  actions: {
    setLogo: ({ commit }: { commit: Commit }, logo: string) =>
      commit("SET_LOGO", logo),

    setJwt: ({ commit }: { commit: Commit }, jwt: string) =>
      commit("SET_JWT", jwt),

    setError: ({ commit }: { commit: Commit }, error_msg: string) =>
      commit("SET_ERROR", error_msg),

    resetTabs: ({ commit }: { commit: Commit }) => commit("SET_TABS", []),

    setOpendInTab: (
      { commit }: { commit: Commit },
      { tabId: string, opened: boolean }
    ) => commit("SET_OPENED_IN_TAB", { tabId: string, opened: boolean }),

    unsetJwt: ({ commit }: { commit: Commit }) => commit("SET_JWT", ""),

    setCurrentView: ({ commit }: { commit: Commit }, currentView: string) =>
      commit("SET_CURRENT_VIEW", currentView),

    setCurrentNotification: (
      { commit }: { commit: Commit },
      currentNotification: number
    ) => commit("SET_CURRENT_NOTIFICATION", currentNotification),

    setCurrentNotificationToLast: ({ commit }: { commit: Commit }) =>
      commit("SET_CURRENT_NOTIFICATION_TO_LAST"),

    decCurrentNotification: ({ commit }: { commit: Commit }) =>
      commit("DEC_CURRENT_NOTIFICATION"),

    incCurrentNotification: ({ commit }: { commit: Commit }) =>
      commit("INC_CURRENT_NOTIFICATION"),

    appendToNotifications: (
      { commit }: { commit: Commit },
      payload: INotificationObject
    ) => commit("APPEND_TO_NOTIFICATIONS", payload),

    async getTabsFromServer({ commit }) {
      await axios
        .get("setup/tabs")
        .then((response) => {
          commit("SET_TABS", response.data);
          commit("SET_LOGO", response.data.logo);
        })
        .catch((error) => commit("SET_TABS", []));
    },

    async getNotificationsFromServer({ commit }) {
      await axios.get("notifications").then((response) => {
        commit(
          "SET_NOTIFICATIONS",
          extractNotifications(response.data.notifications)
        );
        commit("SET_CURRENT_NOTIFICATION_TO_LAST");
      });
    },

    enableNotifications: ({ commit }: { commit: Commit }) =>
      commit("SET_SHOW_NOTIFICATIONS_STATE", true),

    disableNotifications: ({ commit }: { commit: Commit }) =>
      commit("SET_SHOW_NOTIFICATIONS_STATE", false),

    setAdminForceReload: ({ commit }: { commit: Commit }, tab: string) =>
      commit("SET_ADMIN_FORCE_RELOAD", { tab: tab, state: true }),

    unsetAdminForceReload: ({ commit }: { commit: Commit }, tab: string) =>
      commit("SET_ADMIN_FORCE_RELOAD", { tab: tab, state: false }),
  },
  getters: {
    getLogo: (state) => state.logo,
    getJwt: (state) => state.jwt,
    getError: (state) => state.error,
    getTabs: (state) => state.tabs,
    getCurrentView: (state) => state.currentView || "",
    getAdminForceReload: (state) => (tab) => {
      return state.adminForceReload[tab];
    },
    getNotifications: (state) => state.notifications || [],
    getCurrentNotification: (state) => state.currentNotification || 0,
    getShowNotifications: (state) => state.showNotifications,
    getNotificationsLength: (state) => {
      if (state.notifications) return state.notifications.length;
      else return 0;
    },
  },
  plugins: [vuexPersister.persist],
});
