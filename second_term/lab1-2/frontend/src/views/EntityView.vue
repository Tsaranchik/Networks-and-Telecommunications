<template>
  <div v-if="!config" class="center-layout">
    <ErrorState title="404" :message="$t('table.empty')" />
  </div>

  <div v-else class="entity-page">
    <FiltersPanel
      :title="$t(`entities.${config.key}`)"
      :fields="config.filterFields"
      :filters="filters"
      :lookups="lookups"
      @update:filters="filters = $event"
      @submit="applyFilters"
      @reset="resetFilters"
    />

    <ErrorState
      v-if="errorMessage"
      :title="$t('app.unknownError')"
      :message="errorMessage"
      :retry-label="$t('app.retry')"
      @retry="loadRows"
    />

    <DataTableCard
      v-else
      :title="$t(`entities.${config.key}`)"
      :columns="config.columns"
      :rows="rows"
      :total="total"
      :limit="limit"
      :offset="offset"
      :sort-by="sortBy"
      :sort-dir="sortDir"
      :loading="loading"
      @create="openCreateDialog"
      @edit="openEditDialog"
      @delete="removeRow"
      @sort="changeSort"
      @change-page="changePage"
      @change-limit="changeLimit"
    />

    <CrudDialog
      :open="dialogOpen"
      :title="dialogTitle"
      :fields="config.formFields"
      :model-value="formValues"
      :errors="formErrors"
      :lookups="lookups"
      :saving="saving"
      @update:model-value="formValues = $event"
      @save="saveDialog"
      @close="closeDialog"
    />
  </div>
</template>

<script setup>
import { computed, ref, watch } from "vue";
import { useI18n } from "vue-i18n";
import { useRoute } from "vue-router";

import { createEntity, deleteEntity, fetchCollection, updateEntity } from "@/api/resources";
import CrudDialog from "@/components/CrudDialog.vue";
import DataTableCard from "@/components/DataTableCard.vue";
import ErrorState from "@/components/ErrorState.vue";
import FiltersPanel from "@/components/FiltersPanel.vue";
import { useAutoRefresh } from "@/composables/useAutoRefresh";
import { entityConfigs } from "@/config/entities";
import { useAppStore } from "@/stores/app";
import { useAuthStore } from "@/stores/auth";
import { normalizeApiError } from "@/utils/formatters";
import { validateSchema } from "@/utils/validation";

const route = useRoute();
const { t } = useI18n();

const appStore = useAppStore();
const authStore = useAuthStore();

const rows = ref([]);
const total = ref(0);
const loading = ref(false);
const saving = ref(false);
const errorMessage = ref("");
const lookups = ref({});
const filters = ref({});
const sortBy = ref("id");
const sortDir = ref("asc");
const limit = ref(authStore.defaultPageSize);
const offset = ref(0);
const dialogOpen = ref(false);
const editingRow = ref(null);
const formValues = ref({});
const formErrors = ref({});

const entityKey = computed(() => String(route.params.entityKey || ""));
const config = computed(() => entityConfigs[entityKey.value] || null);

const dialogTitle = computed(() =>
  editingRow.value ? t("table.editDialog") : t("table.createDialog"),
);

function createEmptyValues(definition) {
  return definition.reduce((accumulator, field) => {
    accumulator[field.key] = field.type === "text" || field.type === "textarea" ? "" : null;
    return accumulator;
  }, {});
}

function syncTableState() {
  if (!config.value) {
    return;
  }

  const storedState = appStore.ensureTableState(entityKey.value, authStore.defaultPageSize);
  filters.value = {
    ...createEmptyValues(config.value.filterFields),
    ...storedState.filters,
  };
  sortBy.value = storedState.sortBy;
  sortDir.value = storedState.sortDir;
  limit.value = storedState.limit;
  offset.value = storedState.offset;
}

function persistTableState() {
  appStore.setTableState(
    entityKey.value,
    {
      filters: filters.value,
      sortBy: sortBy.value,
      sortDir: sortDir.value,
      limit: limit.value,
      offset: offset.value,
    },
    authStore.defaultPageSize,
  );
}

async function loadLookups() {
  if (!config.value) {
    return;
  }

  const definitions = [...config.value.filterFields, ...config.value.formFields];
  const uniqueLookupFields = definitions.filter((field, index, collection) => {
    return field.lookup && collection.findIndex((candidate) => candidate.key === field.key) === index;
  });

  const nextLookups = {};
  for (const field of uniqueLookupFields) {
    const { items } = await fetchCollection(field.lookup.endpoint, {
      limit: 100,
      sort_by: "id",
      sort_dir: "asc",
    });
    nextLookups[field.key] = items.map((item) => ({
      value: item[field.lookup.valueKey],
      label: item[field.lookup.labelKey],
    }));
  }
  lookups.value = nextLookups;
}

function buildQueryParams() {
  const params = {
    limit: limit.value,
    offset: offset.value,
    sort_by: sortBy.value,
    sort_dir: sortDir.value,
  };

  Object.entries(filters.value).forEach(([key, value]) => {
    if (value !== null && value !== undefined && value !== "") {
      params[key] = value;
    }
  });

  return params;
}

async function loadRows() {
  if (!config.value) {
    return;
  }

  loading.value = true;
  errorMessage.value = "";

  try {
    const response = await fetchCollection(config.value.endpoint, buildQueryParams());
    rows.value = response.items;
    total.value = response.total;
  } catch (error) {
    errorMessage.value = normalizeApiError(error, t("app.unknownError"));
  } finally {
    loading.value = false;
  }
}

function openCreateDialog() {
  editingRow.value = null;
  formValues.value = createEmptyValues(config.value.formFields);
  formErrors.value = {};
  dialogOpen.value = true;
}

function openEditDialog(row) {
  editingRow.value = row;
  formValues.value = config.value.formFields.reduce((accumulator, field) => {
    accumulator[field.key] = row[field.key] ?? null;
    return accumulator;
  }, {});
  formErrors.value = {};
  dialogOpen.value = true;
}

function closeDialog() {
  dialogOpen.value = false;
  formErrors.value = {};
}

function normalizePayload(values) {
  return Object.fromEntries(
    Object.entries(values).map(([key, value]) => [key, value === "" ? null : value]),
  );
}

async function saveDialog() {
  formErrors.value = await validateSchema(config.value.schema(t), formValues.value);
  if (Object.keys(formErrors.value).length) {
    return;
  }

  saving.value = true;
  try {
    const payload = normalizePayload(formValues.value);
    if (editingRow.value) {
      await updateEntity(config.value.endpoint, editingRow.value.id, payload);
    } else {
      await createEntity(config.value.endpoint, payload);
    }
    dialogOpen.value = false;
    await loadLookups();
    await loadRows();
  } catch (error) {
    formErrors.value = {
      form: normalizeApiError(error, t("app.unknownError")),
    };
  } finally {
    saving.value = false;
  }
}

async function removeRow(row) {
  if (!window.confirm(t("table.deleteConfirm"))) {
    return;
  }
  try {
    await deleteEntity(config.value.endpoint, row.id);
    await loadRows();
  } catch (error) {
    errorMessage.value = normalizeApiError(error, t("app.unknownError"));
  }
}

async function applyFilters() {
  offset.value = 0;
  persistTableState();
  await loadRows();
}

async function resetFilters() {
  filters.value = createEmptyValues(config.value.filterFields);
  offset.value = 0;
  appStore.resetTableState(entityKey.value, authStore.defaultPageSize);
  syncTableState();
  await loadRows();
}

async function changeSort(nextSortKey) {
  if (sortBy.value === nextSortKey) {
    sortDir.value = sortDir.value === "asc" ? "desc" : "asc";
  } else {
    sortBy.value = nextSortKey;
    sortDir.value = "asc";
  }
  persistTableState();
  await loadRows();
}

async function changePage(nextPage) {
  offset.value = (nextPage - 1) * limit.value;
  persistTableState();
  await loadRows();
}

async function changeLimit(nextLimit) {
  limit.value = nextLimit;
  offset.value = 0;
  persistTableState();
  await loadRows();
}

watch(
  config,
  async (nextConfig) => {
    if (!nextConfig) {
      return;
    }
    syncTableState();
    await loadLookups();
    await loadRows();
  },
  { immediate: true },
);

useAutoRefresh(
  loadRows,
  computed(() => authStore.autoRefreshSeconds * 1000),
  computed(() => Boolean(config.value)),
);
</script>
