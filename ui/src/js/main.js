// ─── 1. Styles (static imports are fine — CSS has no jQuery dependency) ───────
import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap-table/dist/bootstrap-table.min.css';
import 'bootstrap-table/dist/extensions/sticky-header/bootstrap-table-sticky-header.min.css';
import 'bootstrap-icons/font/bootstrap-icons.css';
import '@fortawesome/fontawesome-free/css/all.min.css';
import '../css/main.css';

// ─── 2. Core libraries ────────────────────────────────────────────────────────
import $ from 'jquery';
import * as Popper from '@popperjs/core';
import * as bootstrap from 'bootstrap';
import * as XLSX from 'xlsx';
import moment from 'moment';
import 'moment/dist/locale/en-gb';
import { Chart, registerables } from 'chart.js';
import 'chartjs-adapter-moment';

Chart.register(...registerables);

// ─── 3. Expose globals BEFORE any jQuery plugin loads ─────────────────────────
// jQuery plugins (tableExport, bootstrap-table extensions) reference jQuery/$
// as a global at IIFE eval time. Static ESM imports are hoisted, so we use
// top-level await + dynamic import() to guarantee the assignment above runs first.
window.$ = $;
window.jQuery = $;
window.Popper = Popper;
window.bootstrap = bootstrap;
window.XLSX = XLSX;
window.moment = moment;
window.Chart = Chart;


// ─── 4. jQuery plugins — dynamic imports so window.jQuery is already set ──────
await import('bootstrap-table');
await import('bootstrap-table/dist/extensions/auto-refresh/bootstrap-table-auto-refresh.min.js');
await import('tableexport.jquery.plugin/tableExport.min.js');
await import('bootstrap-table/dist/extensions/export/bootstrap-table-export.min.js');
await import('bootstrap-table/dist/extensions/sticky-header/bootstrap-table-sticky-header.min.js');

// ─── 5. Application modules ───────────────────────────────────────────────────
await import('./darkmode.js');
await import('./table.js');
await import('./trendschart.js');
await import('./edit-watchlist.js');
await import('./app.js');
