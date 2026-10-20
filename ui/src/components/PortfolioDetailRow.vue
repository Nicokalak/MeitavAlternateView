<template>
  <tr class="detail-row">
    <td :colspan="colspan" class="p-0 border-0">
      <div class="container-fluid py-2 px-3">
        <div v-if="loading" class="text-center py-3">
          <div class="spinner-border spinner-border-sm text-secondary" role="status">
            <span class="visually-hidden">Loading…</span>
          </div>
        </div>

        <div v-else-if="error" class="text-danger small py-2">
          Failed to load details ({{ error }})
        </div>

        <template v-else-if="detail">
          <dl class="row mb-1">
            <dt class="col-xl-2 col-md-3 col-2">52w range</dt>
            <dd class="col-xl-2 col-md-3 col-3">
              <RangeBar :min="round(detail.fiftyTwoWeekLow)" :max="round(detail.fiftyTwoWeekHigh)" :value="round(price)" />
            </dd>
            <div class="w-100 d-md-none d-sm-block"></div>

            <dt class="col-xl-2 col-md-3 col-2">price</dt>
            <dd class="col-xl-2 col-md-3 col-3">{{ round(price) }}</dd>
            <div class="w-100 d-md-none d-sm-block"></div>

            <dt class="col-xl-2 col-md-3 col-2">52d avg</dt>
            <dd class="col-xl-2 col-md-3 col-3">{{ round(detail.fiftyDayAverage) }}</dd>
            <div class="w-100 d-md-none d-sm-block"></div>

            <dt class="col-xl-2 col-md-3 col-2">day range</dt>
            <dd class="col-xl-2 col-md-3 col-3">
              <RangeBar :min="round(detail.regularMarketDayLow)" :max="round(detail.regularMarketDayHigh)" :value="round(price)" />
            </dd>
            <div class="w-100 d-md-none d-sm-block"></div>

            <dt class="col-xl-2 col-md-3 col-2">prev close</dt>
            <dd class="col-xl-2 col-md-3 col-3">{{ round(detail.regularMarketPreviousClose) }}</dd>
            <div class="w-100 d-md-none d-sm-block"></div>

            <dt class="col-xl-2 col-md-3 col-2">volume</dt>
            <dd class="col-xl-2 col-md-3 col-3">{{ bigNum(detail.regularMarketVolume) }}</dd>
            <div class="w-100 d-md-none d-sm-block"></div>

            <dt class="col-xl-2 col-md-3 col-2">volume 10D</dt>
            <dd class="col-xl-2 col-md-3 col-3">{{ bigNum(detail.averageDailyVolume10Day) }}</dd>
            <div class="w-100 d-md-none d-sm-block"></div>

            <dt class="col-xl-2 col-md-3 col-2">volume 3M</dt>
            <dd class="col-xl-2 col-md-3 col-3">{{ bigNum(detail.averageDailyVolume3Month) }}</dd>
            <div class="w-100 d-md-none d-sm-block"></div>

            <dt class="col-xl-2 col-md-3 col-2">change</dt>
            <dd class="col-xl-2 col-md-3 col-3">
              <span :class="colorClass(changeVal)">{{ round(changeVal) }}</span>
            </dd>
            <div class="w-100 d-md-none d-sm-block"></div>

            <dt class="col-xl-2 col-md-3 col-2">change (%)</dt>
            <dd class="col-xl-2 col-md-3 col-3">
              <span :class="colorClass(changePct)">{{ roundPercent(changePct) }}</span>
            </dd>
            <div class="w-100 d-md-none d-sm-block"></div>

            <template v-if="detail.averageAnalystRating">
              <dt class="col-xl-2 col-md-3 col-2">rating</dt>
              <dd class="col-xl-2 col-md-3 col-3">{{ detail.averageAnalystRating }}</dd>
              <div class="w-100 d-md-none d-sm-block"></div>
            </template>

            <dt class="col-xl-2 col-md-3 col-2">earnings</dt>
            <dd class="col-xl-2 col-md-3 col-3">{{ earningsDisplay }}</dd>
            <div class="w-100 d-md-none d-sm-block"></div>

            <dt class="col-xl-2 col-md-3 col-2">trend ratio</dt>
            <dd class="col-xl-2 col-md-3 col-3">{{ trendRatio }}</dd>
            <div class="w-100 d-md-none d-sm-block"></div>
          </dl>

          <div>
            <a
              class="link-primary fa-lg"
              target="_blank"
              :href="'https://finance.yahoo.com/quote/' + row.symbol"
              title="more info..."
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" class="bi bi-arrow-up-right-circle" viewBox="0 0 16 16">
                <path fill-rule="evenodd" d="M1 8a7 7 0 1 0 14 0A7 7 0 0 0 1 8zm15 0A8 8 0 1 1 0 8a8 8 0 0 1 16 0zM5.854 10.803a.5.5 0 1 1-.708-.707L9.243 6H6.475a.5.5 0 1 1 0-1h3.975a.5.5 0 0 1 .5.5v3.975a.5.5 0 1 1-1 0V6.707l-4.096 4.096z"/>
              </svg>
            </a>
          </div>
        </template>
      </div>
    </td>
  </tr>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import RangeBar from './RangeBar.vue';

/**
 * Expandable detail row for a single stock — replaces the legacy
 * detailFormatter() / getDetailedRow() string concatenator.
 */

const props = defineProps({
    row: { type: Object, required: true },
    colspan: { type: Number, default: 14 },
});

const loading = ref(true);
const error = ref('');
const detail = ref(null);
const marketStateKey = ref('regular');

function round(v) {
    return Math.round((v + Number.EPSILON) * 100) / 100;
}
function roundPercent(v) {
    return isNaN(v) ? '-' : round(v) + '%';
}
function bigNum(v) {
    if (isNaN(v)) return '-';
    return round(v).toLocaleString('en-US');
}
function colorClass(v) {
    if (v > 0) return 'text-success';
    if (v < 0) return 'text-danger';
    return '';
}

const price = computed(() => {
    if (!detail.value) return 0;
    return detail.value[marketStateKey.value + 'MarketPrice'] ?? 0;
});

const changeVal = computed(() => {
    if (!detail.value) return 0;
    return (detail.value[marketStateKey.value + 'MarketChange'] ?? 0) * props.row.quantity;
});

const changePct = computed(() => {
    if (!detail.value) return 0;
    return detail.value[marketStateKey.value + 'MarketChangePercent'] ?? 0;
});

const earningsDisplay = computed(() => {
    if (!detail.value || !detail.value.earningsTimestamp) return '';
    const fmt = new Intl.DateTimeFormat('en-GB', {
        day: '2-digit', month: '2-digit', year: 'numeric',
        hour: '2-digit', minute: '2-digit', hour12: false,
    });
    return fmt.format(new Date(detail.value.earningsTimestamp * 1000));
});

const trendRatio = computed(() => {
    if (!detail.value) return '-';
    const ratio = (detail.value.regularMarketVolume / detail.value.averageDailyVolume3Month) * 100;
    return roundPercent(ratio);
});

onMounted(async () => {
    try {
        const res = await fetch('ticker/' + props.row.symbol);
        if (!res.ok) throw new Error(String(res.status));
        const data = await res.json();
        marketStateKey.value = (data['market-state-4calc'] || 'regular').toLowerCase();
        detail.value = data.stock.api_data;
    } catch (err) {
        error.value = err.message;
    } finally {
        loading.value = false;
    }
});
</script>
