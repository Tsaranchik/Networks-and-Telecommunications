const PREFIX = "stipend.frontend";

export function loadStorageItem(key, fallbackValue) {
  try {
    const raw = window.localStorage.getItem(`${PREFIX}.${key}`);
    return raw ? JSON.parse(raw) : fallbackValue;
  } catch {
    return fallbackValue;
  }
}

export function saveStorageItem(key, value) {
  window.localStorage.setItem(`${PREFIX}.${key}`, JSON.stringify(value));
}

export function removeStorageItem(key) {
  window.localStorage.removeItem(`${PREFIX}.${key}`);
}
