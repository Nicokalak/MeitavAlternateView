import json
import os
import requests
import pandas as pd
from flask import Flask

app = Flask(__name__, static_url_path='/static/')
symbols_qty = {}
API = 'https://query1.finance.yahoo.com/v7/finance/quote?&symbols='


def get_table():
    r = requests.get(os.getenv('portfolio_link'))
    return r.text


def calc_trend(market_state, data):
    result = {'marketState': market_state, 'trend': 0}
    key = market_state.lower() + 'MarketChange'
    for d in data:
        if key in d:
            result['trend'] += d[key] * symbols_qty[d['symbol']]
    return result


@app.route('/trend')
def get_trend():
    r = requests.get(API + ','.join(symbols_qty.keys()))
    print(r.text)
    data = json.loads(r.text)['quoteResponse']['result']
    if len(data) > 0:
        return calc_trend(data[0]['marketState'], data)
    else:
        raise RuntimeError()



@app.route('/portfolio')
def get_data():
    # execute only if run as a script
    df = pd.read_html(get_table())[0]
    data = json.loads(
        df[['Symbol', 'Qty', 'Change', 'Last', 'Day\'s Value', 'Average Cost',  'Gain', 'Profit/ Loss', 'Value']].
        to_json(orient='records'))
    for d in data:
        d['percent_change'] = (float(d['Change']) / (float(d['Last']) - float(d['Change']))) * 100
    global symbols_qty
    symbols_qty = dict(map(lambda kv: (kv['Symbol'], kv['Qty']), data))
    return json.dumps(data)


@app.route('/')
def root():
    return app.send_static_file('index.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
