function trends() {
    $.get("trends", function (trends) {
        const down = (ctx, value) => ctx.p0.parsed.y > ctx.p1.parsed.y ? value : undefined;
        const up = (ctx, value) => ctx.p0.parsed.y <= ctx.p1.parsed.y ? value : undefined;
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