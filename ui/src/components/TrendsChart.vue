<template>
  <!-- Market Status Header (sticky) -->
  <div id="market-status-container" class="sticky-top bg-body py-2 z-3">
    <h2 class="m-0 placeholder-glow" id="market_status">
      <span v-if="!marketStatusHtml" class="placeholder col-3 rounded"></span>
      <span v-else v-html="marketStatusHtml"></span>
    </h2>
  </div>

  <!-- Market Stats Cards -->
  <div class="row pt-2">
    <div class="col-12">
      <div id="market-stats" class="d-flex flex-wrap gap-2" :style="{ display: stats.loaded ? '' : 'none' }">
        <!-- Gainer / % -->
        <div class="card flex-fill placeholder-glow" style="min-width:130px">
          <div class="card-body p-2 text-center">
            <span class="fw-semibold text-success" id="top-gainer">
              <span v-if="!stats.loaded" class="placeholder col-5 rounded"></span>
              <span v-else>{{ stats.topGainer }}</span>
            </span>
            <span class="text-body-secondary"> / </span>
            <span class="fw-semibold text-success" id="top-gainer-percent">
              <span v-if="!stats.loaded" class="placeholder col-5 rounded"></span>
              <span v-else>{{ stats.topGainerPct }}</span>
            </span>
          </div>
          <div class="card-footer py-1 text-center text-body-secondary small">Gainer ($) / (%)</div>
        </div>
        <!-- Loser / % -->
        <div class="card flex-fill placeholder-glow" style="min-width:130px">
          <div class="card-body p-2 text-center">
            <span class="fw-semibold text-danger" id="top-loser">
              <span v-if="!stats.loaded" class="placeholder col-5 rounded"></span>
              <span v-else>{{ stats.topLoser }}</span>
            </span>
            <span class="text-body-secondary"> / </span>
            <span class="fw-semibold text-danger" id="top-loser-percent">
              <span v-if="!stats.loaded" class="placeholder col-5 rounded"></span>
              <span v-else>{{ stats.topLoserPct }}</span>
            </span>
          </div>
          <div class="card-footer py-1 text-center text-body-secondary small">Loser ($) / (%)</div>
        </div>
        <!-- Mover / Trending -->
        <div class="card flex-fill placeholder-glow" style="min-width:130px">
          <div class="card-body p-2 text-center">
            <span class="fw-semibold" id="top-mover">
              <span v-if="!stats.loaded" class="placeholder col-4 rounded"></span>
              <span v-else>{{ stats.topMover }}</span>
            </span>
            <span class="text-body-secondary"> / </span>
            <span class="fw-semibold" id="trending">
              <span v-if="!stats.loaded" class="placeholder col-4 rounded"></span>
              <span v-else>{{ stats.trending }}</span>
            </span>
          </div>
          <div class="card-footer py-1 text-center text-body-secondary small">Mover / Trending</div>
        </div>
        <!-- Watchlist -->
        <div class="card flex-fill placeholder-glow" style="min-width:90px">
          <div class="card-body p-2 text-center">
            <span class="fw-semibold text-info" id="watchlist-trend">
              <span v-if="!stats.loaded" class="placeholder col-6 rounded"></span>
              <span v-else>{{ stats.watchlistTrend }}</span>
            </span>
          </div>
          <div class="card-footer py-1 text-center text-body-secondary small">Watchlist</div>
        </div>
        <!-- +/- -->
        <div class="card flex-fill placeholder-glow" style="min-width:90px">
          <div class="card-body p-2 text-center" id="up-down">
            <span class="fw-semibold text-success">
              <span v-if="!stats.loaded" class="placeholder col-3 rounded"></span>
              <span v-else>{{ stats.up }}</span>
            </span>
            <span class="text-body-secondary"> / </span>
            <span class="fw-semibold text-danger">
              <span v-if="!stats.loaded" class="placeholder col-3 rounded"></span>
              <span v-else>{{ stats.down }}</span>
            </span>
          </div>
          <div class="card-footer py-1 text-center text-body-secondary small">+/-</div>
        </div>
      </div>
    </div>
  </div>

  <!-- Trends Chart Canvas -->
  <div class="row mt-4">
    <div class="col-12">
      <canvas ref="trendsCanvas" id="trends"></canvas>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import { Chart } from 'chart.js';

/**
 * Encapsulates the trends Chart.js line chart and market stats header cards.
 * Exposes initChart() and updateTrends() on the window for backward-compat
 * calls from app.js (which still orchestrates load order).
 */

const trendsCanvas = ref(null);
const marketStatusHtml = ref('');
const stats = reactive({
    loaded: false,
    topGainer: '',
    topGainerPct: '',
    topLoser: '',
    topLoserPct: '',
    topMover: '',
    trending: '',
    watchlistTrend: '',
    up: 0,
    down: 0,
});

const trendsObj = {
    PRE_histo: {},
    REGULAR_histo: {},
    POST_histo: {},
};

let chart = null;

function round(value) {
    return Math.round((value + Number.EPSILON) * 100) / 100;
}

function createSpan(val, val2) {
    function getClass(v) {
        return v > 0 ? 'success' : v < 0 ? 'danger' : 'secondary';
    }
    return (
        `<span class="state-badge state-badge-${getClass(val)} position-relative">${val}` +
        `<span class="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-${getClass(val2)}">${val2}</span></span>`
    );
}

/** Populate market stats from the /marketState API response. */
function trend_stats(trendObj) {
    const marketState = trendObj.marketState.toLowerCase();
    marketStatusHtml.value =
        marketState.charAt(0).toUpperCase() + marketState.slice(1) + ' market  ' +
        createSpan(round(trendObj.trend), round(trendObj.yahoo_trend));

    stats.topGainer = trendObj['top-gainer'].symbol;
    stats.topGainerPct = trendObj['top-gainer%'].symbol;
    stats.topMover = trendObj['top-mover'].symbol;
    stats.topLoser = trendObj['top-loser'].symbol;
    stats.topLoserPct = trendObj['top-loser%'].symbol;
    stats.watchlistTrend = round(trendObj.watchlist_trend) + '%';
    stats.up = round(trendObj['up-down'].up);
    stats.down = round(trendObj['up-down'].down);
    stats.trending = trendObj.trending.symbol;
    stats.loaded = true;
    console.log(trendObj);
}

/** Fetch /trends and push new data points into the chart. */
function update_trends() {
    if (!chart) return;
    $.get('trends', function (trends) {
        for (const key in trends) {
            for (const t in trends[key]) {
                trendsObj[key][t] = trends[key][t];
            }
        }
        chart.update();
    }).fail(function (jqXHR) {
        console.error('Failed to load trends:', jqXHR.status, jqXHR.statusText);
    });
}

/** Initialise the Chart.js instance on the canvas element. */
function init_chart() {
    const down = (ctx) => ctx.p0.parsed.y > ctx.p1.parsed.y ? 'rgb(213, 76, 76)' : undefined;
    const up = (ctx) => ctx.p0.parsed.y < ctx.p1.parsed.y ? 'rgb(0, 139, 0)' : undefined;
    const skipped = (ctx, value) =>
        new Date(ctx.p1.parsed.x) - new Date(ctx.p0.parsed.x) > 3.6e+7 ? value : undefined;

    const data = {
        datasets: [
            {
                label: 'PRE Market',
                data: trendsObj.PRE_histo,
                borderColor: '#0d6efd',
                backgroundColor: '#0d6efd',
                pointStyle: 'rectRounded',
                tension: 0.3,
                segment: {
                    borderColor: (ctx) => skipped(ctx, 'rgba(0,0,0,0.2)') || up(ctx) || down(ctx),
                    borderDash: (ctx) => skipped(ctx, [6, 6]),
                },
            },
            {
                label: 'Regular Market',
                data: trendsObj.REGULAR_histo,
                borderColor: '#20c997',
                backgroundColor: '#20c997',
                pointStyle: 'rectRounded',
                tension: 0.3,
                segment: {
                    borderColor: (ctx) => skipped(ctx, 'rgba(0,0,0,0.2)') || up(ctx) || down(ctx),
                    borderDash: (ctx) => skipped(ctx, [6, 6]),
                },
            },
            {
                label: 'POST Market',
                data: trendsObj.POST_histo,
                borderColor: '#fd7e14',
                backgroundColor: '#fd7e14',
                pointStyle: 'rectRounded',
                tension: 0.3,
                segment: {
                    borderColor: (ctx) => skipped(ctx, 'rgba(0,0,0,0.2)') || up(ctx) || down(ctx),
                    borderDash: (ctx) => skipped(ctx, [6, 6]),
                },
            },
        ],
    };

    const config = {
        type: 'line',
        data,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    display: false,
                    type: 'time',
                    time: {
                        parser: "yyyyMMdd'T'HH:mm:ss",
                        minUnit: 'minute',
                    },
                    ticks: { stepSize: 30 },
                },
            },
            plugins: {
                legend: { display: false },
            },
        },
    };

    chart = new Chart(trendsCanvas.value, config);
}

onMounted(() => {
    // Expose globally for backward-compatible calls from app.js
    window.init_chart = init_chart;
    window.update_trends = update_trends;
    window.trend_stats = trend_stats;
});
</script>
