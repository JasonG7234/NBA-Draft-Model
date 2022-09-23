import pandas as pd
import numpy as np
import math
from utils import *

def jason_3pt_confidence(df):
    cast_column_to_float(df, '3FG%')
    cast_column_to_float(df, '3PAr')
    df['3 Point Confidence'] = 2/(1/df['3FG%']+1/df['3PAr'])
    return df

def percent_assisted_overall(df):
    df['% Assisted'] = (
        (df['%Astd @ Rim']/100*df['% Shots @ Rim']) +
        (df['% Shots @ Mid']/100*df['%Astd @ Mid']) +
        (df['%Astd @ 3']/100*df['% Shots @ 3'])
    )
    #draw_conclusions_on_column(df, '% Assisted')
    return df

def self_created_dunks(df):
    df["Dunks per Minute"] = df['# Dunks'] / df['MP']
    df["Rim Shots per Minute"] = (df['% Shots @ Rim'] * df['FGA/40']) / 4000
    df["Dunk vs Rim Shot Percentage"] = round(df["Dunks per Minute"] / df["Rim Shots per Minute"]*100, 2)
    df["% Dunks Unassisted"] = (100-df['%Astd @ Rim'])*(df['Dunk vs Rim Shot Percentage']*df['% Shots @ Rim']/100)/100
    df["Rim Shot Creation"] = ""
    for index, row in df.iterrows():
        _RSC = (2/math.pow(math.e, row['%Astd @ Rim']/150))*(row['FG% @ Rim']/2)+(row['% Shots @ Rim']*row['FGA/100Poss']*0.01)
        df.loc[index, 'Rim Shot Creation'] = round(_RSC, 3)
    df.drop(["Rim Shots per Minute", "Dunks per Minute"], axis=1, inplace=True)
    return df

def bentaylor_stats(df):
    df["3 Point Proficiency"] = ""
    df['Box Score Creation'] = ""
    df['Offensive Load'] = ""
    df['Adjusted TOV%'] = ""
    for index, row in df.iterrows():
        _3PA = -abs(float(row['3FGA/100Poss']))
        if (_3PA == 0):
            _3PP = 0
        else:
            _3P = float(row['3FG%'])
            _3PP = (((2/(1+math.pow(math.e, _3PA))-1)*_3P)+(_3P*float(row['3PAr'])))/2
        df.loc[index, '3 Point Proficiency'] = round(_3PP, 3)
        _AST = float(row['AST/100Poss'])
        _PTS = float(row['PTS/100Poss'])
        _TOV = float(row['TOV/100Poss'])
        _BSC = _AST*0.1843+(_PTS+_TOV)*0.0969-2.3021*(_3PP)+0.0582*(_AST*(_PTS+_TOV)*_3PP)-1.1942
        df.loc[index, 'Box Score Creation'] = round(_BSC, 3)
        _FGA = float(row['FGA/100Poss'])
        _FTA = float(row['FTA/100Poss'])
        _OL = ((_AST-(0.38*_BSC))*0.75)+_FGA+_FTA*0.44+_BSC+_TOV
        df.loc[index, 'Offensive Load'] = round(_OL, 3)
        _cTOV = _TOV / _OL
        df.loc[index, 'Adjusted TOV%'] = round(_cTOV, 3)
    #df[].fillna(df['Box Score Creation'].mean())
    df['Box Score Creation'] = pd.to_numeric(df['Box Score Creation'], downcast="float")
    print(df['Box Score Creation'].dtype)
    return df

def add_conference(df):
    ACC = ['Boston College', 'Clemson', 'Duke', 'UNC', 'North Carolina', 'NC State', 'Wake Forest', 'Florida State', 'Georgia Tech', 'Louisville', 'Miami', 'Notre Dame', 'Pitt', 'Syracuse', 'Virginia Tech', 'Virginia']
    BIG_EAST = ['Butler', 'Creighton', 'DePaul', 'Georgetown', 'Marquette', 'Providence', 'Seton Hall', "St. John's (NY)", 'UConn', 'Villanova', 'Xavier']
    SEC = ['Alabama', 'Arkansas', 'Auburn', 'Florida', 'Georgia', 'Kentucky', 'LSU', 'Ole Miss', 'Mississippi State', 'Missouri', 'South Carolina', 'Tennessee', 'Texas A&M', 'Vanderbilt']
    BIG_TEN = ['Illinois', 'Indiana', 'Iowa', 'Maryland', 'Michigan State', 'Michigan', 'Minnesota', 'Nebraska', 'Northwestern', 'Ohio State', 'Penn State', 'Purdue', 'Rutgers', 'Wisconsin']
    WCC = ['Gonzaga', 'Pepperdine', 'Santa Clara', 'BYU', "Saint Mary's", 'San Francisco']
    BIG_12 = ['Baylor', 'Iowa State', 'Kansas', 'Kansas State', 'Oklahoma', 'Oklahoma State', 'Texas', 'TCU', 'Texas Tech', 'West Virginia']
    PAC_12 = ['Oregon', 'USC', 'UCLA', 'Arizona State', 'Arizona', 'California', 'Colorado', 'Utah', 'Oregon State', 'Stanford', 'Washington', 'Washington State']
    MWC = ['Air Force', 'Boise State', 'Colorado State', 'Fresno State', 'Nevada', 'New Mexico', 'San Diego State', 'San Jose State', 'UNLV', 'Utah State', 'Wyoming']
    AAC = ['Cincinnati', 'East Carolina', 'Houston', 'Memphis', 'SMU', 'South Florida', 'Temple', 'Tulane', 'Tulsa', 'Wichita State', 'Central Florida']
    A10 = ['Davidson', 'Dayton', 'Duquesne', 'Fordham', 'George Mason', 'George Washington', 'La Salle', 'Rhode Island', 'Richmond', "St. Joseph's", 'Saint Louis', 'St. Bonaventure', 'UMass', 'VCU']
    
    df['Conference'] = 'Other'
    for index, row in df.iterrows():
        school = row['School']
        if school in ACC:
            df.loc[index, 'Conference'] = 'ACC'
        if school in BIG_EAST:
            df.loc[index, 'Conference'] = 'Big East'
        if school in SEC:
            df.loc[index, 'Conference'] = 'SEC'
        if school in BIG_TEN:
            df.loc[index, 'Conference'] = 'Big Ten'
        if school in WCC:
            df.loc[index, 'Conference'] = 'WCC'
        if school in BIG_12:
            df.loc[index, 'Conference'] = 'Big 12'
        if school in PAC_12:
            df.loc[index, 'Conference'] = 'Pac-12'
        if school in MWC:
            df.loc[index, 'Conference'] = 'MWC'
        if school in AAC:
            df.loc[index, 'Conference'] = 'AAC'
        if school in A10:
            df.loc[index, 'Conference'] = 'AAC'
    return df


    
def play_styles(df):
    pg = df[df['Position 1'] == 'PG']
    pg['Floor General'] = pg['Pure Point Rating'].rank(na_option='bottom', pct=True)
    pg['Athletic'] = pg['% Shots @ Rim'].rank(na_option='keep', pct=True)
    pg['Scorer'] = pg['PTS/40'].rank(na_option='bottom', pct=True)
    pg['Shooter'] = pg['3FG%'].rank(na_option='bottom', pct=True)
    pg['Play Style'] = pg[['Floor General','Athletic','Scorer','Shooter']].idxmax(axis=1)
    pg.drop(['Floor General','Athletic','Scorer','Shooter'], axis=1, inplace=True)
    
    c = df[df['Position 1'] == 'C']
    c['Stretch'] = c['3FGM/40'].rank(na_option='keep', pct=True)
    for index, row in c.iterrows():
        if row['3FGM/40'] <= 1:
            c.loc[index, 'Stretch%'] = 0
    c['Rebounder'] = c['ORB%'].rank(na_option='keep', pct=True)
    c['Play Finisher'] = c['2FG%'].rank(na_option='keep', pct=True)
    c['Short Roll'] = c['AST%'].rank(na_option='keep', pct=True)
    c['Post Up'] = c['%Astd @ Rim'].rank(na_option='keep', ascending=False, pct=True)
    c['Play Style'] = c[['Stretch','Rebounder','Play Finisher','Short Roll', 'Post Up']].idxmax(axis=1)
    c.drop(['Stretch','Rebounder','Play Finisher','Short Roll', 'Post Up'], axis=1, inplace=True)
    
    wing = df[(df['Position 1'] == 'SF') | (df['Position 1'] == 'SG')]
    wing['Scorer'] = wing['PTS/40'].rank(na_option='keep', pct=True)
    wing['Shooter'] = wing['% Shots @ 3'].rank(na_option='keep', pct=True)
    wing['Slasher'] = wing['% Shots @ Rim'].rank(na_option='keep', pct=True)
    wing['Play Style'] = wing[['Scorer','Shooter','Slasher']].idxmax(axis=1)
    for index, row in wing.iterrows():
        if row['Scorer'] <= 0.675 and row['Slasher'] <= 0.675 and row['Shooter'] <= 0.675:
            wing.loc[index, 'Play Style'] = 'Connector'
    wing.drop(['Scorer','Shooter','Slasher'], axis=1, inplace=True)
    
    pf = df[df['Position 1'] == 'PF']
    pf['Stretch'] = pf['3FGM/40'].rank(na_option='keep', pct=True)
    for index, row in pf.iterrows():
        if row['3FGM/40'] <= 1.75:
            pf.loc[index, 'Stretch'] = 0
    pf['Energy'] = pf['ORB%'].rank(na_option='keep', pct=True)
    pf['Playmaker'] = pf['AST%'].rank(na_option='keep', pct=True)
    pf['Scorer'] = pf['PTS/40'].rank(na_option='keep', pct=True)
    pf['Play Style'] = pf[['Stretch','Energy','Playmaker','Scorer']].idxmax(axis=1)
    for index, row in pf.iterrows():
        if row['Scorer'] <= 0.675 and row['Playmaker'] <= 0.675 and row['Stretch'] <= 0.675 and row['Energy'] <= 0.675:
            pf.loc[index, 'Play Style'] = 'Connector'
    pf.drop(['Stretch','Energy','Playmaker','Scorer'], axis=1, inplace=True)
    new_df = pd.concat([pg, wing,pf,c], axis=0)
    return new_df.sort_values(by=['BPM'], ascending=False)

def athleticism(df):
    df["Dunks per Minute Played"] = df['# Dunks'] / df['MP']
    df['Stock%'] = df['STL%'] * df['BLK%']
    df['%Unastd @ Rim'] = 100-df['%Astd @ Rim']
    df['Shots @ Rim / 100'] = df['% Shots @ Rim'] * df['FGA/100Poss'] / 100
    df['Unassisted Shots @ Rim /100Poss'] = df['%Unastd @ Rim'] * df['Shots @ Rim / 100'] / 100
    df = normalize(df, 'Height', True)
    df = normalize(df, 'Stock%')
    df["Athleticism?"] = (df['Height Normalized']) * (df["Dunks per Minute Played"]+1) * (df["Stock% Normalized"]) * (df['Unassisted Shots @ Rim / 100 Possessions'])*50
    return df

def touch(df):
    df = normalize(df, 'Height', True)
    df = df[df['Height'] < 78]
    df = df[df['# Dunks'] < 5]
    df["Midrange Game"] = 2/(1/(100-df['%Astd @ Mid'])+1/df['FG% @ Mid'])
    df["Rim Game"] = 2/(1/(100-df['%Astd @ Rim'])+1/df['FG% @ Rim'])
    #draw_conclusions_on_column(df, 'Midrange Game', num_top=25)
    
    df["Touch Indicators"] = 2/(1/df['Midrange Game']+1/df['Rim Game'])
    return df

def add_aux_columns(df):
    df['3FGA/100Poss'].fillna(0)
    df['3PAr'].fillna(0)
    df['3FG%'].fillna(0)
    df['Draft Day Age'].fillna(df['Draft Day Age'].mean())
    df = jason_3pt_confidence(df)
    df = bentaylor_stats(df)
    df = athleticism(df)
    df = percent_assisted_overall(df)
    df = self_created_dunks(df)
    df = play_styles(df)
    df['Stock%'] = 2/(1/df['STL%'] + 1/df['BLK%'])
    df = normalize(df, 'Height')
    df = normalize(df, 'SOS')
    df = normalize(df, 'Draft Day Age', True)
    
    df['Box Score Creation'].replace('', np.nan, inplace=True)
    df['Box Score Creation'].astype(float)
    
    df['Helio Score'] = (df['Box Score Creation'] * (df['Height Normalized']+0.05) * (df['SOS Normalized']+1) * df['Draft Day Age Normalized'])
    df.loc[df['G'] <= 15, 'Helio Score'] = df['Helio Score']*(df['G']/15)
    df['Box Score Creation'].astype(float)
    for index, row in df.nlargest(25, ['Helio Score']).iterrows():
        df.loc[index, 'Play Style'] = 'Primary'
    df.drop(['Height Normalized', 'SOS Normalized', 'Draft Day Age Normalized'], axis=1, inplace=True)
    #draw_conclusions_on_column(df, '"% Dunks Unassisted"', num_top=25)
    #get_value_at_column_by_player_name(df, "Ja Morant", "Helio Score", True)
    
    return reorder_aux_columns(df)

def reorder_aux_columns(df):
    return df[['RealGM ID','Season','Name',
                'Position 1','Position 2','Play Style',
                'School','Conference','Wins','Losses','SOS',
                'Class','Birthday','Draft Day Age',
                'RSCI','G','GS','MP','PER','TS%','eFG%','3PAr','FTr','PProd','ORB%','DRB%','TRB%','AST%','STL%','BLK%','Stock%','TOV%','Adjusted TOV%','USG%','Offensive Load','OWS','DWS','WS','WS/40','OBPM','DBPM','BPM','AST/TOV','OFF RTG','DEF RTG','Hands-On Buckets','Pure Point Rating',
                'FG/40','FGA/40','FG%','2FGM/40','2FGA/40','2FG%','3FGM/40','3FGA/40','3FG%',"3 Point Proficiency",'3 Point Confidence','FT/40','FTA/40','FT%','TRB/40','AST/40','STL/40','BLK/40','TOV/40','PF/40','PTS/40',
                'FGM/100Poss','FGA/100Poss','2FGM/100Poss','2FGA/100Poss','3FGM/100Poss','3FGA/100Poss','FT/100Poss','FTA/100Poss','TRB/100Poss','AST/100Poss','STL/100Poss','BLK/100Poss','TOV/100Poss','PF/100Poss','PTS/100Poss','FGA/100Poss',
                '# Dunks',"Dunk vs Rim Shot Percentage","% Dunks Unassisted","Dunks per Minute Played",
                '% Shots @ Rim','FG% @ Rim','%Astd @ Rim','% Shots @ Mid','FG% @ Mid','%Astd @ Mid','% Shots @ 3','%Astd @ 3','% Assisted',
                'AAU Season','AAU Team','AAU League','AAU GP','AAU GS','AAU MIN','AAU PTS','AAU FGM','AAU FGA','AAU FG%','AAU 3PM','AAU 3PA','AAU 3P%','AAU FTM','AAU FTA','AAU FT%','AAU ORB','AAU DRB','AAU TRB','AAU AST','AAU STL','AAU BLK','AAU TOV','AAU PF',
                'Event Year','Event Name','Event GP','Event MIN','Event PTS','Event FGM','Event FGA','Event FG%','Event 3PM','Event 3PA','Event 3P%','Event FTM','Event FTA','Event FT%','Event TRB','Event AST','Event STL','Event BLK','Event TOV','Event PF','Event Placement',
                'Box Score Creation','Rim Shot Creation','Helio Score']]
    
import sys
sys.path.append("./src")


df = pd.read_csv("data/db_2022.csv")
df = df[df['MP'] >= 100]
df = add_aux_columns(df)
df.to_csv('data/db_2022_special.csv', index=False)
#get_value_at_column_by_player_name(df, "Ja Morant", "Helio Score")
#add_aux_columns(df).to_csv("data/jason_db.csv", index=False)
#for index, row in df.iterrows():
#draw_conclusions_on_player(df, "Baylor Scheierman")

#print(get_value_at_column_by_player_name(df, "Baylor Scheierman", 'USG%'))
#draw_conclusions_on_column(df, 'USG%')
# Scheierman, Terq, Harrison Ingram, Sasser, Tshiebwe, Matthew Cleveland, Strawther, Tyrese Hunter, Taran Armstrong, Kaluma
'''1. Terq?
2. Kaluma
3. Scheierman
4. Tshiebwe
5. Taran Armstrong
6. Strawther
7. Tyrese Hunter
8. Marcus Sasser
9. Harrison Ingram
10. Cleveland
'''