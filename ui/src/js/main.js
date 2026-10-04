// ─── 1. Styles ───────────────────────────────────────────────────────────────
import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap-table/dist/bootstrap-table.min.css';
import 'bootstrap-table/dist/extensions/sticky-header/bootstrap-table-sticky-header.min.css';
import 'bootstrap-icons/font/bootstrap-icons.css';
import '@fortawesome/fontawesome-free/css/all.min.css';
import '../css/main.css';

// ─── 2. Core Libraries & Global Assignment ───────────────────────────────────
import $ from 'jquery';
import * as Popper from '@popperjs/core';
import * as bootstrap from 'bootstrap';

import { Chart, registerables } from 'chart.js';
import 'chartjs-adapter-date-fns';

Chart.register(...registerables);

// Expose globals so legacy jQuery plugins can find them at evaluation time
window.$ = window.jQuery = $;
window.Popper = Popper;
window.bootstrap = bootstrap;

window.Chart = Chart;

// ─── 3. Load Core Bootstrap Table First, Then Extensions ──────────────────────
// Load core bootstrap-table sequentially first so it registers on jQuery
await import('bootstrap-table');

// Now that core is guaranteed to be loaded, load extensions concurrently
await Promise.all([
    import('bootstrap-table/dist/extensions/auto-refresh/bootstrap-table-auto-refresh.min.js'),
    import('bootstrap-table/dist/extensions/sticky-header/bootstrap-table-sticky-header.min.js'),
]);

await Promise.all([
    import('./darkmode.js'),
    import('./table.js'),
    import('./trendschart.js'),
    import('./edit-watchlist.js'),
    import('./app.js'),
]);