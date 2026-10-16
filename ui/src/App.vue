<template>
  <DarkModeToggle />
  <div class="container-fluid">
    <TrendsChart />
    <PortfolioTable />
  </div>
  <WatchlistModal />
</template>

<script setup>
import DarkModeToggle from './components/DarkModeToggle.vue';
import TrendsChart from './components/TrendsChart.vue';
import PortfolioTable from './components/PortfolioTable.vue';
import WatchlistModal from './components/WatchlistModal.vue';

/** Root application component — composes all page-level Vue components. */
</script>
