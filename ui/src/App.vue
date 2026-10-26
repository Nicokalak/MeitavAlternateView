<template>
  <DarkModeToggle />
  <ErrorPage
    v-if="unauthorized"
    :code="401"
    title="Unauthorized"
    message="Oops! You do not have permission to access this resource."
  />
  <div v-else class="container-fluid">
    <TrendsChart ref="trendsChart" />
    <PortfolioTable ref="portfolioTable" @portfolio-loaded="onPortfolioLoaded" />
  </div>
  <WatchlistModal v-if="!unauthorized" @watchlist-saved="onWatchlistSaved" />
</template>

<script setup lang="ts">
import { ref } from 'vue';
import DarkModeToggle from './components/DarkModeToggle.vue';
import TrendsChart from './components/TrendsChart.vue';
import PortfolioTable from './components/PortfolioTable.vue';
import WatchlistModal from './components/WatchlistModal.vue';
import ErrorPage from './components/ErrorPage.vue';
import { unauthorized } from './js/api';

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
