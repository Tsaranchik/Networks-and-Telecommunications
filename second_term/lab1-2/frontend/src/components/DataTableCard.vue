<template>
  <section class="table-card">
    <header class="table-card__header">
      <div>
        <p class="table-card__eyebrow">{{ $t('table.title') }}</p>
        <h2>{{ title }}</h2>
      </div>
      <button class="button button--primary" type="button" @click="$emit('create')">
        {{ $t('app.create') }}
      </button>
    </header>

    <div class="table-card__meta">
      <span>{{ $t('app.searchResult', { count: total }) }}</span>
      <label class="table-card__page-size">
        <span>{{ $t('app.rowsPerPage') }}</span>
        <select :value="limit" @change="$emit('change-limit', Number($event.target.value))">
          <option v-for="pageSize in [10, 20, 50, 100]" :key="pageSize" :value="pageSize">
            {{ pageSize }}
          </option>
        </select>
      </label>
    </div>

    <div class="table-card__scroll">
      <table class="data-table">
        <colgroup>
          <col class="data-table__col data-table__col--index" />
          <col
            v-for="column in columns"
            :key="`col-${column.key}`"
            :class="[
              'data-table__col',
              column.type === 'number' ? 'data-table__col--number' : 'data-table__col--text',
            ]"
          />
          <col class="data-table__col data-table__col--actions" />
        </colgroup>
        <thead>
          <tr>
            <th class="data-table__index">#</th>
            <th
              v-for="column in columns"
              :key="column.key"
              :class="[
                column.sortable && 'data-table__sortable',
                column.type === 'number' ? 'data-table__header--number' : 'data-table__header--text',
              ]"
              @click="column.sortable && $emit('sort', column.key)"
            >
              <span>{{ $t(column.labelKey) }}</span>
              <small v-if="sortBy === column.key">{{ sortDir === 'asc' ? '↑' : '↓' }}</small>
            </th>
            <th class="data-table__actions-heading">{{ $t('app.edit') }}</th>
          </tr>
        </thead>
        <tbody v-if="rows.length">
          <tr v-for="(row, index) in rows" :key="row.id">
            <td class="data-table__index">{{ createSequentialIndex(offset, index) }}</td>
            <td
              v-for="column in columns"
              :key="column.key"
              :class="{
                'data-table__cell--text': column.type === 'text' || column.type === 'select',
                'data-table__cell--number': column.type === 'number',
              }"
            >
              {{ renderCell(row, column) }}
            </td>
            <td class="data-table__actions">
              <div class="data-table__actions-group">
                <button class="button button--ghost" type="button" @click="$emit('edit', row)">
                  {{ $t('app.edit') }}
                </button>
                <button class="button button--ghost-danger" type="button" @click="$emit('delete', row)">
                  {{ $t('app.delete') }}
                </button>
              </div>
            </td>
          </tr>
        </tbody>
        <tbody v-else>
          <tr>
            <td :colspan="columns.length + 2" class="data-table__empty">
              {{ loading ? $t('app.loading') : $t('table.empty') }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <footer class="table-card__footer">
      <button class="button button--ghost" type="button" :disabled="page <= 1" @click="$emit('change-page', page - 1)">
        &lt;
      </button>
      <span>{{ $t('app.page') }} {{ page }} / {{ totalPages }}</span>
      <button
        class="button button--ghost"
        type="button"
        :disabled="page >= totalPages"
        @click="$emit('change-page', page + 1)"
      >
        &gt;
      </button>
    </footer>
  </section>
</template>

<script setup>
import { computed } from "vue";
import { useI18n } from "vue-i18n";

import { createSequentialIndex, formatNumber } from "@/utils/formatters";

const props = defineProps({
  title: {
    type: String,
    required: true,
  },
  columns: {
    type: Array,
    required: true,
  },
  rows: {
    type: Array,
    required: true,
  },
  total: {
    type: Number,
    default: 0,
  },
  limit: {
    type: Number,
    default: 20,
  },
  offset: {
    type: Number,
    default: 0,
  },
  sortBy: {
    type: String,
    default: "id",
  },
  sortDir: {
    type: String,
    default: "asc",
  },
  loading: {
    type: Boolean,
    default: false,
  },
});

defineEmits(["create", "edit", "delete", "sort", "change-page", "change-limit"]);

const { locale } = useI18n();

const page = computed(() => Math.floor(props.offset / props.limit) + 1);
const totalPages = computed(() => Math.max(1, Math.ceil(props.total / props.limit)));

function renderCell(row, column) {
  const rawValue = column.displayKey ? row[column.displayKey] || row[column.key] : row[column.key];
  if (column.type === "number") {
    return formatNumber(rawValue, locale.value);
  }
  return rawValue || "—";
}
</script>
