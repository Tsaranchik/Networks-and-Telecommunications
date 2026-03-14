<template>
  <div v-if="open" class="dialog-overlay" @click="$emit('close')">
    <div class="dialog dialog--preview" @click.stop>
      <header class="dialog__header">
        <div>
          <p class="dialog__eyebrow">{{ title }}</p>
          <h3>{{ $t('app.preview') }}</h3>
        </div>
        <button class="button button--ghost" type="button" @click="$emit('close')">
          {{ $t('app.close') }}
        </button>
      </header>

      <div class="preview-card">
        <img v-if="isImage" :src="mediaUrl" alt="preview" class="preview-card__media" />
        <video v-else controls class="preview-card__media">
          <source :src="mediaUrl" />
        </video>
      </div>

      <div class="dialog__footer">
        <button
          v-if="removable"
          class="button button--danger"
          type="button"
          @click="$emit('remove')"
        >
          {{ $t('app.removeFile') }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from "vue";

const props = defineProps({
  open: {
    type: Boolean,
    required: true,
  },
  mediaUrl: {
    type: String,
    default: "",
  },
  title: {
    type: String,
    default: "",
  },
  removable: {
    type: Boolean,
    default: false,
  },
});

defineEmits(["close", "remove"]);

const isImage = computed(() => /\.(png|jpe?g|gif|svg|webp)$/i.test(props.mediaUrl));
</script>
