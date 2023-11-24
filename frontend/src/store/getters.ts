export default {
  // General
  getLogo: (state) => state.logo,
  getJwt: (state) => state.jwt,
  getError: (state) => state.error,
  getTabs: (state) => state.tabs,
  getCurrentView: (state) => state.currentView || "",
  getTheme: (state) => state.theme,

  // Admin View
  getAdminForceReload: (state) => (tab) => {
    return state.adminForceReload[tab];
  },

  // Notifications
  getNotifications: (state) => {
    const filteredNotifications = state.notifications.filter((item) => {
      // Check positions argument
      return (
        item.positions.includes("all") ||
        item.positions.includes(state.currentView)
      );
    });
    return filteredNotifications;
  },
  getCurrentNotificationIndex: (state) => state.currentNotificationIndex || 0,
  getShowNotifications: (state) => state.showNotifications,
  getNotificationsLength: (state) => {
    if (state.notifications) return state.notifications.length;
    else return 0;
  },

  // Questionaires
  getShowQuestionaires: (state) => state.showQuestionaires,
  getQuestionaires: (state) => state.questionaires || [],
  getCurrentQuestionaireIndex: (state) => state.currentQuestionaireIndex || 0,
  getQuestionairesLength: (state) => {
    if (state.questionaires) return state.questionaires.length;
    else return 0;
  },

  // DrawIO
  getDrawioData: (state) => state.drawioEncodedData,
};
