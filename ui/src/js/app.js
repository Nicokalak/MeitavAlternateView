function updateStickyOffsets() {
    var marketStatusHeight = $('#market-status-container').outerHeight() || 0;
    var toolbarHeight = $('.fixed-table-toolbar').outerHeight() || 0;

    document.documentElement.style.setProperty('--toolbar-sticky-top', marketStatusHeight + 'px');

    var totalOffset = marketStatusHeight + toolbarHeight;
    var table = $('#table').data('bootstrap.table');
    if (table) {
        table.options.stickyHeaderOffsetY = totalOffset;
    }
    $('.sticky-header-container').css('top', totalOffset + 'px');
}

function initBootstrapTable() {
    if (typeof window.init_chart === 'function') {
        window.init_chart();
    }
    $('#table').bootstrapTable({
        onLoadSuccess: function () {
            $.get('marketState', function (trendObj) {
                if (typeof window.trend_stats === 'function') {
                    window.trend_stats(trendObj);
                }
            }).done(function () {
                if (typeof window.update_trends === 'function') {
                    window.update_trends();
                }
                updateStickyOffsets();
            }).fail(function (jqXHR) {
                console.error('Failed to load market state:', jqXHR.status, jqXHR.statusText);
            });
        },
        onLoadError: function (status) {
            if (status === 401) {
                window.location.reload();
            }
        },
        onSearch: function (name, e, c) {
            if (e.data.length === 0) {
                $(e.$body).find('tr.no-records-found > td').append(
                    ' for <a target="_blank" href="https://finance.yahoo.com/quote/' + name + '">' + name + '</a>');
            }
        },
        buttonsOrder: ['refresh', 'autoRefresh', 'columns', 'toggleWatchListBtn', 'editWatchListBtn'],
        classes: ['table', 'table-sm', 'table-striped', 'table-hover', 'caption-top'],
    });
    $('.columns-start.btn-group').prepend($('#customSearch').detach());

    var marketStatusContainer = document.getElementById('market-status-container');
    if (window.ResizeObserver && marketStatusContainer) {
        new ResizeObserver(updateStickyOffsets).observe(marketStatusContainer);
    }
    $(window).on('resize scroll', updateStickyOffsets);
    updateStickyOffsets();
}

// Initialise when PortfolioTable.vue signals the <table> element is mounted.
// Falls back to direct execution if already mounted or DOMContentLoaded.
if (document.getElementById('table') && typeof window.init_chart === 'function') {
    initBootstrapTable();
} else {
    document.addEventListener('portfolio-table-mounted', initBootstrapTable, { once: true });
    window.addEventListener('DOMContentLoaded', () => {
        if (!document.querySelector('.bootstrap-table') && document.getElementById('table')) {
            initBootstrapTable();
        }
    }, { once: true });
}
