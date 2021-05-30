
function detailFormatter(index, row) {
    let html = '<div class="container-fluid"><div class="row justify-content-start" id="ticker-' + row.Symbol +'"></div></div>'
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
    let a = round(data.map(function (row) {
        return row['Profit/ Loss'];
    }).reduce(function (sum, i) {
        return Number.parseFloat(sum + i);
    }, 0))
    let b = round(data.map(function (row) {
        return row['Average Cost'] * row['Qty'];
    }).reduce(function (sum, i) {
        return Number.parseFloat(sum + i);
    }, 0))

    let result = (a / b) * 100 ;
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