import { createStore } from "vuex";

// Create a new store instance.
export const store = createStore({
  state() {
    return {
      currentView: "documentation",
    };
  },
  mutations: {
    changeCurrentView(state) {
      if (state.currentView !== "client") {
        state.currentView = "client";
      } else {
        state.currentView = "documentation";
      }
    },
  },
});
