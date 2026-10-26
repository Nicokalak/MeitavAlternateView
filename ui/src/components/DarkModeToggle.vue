<template>
  <!-- Headless theme controller — synchronises reactive theme state -->
</template>

<script setup lang="ts">
import { onMounted, watch } from 'vue';
import { theme, setTheme } from '../js/darkmode';

/**
 * Synchronises Bootstrap's data-bs-theme attribute with reactive theme state.
 */
watch(theme, (newTheme) => {
  setTheme(newTheme, false);
});

onMounted(() => {
  setTheme(theme.value, false);
});
</script>
