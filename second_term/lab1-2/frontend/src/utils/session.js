import { loadStorageItem, removeStorageItem, saveStorageItem } from "./storage";

const SESSION_KEY = "session";

export function loadSession() {
  return loadStorageItem(SESSION_KEY, {
    accessToken: "",
    refreshToken: "",
    user: null,
  });
}

export function saveSession(session) {
  saveStorageItem(SESSION_KEY, session);
  window.dispatchEvent(
    new CustomEvent("session:updated", {
      detail: session,
    }),
  );
}

export function clearSession() {
  removeStorageItem(SESSION_KEY);
  window.dispatchEvent(new Event("session:cleared"));
}

export function getAccessToken() {
  return loadSession().accessToken;
}

export function getRefreshToken() {
  return loadSession().refreshToken;
}

export function getSessionUser() {
  return loadSession().user;
}
