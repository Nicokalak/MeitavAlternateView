function trend_stats(trendObj) {
    let span;
    if (trendObj.trend > 0) {
        span = '<span class="badge bg-success">' + round(trendObj.trend) + '</span>';
    } else if (trendObj.trend < 0) {
        span = '<span class="badge bg-danger">' + round(trendObj.trend) + '</span>';
    } else { // == 0
        span = '<span class="badge bg-secondary">' + round(trendObj.trend) + '</span>';
    }
    market_state = trendObj.marketState.toLowerCase();
    $("#market_status").html(market_state.charAt(0).toUpperCase() + market_state.slice(1) + ' market  ' + span);
    $("#top-gainer").text(trendObj['top-gainer'].symbol);
    $("#top-mover").text(trendObj['top-mover'].symbol);
    $("#top-loser").text(trendObj['top-loser'].symbol);
    $("#market-stats").show(200);
    console.log(trendObj);
}

function trends() {
    $.get("trends", function (trends) {
        const down = (ctx, value) => ctx.p0.parsed.y > ctx.p1.parsed.y ? value : undefined;
        const up = (ctx, value) => ctx.p0.parsed.y < ctx.p1.parsed.y ? value : undefined;
        const data = {
            datasets: [{
                label: "trends",
                data: trends,
                segment: {
                    borderColor: ctx => up(ctx, 'rgba(72,141,22,0.2)') || down(ctx, 'rgb(234,15,15)'),
                }
            },]
        };
        const config = {
            type: 'line',
            data: data,
            options: {
                scales: {
                    x: {
                        display: false
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        };
        var myChart = new Chart(
            $('#trends'),
            config
        );
    });
}