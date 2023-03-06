import { Commit, createStore } from "vuex";
import VuexPersister from "vuex-persister";
import { generateTabs } from "@/helpers";
import { ITabObject } from "@/types";
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
    tabs: Array<ITabObject>,
    error: "",
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

    async getTabsFromServer({ commit }) {
      await axios
        .get("setup/tabs")
        .then((response) => {
          commit("SET_TABS", response.data);
          commit("SET_LOGO", response.data.logo);
        })
        .catch((error) => commit("SET_TABS", []));
    },
  },
  getters: {
    getLogo: (state) => state.logo,
    getJwt: (state) => state.jwt,
    getError: (state) => state.error,
    getTabs: (state) => state.tabs,
    getCurrentView: (state) => state.currentView,
  },
  plugins: [vuexPersister.persist],
});
