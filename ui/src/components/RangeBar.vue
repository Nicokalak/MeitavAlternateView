<template>
  <div class="container-fluid p-0">
    <div class="row">
      <div class="col-3 pe-0">{{ min }}</div>
      <div class="col-6">
        <input disabled type="range" class="form-range range" :value="value" :min="min" :max="max" />
      </div>
      <div class="col-3 ps-0">{{ max }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
/** Displays a disabled range slider between min and max with current value indicator. */
defineProps<{
    min: number;
    max: number;
    value: number;
}>();
</script>
