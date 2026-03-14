<template>
  <div class="auth-layout">
    <section class="auth-card auth-card--wide">
      <div class="auth-card__topbar">
        <p class="auth-card__eyebrow">Vue SPA</p>
        <LanguageSwitcher :model-value="appStore.language" :options="languageOptions" @update:model-value="appStore.setLanguage($event)" />
      </div>
      <h1>{{ $t('auth.registerTitle') }}</h1>
      <p class="auth-card__subtitle">{{ $t('auth.registerSubtitle') }}</p>

      <div class="auth-card__grid">
        <label class="field-control">
          <span class="field-control__label">{{ $t('fields.last_name') }} <strong>*</strong></span>
          <input v-model="form.last_name" class="field-control__input" type="text" />
          <p v-if="errors.last_name" class="field-control__error">{{ errors.last_name }}</p>
        </label>
        <label class="field-control">
          <span class="field-control__label">{{ $t('fields.first_name') }} <strong>*</strong></span>
          <input v-model="form.first_name" class="field-control__input" type="text" />
          <p v-if="errors.first_name" class="field-control__error">{{ errors.first_name }}</p>
        </label>
        <label class="field-control">
          <span class="field-control__label">{{ $t('fields.middle_name') }}</span>
          <input v-model="form.middle_name" class="field-control__input" type="text" />
          <p v-if="errors.middle_name" class="field-control__error">{{ errors.middle_name }}</p>
        </label>
        <label class="field-control">
          <span class="field-control__label">{{ $t('fields.email') }} <strong>*</strong></span>
          <input v-model="form.email" class="field-control__input" type="email" />
          <p v-if="errors.email" class="field-control__error">{{ errors.email }}</p>
        </label>
        <label class="field-control">
          <span class="field-control__label">{{ $t('fields.username') }} <strong>*</strong></span>
          <input v-model="form.username" class="field-control__input" type="text" />
          <p v-if="errors.username" class="field-control__error">{{ errors.username }}</p>
        </label>
        <label class="field-control">
          <span class="field-control__label">{{ $t('auth.password') }} <strong>*</strong></span>
          <input v-model="form.password" class="field-control__input" type="password" />
          <p v-if="errors.password" class="field-control__error">{{ errors.password }}</p>
        </label>
        <label class="field-control">
          <span class="field-control__label">{{ $t('auth.passwordConfirm') }} <strong>*</strong></span>
          <input v-model="form.password_confirm" class="field-control__input" type="password" />
          <p v-if="errors.password_confirm" class="field-control__error">{{ errors.password_confirm }}</p>
        </label>
      </div>

      <p v-if="serverError" class="form-message form-message--error">{{ serverError }}</p>

      <div class="auth-card__actions">
        <button class="button button--primary" type="button" :disabled="submitting" @click="submit">
          {{ submitting ? $t('app.loading') : $t('auth.register') }}
        </button>
        <RouterLink class="button button--ghost" :to="{ name: 'login' }">
          {{ $t('auth.haveAccount') }}
        </RouterLink>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, reactive, ref } from "vue";
import { useI18n } from "vue-i18n";
import { useRouter } from "vue-router";
import * as yup from "yup";

import LanguageSwitcher from "@/components/LanguageSwitcher.vue";
import { useAppStore } from "@/stores/app";
import { useAuthStore } from "@/stores/auth";
import { normalizeApiError } from "@/utils/formatters";
import { validateSchema } from "@/utils/validation";

const appStore = useAppStore();
const authStore = useAuthStore();
const router = useRouter();
const { t } = useI18n();

const form = reactive({
  last_name: "",
  first_name: "",
  middle_name: "",
  email: "",
  username: "",
  password: "",
  password_confirm: "",
});

const errors = ref({});
const serverError = ref("");
const submitting = ref(false);

const languageOptions = computed(() => [
  { value: "ru", label: t("language.ru") },
  { value: "en", label: t("language.en") },
]);

const schema = yup.object({
  last_name: yup.string().trim().required(t("validation.required")),
  first_name: yup.string().trim().required(t("validation.required")),
  middle_name: yup.string().nullable(),
  email: yup.string().trim().email(t("validation.email")).required(t("validation.required")),
  username: yup.string().trim().required(t("validation.required")),
  password: yup.string().trim().min(6, t("validation.minPassword")).required(t("validation.required")),
  password_confirm: yup
    .string()
    .oneOf([yup.ref("password")], t("validation.passwordsMustMatch"))
    .required(t("validation.required")),
});

async function submit() {
  errors.value = await validateSchema(schema, form);
  serverError.value = "";
  if (Object.keys(errors.value).length) {
    return;
  }

  submitting.value = true;
  try {
    await authStore.register({
      ...form,
      middle_name: form.middle_name || null,
    });
    await router.push({ name: "profile" });
  } catch (error) {
    serverError.value = normalizeApiError(error, t("app.unknownError"));
  } finally {
    submitting.value = false;
  }
}
</script>
