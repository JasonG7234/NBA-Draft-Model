
from sqlalchemy import create_engine

engine = create_engine("sqlite:///project.db", echo=False)


import sys
sys.path.insert(0, '../../')
from utils import *
import pandas as pd

df = pd.read_csv('../../data/draft_db_2023_special.csv')

df = convert_number_to_class(df)
df['Adjusted TOV%'] = df['Adjusted TOV%']*100
df['FG%'] = df['FG%']*100
df['2FG%'] = df['2FG%']*100
df['3FG%'] = df['3FG%']*100
df['FT%'] = df['FT%']*100
df['3 Point Confidence'] = round(df['3 Point Confidence']*100, 1)
df['Unassisted Shots @ Rim /100Poss'] = round(df['Unassisted Shots @ Rim /100Poss'], 2)
df['Dunks per Minute Played'] = round(df['Dunks per Minute Played'], 5)
df['% Assisted'] = round(df['% Assisted'], 1)
df['Helio Score'] = round(df['Helio Score'], 3)

df['Stock%'] = round(df['Stock%'], 1)
df['Offensive Load'] = round(df['Offensive Load'], 1)
df.to_sql('players', con=engine, index=False)
