import {
  createRouter,
  createWebHistory,
} from "vue-router";

import DefaultLayout from
  "@/layouts/DefaultLayout.vue";

import DashboardView from
  "@/views/DashboardView.vue";

import ExplorerView from
  "@/views/ExplorerView.vue";

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
      path: "/",
      component: DefaultLayout,

      children: [
        {
          path: "",
          name: "dashboard",
          component: DashboardView,
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

export default router;
