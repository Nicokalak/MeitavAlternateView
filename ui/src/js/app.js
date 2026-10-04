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

$(function () {
    init_chart();
    $('#table').bootstrapTable({
        onLoadSuccess: function () {
            $.get("marketState", function (trendObj) {
                trend_stats(trendObj);
            }).done(function () {
                update_trends();
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
        buttonsOrder: ['refresh', 'autoRefresh', 'columns', 'toggleWatchListBtn'],
        classes: ['table', 'table-sm', 'table-striped', 'table-hover', 'caption-top'],

    });
    $('.columns-start.btn-group').prepend($('#customSearch').detach());

    var marketStatusContainer = document.getElementById('market-status-container');
    if (window.ResizeObserver && marketStatusContainer) {
        new ResizeObserver(updateStickyOffsets).observe(marketStatusContainer);
    }
    $(window).on('resize scroll', updateStickyOffsets);
    updateStickyOffsets();
});
