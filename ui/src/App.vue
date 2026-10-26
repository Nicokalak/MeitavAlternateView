<template>
  <DarkModeToggle />
  <div class="container-fluid">
    <TrendsChart ref="trendsChart" />
    <PortfolioTable ref="portfolioTable" @portfolio-loaded="onPortfolioLoaded" />
  </div>
  <WatchlistModal @watchlist-saved="onWatchlistSaved" />
</template>

<script setup lang="ts">
import { ref } from 'vue';
import DarkModeToggle from './components/DarkModeToggle.vue';
import TrendsChart from './components/TrendsChart.vue';
import PortfolioTable from './components/PortfolioTable.vue';
import WatchlistModal from './components/WatchlistModal.vue';

/** Root application component — composes all page-level Vue components. */

const trendsChart = ref<InstanceType<typeof TrendsChart> | null>(null);
const portfolioTable = ref<InstanceType<typeof PortfolioTable> | null>(null);

function onPortfolioLoaded(): void {
    void trendsChart.value?.fetchMarketState();
}

function onWatchlistSaved(): void {
    void portfolioTable.value?.fetchPortfolio();
}
</script>
