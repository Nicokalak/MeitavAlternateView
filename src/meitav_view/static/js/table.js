function totalPercent (data) {
    let daysVal = round(data.filter(isInPortfolio).map(function (row) {
        return row.day_val;
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

function isInPortfolio(row) {
   return row.type.toLowerCase() !== "w";
}

function totalDayPercent (data) {
    let daysVal = round(data.filter(isInPortfolio).map(function (row) {
        return row.day_val;
    }).reduce(function (sum, i) {
        return Number.parseFloat(sum + i);
    }, 0))
    let startPrice = calcStartPrice(data);

    let result = (daysVal / startPrice) * 100 ;
    if (result > 0) {
        return '<span class="text-success">' + roundPercent(result) +'</span>';
    } else if (result < 0) {
        return '<span class="text-danger">' + roundPercent(result) +'</span>';
    } else { // result 0
        return roundPercent(result);
    }
}

function calcAvgCost(data) {
    return round(data.filter(isInPortfolio).map(function (row) {
        return row.total_val - row.total_change;
    }).reduce(function (sum, i) {
        return Number.parseFloat(sum + i);
    }, 0))
}

function calcStartPrice(data) {
    return round(data.filter(isInPortfolio).map(function (row) {
        let q = row.type.toLowerCase() === "e" ? row.quantity : row.quantity * 100
        return (row.last_price - row.change) * q;
    }).reduce(function (sum, i) {
        return Number.parseFloat(sum + i);
    }, 0))
}

function detailFormatter(index, row) {
    let html = '<div class="container-fluid">' +
        '<div class="row justify-content-start" id="ticker-' + row.symbol +'"></div>' +
        '<div class="row justify-content-start" id="ticker-' + row.symbol +'-link"></div>' +
        '</div>'
    $.get("ticker/" + row.symbol, function (detailedStock) {
        let state = detailedStock['market-state-4calc'].toLowerCase();
        let stock = detailedStock['stock'].api_data;
        let container = $("#ticker-" + row.symbol);
        container.append('<dl class="row">'
            + getDetailedRow('52w range', getRange(round(stock['fiftyTwoWeekLow']),
                round(stock['fiftyTwoWeekHigh']), round(stock[state + 'MarketPrice']) ) )
            + getDetailedRow('price', (stock[state + 'MarketPrice']), round, false )
            + getDetailedRow('52d avg', stock['fiftyDayAverage'], round )
            + getDetailedRow('day range', getRange(round(stock['regularMarketDayLow']),
                round(stock['regularMarketDayHigh']), round(stock[state + 'MarketPrice']) ))
            + getDetailedRow('prev close', stock['regularMarketPreviousClose'], round )
            + getDetailedRow('volume', stock['regularMarketVolume'], bigNum )
            + getDetailedRow('volume 10D', stock['averageDailyVolume10Day'], bigNum )
            + getDetailedRow('volume 3M', stock['averageDailyVolume3Month'], bigNum )
            + getDetailedRow('change', stock[state  + 'MarketChange'] * row.quantity, round, true )
            + getDetailedRow('change (%)', (stock[state + 'MarketChangePercent']), roundPercent, true )
            + (stock['averageAnalystRating'] ? getDetailedRow('rating', (stock['averageAnalystRating']), undefined, false ) : "")
            + getDetailedRow('earnings', stock['earningsTimestamp'], (time) => (time ? moment(time * 1000).locale('en-gb').format('l LT') : ""), false)
            + getDetailedRow('trend ratio', (stock['regularMarketVolume'] /  stock['averageDailyVolume3Month']) * 100, roundPercent)
            + '</dl>'
        )
        $("#ticker-" + row.symbol + '-link').html(
            '<a title="more info..." class="link-primary fa-lg" target="_blank" href="https://finance.yahoo.com/quote/' + row.symbol +'"><svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" class="bi bi-arrow-up-right-circle" viewBox="0 0 16 16">\n' +
            '  <path fill-rule="evenodd" d="M1 8a7 7 0 1 0 14 0A7 7 0 0 0 1 8zm15 0A8 8 0 1 1 0 8a8 8 0 0 1 16 0zM5.854 10.803a.5.5 0 1 1-.708-.707L9.243 6H6.475a.5.5 0 1 1 0-1h3.975a.5.5 0 0 1 .5.5v3.975a.5.5 0 1 1-1 0V6.707l-4.096 4.096z"/>\n' +
            '</svg></a>')
    });
    return html;
}

function getRange(min, max, val) {
    return '<div class="container-fluid p-0">' +
        '<div class="row">' +
        '<div class="col-3 pe-0">' + min +'</div>' +
        '<div class="col-6"><input disabled="" type="range" class="form-range range"' +
        ' value="' + val + '" min="' + min + '" max="' + max +'"></div>' +
        '<div class="col-3 ps-0">'+ max +'</div>' +
        '</div></div>'
}

function shouldShowEarning(timestmp) {
    let days = daysCountToEarn(timestmp);
    return days >= 0 && days < 14
}

function daysCountToEarn(timestmp) {
    let tdiff = new Date(timestmp) - new Date();
    return Math.ceil(tdiff / (1000 * 60 * 60 * 24));
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

    return '<dt class="col-xl-2 col-md-3 col-2">' + key + '</dt>' +
        '<dd class="col-xl-2 col-md-3 col-3"><span class="' + clazz + '">'+ (formater !== undefined ? formater(val) : val) + '</span></dd>' +
        '<div class="w-100 d-md-none d-sm-block"></div>'
}

function cellStyle(value, row) {
    if (isInPortfolio((row))) {
        if (value > 0) {
            return {classes: 'text-success'};
        } else if (value < 0) {
            return {classes: 'text-danger'};
        } else {
            return {classes: ''}
        }
    } else {
        if (value > 0) {
            return {classes: 'text-success'};
        } else if (value < 0) {
            return {classes: 'text-danger'};
        } else {
            return {classes: ''}
        }
    }
}

function round(value) {
    return Math.round((value + Number.EPSILON) * 100) / 100;
}

function roundPercent(value) {
    return isNaN(value)? "-" : round(value) + "%";
}
function bigNum(value) {
    if (isNaN(value)) return "-"
    return round(value).toLocaleString("en-US");
}

function symbolFormatter(value, row) {
    let d = '<div class="d-flex">' + value +'</div>'

    function getSymbolTag(classses, text) {
        return '<div><span class="badge ' + classses + '">' + text + '</span></div>';
    }

    if (row.type === 'O') {
        d += getSymbolTag('text-bg-danger', row.p_or_c + row.strike + ' ' + row.expiration)
    }

    if (shouldShowEarning(row.api_data['earningsTimestamp'] * 1000)) {
        d += getSymbolTag("text-bg-info", moment(row.api_data['earningsTimestamp'] * 1000).locale("en-gb").calendar());
    }

    if (row.api_data['dividendDate'] !== undefined && row.api_data['trailingAnnualDividendRate'] > 0 ) {
        let divAmount = row.api_data['trailingAnnualDividendRate'] / 4;
        d += getSymbolTag("text-bg-success", moment(row.api_data['dividendDate'] * 1000).format('DD/MM') + ' '
            + round(divAmount) + 'x' + row.quantity + '=' + round(divAmount * row.quantity) + '$')
    }

    return d;
}

function gainTotal(data) {
    let totalProfit = round(data.filter(isInPortfolio).map(function (row) {
        return row.total_change;
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
function totalPriceNoStyle(data) {
    return totalPrice(data, this.field, false)
}
function totalPrice(data, f, style = true) {
    let field = f ? f : this.field;
    let result = round(data.filter(isInPortfolio).map(function (row) {
        return row[field];
    }).reduce(function (sum, i) {
        return Number.parseFloat(sum + i);
    }, 0));
    if (style && result > 0) {
        return '<span class="text-success">' + bigNum(result) +'</span>';
    } else if (style && result < 0) {
        return '<span class="text-danger">' + bigNum(result) +'</span>';
    } else { // result 0
        return bigNum(result);
    }
}

function watchListStyle(row, index) {
    if (!isInPortfolio(row)) {
        return {
            classes: "table-info bg-opacity-75"
        }
    }
    return {
        classes: ""
    }
}

function buttons () {
    return {
        toggleWatchListBtn: {
            text: 'toggle watch list',
            icon: 'bi-toggle-off',
            event: function () {
                this["watchlistToggle"] = !this["watchlistToggle"]
                let toggle = this["watchlistToggle"]
                $('#table').bootstrapTable('filterBy', {
                    "type":  this["watchlistToggle"] ? ["E", "O"] : ["E", "O", "W"]
                });
                if (toggle) {
                    $('[name=toggleWatchListBtn] > i').removeClass('bi-toggle-off').addClass('bi-toggle-on');
                } else {
                    $('[name=toggleWatchListBtn] > i').removeClass('bi-toggle-on').addClass('bi-toggle-off');
                }
            },
            attributes: {
                title: 'toggle watch list'
            }
        },
        editWatchListBtn: {
            text: 'edit watchlist',
            icon: 'bi bi-pencil',
            attributes: {
                'title': 'edit watch list',
                'data-bs-toggle': "modal",
                'data-bs-target': "#editWatchListModal"
            }
        }
    }
}


