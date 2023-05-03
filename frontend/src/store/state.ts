import {
  ITabObject,
  INotificationObject,
  IQuestionaireQuestionObject,
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

  // Questionaires
  questionaires: new Array<IQuestionaireQuestionObject>(),
  currentQuestionaireIndex: 0,
  showQuestionaires: true,

  // Admin Reloads
  adminForceReload: {
    submissions: false,
    exercises: false,
    notifications: false,
    feedback: false,
    questionaire: false,
  },

  // DrawIO
  drawioEncodedData: "",
};
