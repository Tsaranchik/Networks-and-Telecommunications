<template>
  <div class="center-layout">
    <ErrorState
      title="404"
      :message="$t('app.noData')"
      :retry-label="$t('app.close')"
      @retry="$router.push({ name: 'profile' })"
    />
  </div>
</template>

<script setup>
import ErrorState from "@/components/ErrorState.vue";
</script>
