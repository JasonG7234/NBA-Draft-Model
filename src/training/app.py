import os

from flask import Flask, render_template, request, send_from_directory, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from model import Picks, Players

import sys
sys.path.insert(0, '../../')
from utils import *

app = Flask(__name__, static_folder='static')
app.secret_key = "super secret key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
# SETUP THE DB
# initialize the app with the extension

KEYS = ["RealGM ID","Season","Name","Position 1","Position 2","Play Style","Height","Weight","School","Conference","Wins","Losses","SOS","Class","Birthday","Draft Day Age","RSCI","G","GS","MP","PER","TS%","eFG%","3PAr","FTr","PProd","ORB%","DRB%","TRB%","AST%","STL%","BLK%","Stock%","TOV%","Adjusted TOV%","USG%","Offensive Load","OWS","DWS","WS","WS/40","OBPM","DBPM","BPM","AST/TOV","OFF RTG","DEF RTG","Hands-On Buckets","Pure Point Rating","FG/40","FGA/40","FG%","2FGM/40","2FGA/40","2FG%","3FGM/40","3FGA/40","3FG%","3 Point Proficiency","3 Point Confidence","FT/40","FTA/40","FT%","TRB/40","AST/40","STL/40","BLK/40","TOV/40","PF/40","PTS/40","FGM/100Poss","FGA/100Poss","2FGM/100Poss","2FGA/100Poss","3FGM/100Poss","3FGA/100Poss","FT/100Poss","FTA/100Poss","TRB/100Poss","AST/100Poss","STL/100Poss","BLK/100Poss","TOV/100Poss","PF/100Poss","PTS/100Poss","# Dunks","Dunk vs Rim Shot Percentage","% Dunks Unassisted","Dunks per Minute Played","Unassisted Shots @ Rim /100Poss","% Shots @ Rim","FG% @ Rim","%Astd @ Rim","% Shots @ Mid","FG% @ Mid","%Astd @ Mid","% Shots @ 3","%Astd @ 3","% Assisted","AAU Season","AAU Team","AAU League","AAU GP","AAU GS","AAU MIN","AAU PTS","AAU FGM","AAU FGA","AAU FG%","AAU 3PM","AAU 3PA","AAU 3P%","AAU FTM","AAU FTA","AAU FT%","AAU ORB","AAU DRB","AAU TRB","AAU AST","AAU STL","AAU BLK","AAU TOV","AAU PF","Event Year","Event Name","Event GP","Event MIN","Event PTS","Event FGM","Event FGA","Event FG%","Event 3PM","Event 3PA","Event 3P%","Event FTM","Event FTA","Event FT%","Event TRB","Event AST","Event STL","Event BLK","Event TOV","Event PF","Event Placement","Finishing Score","Shooting Score","Shot Creation Score","Passing Score","Rebounding Score","Athleticism Score","Defense Score","College Productivity Score","Percentile Score","Box Score Creation","Rim Shot Creation","Helio Score","Draft Score","Image Link"]

# HOME
@app.route("/", methods=['POST', 'GET'])
def index():
    players = get_random_players()
    session['p1'] = players[0]
    session['p2'] = players[1]
    if (session["blind_mode"] == True):
        # User is entering blind mode - mask name and image for next draft
        players[0]['image_link'] = 'https://basketball.realgm.com/images/nba/4.2/profiles/photos/2006/player_photo.jpg'
        players[1]['image_link'] = 'https://basketball.realgm.com/images/nba/4.2/profiles/photos/2006/player_photo.jpg'
        players[0]['name'] = 'Player 1'
        players[1]['name'] = 'Player 2'
        return render_template('index.html', o1 = players[0], o2 = players[1], blind=True, int=int, round=round)
    else:
        return render_template('index.html', o1 = players[0], o2 = players[1], blind=False, int=int, round=round)

# HANDLE FORM SUBMIT
@app.route('/handle_data', methods=['POST'])
def handle_data():
    if (request.form.get('action1')):
        save_pick_winner(session['p1'], session['p2'])
    elif (request.form.get('action2')):
        save_pick_winner(session['p2'], session['p1'])
    session['blind_mode'] = 'blind' in request.form
    return redirect(url_for("index"))

# GET ICON
@app.route("/static/favicon.ico")
def fav():
    print(os.path.join(app.root_path, 'static'))
    return send_from_directory(app.static_folder, 'favicon.png')

from sqlalchemy.sql.expression import func

# DATABASE CALLS
def get_random_players(): 
    import random
    res = db.session.query(Players).filter(Players.fg_pct_at_rim.is_not(None)).order_by(func.random()).limit(2)
    players = []
    for player in res:
        d = player.__dict__
        d.pop('_sa_instance_state')
        players.append(d)
    return players

def save_pick_winner(winning_player, losing_player):
    win_id = winning_player['realgm_id']
    win_name = winning_player['name']
    lose_id = losing_player['realgm_id']
    lose_name = losing_player['name']
    pick = Picks(date=request.date, ip=request.remote_addr, user_agent=str(request.user_agent),
                win_player_id=win_id, win_player_name=win_name, lose_player_id=lose_id, lose_player_name=lose_name)
    db.session.add(pick)
    db.session.commit()

# RAW SQL EXECUTION
# def execute_sql(sql_text):
#     with engine.connect() as conn:
#         result = conn.execute(text(sql_text))
#     return result

# RUN
if __name__ == "__main__":
    app.run(host="localhost", port=8000)