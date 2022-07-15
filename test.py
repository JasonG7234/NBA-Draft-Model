import pandas as pd
import math
import plotly.express as px  
import streamlit as st 
from utils import *

def jason_3pt_confidence(df):
    cast_column_to_float(df, '3FG%')
    cast_column_to_float(df, '3PAr')
    df['3 Point Confidence'] = df['3FG%']*df['3PAr']
    return df

def percent_assisted_overall(df):
    df['% Assisted'] = (
        (df['%Astd @ Rim']/100*df['% Shots @ Rim']) +
        (df['% Shots @ Mid']/100*df['%Astd @ Mid']) +
        (df['%Astd @ 3']/100*df['% Shots @ 3'])
    )
    return df

def bentaylor_stats(df):
    df["3 Point Proficiency"] = ""
    df['Box Score Creation'] = ""
    df['Offensive Load'] = ""
    df['Adjusted TOV%'] = ""
    for index, row in df.iterrows():
        if not pd.isna(row['3FGA/100Poss']):
            _3PA = -abs(float(row['3FGA/100Poss']))
            _3P = float(row['3FG%'])
            _3PP = (((2/(1+math.pow(math.e, _3PA))-1)*_3P)+(float(row['3FG%'])*float(row['3PAr'])))/2
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
    df['Box Score Creation'].replace('', np.nan, inplace=True)
    df['Box Score Creation'].astype(float)
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

def set_up_streamlit(df):
    st.set_page_config(page_title="NBA Draft Model", page_icon=":bar_chart:", layout="wide")

    st.sidebar.header("Please Filter Here:")
    position = st.sidebar.multiselect(
        "Select the primary position:",
        options=df["Position 1"].unique(),
        default=df["Position 1"].unique()
    )

    season = st.sidebar.multiselect(
        "Select the season:",
        options=df["Season"].unique(),
        default=df["Season"].unique()
    )

    classification = st.sidebar.multiselect(
        "Select the class/year:",
        options=df["Class"].unique(),
        default=df["Class"].unique()
    )
    st.sidebar.text("Class 1 = Freshmen, Class 2 = Sophomore, etc.")

    df_selection = df.query(
        "'Position 1' == @position & Season == @season & Class == @classification"
    )
    df['Position 2'] = df['Position 2'].fillna('')
    df = df.round({'PER': 1})
    st.dataframe(df)

    bsc = (
        df_selection.groupby(by=["Class"]).mean()[["Box Score Creation"]].sort_values(by="Box Score Creation")
    )
    fig_bsc = px.bar(
        bsc,
        x="Box Score Creation",
        y=bsc.index,
        orientation="h",
        title="<b>Box Score Creation by Year</b>",
        color_discrete_sequence=["#0083B8"] * len(bsc),
        template="plotly_white",
    )
    fig_bsc.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=(dict(showgrid=False))
    )

    offensive_load_by_position = df_selection.groupby(by=["Position 1"]).mean()[["Offensive Load"]]
    fig_offensive_load = px.bar(
        offensive_load_by_position,
        x='Position 1',
        y="Offensive Load",
        title="<b>Offensive Load By Position</b>",
        color_discrete_sequence=["#0083B8"] * len(offensive_load_by_position),
        template="plotly_white",
    )
    fig_offensive_load.update_layout(
        xaxis=dict(tickmode="linear"),
        plot_bgcolor="rgba(0,0,0,0)",
        yaxis=(dict(showgrid=False)),
    )

    left_column, right_column = st.columns(2)
    left_column.plotly_chart(fig_offensive_load, use_container_width=True)
    right_column.plotly_chart(fig_bsc, use_container_width=True)
    #df.to_csv('temp_master.csv', index=False)
    hide_st_style = """
                <style>
                #dfMenu {visibility: hidden;}
                footer {visibility: hidden;}
                header {visibility: hidden;}
                </style>
                """
    st.markdown(hide_st_style, unsafe_allow_html=True)
    
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

    
def add_aux_columns(df):
    #df = jason_3pt_confidence(df)
    df = bentaylor_stats(df)
    df = normalize(df, 'Height')
    df = normalize(df, 'SOS')
    df = normalize(df, 'Draft Day Age', True)
    
    df['Box Score Creation'].replace('', np.nan, inplace=True)
    df['Box Score Creation'].astype(float)
    df['Helio Score'] = (df['Box Score Creation'] * (df['Height Normalized']+0.05) * df['SOS Normalized'] * df['Draft Day Age Normalized'])
    df.loc[df['G'] <= 15, 'Helio Score'] = df['Helio Score']*(df['G']/15)
    for index, row in df.nlargest(25, ['Helio Score']).iterrows():
        df.loc[index, 'Play Style'] = 'Primary'
    df.drop(['Height Normalized', 'SOS Normalized', 'Draft Day Age Normalized'], axis=1, inplace=True)
    #draw_conclusions_on_column(df, '3 Point Confidence', num_top=15)
    return df

def reorder_final_columns_with_playstyle(df):
    return df[['RealGM ID','Season','Name',
                'Position 1','Position 2','Play Style',
                'School','Conference','Wins','Losses','SOS',
                'Class','Birthday','Draft Day Age',
                'Height','Weight','Height w/o Shoes','Height w/ Shoes','Wingspan','Standing Reach','Body Fat %','Hand Length','Hand Width',
                'RSCI','G','GS','MP','PER','TS%','eFG%','3PAr','FTr','PProd','ORB%','DRB%','TRB%','AST%','STL%','BLK%','TOV%','USG%','OWS','DWS','WS','WS/40','OBPM','DBPM','BPM','ATS/TOV','OFF RTG','DEF RTG','Hands-On Buckets','Pure Point Rating',
                'FG/40','FGA/40','FG%','2FGM/40','2FGA/40','2FG%','3FGM/40','3FGA/40','3FG%','FT/40','FTA/40','FT%','TRB/40','AST/40','STL/40','BLK/40','TOV/40','PF/40','PTS/40',
                'FGM/100Poss','FGA/100Poss','2FGM/100Poss','2FGA/100Poss','3FGM/100Poss','3FGA/100Poss','FT/100Poss','FTA/100Poss','TRB/100Poss','AST/100Poss','STL/100Poss','BLK/100Poss','TOV/100Poss','PF/100Poss','PTS/100Poss','FGA/100Poss',
                '# Dunks','% Shots @ Rim','FG% @ Rim','%Astd @ Rim','% Shots @ Mid','FG% @ Mid','%Astd @ Mid','% Shots @ 3','%Astd @ 3',
                'AAU Season','AAU Team','AAU League','AAU GP','AAU GS','AAU MIN','AAU PTS','AAU FGM','AAU FGA','AAU FG%','AAU 3PM','AAU 3PA','AAU 3P%','AAU FTM','AAU FTA','AAU FT%','AAU ORB','AAU DRB','AAU TRB','AAU AST','AAU STL','AAU BLK','AAU TOV','AAU PF',
                'Event Year','Event Name','Event GP','Event MIN','Event PTS','Event FGM','Event FGA','Event FG%','Event 3PM','Event 3PA','Event 3P%','Event FTM','Event FTA','Event FT%','Event TRB','Event AST','Event STL','Event BLK','Event TOV','Event PF','Event Placement'
                ]]
    
df = pd.read_csv('temp.csv')
df = add_aux_columns(df)
df.to_csv('temp.csv', index=False)



