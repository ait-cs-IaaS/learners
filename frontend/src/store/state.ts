import {
  ITabObject,
  INotificationObject,
  IQuestionnaireQuestionObject,
} from "@/types";

export default {
  logo: "",
  jwt: "",
  currentView: "",
  tabs: new Array<ITabObject>(),
  error: "",
  theme: new Array(),

  // Notifications
  notifications: new Array<INotificationObject>(),
  currentNotificationIndex: 0,
  showNotifications: true,

  // Questionnaires
  questionnaires: new Array<IQuestionnaireQuestionObject>(),
  currentQuestionnaireIndex: 0,
  showQuestionnaires: true,

  // Admin Reloads
  adminForceReload: {
    submissions: false,
    exercises: false,
    notifications: false,
    feedback: false,
    questionnaire: false,
  },

  // DrawIO
  drawioEncodedData: "",
};
