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

<script setup>
/** Displays a disabled range slider between min and max with current value indicator. */
defineProps({
    min: { type: Number, required: true },
    max: { type: Number, required: true },
    value: { type: Number, required: true },
});
</script>
