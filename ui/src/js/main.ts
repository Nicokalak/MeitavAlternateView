// ─── 1. Styles ───────────────────────────────────────────────────────────────
import 'bootstrap/dist/css/bootstrap.min.css';
import '../css/main.css';

// ─── 2. Core Libraries ──────────────────────────────────────────────────────
// Importing the Bootstrap plugins registers their data-bs-* delegated handlers
// (data-bs-toggle="modal" / "dropdown", data-bs-dismiss="modal") on the document.
import 'bootstrap/js/dist/dropdown';
import 'bootstrap/js/dist/modal';
import {
  Chart,
  LineController,
  LineElement,
  LinearScale,
  PointElement,
  TimeScale,
  Tooltip,
} from 'chart.js';
import 'chartjs-adapter-date-fns';

Chart.register(LineController, LineElement, PointElement, LinearScale, TimeScale, Tooltip);

// ─── 3. Initialise Theme Before Mount ────────────────────────────────────────
import './darkmode';

// ─── 4. Mount Vue App ────────────────────────────────────────────────────────
import { createApp } from 'vue';
import App from '../App.vue';

createApp(App).mount('#app');
