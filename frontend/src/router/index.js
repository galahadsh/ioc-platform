


import {
  createRouter,
  createWebHistory,
} from "vue-router";


import { useAuthStore } from "@/stores/auth.store";









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
      component: () => import("@/views/ChangePasswordView.vue"),
    },


    {
      path: "/login",
      name: "login",
      component: () => import("@/views/LoginView.vue"),
      meta: { public: true },
    },

    {
      path: "/",
      component: () => import("@/layouts/DefaultLayout.vue"),

      children: [
        {
          path: "",
          name: "dashboard",
          component: () => import("@/views/DashboardView.vue"),
        },
        {
          path: "documents",
          name: "documents",
          component: () => import("@/features/documents/views/DocumentsView.vue"),
        },
        {
          path: "explorer",
          name: "explorer",
          component: () => import("@/views/ExplorerView.vue"),
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
