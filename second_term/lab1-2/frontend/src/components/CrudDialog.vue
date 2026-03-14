<template>
  <div v-if="open" class="dialog-overlay" @click="$emit('close')">
    <div class="dialog" @click.stop>
      <header class="dialog__header">
        <div>
          <p class="dialog__eyebrow">{{ $t('table.title') }}</p>
          <h3>{{ title }}</h3>
        </div>
        <button class="button button--ghost" type="button" @click="$emit('close')">
          {{ $t('app.close') }}
        </button>
      </header>

      <div class="dialog__body">
        <FieldControl
          v-for="field in fields"
          :key="field.key"
          :field="field"
          :label="$t(field.labelKey)"
          :model-value="modelValue[field.key]"
          :error="errors[field.key]"
          :options="lookups[field.key] || []"
          :required="field.required"
          @update:model-value="updateField(field.key, $event)"
        />
      </div>

      <p v-if="errors.form" class="form-message form-message--error">{{ errors.form }}</p>
      <p class="dialog__hint">{{ $t('app.requiredHint') }}</p>

      <footer class="dialog__footer">
        <button class="button button--ghost" type="button" @click="$emit('close')">
          {{ $t('app.cancel') }}
        </button>
        <button class="button button--primary" type="button" :disabled="saving" @click="$emit('save')">
          {{ saving ? $t('app.loading') : $t('app.save') }}
        </button>
      </footer>
    </div>
  </div>
</template>

<script setup>
import FieldControl from "@/components/FieldControl.vue";

const props = defineProps({
  open: {
    type: Boolean,
    required: true,
  },
  title: {
    type: String,
    required: true,
  },
  fields: {
    type: Array,
    required: true,
  },
  modelValue: {
    type: Object,
    required: true,
  },
  errors: {
    type: Object,
    default: () => ({}),
  },
  lookups: {
    type: Object,
    default: () => ({}),
  },
  saving: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits(["close", "save", "update:modelValue"]);

function updateField(key, value) {
  emit("update:modelValue", {
    ...props.modelValue,
    [key]: value,
  });
}
</script>
