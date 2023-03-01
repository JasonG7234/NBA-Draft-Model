
from flask import Flask, render_template, request, send_from_directory, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, static_folder='static')
app.secret_key = "super secret key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

import sys
sys.path.insert(0, '../../')
from utils import *
import pandas as pd

df = pd.read_csv('../../data/draft_db_2023_special.csv')
df = convert_number_to_class(df)
df['Adjusted TOV%'] = df['Adjusted TOV%']*100
df['TS%'] = df['TS%']*100
df['FG%'] = df['FG%']*100
df['2FG%'] = df['2FG%']*100
df['3FG%'] = df['3FG%']*100
df['FT%'] = df['FT%']*100
df['3 Point Confidence'] = round(df['3 Point Confidence']*100, 1)
df['Unassisted Shots @ Rim /100Poss'] = round(df['Unassisted Shots @ Rim /100Poss'], 2)
df['Dunks per Minute Played'] = round(df['Dunks per Minute Played'], 1)
df['% Assisted'] = round(df['% Assisted'], 1)

df['Stock%'] = round(df['Stock%'], 1)
df['Offensive Load'] = round(df['Offensive Load'], 1)

df['Athleticism Score'] = round(df['Athleticism Score']*100, 3)
df['Passing Score'] = round(df['Passing Score']*100, 3)
df['Shooting Score'] = round(df['Shooting Score']*100, 3)
df['Finishing Score'] = round(df['Finishing Score']*100, 3)
df['Rebounding Score'] = round(df['Rebounding Score']*100, 3)
df['Defense Score'] = round(df['Defense Score']*100, 3)
df['Shot Creation Score'] = round(df['Shot Creation Score']*100, 3)
df['College Productivity Score'] = round(df['College Productivity Score']*100, 3)
df['Draft Score'] = round(df['Draft Score']*100, 3)

with app.app_context():
    df.to_sql('players', con=db.engine, index=False)

        