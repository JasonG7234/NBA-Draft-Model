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
        (df['% Shots @ Mid']/100*df['%Astd @ Mid']) +
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
    
    #Pure points
    temp = df[(df['Position 1'] == 'PG') & (df['Position 2'] != 'SG')]
    pg = create_percentile_ranks_by_position_group(temp)
    #Combos
    temp = df[((df['Position 1'] == 'PG') & (df['Position 2'] == 'SG')) | ((df['Position 1'] == 'SG') & (df['Position 2'] == 'PG'))]
    g = create_percentile_ranks_by_position_group(temp)
    #Pure 2s
    temp = df[(df['Position 1'] == 'SG') & ((df['Position 2'] != 'PG') & (df['Position 2'] != 'SF'))]
    sg = create_percentile_ranks_by_position_group(temp)
    #Wings
    temp = df[((df['Position 1'] == 'SG') & (df['Position 2'] == 'SF')) | ((df['Position 1'] == 'SF') & (df['Position 2'] == 'SG'))]
    gf = create_percentile_ranks_by_position_group(temp)
    #Pure 3s
    temp = df[(df['Position 1'] == 'SF') & ((df['Position 2'] != 'SG') & (df['Position 2'] != 'PF'))]
    sf = create_percentile_ranks_by_position_group(temp)
    #Forwards
    temp = df[((df['Position 1'] == 'SF') & (df['Position 2'] == 'PF')) | ((df['Position 1'] == 'PF') & (df['Position 2'] == 'SF'))]
    f = create_percentile_ranks_by_position_group(temp)
    #Pure 4s
    temp = df[(df['Position 1'] == 'PF') & ((df['Position 2'] != 'SF') & (df['Position 2'] != 'C'))]
    pf = create_percentile_ranks_by_position_group(temp)
    #Bigs
    temp = df[((df['Position 1'] == 'PF') & (df['Position 2'] == 'C')) | ((df['Position 1'] == 'C') & (df['Position 2'] == 'PF'))]
    b = create_percentile_ranks_by_position_group(temp)
    #Pure 5s
    temp = df[(df['Position 1'] == 'C') & (df['Position 2'] != 'PF')]
    c = create_percentile_ranks_by_position_group(temp)
    
    df_temp = pd.concat([pg, g, sg, gf, sf, f, pf, b, c], axis=0)
    #draw_conclusions_on_column(df_temp, "Overall Score")
    return df_temp

def create_percentile_ranks_by_position_group(temp):
    temp['FTr Rank'] = temp['FTr'].rank(pct=True, ascending=True)
    temp['STK% Rank'] = temp['Stock%'].rank(pct=True, ascending=True)
    temp['%A@R Rank'] = temp['%Astd @ Rim'].rank(pct=True, ascending=False)
    temp['#D Rank'] = temp['# Dunks'].rank(pct=True, ascending=True)
    temp['PPR Rank'] = temp['Pure Point Rating'].rank(pct=True, ascending=True)
    temp['AST/40 Rank'] = temp['AST/40'].rank(pct=True, ascending=True)
    temp['A/V Rank'] = temp['AST/TOV'].rank(pct=True, ascending=True)
    temp['TRB% Rank'] = temp['TRB%'].rank(pct=True, ascending=True)
    temp['3PP Rank'] = temp['3 Point Proficiency'].rank(pct=True, ascending=True)
    temp['FT% Rank'] = temp['FT%'].rank(pct=True, ascending=True)
    temp['F%@M Rank'] = temp['FG% @ Mid'].rank(pct=True, ascending=True)
    temp['F%@R Rank'] = temp['FG% @ Rim'].rank(pct=True, ascending=True)
    temp['%S@R Rank'] = temp['% Shots @ Rim'].rank(pct=True, ascending=True)
    temp['DR Rank'] = temp['DEF RTG'].rank(pct=True, ascending=False)
    temp['HOB Rank'] = temp['Hands-On Buckets'].rank(pct=True, ascending=True)
    temp['%A@M Rank'] = temp['%Astd @ Mid'].rank(pct=True, ascending=False)
    temp['OL Rank'] = temp['Offensive Load'].rank(pct=True, ascending=True)
    temp['%A@3 Rank'] = temp['%Astd @ 3'].rank(pct=True, ascending=False)
    temp['SOS Rank'] = temp['SOS'].rank(pct=True, ascending=True)
    temp['WS/40 Rank'] = temp['WS/40'].rank(pct=True, ascending=True)
    temp['BPM Rank'] = temp['BPM'].rank(pct=True, ascending=True)
    # -----------------------------------------------------------------------
    temp['Athleticism Score'] = round((temp['FTr Rank']+temp['#D Rank']+temp['STK% Rank']+temp['%A@R Rank'])/4, 3)
    temp['Passing Score'] = round((temp['PPR Rank']+temp['AST/40 Rank']+temp['A/V Rank'])/3, 3)
    temp['Rebounding Score'] = temp['TRB% Rank']
    temp['Shooting Score'] = round((temp['3PP Rank']+temp['F%@M Rank'])+temp['FT% Rank']/3, 3)
    temp['Finishing Score'] = round((temp['F%@R Rank']+temp['%S@R Rank'])/2, 3)
    #draw_conclusions_on_column(temp, 'Finishing Score', num_top=20)
    temp['Defense Score'] = round((temp['STK% Rank']+temp['DR Rank'])/2, 3)
    temp['Shot Creation Score'] = round((temp['HOB Rank']+temp['%A@M Rank']+temp['OL Rank']+temp['%A@3 Rank'])/4, 3)
    temp['College Productivity Score'] = round((temp['SOS Rank']+temp['WS/40 Rank']+temp['BPM Rank'])/3, 3)
    # -----------------------------------------------------------------------
    temp['Athleticism Score'] = temp['Athleticism Score'].rank(pct=True, ascending=True)
    temp['Passing Score'] = temp['Passing Score'].rank(pct=True, ascending=True)
    temp['Shooting Score'] = temp['Shooting Score'].rank(pct=True, ascending=True)
    temp['Finishing Score'] = temp['Finishing Score'].rank(pct=True, ascending=True)
    temp['Defense Score'] = temp['Defense Score'].rank(pct=True, ascending=True)
    temp['Shot Creation Score'] = temp['Shot Creation Score'].rank(pct=True, ascending=True)
    temp['College Productivity Score'] = temp['College Productivity Score'].rank(pct=True, ascending=True)
    # -----------------------------------------------------------------------
    temp['Percentile Score'] = round((temp['Athleticism Score']+temp['Passing Score']+temp['Shooting Score']+temp['Finishing Score']+temp['Defense Score']+temp['Shot Creation Score']+temp['College Productivity Score']+temp['Rebounding Score'])/8, 3)*100
    # -----------------------------------------------------------------------------
    temp.drop(['BPM Rank', 'WS/40 Rank', 'SOS Rank', '%A@3 Rank', 'OL Rank', '%A@M Rank', 'HOB Rank', 'DR Rank', '%S@R Rank', 'F%@R Rank', 'F%@M Rank', 
               '3PP Rank', 'FT% Rank', 'TRB% Rank', 'A/V Rank', 'AST/40 Rank', 'PPR Rank', '#D Rank', '%A@R Rank', 'STK% Rank', 'FTr Rank'], axis=1, inplace=True)
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
    return df[['RealGM ID','Season','Name',
                'Position 1','Position 2','Play Style','Height','Weight',
                'School','Conference','Wins','Losses','SOS',
                'Class','Birthday','Draft Day Age',
                'RSCI','G','GS','MP','PER','TS%','eFG%','3PAr','FTr','PProd','ORB%','DRB%','TRB%','AST%','STL%','BLK%','Stock%','Harmonic STK%','TOV%','Adjusted TOV%','USG%','Offensive Load','OWS','DWS','WS','WS/40','OBPM','DBPM','BPM','AST/TOV','OFF RTG','DEF RTG','Hands-On Buckets','Pure Point Rating',
                'FG/40','FGA/40','FG%','2FGM/40','2FGA/40','2FG%','3FGM/40','3FGA/40','3FG%',"3 Point Proficiency",'3 Point Confidence','FT/40','FTA/40','FT%','TRB/40','AST/40','STL/40','BLK/40','TOV/40','PF/40','PTS/40',
                'FGM/100Poss','FGA/100Poss','2FGM/100Poss','2FGA/100Poss','3FGM/100Poss','3FGA/100Poss','FT/100Poss','FTA/100Poss','TRB/100Poss','AST/100Poss','STL/100Poss','BLK/100Poss','TOV/100Poss','PF/100Poss','PTS/100Poss',
                '# Dunks',"Dunk vs Rim Shot Percentage","% Dunks Unassisted","Dunks per Minute Played","Unassisted Shots @ Rim /100Poss",
                '% Shots @ Rim','FG% @ Rim','%Astd @ Rim','% Shots @ Mid','FG% @ Mid','%Astd @ Mid','% Shots @ 3','%Astd @ 3','% Assisted',
                'AAU Season','AAU Team','AAU League','AAU GP','AAU GS','AAU MIN','AAU PTS','AAU FGM','AAU FGA','AAU FG%','AAU 3PM','AAU 3PA','AAU 3P%','AAU FTM','AAU FTA','AAU FT%','AAU ORB','AAU DRB','AAU TRB','AAU AST','AAU STL','AAU BLK','AAU TOV','AAU PF',
                'Event Year','Event Name','Event GP','Event MIN','Event PTS','Event FGM','Event FGA','Event FG%','Event 3PM','Event 3PA','Event 3P%','Event FTM','Event FTA','Event FT%','Event TRB','Event AST','Event STL','Event BLK','Event TOV','Event PF','Event Placement',
                'Finishing Score','Shooting Score','Shot Creation Score','Passing Score','Rebounding Score','Athleticism Score','Defense Score','College Productivity Score','Percentile Score',
                'Box Score Creation','Rim Shot Creation','Helio Score','Draft Score','Image Link']]
    
import sys
sys.path.append("./src")

def main():
    df = pd.read_csv("data/draft_db.csv")
    df = add_aux_columns(df)
    df.to_csv("data/draft_db.csv", index=False)
    
main()