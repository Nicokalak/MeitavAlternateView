// esbuild inject shim — used by Vite's dep pre-bundler (optimizeDeps.esbuildOptions.inject).
// Exporting $ and jQuery as named bindings causes esbuild to replace all unresolved
// global references to `$` / `jQuery` inside pre-bundled deps (e.g. tableExport.min.js).
import $ from 'jquery';
export { $ as jQuery, $ as $ }; // eslint-disable-line import/no-duplicates
