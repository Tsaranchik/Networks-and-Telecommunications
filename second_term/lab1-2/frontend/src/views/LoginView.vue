<template>
  <div class="auth-layout">
    <section class="auth-card">
      <div class="auth-card__topbar">
        <p class="auth-card__eyebrow">Vue SPA</p>
        <LanguageSwitcher :model-value="appStore.language" :options="languageOptions" @update:model-value="appStore.setLanguage($event)" />
      </div>
      <h1>{{ $t('auth.loginTitle') }}</h1>
      <p class="auth-card__subtitle">{{ $t('auth.loginSubtitle') }}</p>

      <label class="field-control">
        <span class="field-control__label">{{ $t('auth.username') }} <strong>*</strong></span>
        <input v-model="form.username" class="field-control__input" type="text" />
        <p v-if="errors.username" class="field-control__error">{{ errors.username }}</p>
      </label>

      <label class="field-control">
        <span class="field-control__label">{{ $t('auth.password') }} <strong>*</strong></span>
        <input v-model="form.password" class="field-control__input" type="password" />
        <p v-if="errors.password" class="field-control__error">{{ errors.password }}</p>
      </label>

      <p v-if="serverError" class="form-message form-message--error">{{ serverError }}</p>

      <div class="auth-card__actions">
        <button class="button button--primary" type="button" :disabled="submitting" @click="submit">
          {{ submitting ? $t('app.loading') : $t('auth.enter') }}
        </button>
        <RouterLink class="button button--ghost" :to="{ name: 'register' }">
          {{ $t('auth.noAccount') }}
        </RouterLink>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, reactive, ref } from "vue";
import { useI18n } from "vue-i18n";
import { useRoute, useRouter } from "vue-router";
import * as yup from "yup";

import LanguageSwitcher from "@/components/LanguageSwitcher.vue";
import { useAppStore } from "@/stores/app";
import { useAuthStore } from "@/stores/auth";
import { normalizeApiError } from "@/utils/formatters";
import { validateSchema } from "@/utils/validation";

const appStore = useAppStore();
const authStore = useAuthStore();
const route = useRoute();
const router = useRouter();
const { t } = useI18n();

const form = reactive({
  username: "",
  password: "",
});

const errors = ref({});
const serverError = ref("");
const submitting = ref(false);

const languageOptions = computed(() => [
  { value: "ru", label: t("language.ru") },
  { value: "en", label: t("language.en") },
]);

const schema = yup.object({
  username: yup.string().trim().required(t("validation.required")),
  password: yup.string().trim().required(t("validation.required")),
});

async function submit() {
  errors.value = await validateSchema(schema, form);
  serverError.value = "";
  if (Object.keys(errors.value).length) {
    return;
  }

  submitting.value = true;
  try {
    await authStore.login(form);
    await router.push(route.query.redirect || { name: "profile" });
  } catch (error) {
    serverError.value = normalizeApiError(error, t("app.unknownError"));
  } finally {
    submitting.value = false;
  }
}
</script>
