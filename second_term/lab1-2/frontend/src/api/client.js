import axios from "axios";

import { clearSession, getAccessToken, getRefreshToken, loadSession, saveSession } from "@/utils/session";

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8001";

export const publicHttp = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000,
});

export const http = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000,
});

let refreshPromise = null;

http.interceptors.request.use((config) => {
  const token = getAccessToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

http.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    const errorCode = error?.response?.data?.detail?.code;

    if (
      error?.response?.status === 401 &&
      errorCode === "tokenExpiredException" &&
      !originalRequest?._retry &&
      getRefreshToken()
    ) {
      originalRequest._retry = true;

      refreshPromise ??= publicHttp
        .post("/auth/refresh", {
          refresh_token: getRefreshToken(),
        })
        .then((response) => {
          const previousSession = loadSession();
          saveSession({
            accessToken: response.data.access_token,
            refreshToken: response.data.refresh_token,
            user: response.data.user || previousSession.user,
          });
        })
        .catch((refreshError) => {
          clearSession();
          throw refreshError;
        })
        .finally(() => {
          refreshPromise = null;
        });

      await refreshPromise;
      originalRequest.headers.Authorization = `Bearer ${getAccessToken()}`;
      return http(originalRequest);
    }

    if (error?.response?.status === 401 && errorCode !== "tokenExpiredException") {
      clearSession();
    }

    throw error;
  },
);
