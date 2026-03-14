<template>
  <section class="error-state">
    <p class="error-state__eyebrow">System Notice</p>
    <h2>{{ title }}</h2>
    <p>{{ message }}</p>
    <button v-if="retryLabel" class="button button--primary" type="button" @click="$emit('retry')">
      {{ retryLabel }}
    </button>
  </section>
</template>

<script setup>
defineProps({
  title: {
    type: String,
    required: true,
  },
  message: {
    type: String,
    required: true,
  },
  retryLabel: {
    type: String,
    default: "",
  },
});

defineEmits(["retry"]);
</script>
