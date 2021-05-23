import json
import os
import time

import requests
import pandas as pd
from flask import Flask, send_from_directory, Response

app = Flask(__name__, static_url_path='/static/')
symbols_qty = {}
API = 'https://query1.finance.yahoo.com/v7/finance/quote?&symbols='
api_data = []
trends = {}


def get_table():
    r = requests.get(os.getenv('portfolio_link'))
    return r.text


def add_trend(trend: float):
    global trends
    if len(trends) > 15:
        first = min(trends.keys())
        if trend == 0:
            return
        del trends[first]
    trends[time.time()] = trend


def calc_trend(market_state, data):
    result = {'marketState': market_state, 'trend': 0}
    change = market_state.lower() + 'MarketChange'
    vol = market_state.lower() + 'Volume'
    for d in data:
        if change in d:
            result['trend'] += d[change] * symbols_qty[d['symbol']]
    result['top-gainer'] = max(data, key=lambda x: x[change] if change in x else 0)
    result['top-loser'] = min(data, key=lambda x: x[change] if change in x else 0)
    result['top-mover'] = max(data, key=lambda x: x[vol] if vol in x else 0)
    add_trend(result['trend'])
    return result


@app.route('/marketState')
def get_market_state():
    r = requests.get(API + ','.join(symbols_qty.keys()))
    print(r.text)
    data = json.loads(r.text)['quoteResponse']['result']
    global api_data
    api_data = data
    if len(data) > 0:
        return calc_trend(data[0]['marketState'], data)
    else:
        raise RuntimeError()


@app.route('/trends')
def get_trends():
    return trends


@app.route('/ticker/<name>')
def ticker_data(name):
    for ticker in api_data:
        if name == ticker['symbol']:
            return ticker
    return {}


@app.route('/portfolio')
def get_data():
    # execute only if run as a script
    df = pd.read_html(get_table())[0]
    data = json.loads(
        df[['Symbol', 'Qty', 'Change', 'Last', 'Day\'s Value', 'Average Cost',  'Gain', 'Profit/ Loss', 'Value']].
        to_json(orient='records'))
    for d in data:
        d['percent_change'] = 0 if d['Change'] == 0 \
            else (float(d['Change']) / (float(d['Last']) - float(d['Change']))) * 100
    global symbols_qty
    symbols_qty = dict(map(lambda kv: (kv['Symbol'], kv['Qty']), data))
    return Response(json.dumps(data), mimetype='application/json')


@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('static/js', path)


@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static', 'favicon.ico', mimetype='image/x-icon')


@app.route('/')
def root():
    return app.send_static_file('index.html')


if __name__ == '__main__':
    app.run( port=8080)
