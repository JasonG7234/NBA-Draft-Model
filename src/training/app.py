import os

from flask import Flask, render_template, request, send_from_directory
import pandas as pd
import numpy as np

import sys
sys.path.insert(0, '../../')
from utils import *

app = Flask(__name__, static_folder='static')

df = convert_number_to_class(pd.read_csv("../../data/draft_db_2023_special.csv"))
df = df[(df['Season'] != '2008-09') & (df['Season'] != '2009-10') & (df['Season'] != '2010-11')]
df['Position 2'] = df['Position 2'].replace(np.nan, '-')
df = df.fillna(0)

@app.route("/", methods=['POST', 'GET'])
def index():
    
    items = df.sample(n=2)
    players = items.to_dict(orient='records')
    print(players[0]['Position 2'])
    if request.form.get('action1') == 'Item 1 is better!':
        print("player 1 is better")
    elif request.form.get('action2') == 'Item 2 is better!':
        print("player 2 is better")
    elif request.form.get('blind') == 'Try Blind':
        print("BLIND")
    else:
        print('end')
            
    return render_template('choose.html', o1 = players[0], o2 = players[1], int=int, round=round)

@app.route("/static/favicon.ico") # 2 add get for favicon
def fav():
    print(os.path.join(app.root_path, 'static'))
    return send_from_directory(app.static_folder, 'favicon.png') # for sure return the file


if __name__ == "__main__":
    app.run(host="localhost", port=8000, debug=True)