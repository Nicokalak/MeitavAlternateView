function totalPercent (data) {
    let daysVal = round(data.map(function (row) {
        return row['Day\'s Value'];
    }).reduce(function (sum, i) {
        return Number.parseFloat(sum + i);
    }, 0))
    let avgcost = calcAvgCost(data);

    let result = (daysVal / avgcost) * 100 ;
    if (result > 0) {
        return '<span class="text-success">' + roundPercent(result) +'</span>';
    } else if (result < 0) {
        return '<span class="text-danger">' + roundPercent(result) +'</span>';
    } else { // result 0
        return roundPercent(result);
    }
}

function calcAvgCost(data) {
    return round(data.map(function (row) {
        return row['Average Cost'] * row['Qty'];
    }).reduce(function (sum, i) {
        return Number.parseFloat(sum + i);
    }, 0))
}
function detailFormatter(index, row) {
    let html = '<div class="container-fluid">' +
        '<div class="row justify-content-start" id="ticker-' + row.Symbol +'"></div>' +
        '<div class="row justify-content-start" id="ticker-' + row.Symbol +'-link"></div>' +
        '</div>'
    $.get("ticker/" + row.Symbol, function (stock) {
        let container = $("#ticker-" + row.Symbol);
        container.append('<dl class="row">'
            + getDetailedRow('day high', stock['regularMarketDayHigh'], round )
            + getDetailedRow('52w high',  stock['fiftyTwoWeekHigh'], round )
            + getDetailedRow('52d avg', stock['fiftyDayAverage'], round )
            + getDetailedRow('day low', stock['regularMarketDayLow'], round )
            + getDetailedRow('52w low', stock['fiftyTwoWeekLow'], round )
            + getDetailedRow('prev close', stock['regularMarketPreviousClose'], round )
            + getDetailedRow('vol', stock['regularMarketVolume'], bigNum )
            + getDetailedRow('change', stock[market_state  + 'MarketChange'] * row.Qty, round, true )
            + getDetailedRow('change (%)', (stock[market_state + 'MarketChangePercent']), roundPercent, true )
            + '</dl>'
        )
        $("#ticker-" + row.Symbol + '-link').html(
            '<a title="more info..." class="link-primary fa-lg" target="_blank" href="https://finance.yahoo.com/quote/' + row.Symbol +'"><svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" class="bi bi-arrow-up-right-circle" viewBox="0 0 16 16">\n' +
            '  <path fill-rule="evenodd" d="M1 8a7 7 0 1 0 14 0A7 7 0 0 0 1 8zm15 0A8 8 0 1 1 0 8a8 8 0 0 1 16 0zM5.854 10.803a.5.5 0 1 1-.708-.707L9.243 6H6.475a.5.5 0 1 1 0-1h3.975a.5.5 0 0 1 .5.5v3.975a.5.5 0 1 1-1 0V6.707l-4.096 4.096z"/>\n' +
            '</svg></a>')
    });
    return html;
}
function getDetailedRow(key, val, formater, color=false) {
    let clazz = "";
    if (color) {
        if(val > 0) {
            clazz = "text-success";
        } else if (val < 0) {
            clazz = "text-danger";
        }
    }

    return '<dt class="col-2">' + key + '</dt>' +
        '<dd class="col-2"><span class="' + clazz + '">'+ (formater !== undefined ? formater(val) : val) + '</span></dd>' +
        '<div class="w-100 d-md-none d-sm-block"></div>'
}

function cellStyle(value) {
    if (value > 0) {
        return { classes: 'table-success' };
    } else if (value < 0) {
        return { classes: 'table-danger' };
    } else {
        return { classes: '' }
    }
}

function round(value) {
    return Math.round((value + Number.EPSILON) * 100) / 100;
}

function roundPercent(value) {
    return round(value) + " %";
}
function bigNum(value) {
    return value.toString().replace(/\B(?<!\.\d*)(?=(\d{3})+(?!\d))/g, ",") + " $";

}

function gainTotal(data) {
    let totalProfit = round(data.map(function (row) {
        return row['Profit/ Loss'];
    }).reduce(function (sum, i) {
        return Number.parseFloat(sum + i);
    }, 0))
    let avgCost = calcAvgCost(data)

    let result = (totalProfit / avgCost) * 100 ;
    if (result > 0) {
        return '<span class="text-success">' + roundPercent(result) +'</span>';
    } else if (result < 0) {
        return '<span class="text-danger">' + roundPercent(result) +'</span>';
    } else { // result 0
        return roundPercent(result);
    }
}

function totalPrice(data) {
    let field = this.field;
    let result = round(data.map(function (row) {
        return row[field];
    }).reduce(function (sum, i) {
        return Number.parseFloat(sum + i);
    }, 0))
    if (result > 0) {
        return '<span class="text-success">' + bigNum(result) +'</span>';
    } else if (result < 0) {
        return '<span class="text-danger">' + bigNum(result) +'</span>';
    } else { // result 0
        return result;
    }
}