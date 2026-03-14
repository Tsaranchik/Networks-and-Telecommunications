import { createRouter, createWebHistory } from "vue-router";

import AppShell from "@/components/AppShell.vue";
import EntityView from "@/views/EntityView.vue";
import LoginView from "@/views/LoginView.vue";
import NotFoundView from "@/views/NotFoundView.vue";
import ProfileView from "@/views/ProfileView.vue";
import RegisterView from "@/views/RegisterView.vue";
import { useAuthStore } from "@/stores/auth";

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: "/",
      redirect: "/profile",
    },
    {
      path: "/login",
      name: "login",
      component: LoginView,
      meta: {
        public: true,
      },
    },
    {
      path: "/register",
      name: "register",
      component: RegisterView,
      meta: {
        public: true,
      },
    },
    {
      path: "/",
      component: AppShell,
      meta: {
        requiresAuth: true,
      },
      children: [
        {
          path: "profile",
          name: "profile",
          component: ProfileView,
          meta: {
            requiresAuth: true,
          },
        },
        {
          path: "tables/:entityKey",
          name: "entity",
          component: EntityView,
          props: true,
          meta: {
            requiresAuth: true,
          },
        },
      ],
    },
    {
      path: "/:pathMatch(.*)*",
      name: "not-found",
      component: NotFoundView,
    },
  ],
});

router.beforeEach((to) => {
  const authStore = useAuthStore();

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    return {
      name: "login",
      query: {
        redirect: to.fullPath,
      },
    };
  }

  if (to.meta.public && authStore.isAuthenticated) {
    return { name: "profile" };
  }

  return true;
});
