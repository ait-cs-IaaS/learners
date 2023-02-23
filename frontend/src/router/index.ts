// Composables
import { createRouter, createWebHistory } from "vue-router";
import { store } from "@/store";
import axios from "axios";

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

  // Authenticate using the backend
  let auth = await axios.get("authentication");
  if (authRequired && !auth.data.user) {
    return "/login";
  }

  // Get tabs from backend
  await store.dispatch("getTabsFromServer");
});

export default router;
