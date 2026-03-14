<template>
  <label class="field-control" :class="{ 'field-control--compact': compact }">
    <span class="field-control__label">
      {{ label }}
      <strong v-if="required">*</strong>
    </span>

    <input
      v-if="field.type === 'text' || field.type === 'number'"
      class="field-control__input"
      :type="field.inputType || (field.type === 'number' ? 'number' : 'text')"
      :step="field.step || 'any'"
      :value="modelValue ?? ''"
      @input="emitValue($event.target.value)"
    />

    <textarea
      v-else-if="field.type === 'textarea'"
      class="field-control__input field-control__input--textarea"
      :value="modelValue ?? ''"
      @input="$emit('update:modelValue', $event.target.value)"
    />

    <select
      v-else-if="field.type === 'select'"
      class="field-control__input"
      :value="modelValue ?? ''"
      @change="emitValue($event.target.value)"
    >
      <option value="">{{ placeholder }}</option>
      <option v-for="option in options" :key="option.value" :value="option.value">
        {{ option.label }}
      </option>
    </select>

    <UploadField
      v-else-if="field.type === 'upload'"
      :label="label"
      :model-value="modelValue"
      :accept="field.accept"
      @update:model-value="$emit('update:modelValue', $event)"
    />

    <p v-if="error" class="field-control__error">{{ error }}</p>
  </label>
</template>

<script setup>
import UploadField from "@/components/UploadField.vue";

const props = defineProps({
  field: {
    type: Object,
    required: true,
  },
  label: {
    type: String,
    required: true,
  },
  modelValue: {
    type: [String, Number, null],
    default: "",
  },
  error: {
    type: String,
    default: "",
  },
  options: {
    type: Array,
    default: () => [],
  },
  required: {
    type: Boolean,
    default: false,
  },
  compact: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits(["update:modelValue"]);

const placeholder = "—";

function emitValue(value) {
  if (props.field.type === "number") {
    if (value === "") {
      return emit("update:modelValue", null);
    }
    return emit("update:modelValue", Number(value));
  }

  if (props.field.type === "select") {
    if (value === "") {
      return emit("update:modelValue", null);
    }
    return emit("update:modelValue", Number.isNaN(Number(value)) ? value : Number(value));
  }

  emit("update:modelValue", value);
}
</script>
