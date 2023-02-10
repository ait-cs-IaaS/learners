import router from "@/router";
import { store } from "@/store";
import ITabObject from "@/types/index";
import ymlconfig from "../../../frontend_config.yml";

export const newTabObject = (options?: Partial<ITabObject>): ITabObject => {
  const defaultValue: ITabObject = {
    id: "",
    icon: "",
    tooltip: "",
    type: "",
    target: "",
    url: "",
    admin: false,
    badgevalue: 0,
  };

  let newTab = {
    ...defaultValue,
    ...options,
  };

  if (!newTab.icon) newTab.icon = defaultIcon(newTab);
  if (!newTab.tooltip) newTab.tooltip = newTab.id.replace(/[^a-zA-Z0-9]/g, " ");

  return newTab;
};

export const generateTabs = (rawtabs) => {
  // let tabs = (rawtabs || []).map((tab) => {
  //   return {...tab, type: "default"}
  // })

  // let default_tabs = (ymlconfig.default_tabs || []).map((tab) => {
  //   return {...tab, type: "default", url: `http://localhost:5000/statics/hugo/participant/en/${tab.id}`}
  // })
  // console.debug(default_tabs)
  // let staticsites_tabs = (ymlconfig.staticsites_tabs || []).map((tab) => {
  //   return {...tab, type: "static"}
  // })
  // let client_tabs = (ymlconfig.client_tabs || []).map((tab, index) => {
  //   return {
  //       ...tab,
  //       type: "client",
  //       badgevalue: (ymlconfig.client_tabs.length > 1) ? (index + 1) : 0
  //   }
  // })

  // let mergedList = [].concat(default_tabs, client_tabs, staticsites_tabs);

  let tabs = (rawtabs || []).map((newtab) => {
    return newTabObject(newtab);
  });

  console.log("tabs");
  console.log(tabs);

  return tabs;
};

function defaultIcon(newTab) {
  // default
  if (newTab.type === "default") {
    switch (newTab.id) {
      case "documentation":
        return "mdi-file-document-outline";
      case "exercises":
        return "mdi-play-circle-outline";
      case "presentations":
        return "mdi-presentation";
    }
  }
  // admin
  else if (newTab.type === "admin") {
    return "mdi-shield-crown-outline";
  }
  // clients
  else if (newTab.type === "client") {
    return "mdi-monitor";
  }
  // staticsites
  else if (newTab.type === "static") {
    switch (newTab.id) {
      case "mitre":
        return "mdi-alpha-m-box-outline";
      case "drawio":
        return "mdi-graph-outline";
      default:
        return "mdi-web";
    }
  }
  return "mdi-border-none-variant";
}
