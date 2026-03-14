<template>
  <div class="language-switcher" role="group" aria-label="Language switcher">
    <button
      v-for="option in options"
      :key="option.value"
      class="language-switcher__option"
      :class="{ 'language-switcher__option--active': modelValue === option.value }"
      type="button"
      @click="$emit('update:modelValue', option.value)"
    >
      {{ option.label }}
    </button>
  </div>
</template>

<script setup>
defineProps({
  modelValue: {
    type: String,
    required: true,
  },
  options: {
    type: Array,
    required: true,
  },
});

defineEmits(["update:modelValue"]);
</script>
