import { defineStore } from "pinia";

import { setI18nLocale } from "@/i18n";
import { loadStorageItem, saveStorageItem } from "@/utils/storage";

const UI_STORAGE_KEY = "ui";

function defaultUiState() {
  return {
    language: "ru",
    tableStates: {},
  };
}

export const useAppStore = defineStore("app", {
  state: () => ({
    initialized: false,
    language: "ru",
    tableStates: {},
  }),
  actions: {
    initialize() {
      if (this.initialized) {
        return;
      }

      const savedState = loadStorageItem(UI_STORAGE_KEY, defaultUiState());
      this.language = savedState.language || "ru";
      this.tableStates = savedState.tableStates || {};
      setI18nLocale(this.language);
      this.initialized = true;
    },
    persist() {
      saveStorageItem(UI_STORAGE_KEY, {
        language: this.language,
        tableStates: this.tableStates,
      });
    },
    setLanguage(language) {
      this.language = language;
      setI18nLocale(language);
      this.persist();
    },
    ensureTableState(entityKey, defaultLimit = 20) {
      if (!this.tableStates[entityKey]) {
        this.tableStates[entityKey] = {
          filters: {},
          sortBy: "id",
          sortDir: "asc",
          limit: defaultLimit,
          offset: 0,
        };
      }
      return this.tableStates[entityKey];
    },
    setTableState(entityKey, partialState, defaultLimit = 20) {
      const currentState = this.ensureTableState(entityKey, defaultLimit);
      this.tableStates[entityKey] = {
        ...currentState,
        ...partialState,
      };
      this.persist();
    },
    resetTableState(entityKey, defaultLimit = 20) {
      this.tableStates[entityKey] = {
        filters: {},
        sortBy: "id",
        sortDir: "asc",
        limit: defaultLimit,
        offset: 0,
      };
      this.persist();
    },
  },
});
