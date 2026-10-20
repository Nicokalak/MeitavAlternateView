<template>
  <DarkModeToggle />
  <div class="container-fluid">
    <TrendsChart ref="trendsChart" />
    <PortfolioTable ref="portfolioTable" @portfolio-loaded="onPortfolioLoaded" />
  </div>
  <WatchlistModal @watchlist-saved="onWatchlistSaved" />
</template>

<script setup>
import { ref } from 'vue';
import DarkModeToggle from './components/DarkModeToggle.vue';
import TrendsChart from './components/TrendsChart.vue';
import PortfolioTable from './components/PortfolioTable.vue';
import WatchlistModal from './components/WatchlistModal.vue';

/** Root application component — composes all page-level Vue components. */

const trendsChart = ref(null);
const portfolioTable = ref(null);

function onPortfolioLoaded() {
    trendsChart.value?.fetchMarketState();
}

function onWatchlistSaved() {
    portfolioTable.value?.fetchPortfolio();
}
</script>
