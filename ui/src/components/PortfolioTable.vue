<template>
  <!-- Custom search input (Bootstrap Table will reposition it into the toolbar) -->
  <input type="search" id="customSearch" class="form-control" />

  <!-- Bootstrap Table — all data-* attributes preserved exactly as before -->
  <div class="row">
    <div class="col-12">
      <table
        ref="tableEl"
        class="table-sm table-striped caption-top"
        id="table"
        data-auto-refresh="true"
        data-auto-refresh-interval="300"
        data-auto-refresh-status="false"
        data-url="portfolio"
        data-show-refresh="true"
        data-show-columns-toggle-all="true"
        data-show-columns="true"
        data-search="true"
        data-show-footer="true"
        data-sort-name="percent_change"
        data-detail-view="true"
        data-detail-view-icon="true"
        data-detail-formatter="detailFormatter"
        data-buttons-align="start"
        data-regex-search="true"
        data-search-selector="#customSearch"
        data-sort-order="desc"
        data-row-style="watchListStyle"
        data-buttons="buttons"
        data-buttons-prefix="btn-sm btn"
        data-sticky-header="true"
      >
        <thead>
          <tr>
            <th data-field="symbol" data-formatter="symbolFormatter" data-sortable="true">Symbol</th>
            <th
              data-field="percent_change"
              data-footer-formatter="totalDayPercent"
              data-formatter="roundPercent"
              data-cell-style="cellStyle"
              data-sortable="true"
            >% Change</th>
            <th
              data-visible="false"
              data-field="principle_change"
              data-footer-formatter="totalPercent"
              data-formatter="roundPercent"
              data-cell-style="cellStyle"
              data-sortable="true"
            >% PChange</th>
            <th
              data-visible="false"
              data-field="change"
              data-formatter="round"
              data-cell-style="cellStyle"
              data-sortable="true"
            >Change</th>
            <th data-field="last_price" data-formatter="round" data-sortable="true">Last</th>
            <th data-field="cost" data-formatter="round" data-sortable="true">Cost</th>
            <th
              data-visible="false"
              data-field="total_cost"
              data-sortable="true"
              data-formatter="bigNum"
              data-footer-formatter="totalPriceNoStyle"
            >Total Cost</th>
            <th data-field="quantity" data-sortable="true">Qty</th>
            <th
              data-field="day_val"
              data-footer-formatter="totalPrice"
              data-cell-style="cellStyle"
              data-sortable="true"
            >Day's Value</th>
            <th
              data-field="gain"
              data-formatter="roundPercent"
              data-footer-formatter="gainTotal"
              data-cell-style="cellStyle"
              data-sortable="true"
            >Gain %</th>
            <th
              data-field="total_change"
              data-footer-formatter="totalPrice"
              data-formatter="bigNum"
              data-cell-style="cellStyle"
              data-sortable="true"
            >Profit/Loss</th>
            <th data-field="total_val" data-footer-formatter="totalPrice" data-formatter="bigNum" data-sortable="true">Value</th>
            <th
              data-visible="false"
              data-field="weight"
              data-formatter="roundPercent"
              data-sortable="true"
            >Weight</th>
          </tr>
        </thead>
        <tbody class="table-group-divider"></tbody>
        <tfoot class="table-group-divider"></tfoot>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';

/**
 * Wrapper component for the Bootstrap Table portfolio grid.
 * The table initialisation lifecycle is delegated to app.js
 * (which calls bootstrapTable() after the component mounts and
 * all window.* formatters are registered by table.js).
 */

const tableEl = ref(null);

onMounted(() => {
    // Signal to app.js that the table DOM is ready.
    // app.js listens for this event (or falls back to $(document).ready).
    document.dispatchEvent(new CustomEvent('portfolio-table-mounted'));
});
</script>
