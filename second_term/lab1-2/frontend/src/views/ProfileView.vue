<template>
  <section class="profile-page">
    <header class="page-heading">
      <div>
        <p class="page-heading__eyebrow">{{ $t('app.profile') }}</p>
        <h1>{{ $t('profile.title') }}</h1>
      </div>
      <p class="page-heading__subtitle">{{ $t('profile.subtitle') }}</p>
    </header>

    <div class="profile-grid">
      <article class="panel">
        <header class="panel__header">
          <h2>{{ $t('profile.personal') }}</h2>
        </header>

        <div class="panel__body">
          <FieldControl
            v-for="field in personalFields"
            :key="field.key"
            :field="field"
            :label="$t(field.labelKey)"
            :model-value="profileForm[field.key]"
            :error="profileErrors[field.key]"
            :required="field.required"
            @update:model-value="profileForm[field.key] = $event"
          />
        </div>

        <footer class="panel__footer">
          <button class="button button--primary" type="button" :disabled="savingProfile" @click="saveProfile">
            {{ savingProfile ? $t('app.loading') : $t('profile.saveProfile') }}
          </button>
        </footer>
      </article>

      <article class="panel">
        <header class="panel__header">
          <h2>{{ $t('profile.preferences') }}</h2>
        </header>

        <div class="panel__body">
          <FieldControl
            v-for="field in preferenceFields"
            :key="field.key"
            :field="field"
            :label="$t(field.labelKey)"
            :model-value="preferenceForm[field.key]"
            :error="preferenceErrors[field.key]"
            :required="field.required"
            @update:model-value="preferenceForm[field.key] = $event"
          />

          <label class="field-control">
            <span class="field-control__label">{{ $t('profile.language') }} <strong>*</strong></span>
            <LanguageSwitcher
              :model-value="preferenceForm.default_language"
              :options="languageOptions"
              @update:model-value="preferenceForm.default_language = $event"
            />
          </label>
        </div>

        <footer class="panel__footer">
          <button class="button button--primary" type="button" :disabled="savingPreferences" @click="savePreferences">
            {{ savingPreferences ? $t('app.loading') : $t('profile.savePreferences') }}
          </button>
        </footer>
      </article>
    </div>

    <article class="panel">
      <header class="panel__header">
        <h2>{{ $t('auth.changePassword') }}</h2>
      </header>

      <div class="panel__body panel__body--inline">
        <FieldControl
          v-for="field in passwordFields"
          :key="field.key"
          :field="field"
          :label="$t(field.labelKey)"
          :model-value="passwordForm[field.key]"
          :error="passwordErrors[field.key]"
          :required="field.required"
          @update:model-value="passwordForm[field.key] = $event"
        />
      </div>

      <p v-if="feedback" class="form-message">{{ feedback }}</p>

      <footer class="panel__footer">
        <button class="button button--danger" type="button" :disabled="savingPassword" @click="savePassword">
          {{ savingPassword ? $t('app.loading') : $t('auth.changePassword') }}
        </button>
      </footer>
    </article>
  </section>
</template>

<script setup>
import { computed, reactive, ref, watch } from "vue";
import { useI18n } from "vue-i18n";
import { useRouter } from "vue-router";
import * as yup from "yup";

import FieldControl from "@/components/FieldControl.vue";
import LanguageSwitcher from "@/components/LanguageSwitcher.vue";
import { useAuthStore } from "@/stores/auth";
import { normalizeApiError } from "@/utils/formatters";
import { validateSchema } from "@/utils/validation";

const authStore = useAuthStore();
const router = useRouter();
const { t } = useI18n();

const personalFields = [
  { key: "last_name", labelKey: "fields.last_name", type: "text", required: true },
  { key: "first_name", labelKey: "fields.first_name", type: "text", required: true },
  { key: "middle_name", labelKey: "fields.middle_name", type: "text" },
  { key: "email", labelKey: "fields.email", type: "text", required: true },
  { key: "username", labelKey: "fields.username", type: "text", required: true },
];

const preferenceFields = [
  { key: "default_page_size", labelKey: "profile.defaultPageSize", type: "number", required: true, step: "1" },
  { key: "auto_refresh_seconds", labelKey: "profile.autoRefreshSeconds", type: "number", required: true, step: "1" },
];

const passwordFields = [
  { key: "current_password", labelKey: "auth.currentPassword", type: "text", inputType: "password", required: true },
  { key: "new_password", labelKey: "auth.newPassword", type: "text", inputType: "password", required: true },
];

const profileForm = reactive({
  last_name: "",
  first_name: "",
  middle_name: "",
  email: "",
  username: "",
});

const preferenceForm = reactive({
  default_page_size: 20,
  auto_refresh_seconds: 0,
  default_language: "ru",
});

const passwordForm = reactive({
  current_password: "",
  new_password: "",
});

const profileErrors = ref({});
const preferenceErrors = ref({});
const passwordErrors = ref({});
const feedback = ref("");
const savingProfile = ref(false);
const savingPreferences = ref(false);
const savingPassword = ref(false);

const languageOptions = computed(() => [
  { value: "ru", label: t("language.ru") },
  { value: "en", label: t("language.en") },
]);

watch(
  () => authStore.user,
  (user) => {
    if (!user) {
      return;
    }
    Object.assign(profileForm, {
      last_name: user.last_name,
      first_name: user.first_name,
      middle_name: user.middle_name || "",
      email: user.email,
      username: user.username,
    });
    Object.assign(preferenceForm, {
      default_page_size: user.default_page_size,
      auto_refresh_seconds: user.auto_refresh_seconds,
      default_language: user.default_language,
    });
  },
  { immediate: true },
);

const profileSchema = yup.object({
  last_name: yup.string().trim().required(t("validation.required")),
  first_name: yup.string().trim().required(t("validation.required")),
  middle_name: yup.string().nullable(),
  email: yup.string().trim().email(t("validation.email")).required(t("validation.required")),
  username: yup.string().trim().required(t("validation.required")),
});

const preferenceSchema = yup.object({
  default_page_size: yup.number().typeError(t("validation.required")).min(5).max(100).required(t("validation.required")),
  auto_refresh_seconds: yup.number().typeError(t("validation.required")).min(0).max(3600).required(t("validation.required")),
  default_language: yup.string().oneOf(["ru", "en"]).required(t("validation.required")),
});

const passwordSchema = yup.object({
  current_password: yup.string().trim().required(t("validation.required")),
  new_password: yup.string().trim().min(6, t("validation.minPassword")).required(t("validation.required")),
});

async function saveProfile() {
  profileErrors.value = await validateSchema(profileSchema, profileForm);
  feedback.value = "";
  if (Object.keys(profileErrors.value).length) {
    return;
  }

  savingProfile.value = true;
  try {
    await authStore.updateProfile({
      ...profileForm,
      middle_name: profileForm.middle_name || null,
    });
    feedback.value = t("app.save");
  } catch (error) {
    feedback.value = normalizeApiError(error, t("app.unknownError"));
  } finally {
    savingProfile.value = false;
  }
}

async function savePreferences() {
  preferenceErrors.value = await validateSchema(preferenceSchema, preferenceForm);
  feedback.value = "";
  if (Object.keys(preferenceErrors.value).length) {
    return;
  }

  savingPreferences.value = true;
  try {
    await authStore.updateProfile(preferenceForm);
    feedback.value = t("app.save");
  } catch (error) {
    feedback.value = normalizeApiError(error, t("app.unknownError"));
  } finally {
    savingPreferences.value = false;
  }
}

async function savePassword() {
  passwordErrors.value = await validateSchema(passwordSchema, passwordForm);
  feedback.value = "";
  if (Object.keys(passwordErrors.value).length) {
    return;
  }

  savingPassword.value = true;
  try {
    await authStore.changePassword(passwordForm);
    feedback.value = t("auth.passwordChanged");
    await router.push({ name: "login" });
  } catch (error) {
    feedback.value = normalizeApiError(error, t("app.unknownError"));
  } finally {
    savingPassword.value = false;
  }
}
</script>
