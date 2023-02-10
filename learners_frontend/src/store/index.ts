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
    SET_TABS: (state: { tabs: any }, tabs: any) => (state.tabs = tabs),
    SET_CURRENT_VIEW: (state: { currentView: string }, currentView: string) =>
      (state.currentView = currentView),
  },
  actions: {
    setLogo: ({ commit }: { commit: Commit }, logo: string) =>
      commit("SET_LOGO", logo),
    setJwt: ({ commit }: { commit: Commit }, jwt: string) =>
      commit("SET_JWT", jwt),
    unsetJwt: ({ commit }: { commit: Commit }) => commit("SET_JWT", ""),
    setCurrentView: ({ commit }: { commit: Commit }, currentView: string) =>
      commit("SET_CURRENT_VIEW", currentView),
    async getTabsFromServer({ commit }) {
      try {
        await axios.get("setup/tabs").then((response) => {
          commit("SET_TABS", generateTabs(response.data.tabs));
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
  },
  plugins: [vuexPersister.persist],
});
