import logging
from datetime import datetime, timedelta
import json
import os
from typing import List

import pandas as pd
import requests
from flask import Flask, send_from_directory, Response
from TrendsPersist import TrendPersist
from waitress import serve


app = Flask(__name__, static_url_path='/static/')
symbols_d: List = []
API = 'https://query2.finance.yahoo.com/v7/finance/quote?&symbols='
api_data = {}
trends = {
    "PRE_histo": {},
    "REGULAR_histo": {},
    "POST_histo": {}
}
time_format = '%Y%m%dT%H:%M:%S'
persist = TrendPersist(trends)
logging.basicConfig()
logger = logging.getLogger("waitress")
logger.setLevel(logging.INFO)


def get_table():
    r = requests.get(os.getenv('portfolio_link'))
    return r.text


def add_trend(trends_obj, change_key, data):
    m_state = trends_obj['marketState']
    state_histo = m_state + '_histo'
    if m_state in ('CLOSED', 'PREPRE', 'POSTPOST'):
        return
    for d in data:
        yahoo_symbol_data = api_data[d['s']]
        trends_obj['trend'] += d['dv']
        if change_key in yahoo_symbol_data:
            if d['t'] == "E":
                trends_obj['yahoo_trend'] += yahoo_symbol_data[change_key] * d['q']
            elif m_state == "REGULAR":
                trends_obj['yahoo_trend'] += d['dv']
    trends_for_chart(state_histo, trends_obj['yahoo_trend'])
    persist.save()


def get_symbol_d_key_sum(sym, key):
    return sum(map(lambda sym_d: sym_d[key], filter(lambda t: t['s'] == sym and t['t'] == 'E', symbols_d)))


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


def get_market_state_4calc(market_state):
    return market_state if market_state in ("PRE", "POST", "REGULAR") else "POST"


def calc_trend(market_state):
    result = {'marketState': market_state, 'trend': 0, 'yahoo_trend': 0}
    market_state_4calc = get_market_state_4calc(market_state)
    change = market_state_4calc.lower() + 'MarketChange'
    change_per = market_state_4calc.lower() + 'MarketChangePercent'
    result['trend'] = 0
    add_trend(result, change, symbols_d)
    result['top-gainer'] = max(api_data.values(), key=lambda x: x[change] * get_symbol_d_key_sum(x['symbol'], 'q') if change in x else 0)
    result['top-gainer%'] = max(api_data.values(), key=lambda x: x[change_per] if change in x else 0)
    result['top-loser'] = min(api_data.values(), key=lambda x: x[change] * get_symbol_d_key_sum(x['symbol'], 'q') if change in x else 0)
    result['top-loser%'] = min(api_data.values(), key=lambda x: x[change_per] if change in x else 0)
    result['top-mover'] = max(api_data.values(), key=lambda x: x['regularMarketVolume'] if 'regularMarketVolume' in x else 0)
    result['up-down'] = {
        'up': len(list(filter(lambda sd: sd['g'] > 0, symbols_d))),
        'down': len(list(filter(lambda sd: sd['g'] < 0, symbols_d)))
    }
    return result


@app.route('/marketState')
def get_market_state():
    header = {
        'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
              }
    r = requests.get(API + ','.join(set(map(lambda s: s['s'], symbols_d))), headers=header)
    if r.status_code == 200:
        data = json.loads(r.text)['quoteResponse']['result']
        global api_data
        api_data = dict((v['symbol'], v) for v in data)
        if len(data) > 0:
            return calc_trend(data[0]['marketState'])
    raise RuntimeError()


@app.route('/trends')
def get_trends():
    return trends


@app.route('/ticker/<name>')
def ticker_data(name):
    if name in api_data:
        ticker = api_data[name]
        ticker['market-state-4calc'] = get_market_state_4calc(ticker['marketState'])
        return ticker
    return {}


@app.route('/portfolio')
def get_data():
    data = get_portfolio_data()
    global symbols_d
    symbols_d = list(map(lambda d: {'s': d['Symbol'], 'q': d['Qty'], 'g': d['Gain'],
                                    'dv': d['Day\'s Value'], 't': d['Entry Type']}, data))
    return Response(json.dumps(data), mimetype='application/json')


def get_portfolio_data(sort=None):
    # execute only if run as a script
    df = pd.read_html(get_table())[0]
    data = json.loads(
        df[['Symbol', 'Qty', 'Change', 'Last', 'Day\'s Value',
            'Average Cost', 'Gain', 'Profit/ Loss', 'Value',
            'Entry Type', 'Expiration', 'Strike', 'Put/ Call']].to_json(orient='records'))
    for d in data:
        d['percent_change'] = calc_percent_change(d)
        d['principle_change'] = 0 if d['Change'] == 0 else (float(d['Change']) / d['Average Cost']) * 100

    if sort is not None:
        data.sort(reverse=True, key=lambda s: s[sort] if sort in s else s['percent_change'])
    return data


def calc_percent_change(d):
    if d['Change'] == 0:
        return 0
    elif float(d['Last']) - float(d['Change']) == 0:
        return (float(d['Change']) / (float(d['Last']) - float(d['Change']) + 0.0001)) * 100
    else:
        return float(d['Change']) / (float(d['Last']) - float(d['Change']))


@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('static/js', path)


@app.route('/favicon/<path:icon>')
def favicon(icon):
    return send_from_directory('static/favicon', icon, mimetype='image/x-icon')


@app.route('/')
def root():
    return app.send_static_file('index.html')


if __name__ == '__main__':
    app.logger = logger
    logger.info("starting meitav-view app")
    trends = persist.load()
    logger.info("trends were loaded")

    serve(app, listen="*:8080", url_prefix=os.getenv("URL_PREFIX", ""))
