// ─── 1. Styles ───────────────────────────────────────────────────────────────
import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap-icons/font/bootstrap-icons.css';
import '@fortawesome/fontawesome-free/css/all.min.css';
import '../css/main.css';

// ─── 2. Core Libraries ──────────────────────────────────────────────────────
import * as bootstrap from 'bootstrap';
import { Chart, registerables } from 'chart.js';
import 'chartjs-adapter-date-fns';

Chart.register(...registerables);

// Bootstrap JS is needed for modals/dropdowns — attach to window for Bootstrap's
// internal use (data-bs-toggle attributes require bootstrap on window/global).
window.bootstrap = bootstrap;

// ─── 3. Initialise Theme Before Mount ────────────────────────────────────────
import './darkmode.js';

// ─── 4. Mount Vue App ────────────────────────────────────────────────────────
import { createApp } from 'vue';
import App from '../App.vue';

createApp(App).mount('#app');
