import { defineStore } from "pinia";

import { http, publicHttp } from "@/api/client";
import { useAppStore } from "@/stores/app";
import { clearSession, loadSession, saveSession } from "@/utils/session";

function defaultSession() {
  return {
    accessToken: "",
    refreshToken: "",
    user: null,
  };
}

let sessionUpdatedHandler = null;
let sessionClearedHandler = null;

export const useAuthStore = defineStore("auth", {
  state: () => ({
    initialized: false,
    accessToken: "",
    refreshToken: "",
    user: null,
  }),
  getters: {
    isAuthenticated: (state) => Boolean(state.accessToken),
    defaultPageSize: (state) => state.user?.default_page_size || 20,
    autoRefreshSeconds: (state) => state.user?.auto_refresh_seconds || 0,
    interfaceLanguage: (state) => state.user?.default_language || "ru",
    fullName: (state) => state.user?.full_name || state.user?.username || "",
  },
  actions: {
    initialize() {
      if (this.initialized) {
        return;
      }
      this.syncWithStorage(loadSession());
      sessionUpdatedHandler = (event) => this.syncWithStorage(event.detail);
      sessionClearedHandler = () => this.syncWithStorage(defaultSession());
      window.addEventListener("session:updated", sessionUpdatedHandler);
      window.addEventListener("session:cleared", sessionClearedHandler);
      this.initialized = true;

      if (this.accessToken && !this.user) {
        this.fetchProfile().catch(() => {
          this.logout();
        });
      }
    },
    syncWithStorage(session) {
      this.accessToken = session.accessToken || "";
      this.refreshToken = session.refreshToken || "";
      this.user = session.user || null;

      const appStore = useAppStore();
      if (this.user?.default_language) {
        appStore.setLanguage(this.user.default_language);
      }
    },
    applyAuthResponse(data) {
      const session = {
        accessToken: data.access_token,
        refreshToken: data.refresh_token,
        user: data.user,
      };
      saveSession(session);
      this.syncWithStorage(session);
    },
    async login(credentials) {
      const form = new URLSearchParams();
      form.set("username", credentials.username);
      form.set("password", credentials.password);

      const response = await publicHttp.post("/auth/token", form, {
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
      });
      this.applyAuthResponse(response.data);
      return response.data;
    },
    async register(payload) {
      const response = await publicHttp.post("/auth/register", payload);
      this.applyAuthResponse(response.data);
      return response.data;
    },
    async fetchProfile() {
      const response = await http.get("/auth/me");
      const session = loadSession();
      saveSession({
        ...session,
        user: response.data,
      });
      this.syncWithStorage({
        ...session,
        user: response.data,
      });
      return response.data;
    },
    async updateProfile(payload) {
      const response = await http.put("/auth/me", payload);
      const session = loadSession();
      saveSession({
        ...session,
        user: response.data,
      });
      this.syncWithStorage({
        ...session,
        user: response.data,
      });
      return response.data;
    },
    async changePassword(payload) {
      await http.post("/auth/change-password", payload);
      this.logout();
    },
    async persistLanguage(language) {
      const appStore = useAppStore();
      appStore.setLanguage(language);
      if (!this.isAuthenticated) {
        return;
      }
      await this.updateProfile({
        default_language: language,
      });
    },
    logout() {
      clearSession();
      this.syncWithStorage(defaultSession());
    },
  },
});
