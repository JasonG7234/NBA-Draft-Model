import os

from flask import Flask, render_template, request, send_from_directory, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from model import Picks, Players

import sys
sys.path.insert(0, '../../')
from utils import *

app = Flask(__name__, static_folder='static')
app.secret_key = 'secret_key'
df = convert_number_to_class(pd.read_csv("../../data/draft_db_2023_special.csv"))
df = df[(df['Season'] != '2008-09') & (df['Season'] != '2009-10') & (df['Season'] != '2010-11')]
df['Position 2'] = df['Position 2'].replace(np.nan, '-')
df = df.fillna(0)
# HOME
@app.route("/", methods=['POST', 'GET'])
def index():
        
    items = df.loc[(df['Name'] == 'Brice Sensabaugh') | (df['Name'] == 'Jett Howard')]
    players = items.to_dict(orient='records')
    print(players[0])
    session['p1'] = players[0]
    session['p2'] = players[1]
    if ('blind_mode' in session and session['blind_mode'] == True):
        # User is entering blind mode - mask name and image for next draft
        players[0]['image_link'] = 'https://basketball.realgm.com/images/nba/4.2/profiles/photos/2006/player_photo.jpg'
        players[1]['image_link'] = 'https://basketball.realgm.com/images/nba/4.2/profiles/photos/2006/player_photo.jpg'
        players[0]['name'] = 'Player 1'
        players[1]['name'] = 'Player 2'
        return render_template('index.html', o1 = players[0], o2 = players[1], blind=True, int=int, round=round)
    else:
        return render_template('index.html', o1 = players[0], o2 = players[1], blind=False, int=int, round=round)

# GET ICON
@app.route("/static/favicon.ico")
def fav():
    print(os.path.join(app.root_path, 'static'))
    return send_from_directory(app.static_folder, 'favicon.png')

# RUN
if __name__ == "__main__":
    app.run(host="localhost", port=8000)