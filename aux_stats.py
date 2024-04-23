import pandas as pd
import numpy as np
import math
from utils import *

def jason_3pt_confidence(df):
    df['3 Point Confidence'] = 2/(1/df['3FG%']+1/df['3PAr'])
    return df

def percent_assisted_overall(df):
    cast_column_to_float(df, '%Astd @ 3')
    df['% Assisted'] = (
        (df['%Astd @ Rim']/100*df['% Shots @ Rim']) +
        (df['%Astd @ Mid']/100*df['% Shots @ Mid']) +
        (df['%Astd @ 3']/100*df['% Shots @ 3'])
    )
    #draw_conclusions_on_column(df, '% Assisted')
    return df

def self_created_dunks(df):
    df["Dunks per Minute"] = df['# Dunks'] / df['MP']
    df["Rim Shots per Minute"] = (df['% Shots @ Rim'] * df['FGA/40']) / 4000
    df["Dunk vs Rim Shot Percentage"] = round((df["Dunks per Minute"] / df["Rim Shots per Minute"])*100, 2)
    df["% Dunks Unassisted"] = (100-df['%Astd @ Rim'])*(df['Dunk vs Rim Shot Percentage']*df['% Shots @ Rim']/100)/100
    df["Rim Shot Creation"] = ""
    for index, row in df.iterrows():
        _RSC = (2/math.pow(math.e, row['%Astd @ Rim']/150))*(row['FG% @ Rim']/2)+(row['% Shots @ Rim']*row['FGA/100Poss']*0.01)
        df.loc[index, 'Rim Shot Creation'] = round(_RSC, 3)
    df.drop(["Rim Shots per Minute", "Dunks per Minute"], axis=1, inplace=True)
    return df

def bentaylor_stats(df):
    df["Harmonic STK%"] = (2*df['STL%']*df['BLK%'])/(df['STL%']+df['BLK%'])
    Three_Point_Proficiency = []
    Box_Score_Creation = []
    Offensive_Load = []
    Adjusted_TOV = []
    for index, row in df.iterrows():
        _3PA = -abs(float(row['3FGA/100Poss']))
        if (_3PA == 0):
            _3PP = 0
        else:
            _3P = float(row['3FG%'])
            _3PP = (((2/(1+math.pow(math.e, _3PA))-1)*_3P)+(_3P*float(row['3PAr'])))/2
        Three_Point_Proficiency.append(round(_3PP, 3))
        _AST = float(row['AST/100Poss'])
        _PTS = float(row['PTS/100Poss'])
        _TOV = float(row['TOV/100Poss'])
        _BSC = _AST*0.1843+(_PTS+_TOV)*0.0969-2.3021*(_3PP)+0.0582*(_AST*(_PTS+_TOV)*_3PP)-1.1942
        Box_Score_Creation.append(round(_BSC, 3))
        _FGA = float(row['FGA/100Poss'])
        _FTA = float(row['FTA/100Poss'])
        _OL = ((_AST-(0.38*_BSC))*0.75)+_FGA+_FTA*0.44+_BSC+_TOV
        Offensive_Load.append(round(_OL, 3))
        _cTOV = _TOV / _OL
        Adjusted_TOV.append(round(_cTOV, 3))
    #df[].fillna(df['Box Score Creation'].mean())
    df.loc[:, '3 Point Proficiency'] = Three_Point_Proficiency
    df.loc[:, 'Box Score Creation'] = Box_Score_Creation
    df.loc[:, 'Offensive Load'] = Offensive_Load
    df.loc[:, 'Adjusted TOV%'] = Adjusted_TOV
    df['Box Score Creation'] = pd.to_numeric(df['Box Score Creation'], downcast="float")
    return df

    
def play_styles(df):
    pg = df[df['Position 1'] == 'PG']
    pg.loc[:, 'Floor General'] = pg['Pure Point Rating'].rank(na_option='bottom', pct=True)
    pg.loc[:, 'Athletic'] = pg['% Shots @ Rim'].rank(na_option='keep', pct=True)
    pg.loc[:, 'Scorer'] = pg['PTS/40'].rank(na_option='bottom', pct=True)
    pg.loc[:, 'Shooter'] = pg['3FG%'].rank(na_option='bottom', pct=True)
    pg.loc[:, 'Play Style'] = pg[['Floor General','Athletic','Scorer','Shooter']].idxmax(axis=1)
    pg.drop(['Floor General','Athletic','Scorer','Shooter'], axis=1, inplace=True)
    
    c = df[df['Position 1'] == 'C']
    c.loc[:, 'Stretch'] = c['3FGM/40'].rank(na_option='keep', pct=True)
    for index, row in c.iterrows():
        if row['3FGM/40'] <= 1:
            c.loc[index, 'Stretch%'] = 0
    c.loc[:, 'Rebounder'] = c['ORB%'].rank(na_option='keep', pct=True)
    c.loc[:, 'Play Finisher'] = c['2FG%'].rank(na_option='keep', pct=True)
    c.loc[:, 'Short Roll'] = c['AST%'].rank(na_option='keep', pct=True)
    c.loc[:, 'Post Up'] = c['%Astd @ Rim'].rank(na_option='keep', ascending=False, pct=True)
    c.loc[:, 'Play Style'] = c[['Stretch','Rebounder','Play Finisher','Short Roll', 'Post Up']].idxmax(axis=1)
    c.drop(['Stretch','Rebounder','Play Finisher','Short Roll', 'Post Up'], axis=1, inplace=True)
    
    wing = df[(df['Position 1'] == 'SF') | (df['Position 1'] == 'SG')]
    wing.loc[:, 'Scorer'] = wing['PTS/40'].rank(na_option='keep', pct=True)
    wing.loc[:, 'Shooter'] = wing['% Shots @ 3'].rank(na_option='keep', pct=True)
    wing.loc[:, 'Slasher'] = wing['% Shots @ Rim'].rank(na_option='keep', pct=True)
    wing.loc[:, 'Play Style'] = wing[['Scorer','Shooter','Slasher']].idxmax(axis=1)
    for index, row in wing.iterrows():
        if row['Scorer'] <= 0.675 and row['Slasher'] <= 0.675 and row['Shooter'] <= 0.675:
            wing.loc[index, 'Play Style'] = 'Connector'
    wing.drop(['Scorer','Shooter','Slasher'], axis=1, inplace=True)
    
    pf = df[df['Position 1'] == 'PF']
    pf.loc[:, 'Stretch'] = pf['3FGM/40'].rank(na_option='keep', pct=True)
    for index, row in pf.iterrows():
        if row['3FGM/40'] <= 1.75:
            pf.loc[index, 'Stretch'] = 0
    pf.loc[:, 'Energy'] = pf['ORB%'].rank(na_option='keep', pct=True)
    pf.loc[:, 'Playmaker'] = pf['AST%'].rank(na_option='keep', pct=True)
    pf.loc[:, 'Scorer'] = pf['PTS/40'].rank(na_option='keep', pct=True)
    pf.loc[:, 'Play Style'] = pf[['Stretch','Energy','Playmaker','Scorer']].idxmax(axis=1)
    for index, row in pf.iterrows():
        if row['Scorer'] <= 0.675 and row['Playmaker'] <= 0.675 and row['Stretch'] <= 0.675 and row['Energy'] <= 0.675:
            pf.loc[index, 'Play Style'] = 'Connector'
    pf.drop(['Stretch','Energy','Playmaker','Scorer'], axis=1, inplace=True)
    new_df = pd.concat([pg, wing, pf, c], axis=0)
    return new_df.sort_values(by=['BPM'], ascending=False)

def athleticism(df):
    df["Dunks per Minute Played"] = df['# Dunks'] / df['MP']
    df['Stock%'] = df['STL%'] * df['BLK%']
    df['%Unastd @ Rim'] = 100-df['%Astd @ Rim']
    df['Shots @ Rim / 100'] = df['% Shots @ Rim'] * df['FGA/100Poss'] / 100
    df['Unassisted Shots @ Rim /100Poss'] = df['%Unastd @ Rim'] * df['Shots @ Rim / 100'] / 100
    df = normalize(df, 'Height', True)
    df = normalize(df, 'Stock%')
    df["Athleticism?"] = (df['Height Normalized']) * (df["Dunks per Minute Played"]+1) * (df["Stock% Normalized"]) * (df['Unassisted Shots @ Rim /100Poss'])*50
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

def add_aux_columns(df, divide_by_position=True):
    for col in df.columns:
        if "RealGM" in str(col):
            df[col] = df[col].astype(int)
            df[col] = df[col].astype(str)
        elif pd.to_numeric(df[col], errors='coerce').notna().all():
            df[col] = pd.to_numeric(df[col], errors='coerce').astype(float)
    
    

    df['3FGA/100Poss'].fillna(0)
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
    
    df['Helio Score'] = (df['Box Score Creation'] * (df['Height Normalized']) * (df['SOS Normalized']+1) * df['Draft Day Age Normalized'])
    df.loc[df['G'] <= 15, 'Helio Score'] = df['Helio Score']*(df['G']/15)
    df['Box Score Creation'].astype(float)
    for index, row in df.nlargest(25, ['Helio Score']).iterrows():
        df.loc[index, 'Play Style'] = 'Primary'
    df.drop(['Height Normalized', 'SOS Normalized', 'Draft Day Age Normalized'], axis=1, inplace=True)
    #draw_conclusions_on_column(df, '"% Dunks Unassisted"', num_top=25)
    #get_value_at_column_by_player_name(df, "Ja Morant", "Helio Score", True)
    if (divide_by_position):
        df = divide_by_positions(df)
    else:
        df = create_percentile_ranks_by_position_group(df)
    df = build_draft_ranking_column(df)
    return reorder_aux_columns(df)

def divide_by_positions(df):
    
    # GUARDS - if you can play PG
    # WINGS - if you have SG&SF
    # FORWARDS - if you have PF
    # BIGS - if you have C
    
    # Guards
    temp = df[(df['Position 1'] == 'PG') | (df['Position 2'] == 'PG')]
    g = create_percentile_ranks_by_position_group(temp)
    #Wings - most complex (SG, SG/SF, SF/SG, SF)
    temp = df[((df['Position 1'] == 'SG') & (df['Position 2'] == 'SF')) | ((df['Position 1'] == 'SF') & (df['Position 2'] == 'SG')) | ((df['Position 1'] == 'SF') & (df['Position 2'] != 'SG') & df['Position 2'] != 'PF') | ((df['Position 1'] == 'SG') & (df['Position 2'] != 'SF') & df['Position 2'] != 'PG')]
    w = create_percentile_ranks_by_position_group(temp)
    #Forwards
    temp = df[(df['Position 1'] == 'PF') | (df['Position 2'] == 'PF')]
    f = create_percentile_ranks_by_position_group(temp)
    # Bigs
    temp = df[(df['Position 2'] == 'C') | (df['Position 1'] == 'C')]
    b = create_percentile_ranks_by_position_group(temp)
    
    df_temp = pd.concat([g, w, f, b], axis=0)
    #draw_conclusions_on_column(df_temp, "Overall Score")
    return df_temp
 
def create_percentile_ranks_by_position_group(temp):
    temp = normalize(temp, 'FTr')
    temp = normalize(temp,'Stock%')
    temp = normalize(temp, '%Astd @ Rim')
    temp = normalize(temp, '# Dunks')
    temp = normalize(temp,'Pure Point Rating')
    temp = normalize(temp, 'AST/40')
    temp = normalize(temp, 'AST/TOV')
    temp = normalize(temp, 'TRB%')
    temp = normalize(temp, '3 Point Proficiency')
    temp = normalize(temp, 'FT%')
    temp = normalize(temp, 'FG% @ Mid')
    temp = normalize(temp, 'FG% @ Rim')
    temp = normalize(temp, '% Shots @ Rim')
    temp = normalize(temp, 'Hands-On Buckets')
    temp = normalize(temp, '%Astd @ Mid')
    temp = normalize(temp, 'Offensive Load')
    temp = normalize(temp, '%Astd @ 3')
    temp = normalize(temp, 'SOS')
    temp = normalize(temp, 'WS/40')
    temp = normalize(temp, 'Adj OFF +/-')
    temp = normalize(temp,'Adj DEF +/-')
    # -----------------------------------------------------------------------
    temp.loc[:, 'Athleticism Score'] = round((temp.loc[:, 'FTr Normalized']+temp.loc[:, '# Dunks Normalized']+temp.loc[:, 'Stock% Normalized']+temp.loc[:, '%Astd @ Rim Normalized'])/4, 3)
    temp.loc[:, 'Passing Score'] = round((temp.loc[:, 'Pure Point Rating Normalized']+temp.loc[:, 'AST/40 Normalized']+temp.loc[:, 'AST/TOV Normalized'])/3, 3)
    temp.loc[:, 'Rebounding Score'] = temp['TRB% Normalized']
    temp.loc[:, 'Shooting Score'] = round((temp.loc[:, '3 Point Proficiency Normalized']+temp.loc[:, 'FG% @ Mid Normalized'])+temp.loc[:, 'FT% Normalized']/3, 3)
    temp.loc[:, 'Finishing Score'] = round((temp.loc[:, 'FG% @ Rim Normalized']+temp.loc[:, '% Shots @ Rim Normalized'])/2, 3)
    temp.loc[:, 'Defense Score'] = round((temp.loc[:, 'Stock% Normalized']+temp.loc[:, 'Adj DEF +/- Normalized'])/2, 3)
    temp.loc[:, 'Shot Creation Score'] = round((temp.loc[:, 'Hands-On Buckets Normalized']+temp.loc[:, '%Astd @ Mid Normalized']+temp.loc[:, 'Offensive Load Normalized']+temp.loc[:, '%Astd @ 3 Normalized'])/4, 3)
    temp.loc[:, 'College Productivity Score'] = round((temp.loc[:, 'SOS Normalized']+temp.loc[:, 'WS/40 Normalized']+temp.loc[:, 'Adj OFF +/- Normalized'])/3, 3)
    # -----------------------------------------------------------------------
    temp.loc[:, 'Athleticism Score'] = temp['Athleticism Score'].rank(pct=True, ascending=True)
    temp.loc[:, 'Passing Score'] = temp['Passing Score'].rank(pct=True, ascending=True)
    temp.loc[:, 'Shooting Score'] = temp['Shooting Score'].rank(pct=True, ascending=True)
    temp.loc[:, 'Finishing Score'] = temp['Finishing Score'].rank(pct=True, ascending=True)
    temp.loc[:, 'Defense Score'] = temp['Defense Score'].rank(pct=True, ascending=True)
    temp.loc[:, 'Shot Creation Score'] = temp['Shot Creation Score'].rank(pct=True, ascending=True)
    temp.loc[:, 'College Productivity Score'] = temp['College Productivity Score'].rank(pct=True, ascending=True)
    # -----------------------------------------------------------------------
    temp.loc[:, 'Percentile Score'] = round((temp.loc[:, 'Athleticism Score']+temp.loc[:, 'Passing Score']+temp.loc[:, 'Shooting Score']+temp.loc[:, 'Finishing Score']+temp.loc[:, 'Defense Score']+temp.loc[:, 'Shot Creation Score']+temp.loc[:, 'College Productivity Score']+temp.loc[:, 'Rebounding Score'])/8, 3)*100
    # -----------------------------------------------------------------------------
    temp.drop(['WS/40 Normalized', 'SOS Normalized', '%Astd @ 3 Normalized', 'Offensive Load Normalized', '%Astd @ Mid Normalized', 'Hands-On Buckets Normalized', '% Shots @ Rim Normalized', 'FG% @ Rim Normalized', 'FG% @ Mid Normalized', 
               '3 Point Proficiency Normalized', 'FT% Normalized', 'TRB% Normalized', 'AST/TOV Normalized', 'AST/40 Normalized', 'Pure Point Rating Normalized', '# Dunks Normalized', '%Astd @ Rim Normalized', 'Stock% Normalized', 'FTr Normalized'], axis=1, inplace=True)
    return temp

def build_draft_ranking_column(df):
    df = normalize(df, 'Height')
    df = normalize(df, 'SOS')
    df = normalize(df, 'Draft Day Age', True)
    df = normalize(df, 'RSCI', True)
    #draw_conclusions_on_column(df, "RSCI Normalized", num_top=15)
    df = normalize(df, 'Box Score Creation')
    df = normalize(df, 'Percentile Score')
    df = normalize(df, 'MP')
    #draw_conclusions_on_column(df, "SOS Normalized", num_top=15)
    df['Draft Score'] = 5.5/(
        (0.25/(df['MP Normalized']+0.01)) +
        (0.25/(df['RSCI Normalized']+0.01)) +
        (1/df['Percentile Score Normalized']) +
        (1/df['Box Score Creation Normalized']) +
        (1/df['Draft Day Age Normalized']) +
        (0.5/(df['Height Normalized']+0.01)) +
        (0.5/df['SOS Normalized']))
    return df

def reorder_aux_columns(df):
    df['3FG%'] = df['3FG%']*100
    df['3PAr'] = df['3PAr']*100
    return df[['RealGM ID','Season','Name',
                'Position 1','Position 2','Play Style','Height','Weight',
                'School','Conference','Wins','Losses','SOS',
                'Class','Birthday','Draft Day Age',
                'RSCI','G','GS','MP','PER','TS%','eFG%','3PAr','FTr','PProd','ORB%','DRB%','TRB%','AST%','STL%','BLK%','Stock%','Harmonic STK%','TOV%','Adjusted TOV%','USG%','Offensive Load','OWS','DWS','WS','WS/40','OBPM','DBPM','BPM','AST/TOV','OFF RTG','DEF RTG','Hands-On Buckets','Pure Point Rating',
                'FG/40','FGA/40','FG%','2FGM/40','2FGA/40','2FG%','3FGM/40','3FGA/40','3FG%',"3 Point Proficiency",'3 Point Confidence','FT/40','FTA/40','FT%','TRB/40','AST/40','STL/40','BLK/40','TOV/40','PF/40','PTS/40',
                'FGM/100Poss','FGA/100Poss','2FGM/100Poss','2FGA/100Poss','3FGM/100Poss','3FGA/100Poss','FT/100Poss','FTA/100Poss','TRB/100Poss','AST/100Poss','STL/100Poss','BLK/100Poss','TOV/100Poss','PF/100Poss','PTS/100Poss',
                '# Dunks',"Dunk vs Rim Shot Percentage","% Dunks Unassisted","Dunks per Minute Played","Unassisted Shots @ Rim /100Poss",
                '% Shots @ Rim','FG% @ Rim','%Astd @ Rim','% Shots @ Mid','FG% @ Mid','%Astd @ Mid','% Shots @ 3','%Astd @ 3','% Assisted',
                'Adj OFF +/-', 'Adj DEF +/-',
                'AAU Season','AAU Team','AAU League','AAU GP','AAU GS','AAU MIN','AAU PTS','AAU FGM','AAU FGA','AAU FG%','AAU 3PM','AAU 3PA','AAU 3P%','AAU FTM','AAU FTA','AAU FT%','AAU ORB','AAU DRB','AAU TRB','AAU AST','AAU STL','AAU BLK','AAU TOV','AAU PF',
                'Event Year','Event Name','Event GP','Event MIN','Event PTS','Event FGM','Event FGA','Event FG%','Event 3PM','Event 3PA','Event 3P%','Event FTM','Event FTA','Event FT%','Event TRB','Event AST','Event STL','Event BLK','Event TOV','Event PF','Event Placement',
                'Finishing Score','Shooting Score','Shot Creation Score','Passing Score','Rebounding Score','Athleticism Score','Defense Score','College Productivity Score','Percentile Score',
                'Box Score Creation','Rim Shot Creation','Helio Score','Draft Score','Image Link']]
    
import sys
sys.path.append("./src")

def main():
    df = pd.read_csv("data/draft_db.csv")
    df = add_aux_columns(df)
    df = delete_duplicates(df)
    df.to_csv("data/draft_db.csv", index=False)
    
main()