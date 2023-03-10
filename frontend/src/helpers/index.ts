import { store } from "@/store";
import { INotificationObject, ITabObject } from "@/types/index";
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
        message: `${newNotification?.message}`,
        positions: newNotification?.positions,
      };
    });
  } else {
    newNotifications = <INotificationObject>{
      message: `${JSON.parse(responseData)?.message}`,
      positions: JSON.parse(responseData)?.positions,
    };
  }

  return newNotifications;
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
  console.log(error.message);
  // store.dispatch("setError", "Unknown error");
};
