<template>
  <div class="upload-field">
    <label class="upload-field__dropzone">
      <input class="sr-only" type="file" :accept="accept" @change="handleFileChange" />
      <span class="upload-field__title">{{ label }}</span>
      <span class="upload-field__subtitle">{{ uploading ? `${progress}%` : $t('app.upload') }}</span>
    </label>

    <div v-if="uploading" class="upload-field__progress">
      <span :style="{ width: `${progress}%` }"></span>
    </div>

    <div v-if="resolvedMediaUrl" class="upload-field__actions">
      <button class="button button--ghost" type="button" @click="previewOpen = true">
        {{ $t('app.preview') }}
      </button>
      <button class="button button--ghost-danger" type="button" @click="removeFile">
        {{ $t('app.removeFile') }}
      </button>
    </div>

    <MediaPreviewDialog
      :open="previewOpen"
      :media-url="resolvedMediaUrl"
      :title="label"
      removable
      @close="previewOpen = false"
      @remove="removeFile"
    />
  </div>
</template>

<script setup>
import { computed, ref } from "vue";

import { API_BASE_URL } from "@/api/client";
import { deleteMedia, uploadMedia } from "@/api/resources";
import MediaPreviewDialog from "@/components/MediaPreviewDialog.vue";
import { buildAbsoluteMediaUrl } from "@/utils/formatters";

const props = defineProps({
  modelValue: {
    type: String,
    default: "",
  },
  accept: {
    type: String,
    default: "image/*,video/*",
  },
  label: {
    type: String,
    default: "",
  },
});

const emit = defineEmits(["update:modelValue"]);

const uploading = ref(false);
const progress = ref(0);
const previewOpen = ref(false);

const resolvedMediaUrl = computed(() => buildAbsoluteMediaUrl(API_BASE_URL, props.modelValue));

async function cleanupUploadedFile(fileUrl) {
  if (fileUrl?.startsWith("/uploads/")) {
    try {
      await deleteMedia(fileUrl);
    } catch {
      // Optional cleanup should not block the form.
    }
  }
}

async function handleFileChange(event) {
  const [file] = event.target.files || [];
  if (!file) {
    return;
  }

  uploading.value = true;
  progress.value = 0;

  const previousValue = props.modelValue;
  const formData = new FormData();
  formData.append("file", file);

  try {
    const uploaded = await uploadMedia(formData, (uploadEvent) => {
      if (uploadEvent.total) {
        progress.value = Math.round((uploadEvent.loaded * 100) / uploadEvent.total);
      }
    });
    emit("update:modelValue", uploaded.file_url);
    if (previousValue && previousValue !== uploaded.file_url) {
      await cleanupUploadedFile(previousValue);
    }
  } finally {
    uploading.value = false;
    event.target.value = "";
  }
}

async function removeFile() {
  await cleanupUploadedFile(props.modelValue);
  emit("update:modelValue", null);
  previewOpen.value = false;
}
</script>
