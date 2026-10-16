<template>
  <li class="list-group-item border rounded p-2 mb-2 bg-body-tertiary watchlist-item-row shadow-sm">
    <div class="d-flex align-items-center gap-2">
      <div class="flex-grow-1">
        <div class="input-group input-group-sm">
          <span class="input-group-text px-2"><i class="fas fa-tag text-muted"></i></span>
          <input
            type="text"
            class="form-control form-control-sm text-uppercase fw-semibold watchlist-symbol"
            :name="'watchlist-' + item.symbol"
            placeholder="Symbol"
            v-model="item.symbol"
            autocomplete="off"
            autocapitalize="characters"
          />
        </div>
      </div>
      <div class="d-flex gap-1 flex-shrink-0">
        <button
          class="btn btn-sm toggle-item-details"
          :class="hasValues ? 'btn-outline-primary' : 'btn-outline-secondary'"
          type="button"
          :title="hasValues ? 'Hide Qty & Cost' : 'Set Qty & Cost'"
          :aria-expanded="showExtra"
          @click="toggleExtra"
        >
          <i class="fas fa-sliders-h"></i>
        </button>
        <button class="btn btn-sm btn-outline-danger remove-item delete-item" type="button" title="Remove" @click="emit('remove')">
          <i class="fas fa-trash-alt"></i>
        </button>
      </div>
    </div>

    <div class="d-flex gap-2 mt-2 watchlist-extra-fields" v-show="showExtra">
      <div class="flex-fill">
        <div class="input-group input-group-sm">
          <span class="input-group-text px-2">Qty</span>
          <input
            type="number"
            :name="'watchlist-qty-' + item.symbol"
            min="0"
            step="1"
            class="form-control form-control-sm px-2 watchlist-qty"
            placeholder="0"
            v-model="item.qty"
          />
        </div>
      </div>
      <div class="flex-fill">
        <div class="input-group input-group-sm">
          <span class="input-group-text px-2">Cost</span>
          <input
            type="number"
            :name="'watchlist-cost-' + item.symbol"
            min="0"
            step="any"
            class="form-control form-control-sm px-2 watchlist-cost"
            placeholder="0.00"
            v-model="item.cost"
          />
        </div>
      </div>
    </div>
  </li>
</template>

<script setup>
import { ref, computed } from 'vue';

/** Single watchlist row with inline Qty/Cost toggle. */

const props = defineProps({
    item: { type: Object, required: true },
});
const emit = defineEmits(['remove']);

const showExtra = ref(
    (props.item.qty !== '' && Number(props.item.qty) > 0) ||
    (props.item.cost !== '' && Number(props.item.cost) > 0)
);

const hasValues = computed(() => {
    const q = parseInt(props.item.qty, 10);
    const c = parseFloat(props.item.cost);
    return (!isNaN(q) && q > 0) || (!isNaN(c) && c > 0);
});

function toggleExtra() {
    showExtra.value = !showExtra.value;
}
</script>
