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
            <IconListCheck class="icon me-2 text-primary" />Edit Watch List
          </h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
        </div>

        <div class="modal-body p-3">
          <div class="d-flex justify-content-end align-items-center mb-3">
            <button type="button" class="btn btn-success btn-sm px-3" id="addItemBtn" @click="addItem">
              <IconPlusLg class="icon me-1" />Add Symbol
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
            <IconLayers class="icon fs-2 mb-2 opacity-50" />
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
              <IconCheckCircle class="icon me-1" />{{ successMsg }}
            </span>
            <span
              id="errorMessage"
              class="badge text-bg-danger py-2 px-3 small"
              v-if="errorMsg"
            >
              <IconExclamationCircle class="icon me-1" />{{ errorMsg }}
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
              <IconFloppy class="icon me-1" />Save changes
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';
import WatchlistItem from './WatchlistItem.vue';
import IconCheckCircle from '~icons/bi/check-circle';
import IconExclamationCircle from '~icons/bi/exclamation-circle';
import IconFloppy from '~icons/bi/floppy';
import IconLayers from '~icons/bi/layers';
import IconListCheck from '~icons/bi/list-check';
import IconPlusLg from '~icons/bi/plus-lg';
import type { WatchlistEntry, WatchlistPayload } from '../types';
import { apiFetch } from '../js/api';

/**
 * Modal for editing the watchlist. Manages load/save lifecycle and
 * emits a reactive event when the modal closes after changes.
 */

const emit = defineEmits<{ 'watchlist-saved': [] }>();

let _keyCounter = Date.now();
const items = ref<WatchlistEntry[]>([]);
const saving = ref(false);
const successMsg = ref('');
const errorMsg = ref('');
const modalEl = ref<HTMLElement | null>(null);
let hasChanged = false;
let successTimer: ReturnType<typeof setTimeout> | null = null;
let errorTimer: ReturnType<typeof setTimeout> | null = null;

function makeKey(): number {
    return ++_keyCounter;
}

function addItem(): void {
    items.value.push({ _key: makeKey(), symbol: '', qty: '', cost: '' });
}

function removeItem(index: number): void {
    items.value.splice(index, 1);
}

async function loadWatchlist(): Promise<void> {
    try {
        const res = await apiFetch('watchList');
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = (await res.json()) as Array<Partial<WatchlistPayload> & { qty?: number }> | null;
        items.value = (data || []).map((item): WatchlistEntry => {
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

async function saveChanges(): Promise<void> {
    const updatedList = items.value
        .map((item): WatchlistPayload | null => {
            const symbol = String(item.symbol ?? '').trim().toUpperCase();
            if (!symbol) return null;
            const quantity = item.qty === '' ? 0 : parseInt(String(item.qty), 10);
            const cost = item.cost === '' ? 0.0 : parseFloat(String(item.cost));
            return {
                symbol,
                quantity: isNaN(quantity) ? 0 : Math.max(0, quantity),
                cost: isNaN(cost) ? 0.0 : Math.max(0.0, cost),
            };
        })
        .filter((entry): entry is WatchlistPayload => entry !== null);

    saving.value = true;
    errorMsg.value = '';
    successMsg.value = '';
    if (successTimer) clearTimeout(successTimer);
    if (errorTimer) clearTimeout(errorTimer);

    try {
        const res = await apiFetch('watchList', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(updatedList),
        });
        if (!res.ok) {
            const errBody = (await res.json().catch(() => ({}))) as { detail?: string };
            throw new Error(errBody.detail || `HTTP ${res.status}`);
        }
        const body = (await res.json()) as { message?: string };
        hasChanged = true;
        successMsg.value = body.message || 'Saved successfully';
        successTimer = setTimeout(() => { successMsg.value = ''; }, 3000);
    } catch (err) {
        console.error('Error saving watchlist:', err);
        errorMsg.value = 'Error: ' + (err instanceof Error ? err.message : String(err));
        errorTimer = setTimeout(() => { errorMsg.value = ''; }, 4000);
    } finally {
        saving.value = false;
    }
}

function onModalShow(): void {
    void loadWatchlist();
}

function onModalHide(): void {
    if (hasChanged) {
        emit('watchlist-saved');
        hasChanged = false;
    }
}

onMounted(() => {
    void loadWatchlist();

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
