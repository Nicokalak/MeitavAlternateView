<template>
  <div class="row">
    <div class="col-12">
      <!-- Sticky block: toolbar, refresh indicator and column header move as one element -->
      <div class="portfolio-sticky">
      <div class="portfolio-toolbar d-flex align-items-center">
        <div class="btn-group btn-group" role="group">
          <input
            type="search"
            id="customSearch"
            class="form-control form-control-sm"
            v-model="searchQuery"
          />
          <button
            class="btn btn-secondary"
            type="button"
            @click="fetchPortfolio"
            :disabled="loading"
            :title="loading ? 'Refreshing…' : 'Refresh'"
          >
            <i class="bi bi-arrow-clockwise" :class="{ spin: loading }"></i>
          </button>
          <button
            class="btn btn-secondary"
            :class="{ active: autoRefreshActive }"
            type="button"
            @click="toggleAutoRefresh"
            :title="autoRefreshActive ? 'Pause auto-refresh' : 'Start auto-refresh'"
          >
            <i class="bi bi-clock"></i>
          </button>
          <button
            class="btn btn-secondary"
            type="button"
            @click="watchlistHidden = !watchlistHidden"
            title="Toggle watchlist"
          >
            <i class="bi" :class="watchlistHidden ? 'bi-toggle-on' : 'bi-toggle-off'"></i>
          </button>
          <button
            class="btn btn-secondary"
            type="button"
            data-bs-toggle="modal"
            data-bs-target="#editWatchListModal"
            title="Edit watchlist"
          >
            <i class="bi bi-pencil"></i>
          </button>
                      <button
              class="btn btn-secondary dropdown-toggle"
              type="button"
              data-bs-toggle="dropdown"
              aria-expanded="false"
              title="Columns"
            >
              <i class="bi bi-list-ul"></i>
            </button>
            <ul class="dropdown-menu dropdown-menu-end p-2" style="min-width: 180px" @click.stop>
              <li class="form-check">
                <input
                  class="form-check-input"
                  type="checkbox"
                  id="col-toggle-all"
                  :checked="allOptionalVisible"
                  :indeterminate="someOptionalVisible && !allOptionalVisible"
                  @change="toggleAllColumns"
                />
                <label class="form-check-label small fw-semibold" for="col-toggle-all">Toggle all</label>
              </li>
              <li><hr class="dropdown-divider" /></li>
              <li v-for="col in allColumns" :key="col.key" class="form-check">
                <input
                  class="form-check-input"
                  type="checkbox"
                  :id="'col-' + col.key"
                  :checked="visibleColumns[col.key]"
                  :disabled="col.mandatory"
                  @change="toggleColumn(col)"
                />
                <label class="form-check-label small" :for="'col-' + col.key">{{ col.label }}</label>
              </li>
            </ul>
        </div>
      </div>

      <div class="refresh-progress-bar-container" :class="{ 'is-loading': loading && portfolio.length > 0 }">
        <div class="refresh-progress-bar"></div>
      </div>

      <!-- Header lives outside the horizontal scroller so it can stick to the window -->
      <div v-show="portfolio.length > 0" class="portfolio-head">
        <table
          ref="headTableEl"
          class="table table-sm portfolio-table portfolio-head-table mb-0"
          :style="headTableWidth ? { width: headTableWidth + 'px' } : null"
        >
          <colgroup>
            <col v-for="(w, i) in colWidths" :key="i" :style="{ width: w + 'px' }" />
          </colgroup>
          <thead class="portfolio-thead border border-secondary">
            <tr>
              <th class="detail-toggle-col"></th>
              <template v-for="col in activeColumns" :key="col.key">
                <th
                  class="sortable-header user-select-none"
                  :class="{ 'sortable-header-active': sortKey === col.key }"
                  @click="toggleSort(col.key)"
                  role="button"
                >
                  {{ col.label }}
                  <span v-if="sortKey === col.key" class="ms-1 small">
                    <i :class="sortOrder === 'asc' ? 'bi bi-caret-up-fill' : 'bi bi-caret-down-fill'"></i>
                  </span>
                </th>
              </template>
            </tr>
          </thead>
        </table>
      </div>
      </div>

      <div
        v-if="loading && portfolio.length === 0"
        class="portfolio-skeleton placeholder-glow"
        role="status"
        aria-busy="true"
      >
        <span class="visually-hidden">Loading…</span>
        <table class="table table-sm table-striped portfolio-table mb-0" aria-hidden="true">
          <thead>
            <tr>
              <th class="detail-toggle-col"></th>
              <th v-for="col in activeColumns" :key="col.key" class="fw-normal">
                <span class="placeholder rounded" :style="{ width: col.width ?? '3.5rem' }"></span>
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="n in SKELETON_ROW_COUNT" :key="n">
              <td class="detail-toggle-col"><span class="placeholder rounded" style="width: 1rem"></span></td>
              <td v-for="col in activeColumns" :key="col.key">
                <span class="placeholder rounded" :style="{ width: col.width ?? '3.5rem' }"></span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-show="portfolio.length > 0">
        <div class="portfolio-table-wrap" ref="wrapEl" @scroll.passive="syncHeaderScroll">
        <table class="table table-sm table-striped table-hover caption-top portfolio-table" ref="bodyTableEl">
          <!-- Zero-height header: keeps column widths content-driven and in sync with the sticky header -->
          <thead class="portfolio-thead-sizer" aria-hidden="true">
            <tr>
              <th class="detail-toggle-col"><div class="thead-sizer"></div></th>
              <template v-for="col in activeColumns" :key="col.key">
                <th :style="col.width ? { width: col.width, minWidth: col.width } : null">
                  <div class="thead-sizer fw-bold">
                    {{ col.label }}<span class="ms-1 small"><i class="bi bi-caret-down-fill"></i></span>
                  </div>
                </th>
              </template>
            </tr>
          </thead>
          <tbody class="table-group-divider">
            <template v-for="row in displayedRows" :key="row.symbol">
              <tr :class="rowClass(row)">
                <td
                  class="detail-toggle-col"
                  @click="toggleExpand(row.symbol)"
                  role="button"
                  :title="expandedRows[row.symbol] ? 'Hide details' : 'Show details'"
                >
                  <i class="bi" :class="expandedRows[row.symbol] ? 'bi-dash-lg' : 'bi-plus-lg'"></i>
                </td>
                <template v-for="col in activeColumns" :key="col.key">
                  <td :class="cellClass(col, row)" :style="col.width ? { width: col.width, minWidth: col.width } : null">
                    <template v-if="col.key === 'symbol'">
                      <SymbolCell :row="row" />
                    </template>
                    <template v-else>
                      {{ formatCell(col, row) }}
                    </template>
                  </td>
                </template>
              </tr>
              <PortfolioDetailRow
                v-if="expandedRows[row.symbol]"
                :row="row"
                :colspan="activeColumns.length + 1"
              />
            </template>
          </tbody>
          <tfoot class="table-group-divider fw-bold">
            <tr>
              <td></td>
              <template v-for="col in activeColumns" :key="col.key">
                <td :class="footerCellClass(col)" :style="col.width ? { width: col.width, minWidth: col.width } : null">
                  <span v-if="col.footer" v-html="computeFooter(col)"></span>
                </td>
              </template>
            </tr>
          </tfoot>
        </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch, onMounted, onUnmounted } from 'vue';
import PortfolioDetailRow from './PortfolioDetailRow.vue';
import SymbolCell from './SymbolCell.vue';
import type { PortfolioRow } from '../types';

/**
 * Native Vue 3 portfolio grid — replaces Bootstrap Table and all
 * associated jQuery code (app.js, table.js, window.* formatters).
 */

const emit = defineEmits<{ 'portfolio-loaded': [] }>();

// ─── State ─────────────────────────────────────────────────────────────────

type CellFormat = 'percent' | 'round' | 'bigNum' | null;
type FooterKind =
    | 'totalDayPercent'
    | 'totalPercent'
    | 'gainTotal'
    | 'totalPrice'
    | 'totalCostPlain'
    | null;

interface Column {
    key: keyof PortfolioRow;
    label: string;
    width?: string;
    format: CellFormat;
    footer: FooterKind;
    defaultVisible: boolean;
    /** Always shown; cannot be hidden from the column menu. */
    mandatory?: boolean;
    colored?: boolean;
}

const portfolio = ref<PortfolioRow[]>([]);
const loading = ref(false);
const searchQuery = ref('');
const sortKey = ref<keyof PortfolioRow>('percent_change');
const sortOrder = ref<'asc' | 'desc'>('desc');
const watchlistHidden = ref(false);
const expandedRows = reactive<Record<string, boolean>>({});
const autoRefreshActive = ref(false);
let autoRefreshTimer: ReturnType<typeof setInterval> | null = null;
const AUTO_REFRESH_INTERVAL = 300_000; // 5 minutes
const SKELETON_ROW_COUNT = 8;

// ─── Column Definitions ────────────────────────────────────────────────────

const allColumns: Column[] = [
    { key: 'symbol',           label: 'Symbol',       width: '130px',        format: null,          footer: null,              defaultVisible: true,  mandatory: true },
    { key: 'percent_change',   label: '% Change',     format: 'percent',     footer: 'totalDayPercent', defaultVisible: true,  colored: true },
    { key: 'principle_change', label: '% PChange',    format: 'percent',     footer: 'totalPercent',    defaultVisible: false, colored: true },
    { key: 'change',           label: 'Change',       format: 'round',       footer: null,              defaultVisible: false,  colored: true },
    { key: 'last_price',       label: 'Last',         format: 'round',       footer: null,              defaultVisible: true },
    { key: 'cost',             label: 'Cost',         format: 'round',       footer: null,              defaultVisible: true },
    { key: 'total_cost',       label: 'Total Cost',   format: 'bigNum',      footer: 'totalCostPlain',  defaultVisible: false },
    { key: 'quantity',         label: 'Qty',          format: null,          footer: null,              defaultVisible: true },
    { key: 'day_val',          label: "Day's Value",   format: null,          footer: 'totalPrice',      defaultVisible: true,  colored: true },
    { key: 'gain',             label: 'Gain %',       format: 'percent',     footer: 'gainTotal',       defaultVisible: true,  colored: true },
    { key: 'total_change',     label: 'Profit/Loss',  format: 'bigNum',      footer: 'totalPrice',      defaultVisible: true,  colored: true },
    { key: 'total_val',        label: 'Value',        format: 'bigNum',      footer: 'totalPrice',      defaultVisible: true },
    { key: 'weight',           label: 'Weight',       format: 'percent',     footer: null,              defaultVisible: false },
];

const visibleColumns = reactive<Record<string, boolean>>(
    Object.fromEntries(allColumns.map(c => [c.key, c.mandatory || c.defaultVisible]))
);

const activeColumns = computed(() =>
    allColumns.filter(c => c.mandatory || visibleColumns[c.key])
);

const optionalColumns = allColumns.filter(c => !c.mandatory);
const allOptionalVisible = computed(() => optionalColumns.every(c => visibleColumns[c.key]));
const someOptionalVisible = computed(() => optionalColumns.some(c => visibleColumns[c.key]));

function toggleColumn(col: Column): void {
    if (col.mandatory) return;
    visibleColumns[col.key] = !visibleColumns[col.key];
}

/** Shows every optional column, or hides them all when all are already visible. */
function toggleAllColumns(): void {
    const show = !allOptionalVisible.value;
    for (const col of optionalColumns) visibleColumns[col.key] = show;
}

// ─── Formatting Helpers ────────────────────────────────────────────────────

function round(v: number): number {
    return Math.round((v + Number.EPSILON) * 100) / 100;
}
function roundPercent(v: number): string {
    return isNaN(v) ? '-' : round(v) + '%';
}
function bigNum(v: number | null | undefined): string {
    if (v === null || v === undefined || isNaN(v)) return '-';
    return round(v).toLocaleString('en-US');
}

function formatCell(col: Column, row: PortfolioRow): string | number {
    const v = row[col.key];
    if (v === null || v === undefined) return '-';
    if (typeof v === 'object') return '-';
    switch (col.format) {
        case 'percent': return roundPercent(Number(v));
        case 'round':   return round(Number(v));
        case 'bigNum':  return bigNum(Number(v));
        default:        return v;
    }
}

function cellClass(col: Column, row: PortfolioRow): string {
    if (!col.colored) return '';
    const v = row[col.key];
    if (typeof v !== 'number') return '';
    if (v > 0) return 'text-success';
    if (v < 0) return 'text-danger';
    return '';
}

function rowClass(row: PortfolioRow): string {
    return !isInPortfolio(row) ? 'table-info bg-opacity-75' : '';
}

function footerCellClass(col: Column): string {
    if (!col.footer) return '';
    const val = computeFooterValue(col);
    if (typeof val === 'number') {
        if (val > 0) return 'text-success';
        if (val < 0) return 'text-danger';
    }
    return '';
}

// ─── Portfolio Filtering ───────────────────────────────────────────────────

function isInPortfolio(row: PortfolioRow): boolean {
    return row.type.toLowerCase() !== 'w';
}

// ─── Data Fetching ─────────────────────────────────────────────────────────

async function fetchPortfolio(): Promise<void> {
    loading.value = true;
    try {
        const res = await fetch('portfolio');
        if (res.status === 401) {
            window.location.reload();
            return;
        }
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        portfolio.value = (await res.json()) as PortfolioRow[];
        emit('portfolio-loaded');
    } catch (err) {
        console.error('Failed to load portfolio:', err);
    } finally {
        loading.value = false;
    }
}

// ─── Sorting ───────────────────────────────────────────────────────────────

function toggleSort(key: keyof PortfolioRow): void {
    if (sortKey.value === key) {
        sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc';
    } else {
        sortKey.value = key;
        sortOrder.value = 'desc';
    }
}

// ─── Search / Filter / Sort Pipeline ───────────────────────────────────────

const filteredRows = computed(() => {
    let rows = portfolio.value;

    // Hide watchlist items when toggle is active
    if (watchlistHidden.value) {
        rows = rows.filter(isInPortfolio);
    }

    // Text/regex search
    if (searchQuery.value.trim()) {
        const query = searchQuery.value.trim();
        let matcher: (str: string) => boolean;
        try {
            const regex = new RegExp(query, 'i');
            matcher = (str) => regex.test(str);
        } catch {
            const lower = query.toLowerCase();
            matcher = (str) => str.toLowerCase().includes(lower);
        }
        rows = rows.filter(r =>
            matcher(r.symbol ?? '') ||
            matcher(r.type ?? '') ||
            matcher(r.api_data?.shortName ?? '') ||
            matcher(r.api_data?.longName ?? '')
        );
    }

    return rows;
});

const displayedRows = computed(() => {
    const rows = [...filteredRows.value];
    const key = sortKey.value;
    const dir = sortOrder.value === 'asc' ? 1 : -1;
    rows.sort((a, b) => {
        const va = a[key] ?? 0;
        const vb = b[key] ?? 0;
        if (typeof va === 'string' && typeof vb === 'string') return dir * va.localeCompare(vb);
        if (typeof va === 'number' && typeof vb === 'number') return dir * (va - vb);
        return 0;
    });
    return rows;
});

// ─── Footer Computations ───────────────────────────────────────────────────

const portfolioRows = computed(() => {
    return filteredRows.value.filter(isInPortfolio);
});

function sumField(field: keyof PortfolioRow): number {
    return round(
        portfolioRows.value.reduce((s, r) => {
            const v = r[field];
            return s + (typeof v === 'number' ? v : 0);
        }, 0),
    );
}

function calcAvgCost(): number {
    return round(portfolioRows.value.reduce((s, r) => s + (r.total_val - r.total_change), 0));
}

function calcStartPrice(): number {
    return round(portfolioRows.value.reduce((s, r) => {
        const q = r.type.toLowerCase() === 'e' ? r.quantity : r.quantity * 100;
        return s + (r.last_price - r.change) * q;
    }, 0));
}

function computeFooterValue(col: Column): number | null {
    switch (col.footer) {
        case 'totalDayPercent': {
            const startPrice = calcStartPrice();
            return startPrice === 0 ? 0 : (sumField('day_val') / startPrice) * 100;
        }
        case 'totalPercent': {
            const avgCost = calcAvgCost();
            return avgCost === 0 ? 0 : (sumField('day_val') / avgCost) * 100;
        }
        case 'gainTotal': {
            const totalProfit = sumField('total_change');
            const avgCost = calcAvgCost();
            return avgCost === 0 ? 0 : (totalProfit / avgCost) * 100;
        }
        case 'totalPrice':     return sumField(col.key);
        case 'totalCostPlain': return sumField(col.key);
        default:               return null;
    }
}

function computeFooter(col: Column): string {
    const val = computeFooterValue(col);
    if (val === null) return '';

    switch (col.footer) {
        case 'totalDayPercent':
        case 'totalPercent':
        case 'gainTotal': {
            const formatted = roundPercent(val);
            if (val > 0) return `<span class="text-success">${formatted}</span>`;
            if (val < 0) return `<span class="text-danger">${formatted}</span>`;
            return formatted;
        }
        case 'totalPrice': {
            const formatted = bigNum(val);
            if (val > 0) return `<span class="text-success">${formatted}</span>`;
            if (val < 0) return `<span class="text-danger">${formatted}</span>`;
            return formatted;
        }
        case 'totalCostPlain':
            return bigNum(val);
        default:
            return '';
    }
}

// ─── Row Expansion ─────────────────────────────────────────────────────────

function toggleExpand(symbol: string): void {
    expandedRows[symbol] = !expandedRows[symbol];
}

// ─── Auto-Refresh ──────────────────────────────────────────────────────────

function toggleAutoRefresh(): void {
    autoRefreshActive.value = !autoRefreshActive.value;
    if (autoRefreshActive.value) {
        autoRefreshTimer = setInterval(fetchPortfolio, AUTO_REFRESH_INTERVAL);
    } else {
        if (autoRefreshTimer) clearInterval(autoRefreshTimer);
        autoRefreshTimer = null;
    }
}

// ─── Sticky Header Sync ────────────────────────────────────────────────────

const headTableEl = ref<HTMLTableElement | null>(null);
const wrapEl = ref<HTMLElement | null>(null);
const bodyTableEl = ref<HTMLTableElement | null>(null);
const colWidths = ref<number[]>([]);
const headTableWidth = ref(0);
let resizeObserver: ResizeObserver | null = null;

const roundPx = (v: number): number => Math.round(v * 100) / 100;

/** Copies the body table's measured column widths onto the sticky header table. */
function syncHeaderWidths(): void {
    const table = bodyTableEl.value;
    if (!table) return;

    const widths = Array.from(table.querySelectorAll<HTMLElement>('thead th'), th =>
        roundPx(th.getBoundingClientRect().width)
    );
    const tableWidth = roundPx(table.getBoundingClientRect().width);
    if (tableWidth === 0 || widths.every(w => w === 0)) return;

    const unchanged =
        widths.length === colWidths.value.length &&
        widths.every((w, i) => w === colWidths.value[i]);
    if (!unchanged) colWidths.value = widths;
    if (tableWidth !== headTableWidth.value) headTableWidth.value = tableWidth;
    syncHeaderScroll();
}

let scrollFrame = 0;

/** Mirrors the body wrapper's horizontal scroll onto the sticky header, once per frame. */
function syncHeaderScroll(): void {
    if (scrollFrame) return;
    scrollFrame = requestAnimationFrame(() => {
        scrollFrame = 0;
        if (headTableEl.value && wrapEl.value) {
            headTableEl.value.style.transform = `translate3d(${-wrapEl.value.scrollLeft}px, 0, 0)`;
        }
    });
}

watch([portfolio, activeColumns], syncHeaderWidths, { flush: 'post' });

// ─── Lifecycle ─────────────────────────────────────────────────────────────

onMounted(() => {
    void fetchPortfolio();
    if (typeof ResizeObserver !== 'undefined') {
        resizeObserver = new ResizeObserver(syncHeaderWidths);
        if (bodyTableEl.value) resizeObserver.observe(bodyTableEl.value);
        if (wrapEl.value) resizeObserver.observe(wrapEl.value);
    }
});

onUnmounted(() => {
    if (autoRefreshTimer) clearInterval(autoRefreshTimer);
    if (resizeObserver) resizeObserver.disconnect();
    if (scrollFrame) cancelAnimationFrame(scrollFrame);
});

// Expose fetchPortfolio for external use
defineExpose({ fetchPortfolio });
</script>
