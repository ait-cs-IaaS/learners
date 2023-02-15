import { Commit, createStore } from "vuex";
import VuexPersister from "vuex-persister";
import { generateTabs } from "@/helpers";
import ITabObject from "@/types";
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
  },
  mutations: {
    SET_LOGO: (state: { logo: string }, logo: string) => (state.logo = logo),
    SET_JWT: (state: { jwt: string }, jwt: string) => (state.jwt = jwt),
    SET_TABS: (state: { tabs: any }, newtabs: any) =>
      (state.tabs = generateTabs(state.tabs || [], newtabs)),
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
    setOpendInTab: (
      { commit }: { commit: Commit },
      { tabId: string, opened: boolean }
    ) => commit("SET_OPENED_IN_TAB", { tabId: string, opened: boolean }),
    unsetJwt: ({ commit }: { commit: Commit }) => commit("SET_JWT", ""),
    setCurrentView: ({ commit }: { commit: Commit }, currentView: string) =>
      commit("SET_CURRENT_VIEW", currentView),
    async getTabsFromServer({ commit }) {
      try {
        await axios.get("setup/tabs").then((response) => {
          commit("SET_TABS", response.data.tabs);
        });
      } catch (error) {
        console.error(error);
      }
    },
  },
  getters: {
    getLogo: (state) => state.logo,
    getJwt: (state) => state.jwt,
    getTabs: (state) => state.tabs,
    getCurrentView: (state) => state.currentView,
  },
  plugins: [vuexPersister.persist],
});
