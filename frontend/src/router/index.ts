// Composables
import { createRouter, createWebHistory } from "vue-router";
import { store } from "@/store";
import axios from "axios";
import { httpErrorHandler } from "@/helpers";

const routes = [
  {
    path: "/",
    component: () => import("@/layouts/default/Default.vue"),
    children: [
      {
        path: "",
        name: "Mainpage",
        component: () => import("@/views/Mainpage.vue"),
      },
    ],
  },
  {
    path: "/login",
    component: () => import("@/layouts/default/Default.vue"),
    children: [
      {
        path: "",
        name: "Login",
        component: () => import("@/views/Login.vue"),
      },
    ],
  },
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  linkActiveClass: "active",
  routes,
});

router.beforeEach(async (to) => {
  // No authorization on public pages
  const publicPages = ["/login"];
  const authRequired = !publicPages.includes(to.path);

  // Get authentication
  if (authRequired) {
    const authenticated = await IsAuthenticated();
    if (!authenticated) return "/login";
  }
});

function IsAuthenticated() {
  // Authenticate using the backend
  return axios
    .get("authentication")
    .then((response) => {
      store.dispatch("setError", "");
      store.dispatch("getTabsFromServer");
      return response.data.user;
    })
    .catch((error) => {
      httpErrorHandler(error);
      store.dispatch("resetTabs");
      return false;
    });
}

export default router;
