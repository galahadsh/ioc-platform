import ChangePasswordView from "@/views/ChangePasswordView.vue";


import {
  createRouter,
  createWebHistory,
} from "vue-router";

import LoginView from "@/views/LoginView.vue";
import { useAuthStore } from "@/stores/auth.store";

import DefaultLayout from
  "@/layouts/DefaultLayout.vue";

import DashboardView from
  "@/views/DashboardView.vue";

import ExplorerView from
  "@/views/ExplorerView.vue";

import DocumentsView from
  "@/features/documents/views/DocumentsView.vue";

const EmptyView = (title) => ({
  name: `${title.replaceAll(" ", "")}View`,

  template: `
    <section class="temporary-view">
      <span>MODULE</span>
      <h1>${title}</h1>
      <p>
        Este módulo será implementado
        en el siguiente sprint.
      </p>
    </section>
  `,
});

const router = createRouter({
  history: createWebHistory(),

  routes: [
    {
      path: "/change-password",
      name: "change-password",
      component: ChangePasswordView,
    },


    {
      path: "/login",
      name: "login",
      component: LoginView,
      meta: { public: true },
    },

    {
      path: "/",
      component: DefaultLayout,

      children: [
        {
          path: "",
          name: "dashboard",
          component: DashboardView,
        },
        {
          path: "documents",
          name: "documents",
          component: DocumentsView,
        },
        {
          path: "explorer",
          name: "explorer",
          component: ExplorerView,
        },
        {
          path: "campaigns",
          name: "campaigns",
          component:
            EmptyView("Campaigns"),
        },
        {
          path: "malware",
          name: "malware",
          component:
            EmptyView("Malware"),
        },
        {
          path: "actors",
          name: "actors",
          component:
            EmptyView("Threat Actors"),
        },
        {
          path: "cases",
          name: "cases",
          component:
            EmptyView("Cases"),
        },
        {
          path: "reports",
          name: "reports",
          component:
            EmptyView("Reports"),
        },
      ],
    },

    {
      path: "/:pathMatch(.*)*",
      redirect: "/",
    },
  ],
});


router.beforeEach((to) => {
  const auth = useAuthStore();

  if (!to.meta.public && !auth.isAuthenticated) {
    return {
      name: "login",
      query: { redirect: to.fullPath },
    };
  }

  if (
    auth.isAuthenticated &&
    auth.mustChangePassword &&
    to.path !== "/change-password"
  ) {
    return "/change-password";
  }

  if (to.name === "login" && auth.isAuthenticated) {
    return "/";
  }

  return true;
});

export default router;
