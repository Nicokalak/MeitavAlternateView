import logging
from datetime import datetime, timedelta
import io
import json
import os
import pandas as pd
import requests
from flask import Flask, send_from_directory, Response, send_file, request
from TrendsPersist import TrendPersist
from waitress import serve


app = Flask(__name__, static_url_path='/static/')
symbols_d = {}
API = 'https://query2.finance.yahoo.com/v7/finance/quote?&symbols='
api_data = []
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
    histo_val = 0.0
    if m_state in ('CLOSED', 'PREPRE', 'POSTPOST'):
        return
    for d in data:
        trends_obj['trend'] += symbols_d[d['symbol']]['v']
        if change_key in d:
            histo_val += d[change_key] * symbols_d[d['symbol']]['q']
            trends_obj['yahoo_trend'] += d[change_key] * symbols_d[d['symbol']]['q']
    trends_for_chart(state_histo, histo_val)
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


def get_market_state_4calc(market_state):
    return market_state if market_state in ("PRE", "POST", "REGULAR") else "POST"


def calc_trend(market_state, data):
    result = {'marketState': market_state, 'trend': 0, 'yahoo_trend': 0}
    market_state_4calc = get_market_state_4calc(market_state)
    change = market_state_4calc.lower() + 'MarketChange'
    change_per = market_state_4calc.lower() + 'MarketChangePercent'
    result['trend'] = 0
    add_trend(result, change, data)
    result['top-gainer'] = max(data, key=lambda x: x[change] * symbols_d[x['symbol']]['q'] if change in x else 0)
    result['top-gainer%'] = max(data, key=lambda x: x[change_per] if change in x else 0)
    result['top-loser'] = min(data, key=lambda x: x[change] * symbols_d[x['symbol']]['q'] if change in x else 0)
    result['top-loser%'] = min(data, key=lambda x: x[change_per] if change in x else 0)
    result['top-mover'] = max(data, key=lambda x: x['regularMarketVolume'] if 'regularMarketVolume' in x else 0)
    result['up-down'] = {
        'up': len(list(filter(lambda x: symbols_d[x['symbol']]['g'] > 0, data))),
        'down': len(list(filter(lambda x: symbols_d[x['symbol']]['g'] < 0, data)))
    }
    return result


@app.route('/marketState')
def get_market_state():
    header = {
        'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
              }
    r = requests.get(API + ','.join(symbols_d.keys()), headers=header)
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
    global symbols_d
    symbols_d = dict(map(lambda kv: (kv['Symbol'], {'q': kv['Qty'], 'g': kv['Gain'], 'v': kv['Day\'s Value']}), data))
    return Response(json.dumps(data), mimetype='application/json')


@app.route('/export')
def export():
    sort_name = request.args.get('sortName', default=None)
    df_json = pd.json_normalize(get_portfolio_data(sort_name))
    output = io.BytesIO()
    writer = pd.ExcelWriter(output)
    df_json.to_excel(writer)
    writer.save()
    # Creating the byteIO object from the StringIO Object
    mem = io.BytesIO()
    mem.write(output.getvalue())
    mem.seek(0)
    output.close()

    return send_file(
        mem,
        as_attachment=True,
        download_name='portfolio.xlsx',
        mimetype='application/x-xls'
    )


def get_portfolio_data(sort=None):
    # execute only if run as a script
    df = pd.read_html(get_table())[0]
    data = json.loads(
        df[['Symbol', 'Qty', 'Change', 'Last', 'Day\'s Value',
            'Average Cost', 'Gain', 'Profit/ Loss', 'Value']].to_json(orient='records'))
    for d in data:
        d['percent_change'] = 0 if d['Change'] == 0 \
            else (float(d['Change']) / (float(d['Last']) - float(d['Change']))) * 100
        d['principle_change'] = 0 if d['Change'] == 0 else (float(d['Change']) / d['Average Cost']) * 100

    if sort is not None:
        data.sort(reverse=True, key=lambda s: s[sort] if sort in s else s['percent_change'])
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
    logger.info("starting meitav-view app")
    trends = persist.load()
    logger.info("trends were loaded")
    serve(app, listen="*:8080")
