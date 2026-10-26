<template>
  <div class="symbol-cell">
    <div class="d-flex">{{ row.symbol }}</div>

    <div v-if="row.type === 'O'">
      <span class="badge text-bg-danger">
        {{ row.p_or_c }}{{ row.strike }} {{ row.expiration }}
      </span>
    </div>

    <div v-if="showEarnings">
      <span class="badge text-bg-info">
        {{ earningsLabel }}
      </span>
    </div>

    <div v-if="showDividend">
      <span class="badge text-bg-success">
        {{ dividendLabel }}
      </span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import type { PortfolioRow } from '../types';

/** Renders the symbol column with contextual badges for options, earnings, and dividends. */

const props = defineProps<{
    row: PortfolioRow;
}>();

const _dateFmtShort = new Intl.DateTimeFormat('en-GB', {
    day: '2-digit', month: '2-digit', year: 'numeric',
    hour: '2-digit', minute: '2-digit', hour12: false,
});
const _dateFmtDayMonth = new Intl.DateTimeFormat('en-GB', {
    day: '2-digit', month: '2-digit',
});

function round(v: number): number {
    return Math.round((v + Number.EPSILON) * 100) / 100;
}

function daysCountToEarn(timestampMs: number): number {
    return Math.ceil((timestampMs - Date.now()) / (1000 * 60 * 60 * 24));
}

function formatCalendar(unixMs: number): string {
    const target = new Date(unixMs);
    const diffDays = Math.round((unixMs - Date.now()) / (1000 * 60 * 60 * 24));
    const timeStr = target.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit', hour12: false });
    if (diffDays === 0) return 'Today at ' + timeStr;
    if (diffDays === 1) return 'Tomorrow at ' + timeStr;
    if (diffDays === -1) return 'Yesterday at ' + timeStr;
    if (diffDays > 1 && diffDays < 7) {
        return new Intl.RelativeTimeFormat('en-GB', { numeric: 'auto' }).format(diffDays, 'day') + ' at ' + timeStr;
    }
    return _dateFmtShort.format(target);
}

const showEarnings = computed(() => {
    const ts = props.row.api_data?.earningsTimestamp;
    if (!ts) return false;
    const days = daysCountToEarn(ts * 1000);
    return days >= 0 && days < 14;
});

const earningsLabel = computed(() => {
    const ts = props.row.api_data?.earningsTimestamp;
    if (!ts) return '';
    return formatCalendar(ts * 1000);
});

const showDividend = computed(() => {
    const api = props.row.api_data;
    return api?.dividendDate !== undefined && (api?.trailingAnnualDividendRate ?? 0) > 0;
});

const dividendLabel = computed(() => {
    const api = props.row.api_data;
    if (!api || api.dividendDate === undefined) return '';
    const divAmount = (api.trailingAnnualDividendRate ?? 0) / 4;
    return (
        _dateFmtDayMonth.format(new Date(api.dividendDate * 1000)) + ' ' +
        round(divAmount) + 'x' + props.row.quantity + '=' + round(divAmount * props.row.quantity) + '$'
    );
});
</script>
