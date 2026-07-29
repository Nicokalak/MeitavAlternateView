#!/bin/sh
mkdir -p dist/js dist/css dist/css/fonts dist/webfonts dist/favicon
cp -r src/* dist/

# CSS
cp node_modules/bootstrap/dist/css/bootstrap.min.css dist/css/
cp node_modules/bootstrap-icons/font/bootstrap-icons.css dist/css/
cp -r node_modules/bootstrap-icons/font/fonts/* dist/css/fonts/
cp node_modules/@fortawesome/fontawesome-free/css/all.min.css dist/css/
cp -r node_modules/@fortawesome/fontawesome-free/webfonts/* dist/webfonts/
cp node_modules/bootstrap-table/dist/bootstrap-table.min.css dist/css/

# JS
cp node_modules/jquery/dist/jquery.min.js dist/js/
cp node_modules/@popperjs/core/dist/umd/popper.js dist/js/
cp node_modules/bootstrap/dist/js/bootstrap.bundle.min.js dist/js/
cp node_modules/bootstrap-table/dist/bootstrap-table.min.js dist/js/
cp node_modules/bootstrap-table/dist/extensions/auto-refresh/bootstrap-table-auto-refresh.min.js dist/js/
cp node_modules/bootstrap-table/dist/extensions/export/bootstrap-table-export.min.js dist/js/
cp node_modules/tableexport.jquery.plugin/tableExport.min.js dist/js/
cp node_modules/xlsx/dist/xlsx.full.min.js dist/js/
cp node_modules/chart.js/dist/chart.umd.min.js dist/js/
cp node_modules/moment/min/moment-with-locales.min.js dist/js/
cp node_modules/chartjs-adapter-moment/dist/chartjs-adapter-moment.min.js dist/js/

# Always copy compiled assets to backend static folder
STATIC_TARGET="../src/meitav_view/static"
mkdir -p "$STATIC_TARGET"
cp -r dist/* "$STATIC_TARGET/"
