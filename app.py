import http
import json
import logging
import os
from datetime import datetime, timedelta
from typing import List, Dict
import sys
import pandas as pd
import requests
from flask import Flask, send_from_directory, request, abort
from waitress import serve

from Stock import Stock
from TrendsPersist import TrendPersist

app = Flask(__name__, static_url_path='/static/')
stocks_cache: List[Stock] = list()
API = 'https://query2.finance.yahoo.com/v7/finance/quote?&symbols='
trends = {
    "PRE_histo": {},
    "REGULAR_histo": {},
    "POST_histo": {}
}


def load_config():
    with open(os.getenv("DEFAULT_CONF", "config.json"), 'r') as config_file:
        conf = json.load(config_file)
        config_file.close()
    return conf


def get_portfolio_table():
    try:
        attempts = 0
        r = requests.get(os.getenv('portfolio_link'),
                        headers={'User-Agent': 'Meitav-Viewer/{}'.format(os.getenv("HOSTNAME"))})
        while attempts < config.get('retry_attempts', 3) and r.status_code != http.HTTPStatus.OK.value:
            attempts += 1
            logger.error("failed to get portfolio from Meitav attempt {} stats {} {}"
                         .format(attempts, r.status_code, r.text))
            r = requests.get(os.getenv('portfolio_link'),
                             headers={'User-Agent': 'Meitav-Viewer/{}'.format(os.getenv("HOSTNAME"))})
        return r.text
    except ConnectionError as e:
        logger.error("failed to connect to meitav", e)


def add_trend(trends_obj, change_key):
    trends_obj['trend'] = 0
    trends_obj['watchlist_trend'] = 0
    m_state = trends_obj['marketState']
    state_histo = m_state + '_histo'
    watchlist_sum = 0
    watchlist_count = 0
    if m_state in ('CLOSED', 'PREPRE', 'POSTPOST'):
        return
    for s in stocks_cache:
        yahoo_symbol_data = s.api_data
        trends_obj['trend'] += s.day_val if s.type != "W" else 0
        if s.type == "W":
            watchlist_sum += s.percent_change
            watchlist_count += 1
            trends_obj['watchlist_trend'] = watchlist_sum / watchlist_count
        if change_key in yahoo_symbol_data:
            if s.type == "W":
                continue
            if s.type == "E":
                trends_obj['yahoo_trend'] += yahoo_symbol_data[change_key] * s.quantity
            elif m_state == "REGULAR":
                trends_obj['yahoo_trend'] += s.day_val
    trends_for_chart(state_histo, trends_obj['yahoo_trend'])
    persist.save()


def trends_for_chart(state_histo, histo_val):
    global trends
    curr_histo = trends[state_histo]

    to_delete = []
    for key, state_histo in trends.items():
        for date in state_histo.keys():
            if (datetime.now() - datetime.strptime(date, time_format)) > timedelta(days=1, seconds=43200):
                to_delete.append((key, date))
    for tup in to_delete:
        del trends[tup[0]][tup[1]]

    curr_histo[datetime.now().strftime(time_format)] = histo_val


def get_market_state_key():
    market_state = stocks_cache[0].api_data.get('marketState')
    return market_state.lower() if market_state.lower() in ("pre", "post", "regular") else "post"


@app.route('/marketState')
def get_market_state():
    if len(stocks_cache) == 0:
        abort(http.HTTPStatus.INTERNAL_SERVER_ERROR.value)

    result = {'marketState': stocks_cache[0].api_data.get('marketState'), 'trend': 0, 'yahoo_trend': 0}
    change = get_market_state_key() + 'MarketChange'
    change_per = get_market_state_key() + 'MarketChangePercent'
    add_trend(result, change)
    result['top-gainer'] = max(stocks_cache, key=lambda s: s.api_data.get(change, 0) * s.quantity)
    result['top-gainer%'] = max(stocks_cache, key=lambda s: s.api_data.get(change_per, 0))
    result['top-loser'] = min(stocks_cache, key=lambda s: s.api_data.get(change, 0) * s.quantity)
    result['top-loser%'] = min(stocks_cache, key=lambda s: s.api_data.get(change, 0))
    result['top-mover'] = max(stocks_cache, key=lambda s: s.api_data.get('regularMarketVolume', 0))
    result['up-down'] = {
        'up': len(list(filter(lambda sd: sd.gain is not None and sd.gain > 0, stocks_cache))),
        'down': len(list(filter(lambda sd: sd.gain is not None and sd.gain < 0, stocks_cache)))
    }
    result['trending'] = max(stocks_cache,
                             key=lambda s: s.api_data.get('regularMarketVolume', 0) / s.api_data.get(
                                 'averageDailyVolume3Month', sys.maxsize))
    return result


@app.route('/trends')
def get_trends():
    return trends


@app.route('/ticker/<name>')
def ticker_data(name):
    return {
        'stock': next(filter(lambda x: x.symbol == name, stocks_cache)),
        'market-state-4calc': get_market_state_key()
    }


@app.route('/portfolio')
def get_enriched_portfolio() -> List[Stock]:
    logger.info("request for portfolio from: {} {}".format(request.headers.get("X-Real-Ip"),
                                                           request.headers.get("User-Agent")))
    attempts = 0
    stocks_cache.clear()
    portfolio: List[Stock] = get_portfolio_data()
    watch_list = set(config.get("watch_list", list()))
    logger.debug("watch list is {}".format(watch_list))
    try:
        r = requests.get(API + ','.join(set().union(map(lambda s: s.symbol, portfolio), watch_list)),
                         headers=config["api_headers"])
        while attempts < config.get('retry_attempts', 3) and r.status_code != http.HTTPStatus.OK.value:
            attempts += 1
            logger.error("failed to retrieve data from yahoo {} attempts {}", r.text, attempts)
            r = requests.get(API + ','.join(set().union(map(lambda s: s.symbol, portfolio), watch_list)),
                             headers=config["api_headers"])

        if r.status_code != http.HTTPStatus.OK.value:
            abort(r.status_code, message=r.text)

        yahoo_data = json.loads(r.text)['quoteResponse']['result']
        for stock in portfolio:
            stock.set_api_data(next(filter(lambda s: s['symbol'] == stock.symbol, yahoo_data)))  # expect only one
            stocks_cache.append(stock)
        for watch_stock in watch_list:
            api_data = next(filter(lambda s: s['symbol'] == watch_stock, yahoo_data))  # expect only one
            stock = Stock({
                'Symbol': api_data['symbol'], 'Qty': 0,
                'Gain': None,
                'Day\'s Value': round(api_data.get(get_market_state_key() + 'MarketChange', 0), 2),
                'Entry Type': 'W',
                'Last': api_data.get(get_market_state_key() + 'MarketPrice', 'nan'),
                'Change': api_data.get(get_market_state_key() + 'MarketChange', 'nan')})
            stock.set_api_data(api_data)
            stocks_cache.append(stock)
    except ConnectionError as e:
        logger.error("connection Error while getting API", e)
        abort(http.HTTPStatus.INTERNAL_SERVER_ERROR.value)

    return stocks_cache


def get_portfolio_data() -> List[Stock]:
    # execute only if run as a script
    df = pd.read_html(get_portfolio_table())[0]
    data = json.loads(
        df[['Symbol', 'Qty', 'Change', 'Last', 'Day\'s Value',
            'Average Cost', 'Gain', 'Profit/ Loss', 'Value',
            'Entry Type', 'Expiration', 'Strike', 'Put/ Call']].to_json(orient='records'))
    total_val = 0
    stocks: List[Stock] = list()
    for d in data:
        s = Stock(d)
        stocks.append(s)
        total_val += s.total_val
    for s in stocks:
        s.set_weight(total_val)
    logger.debug("portfolio symbols: {}".format([sub['Symbol'] for sub in data]))
    return stocks


@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('static/js', path)


@app.route('/favicon/<path:icon>')
def favicon(icon):
    if icon == "site.webmanifest":
        return send_from_directory('static/favicon', icon)
    else:
        return send_from_directory('static/favicon', icon, mimetype='image/x-icon')


@app.route('/')
def root():
    return app.send_static_file('index.html')


if __name__ == '__main__':
    config: Dict[str, any] = load_config()
    time_format = config["time_format"]
    persist = TrendPersist(trends)
    logging.basicConfig()
    logger = logging.getLogger("waitress")
    logger.setLevel(os.getenv("APP_LOG_LEVEL", logging.INFO))
    app.logger = logger
    logger.info("starting meitav-view app")
    trends = persist.load()
    logger.info("trends were loaded")

    serve(app, listen="*:{}".format(os.getenv("APP_PORT", 8080)), url_prefix=os.getenv("URL_PREFIX", ""))
