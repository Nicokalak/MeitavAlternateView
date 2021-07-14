import datetime
import io
import json
import os

import requests
import pandas as pd
from flask import Flask, send_from_directory, Response, send_file

app = Flask(__name__, static_url_path='/static/')
symbols_qty = {}
API = 'https://query1.finance.yahoo.com/v7/finance/quote?&symbols='
api_data = []
trends = {}
time_format = '%Y%m%dT%H:%M:%S'


def get_table():
    r = requests.get(os.getenv('portfolio_link'))
    return r.text


def add_trend(trends_obj, change, data):
    if trends_obj['marketState'] in ('CLOSED', 'PREPRE', 'POSTPOST'):
        return
    for d in data:
        if change in d:
            trends_obj['trend'] += d[change] * symbols_qty[d['symbol']]
    global trends
    trend: float = trends_obj['trend']
    if len(trends) > 15:
        first = min(trends.keys())
        del trends[first]
    trends[datetime.datetime.now().strftime(time_format)] = trend


def get_market_state_4calc(market_state):
    return market_state if market_state in ("PRE", "POST", "REGULAR") else "POST"


def calc_trend(market_state, data):
    result = {'marketState': market_state, 'trend': 0}
    market_state_4calc = get_market_state_4calc(market_state)
    change = market_state_4calc.lower() + 'MarketChange'
    change_per = market_state_4calc.lower() + 'MarketChangePercent'
    result['trend'] = 0
    add_trend(result, change, data)
    result['top-gainer'] = max(data, key=lambda x: x[change] * symbols_qty[x['symbol']] if change in x else 0)
    result['top-gainer%'] = max(data, key=lambda x: x[change_per] if change in x else 0)
    result['top-loser'] = min(data, key=lambda x: x[change] * symbols_qty[x['symbol']] if change in x else 0)
    result['top-loser%'] = min(data, key=lambda x: x[change_per] if change in x else 0)
    result['top-mover'] = max(data, key=lambda x: x['regularMarketVolume'] if 'regularMarketVolume' in x else 0)
    result['avg-trends'] = (sum(trends.values()) / len(trends.values())) if len(trends.values()) > 0 else 0
    return result


@app.route('/marketState')
def get_market_state():
    header = {'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
    r = requests.get(API + ','.join(symbols_qty.keys()), headers=header)
    if r.status_code == 200:
        data = json.loads(r.text)['quoteResponse']['result']
        global api_data
        api_data = data
        if len(data) > 0:
            return calc_trend(data[0]['marketState'], data)
    raise RuntimeError()


@app.route('/trends')
def get_trends():
    return trends


@app.route('/ticker/<name>')
def ticker_data(name):
    for ticker in api_data:
        if name == ticker['symbol']:
            ticker['market-state-4calc'] = get_market_state_4calc(ticker['marketState'])
            return ticker
    return {}


@app.route('/portfolio')
def get_data():
    data = get_portfolio_data()
    global symbols_qty
    symbols_qty = dict(map(lambda kv: (kv['Symbol'], kv['Qty']), data))
    return Response(json.dumps(data), mimetype='application/json')


@app.route('/export')
def export():
    df_json = pd.json_normalize(get_portfolio_data())
    output = io.BytesIO()
    writer = pd.ExcelWriter(output)
    df_json.to_excel(writer)
    writer.save()
    # Creating the byteIO object from the StringIO Object
    mem = io.BytesIO()
    mem.write(output.getvalue())
    output.close()

    return send_file(
        mem,
        as_attachment=True,
        download_name='portfolio.xlsx',
        mimetype='application/x-xls'
    )


def get_portfolio_data():
    # execute only if run as a script
    df = pd.read_html(get_table())[0]
    data = json.loads(
        df[['Symbol', 'Qty', 'Change', 'Last', 'Day\'s Value',
            'Average Cost', 'Gain', 'Profit/ Loss', 'Value']].to_json(orient='records'))
    for d in data:
        d['percent_change'] = 0 if d['Change'] == 0 \
            else (float(d['Change']) / (float(d['Last']) - float(d['Change']))) * 100
    return data


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
    app.run(host='0.0.0.0', port=8080)
