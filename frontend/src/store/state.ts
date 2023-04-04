import { ITabObject, INotificationObject, IQuestionaireObject } from "@/types";

export default {
  logo: "",
  jwt: "",
  currentView: "",
  tabs: new Array<ITabObject>(),
  error: "",

  // Notifications
  notifications: new Array<INotificationObject>(),
  currentNotificationIndex: 0,
  showNotifications: true,

  // Questionaires
  questionaires: new Array<IQuestionaireObject>(),
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
};
