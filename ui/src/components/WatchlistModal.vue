<template>
  <div
    class="modal fade"
    id="editWatchListModal"
    tabindex="-1"
    role="dialog"
    aria-labelledby="editModalLabel"
    aria-hidden="true"
    ref="modalEl"
  >
    <div class="modal-dialog modal-dialog-centered modal-lg modal-dialog-scrollable" role="document">
      <div class="modal-content shadow">
        <div class="modal-header py-2 px-3 bg-body-tertiary">
          <h5 class="modal-title fs-6 fw-bold" id="editModalLabel">
            <i class="fas fa-list-check me-2 text-primary"></i>Edit Watch List
          </h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
        </div>

        <div class="modal-body p-3">
          <div class="d-flex justify-content-end align-items-center mb-3">
            <button type="button" class="btn btn-success btn-sm px-3" id="addItemBtn" @click="addItem">
              <i class="fas fa-plus me-1"></i>Add Symbol
            </button>
          </div>

          <ul id="listItems" class="list-group list-group-flush mb-0">
            <WatchlistItem
              v-for="(item, index) in items"
              :key="item._key"
              :item="item"
              @remove="removeItem(index)"
            />
          </ul>

          <div
            id="watchlistEmptyState"
            class="text-center py-4 text-body-secondary"
            v-show="items.length === 0"
          >
            <i class="fas fa-layer-group fa-2x mb-2 opacity-50"></i>
            <p class="mb-0 small">No symbols in watchlist. Click "Add Symbol" to add one.</p>
          </div>
        </div>

        <div class="modal-footer py-2 px-3 bg-body-tertiary d-flex justify-content-between align-items-center">
          <div>
            <span
              id="successMessage"
              class="badge text-bg-success py-2 px-3 small"
              v-if="successMsg"
            >
              <i class="fas fa-check-circle me-1"></i>{{ successMsg }}
            </span>
            <span
              id="errorMessage"
              class="badge text-bg-danger py-2 px-3 small"
              v-if="errorMsg"
            >
              <i class="fas fa-exclamation-circle me-1"></i>{{ errorMsg }}
            </span>
          </div>
          <div class="d-flex gap-2">
            <button type="button" class="btn btn-outline-secondary btn-sm px-3" data-bs-dismiss="modal">Close</button>
            <button
              type="button"
              class="btn btn-primary btn-sm px-3"
              id="saveChanges"
              :disabled="saving"
              @click="saveChanges"
            >
              <i class="fas fa-save me-1"></i>Save changes
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import WatchlistItem from './WatchlistItem.vue';

/**
 * Modal for editing the watchlist. Manages load/save lifecycle and
 * triggers a Bootstrap Table refresh when the modal closes after changes.
 */

let _keyCounter = Date.now();
const items = ref([]);
const saving = ref(false);
const successMsg = ref('');
const errorMsg = ref('');
const modalEl = ref(null);
let hasChanged = false;
let successTimer = null;
let errorTimer = null;

function makeKey() {
    return ++_keyCounter;
}

function addItem() {
    items.value.push({ _key: makeKey(), symbol: '', qty: '', cost: '' });
}

function removeItem(index) {
    items.value.splice(index, 1);
}

async function loadWatchlist() {
    try {
        const res = await fetch('watchList');
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        items.value = (data || []).map((item) => {
            const rawQty = item.quantity ?? item.qty;
            const rawCost = item.cost;
            return {
                _key: makeKey(),
                symbol: item.symbol ?? '',
                qty: rawQty !== undefined && rawQty !== null ? rawQty : '',
                cost: rawCost !== undefined && rawCost !== null ? rawCost : '',
            };
        });
    } catch (err) {
        console.error('Failed to load watchlist:', err);
    }
}

async function saveChanges() {
    const updatedList = items.value
        .map((item) => {
            const symbol = String(item.symbol ?? '').trim().toUpperCase();
            if (!symbol) return null;
            const quantity = item.qty === '' ? 0 : parseInt(item.qty, 10);
            const cost = item.cost === '' ? 0.0 : parseFloat(item.cost);
            return {
                symbol,
                quantity: isNaN(quantity) ? 0 : Math.max(0, quantity),
                cost: isNaN(cost) ? 0.0 : Math.max(0.0, cost),
            };
        })
        .filter(Boolean);

    saving.value = true;
    errorMsg.value = '';
    successMsg.value = '';
    if (successTimer) clearTimeout(successTimer);
    if (errorTimer) clearTimeout(errorTimer);

    try {
        const res = await fetch('watchList', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(updatedList),
        });
        if (!res.ok) {
            const body = await res.json().catch(() => ({}));
            throw new Error(body.detail || `HTTP ${res.status}`);
        }
        const body = await res.json();
        hasChanged = true;
        successMsg.value = body.message || 'Saved successfully';
        successTimer = setTimeout(() => { successMsg.value = ''; }, 3000);
    } catch (err) {
        console.error('Error saving watchlist:', err);
        errorMsg.value = 'Error: ' + err.message;
        errorTimer = setTimeout(() => { errorMsg.value = ''; }, 4000);
    } finally {
        saving.value = false;
    }
}

function onModalShow() {
    loadWatchlist();
}

function onModalHide() {
    if (hasChanged) {
        if (window.$ && $('#table').length) {
            $('#table').bootstrapTable('refresh');
        }
        hasChanged = false;
    }
}

onMounted(() => {
    loadWatchlist();

    if (modalEl.value) {
        modalEl.value.addEventListener('show.bs.modal', onModalShow);
        modalEl.value.addEventListener('hide.bs.modal', onModalHide);
    }
});

onUnmounted(() => {
    if (modalEl.value) {
        modalEl.value.removeEventListener('show.bs.modal', onModalShow);
        modalEl.value.removeEventListener('hide.bs.modal', onModalHide);
    }
    if (successTimer) clearTimeout(successTimer);
    if (errorTimer) clearTimeout(errorTimer);
});
</script>
