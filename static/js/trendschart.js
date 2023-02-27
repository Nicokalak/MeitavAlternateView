function createSpan(val, val2) {
    function getClass(value) {
        if (value > 0) {
            return "success"
        } else if (value < 0) {
            return "danger"
        } else { // == 0
            return "secondary"
        }
    }

    return '<span class="state-badge state-badge-' + getClass(val) + ' position-relative">' +  val +
        '<span class="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-' + getClass(val2) + '">' +
        + val2 +'</span></span>';

}

function trend_stats(trendObj) {
    let totalBadge = createSpan(round(trendObj['trend']), round(trendObj['yahoo_trend']));
    let market_state = trendObj['marketState'].toLowerCase();
    $("#market_status").html(market_state.charAt(0).toUpperCase() + market_state.slice(1) + ' market  ' +  totalBadge );
    $("#market_status_total").text(round(trendObj['trend']));
    $("#top-gainer").text(trendObj['top-gainer'].symbol);
    $("#top-gainer-percent").text(trendObj['top-gainer%'].symbol);
    $("#top-mover").text(trendObj['top-mover'].symbol);
    $("#top-loser").text(trendObj['top-loser'].symbol);
    $("#top-loser-percent").text(trendObj['top-loser%'].symbol);
    $("#watchlist-trend").text(round(trendObj['watchlist_trend']) + '%');
    $("#up-down > .text-success").text(round(trendObj['up-down']['up']));
    $("#up-down > .text-danger").text(round(trendObj['up-down']['down']));
    $("#market-stats").show(200);
    console.log(trendObj);
}
const trendsObj = {
    "PRE_histo": {},
    "REGULAR_histo": {},
    "POST_histo": {}
}
let chart;
function update_trends() {
    $.get("trends", function (trends) {
        for (let trendsKey in trends) {
            for (let t in trends[trendsKey]) {
                trendsObj[trendsKey][t] = trends[trendsKey][t];
            }
        }
        chart.update();
    });
}

function init_chart() {
    const down = (ctx) => ctx.p0.parsed.y > ctx.p1.parsed.y ? 'rgb(213, 76, 76)' : undefined;
    const up = (ctx) => ctx.p0.parsed.y < ctx.p1.parsed.y ? 'rgb(0, 139, 0)' : undefined;
    const skipped = (ctx, value) => new Date(ctx.p1.parsed.x) - new Date(ctx.p0.parsed.x) > 3.6e+7 ? value : undefined;
    const data = {
        datasets: [
            {
                label: "PRE Market",
                data: trendsObj["PRE_histo"],
                borderColor: 'rgb(111, 105, 172)',
                backgroundColor: 'rgb(111, 105, 172)',
                pointStyle: 'rectRounded',
                tension: 0.3,
                segment: {
                    borderColor: ctx => skipped(ctx, 'rgba(0,0,0,0.2)') || up(ctx) || down(ctx),
                    borderDash: ctx => skipped(ctx, [6, 6]),
                }
            },
            {
                label: "Regular Market",
                data: trendsObj["REGULAR_histo"],
                borderColor: 'rgb(190,190,190)',
                backgroundColor: 'rgb(190,190,190)',
                pointStyle: 'rectRounded',
                tension: 0.3,
                segment: {
                    borderColor: ctx => skipped(ctx, 'rgba(0,0,0,0.2)') || up(ctx) || down(ctx),
                    borderDash: ctx => skipped(ctx, [6, 6]),
                }
            },
            {
                label: "POST Market",
                data: trendsObj["POST_histo"],
                borderColor: 'rgb(72,64,159)',
                backgroundColor: 'rgb(72,64,159)',
                pointStyle: 'rectRounded',
                tension: 0.3,
                segment: {
                    borderColor: ctx => skipped(ctx, 'rgba(0,0,0,0.2)') || up(ctx) || down(ctx),
                    borderDash: ctx => skipped(ctx, [6, 6]),
                }
            }
        ]
    };
    const config = {
        type: 'line',
        data: data,
        options: {
            scales: {
                x: {
                    display: false,
                    type: 'time',
                    time: {
                        parser: 'YYYYMMDDTHH:mm:ss',
                        minUnit: 'minute'
                    },
                },
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    };
    chart = new Chart($('#trends'), config);
    update_trends();

}
