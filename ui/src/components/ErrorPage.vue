<template>
  <div class="text-center mt-5" role="alert">
    <h1>Error {{ code }} - {{ title }}</h1>
    <p>{{ message }}</p>
  </div>
</template>

<script setup lang="ts">
/** Full-page error state shown in place of the app. */
defineProps<{
  code: number;
  title: string;
  message: string;
}>();
</script>
