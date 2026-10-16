// ─── 1. Styles ───────────────────────────────────────────────────────────────
import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap-table/dist/bootstrap-table.min.css';
import 'bootstrap-table/dist/extensions/sticky-header/bootstrap-table-sticky-header.min.css';
import 'bootstrap-icons/font/bootstrap-icons.css';
import '@fortawesome/fontawesome-free/css/all.min.css';
import '../css/main.css';

// ─── 2. Core Libraries & Global Assignment ────────────────────────────────────
import $ from 'jquery';
import * as Popper from '@popperjs/core';
import * as bootstrap from 'bootstrap';

import { Chart, registerables } from 'chart.js';
import 'chartjs-adapter-date-fns';

// Initialise theme before mounting to prevent flash of incorrect theme
import './darkmode.js';

Chart.register(...registerables);

// Expose globals so legacy jQuery plugins can find them at evaluation time
window.$ = window.jQuery = $;
window.Popper = Popper;
window.bootstrap = bootstrap;
window.Chart = Chart;

// ─── 3. Load Core Bootstrap Table First, Then Extensions ──────────────────────
await import('bootstrap-table');

await Promise.all([
    import('bootstrap-table/dist/extensions/auto-refresh/bootstrap-table-auto-refresh.min.js'),
    import('bootstrap-table/dist/extensions/sticky-header/bootstrap-table-sticky-header.min.js'),
]);

// ─── 4. Load Table Formatters (registers window.* before Vue mounts) ─────────
await import('./table.js');

// ─── 5. Register Bootstrap Table init listener BEFORE mounting Vue ────────────
// This ensures the 'portfolio-table-mounted' event from PortfolioTable.vue's
// onMounted hook is caught even if it fires synchronously during mount.
await import('./app.js');

// ─── 6. Mount Vue App ─────────────────────────────────────────────────────────
import { createApp } from 'vue';
import App from '../App.vue';

const app = createApp(App);
app.mount('#app');
