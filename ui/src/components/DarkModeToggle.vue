<template>
  <!-- Dark mode toggle renders no DOM — it only manages theme state reactively -->
</template>

<script setup>
import { onMounted, watch } from 'vue';
import { theme, setTheme, getPreferredTheme } from '../js/darkmode.js';

/**
 * Headless component that synchronises Bootstrap's data-bs-theme attribute
 * with the reactive theme state exposed by darkmode.js.
 */
watch(theme, (newTheme) => {
  if (newTheme === 'auto' && window.matchMedia('(prefers-color-scheme: dark)').matches) {
    document.documentElement.setAttribute('data-bs-theme', 'dark');
  } else {
    document.documentElement.setAttribute('data-bs-theme', newTheme);
  }
  localStorage.setItem('theme', newTheme);
});

onMounted(() => {
  setTheme(getPreferredTheme());
});
</script>
