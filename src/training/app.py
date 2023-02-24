import os

from flask import Flask, render_template, request, send_from_directory
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import numpy as np

import sys
sys.path.insert(0, '../../')
from utils import *

app = Flask(__name__, static_folder='static')

# SETUP THE DB
# configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
# initialize the app with the extension
db = SQLAlchemy()
db.init_app(app)
print(db)

# SETUP THE DATAFRAME
df = convert_number_to_class(pd.read_csv("../../data/draft_db_2023_special.csv"))
df = df[(df['Season'] != '2008-09') & (df['Season'] != '2009-10') & (df['Season'] != '2010-11')]
df['Position 2'] = df['Position 2'].replace(np.nan, '-')
df = df.fillna(0)

@app.route("/", methods=['POST', 'GET'])
def index():
    
    items = df.sample(n=2)
    players = items.to_dict(orient='records')
    if (request.form.get('action1') == 'Item 1 is better!'):
        print("player 1 is better")
    elif (request.form.get('action2') == 'Item 2 is better!'):
        print("player 2 is better")
        
    if ('blind' in request.form):
        # User is entering blind mode - mask name and image for next draft
        print(request.form)
        players[0]['Image Link'] = 'https://basketball.realgm.com/images/nba/4.2/profiles/photos/2006/player_photo.jpg'
        players[1]['Image Link'] = 'https://basketball.realgm.com/images/nba/4.2/profiles/photos/2006/player_photo.jpg'
        players[0]['Name'] = 'Player 1'
        players[1]['Name'] = 'Player 2'
        return render_template('index.html', o1 = players[0], o2 = players[1], blind=True, int=int, round=round)
    else:
        return render_template('index.html', o1 = players[0], o2 = players[1], blind=False, int=int, round=round)

@app.route("/static/favicon.ico") # 2 add get for favicon
def fav():
    print(os.path.join(app.root_path, 'static'))
    return send_from_directory(app.static_folder, 'favicon.png')

if __name__ == "__main__":
    app.run(host="localhost", port=8000, debug=True)