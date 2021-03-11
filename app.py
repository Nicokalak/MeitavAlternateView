import json
import os
import requests
import pandas as pd
from flask import Flask
from flask import Flask, Response

app = Flask(__name__, static_url_path='/static/')


def get_table():
    r = requests.get(os.environ.get('portfolio_link'))
    return r.text


@app.route('/portfolio')
def get_data():
    # execute only if run as a script
    df = pd.read_html(get_table())[0]
    data = json.loads(
        df[['Symbol', 'Qty', 'Change', 'Last', 'Day\'s Value', 'Average Cost',  'Gain', 'Profit/ Loss', 'Value']].
        to_json(orient='records'))
    for d in data:
        d['percent_change'] = (float(d['Change']) / (float(d['Last']) - float(d['Change']))) * 100
    return Response(json.dumps(data), mimetype='application/json')


@app.route('/')
def root():
    return app.send_static_file('index.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
