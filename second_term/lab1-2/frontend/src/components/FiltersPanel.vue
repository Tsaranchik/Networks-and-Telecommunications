<template>
  <section class="filters-panel">
    <header class="filters-panel__header">
      <div>
        <p class="filters-panel__eyebrow">{{ $t('app.filters') }}</p>
        <h3>{{ title }}</h3>
      </div>
      <div class="filters-panel__actions">
        <button class="button button--ghost" type="button" @click="$emit('reset')">
          {{ $t('app.reset') }}
        </button>
        <button class="button button--primary" type="button" @click="$emit('submit')">
          {{ $t('app.apply') }}
        </button>
      </div>
    </header>

    <div class="filters-panel__grid">
      <FieldControl
        v-for="field in fields"
        :key="field.key"
        compact
        :field="field"
        :label="$t(field.labelKey)"
        :model-value="filters[field.key]"
        :options="lookups[field.key] || []"
        @update:model-value="updateField(field.key, $event)"
      />
    </div>
  </section>
</template>

<script setup>
import FieldControl from "@/components/FieldControl.vue";

const props = defineProps({
  title: {
    type: String,
    required: true,
  },
  fields: {
    type: Array,
    required: true,
  },
  filters: {
    type: Object,
    required: true,
  },
  lookups: {
    type: Object,
    default: () => ({}),
  },
});

const emit = defineEmits(["update:filters", "submit", "reset"]);

function updateField(key, value) {
  emit("update:filters", {
    ...props.filters,
    [key]: value,
  });
}
</script>
