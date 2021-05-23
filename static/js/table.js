
function detailFormatter(index, row) {
    let html = '<div class="container" id="ticker-' + row.Symbol +'"></div>'
    $.get("ticker/" + row.Symbol, function (stock) {
        let container = $("#ticker-" + row.Symbol);
        container.append('<div class="row">'
            + getDetailedRow('day high', stock['regularMarketDayHigh'], round )
            + getDetailedRow('52w high',  stock['fiftyTwoWeekHigh'], round )
            + getDetailedRow('52d avg', stock['fiftyDayAverage'], round )
            + '</div><div class="row">'
            + getDetailedRow('day low', stock['regularMarketDayLow'], round )
            + getDetailedRow('52w low', stock['fiftyTwoWeekLow'], round )
            + getDetailedRow('prev close', stock['regularMarketPreviousClose'], round )
            + '</div><div class="row">'
            + getDetailedRow('vol', stock['regularMarketVolume'], bigNum )
            + getDetailedRow(market_state + ' change', stock[market_state  + 'MarketChange'] * row.Qty, round, true )
            + getDetailedRow(market_state + ' % change', (stock[market_state + 'MarketChangePercent']), roundPercent, true )
            + '</div>')
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
    return '<div class="col-sm-4"><b>' + key  + ':</b> <span class="' + clazz + '">'
        + (formater !== undefined ? formater(val) : val) + '</span></div>'
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