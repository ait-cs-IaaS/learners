import { store } from "@/store";
import {
  INotificationObject,
  ITabObject,
  IQuestionaireQuestionObject,
} from "@/types/index";
import axios from "axios";

export const generateTabs = (tabs, response) => {
  const newtabs = response.tabs;
  tabs = (newtabs || []).map((newtab) => {
    const i = tabs.findIndex((_element) => _element.id === newtab.id);
    if (i > -1) {
      return {
        ...tabs[i],
        ...newtab,
      };
    } else {
      return <ITabObject>{
        id: `${newtab?.id}`,
        icon: `${newtab?.icon}`,
        tooltip: `${newtab?.tooltip}`,
        _type: `${newtab?._type}`,
        url: `${newtab?.url}`,
        index: newtab?.index,
      };
    }
  });

  const currentView = response.landingpage;

  return { genTabs: tabs, genCurrentView: currentView };
};

export const extractNotifications = (responseData) => {
  let newNotifications;

  if (Array.isArray(responseData)) {
    newNotifications = (responseData || []).map((newNotification) => {
      return <INotificationObject>{
        event: `${newNotification?.event}`,
        message: `${newNotification?.message}`,
        positions: newNotification?.positions,
      };
    });
  } else {
    newNotifications = <INotificationObject>{
      event: `${JSON.parse(responseData)?.event}`,
      message: `${JSON.parse(responseData)?.message}`,
      positions: JSON.parse(responseData)?.positions,
    };
  }

  return newNotifications;
};

export const extractQuestionaires = (responseData) => {
  let newQuestionaires;

  if (Array.isArray(responseData)) {
    newQuestionaires = (responseData || []).map((newQuestionaire) => {
      // event: `${newQuestionaire?.event}`,
      return <IQuestionaireQuestionObject>{
        id: newQuestionaire?.id,
        question: newQuestionaire?.question,
        multiple: newQuestionaire?.multiple,
        answers: JSON.parse(newQuestionaire?.answer_options),
        language: newQuestionaire?.language,
        global_question_id: newQuestionaire?.global_question_id,
        global_questionaire_id: newQuestionaire?.global_questionaire_id,
        page_title: newQuestionaire?.page_title,
      };
    });
  } else {
    newQuestionaires = <IQuestionaireQuestionObject>{
      id: (JSON.parse(responseData)?.question).id,
      question: (JSON.parse(responseData)?.question).question,
      multiple: (JSON.parse(responseData)?.question).multiple,
      answers: JSON.parse((JSON.parse(responseData)?.question).answer_options),
      language: (JSON.parse(responseData)?.question).language,
      global_question_id:
        (JSON.parse(responseData)?.question).global_question_id,
      global_questionaire_id:
        (JSON.parse(responseData)?.question).global_questionaire_id,
      page_title: (JSON.parse(responseData)?.question).page_title,
    };
  }

  return newQuestionaires;
};

export const httpErrorHandler = (error) => {
  if (error === null) throw new Error("Unrecoverable error!! Error is null!");
  if (axios.isAxiosError(error)) {
    //here we have a type guard check, error inside this if will be treated as AxiosError
    const response = error?.response;
    const request = error?.request;
    const config = error?.config; //here we have access the config used to make the api call (we can make a retry using this conf)

    if (error.code === "ERR_NETWORK") {
      store.dispatch("setError", "connection problems...");
    } else if (error.code === "ERR_CANCELED") {
      store.dispatch("setError", "connection canceled...");
    }
    if (response) {
      //The request was made and the server responded with a status code that falls out of the range of 2xx the http status code mentioned above
      const statusCode = response?.status;
      if (statusCode === 404) {
        store.dispatch(
          "setError",
          "The requested resource does not exist or has been deleted"
        );
      } else if (statusCode === 401) {
        store.dispatch("setError", "Please login to access this resource");
        //redirect user to login
      }
    } else if (request) {
      //The request was made but no response was received, `error.request` is an instance of XMLHttpRequest in the browser and an instance of http.ClientRequest in Node.js
    }
  }
  //Something happened in setting up the request and triggered an Error
  console.error(error.message);
  // store.dispatch("setError", "Unknown error");
};

export const setStyles = async (root) => {
  // Get styles from server
  const response = await axios.get("setup/styles");
  store.dispatch("setLogo", response.data.logo);
  store.dispatch("setTheme", response.data.theme);

  const colors = response?.data.theme;
  for (const colorName in colors) {
    root.$vuetify.theme.themes.light.colors[colorName] = colors[colorName];
  }

  const styles = store.getters.getTheme;
};

export const generateColorScale = (steps: number): string[] => {
  const styles = store.getters.getTheme;
  const startColor = styles.secondary;
  const endColor = "#e8e8e8";

  // Parse the starting and ending colors
  const start = hexToRgb(startColor);
  const end = hexToRgb(endColor);

  // Calculate the step sizes for each color channel
  const stepSize = {
    red: (end.red - start.red) / (steps - 1),
    green: (end.green - start.green) / (steps - 1),
    blue: (end.blue - start.blue) / (steps - 1),
  };

  // Generate the color scale
  const colors: string[] = [];
  for (let i = 0; i < steps; i++) {
    const red = Math.round(start.red + stepSize.red * i);
    const green = Math.round(start.green + stepSize.green * i);
    const blue = Math.round(start.blue + stepSize.blue * i);
    colors.push(rgbToHex(red, green, blue));
  }

  return colors;
};

// Helper functions to convert between hex and RGB colors
function hexToRgb(hex: string): { red: number; green: number; blue: number } {
  const r = parseInt(hex.substring(1, 3), 16);
  const g = parseInt(hex.substring(3, 5), 16);
  const b = parseInt(hex.substring(5, 7), 16);
  return { red: r, green: g, blue: b };
}

function rgbToHex(r: number, g: number, b: number): string {
  const hex = [r, g, b]
    .map((c) => {
      const hex = c.toString(16);
      return hex.length === 1 ? "0" + hex : hex;
    })
    .join("");
  return "#" + hex;
}
