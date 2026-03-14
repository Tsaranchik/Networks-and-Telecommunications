<template>
  <div class="shell">
    <aside class="shell__sidebar">
      <div class="shell__brand">
        <p class="shell__eyebrow">Networks Lab</p>
        <h1>{{ $t('app.title') }}</h1>
        <p>{{ $t('app.subtitle') }}</p>
      </div>

      <nav class="shell__nav">
        <RouterLink class="shell__nav-link" :to="{ name: 'profile' }">
          {{ $t('app.profile') }}
        </RouterLink>
        <RouterLink
          v-for="entityKey in entityOrder"
          :key="entityKey"
          class="shell__nav-link"
          :to="{ name: 'entity', params: { entityKey } }"
        >
          {{ $t(`entities.${entityKey}`) }}
        </RouterLink>
      </nav>
    </aside>

    <main class="shell__main">
      <header class="shell__topbar">
        <div>
          <p class="shell__eyebrow">{{ $formatDateValue(new Date(), currentDateLocale) }}</p>
          <h2>{{ currentTitle }}</h2>
        </div>

        <div class="shell__toolbar">
          <LanguageSwitcher
            :model-value="appStore.language"
            :options="languageOptions"
            @update:model-value="changeLanguage"
          />
          <div class="shell__user-card">
            <strong>{{ authStore.fullName }}</strong>
            <span>{{ authStore.user?.username }}</span>
          </div>
          <button class="button button--ghost" type="button" @click="logout">
            {{ $t('app.logout') }}
          </button>
        </div>
      </header>

      <section class="shell__content">
        <RouterView />
      </section>
    </main>
  </div>
</template>

<script setup>
import { computed } from "vue";
import { useI18n } from "vue-i18n";
import { useRoute, useRouter } from "vue-router";

import LanguageSwitcher from "@/components/LanguageSwitcher.vue";
import { entityConfigs, entityOrder } from "@/config/entities";
import { useAppStore } from "@/stores/app";
import { useAuthStore } from "@/stores/auth";

const route = useRoute();
const router = useRouter();
const { t } = useI18n();

const appStore = useAppStore();
const authStore = useAuthStore();

const languageOptions = computed(() => [
  { value: "ru", label: t("language.ru") },
  { value: "en", label: t("language.en") },
]);

const currentTitle = computed(() => {
  if (route.name === "profile") {
    return t("profile.title");
  }
  const entityKey = route.params.entityKey;
  return entityKey && entityConfigs[entityKey] ? t(`entities.${entityKey}`) : t("app.title");
});

const currentDateLocale = computed(() => (appStore.language === "en" ? "en-US" : "ru-RU"));

async function changeLanguage(language) {
  try {
    await authStore.persistLanguage(language);
  } catch {
    // Local language switch still remains active if the profile request fails.
  }
}

function logout() {
  authStore.logout();
  router.push({ name: "login" });
}
</script>
