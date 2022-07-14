import pandas as pd
import math
import plotly.express as px  
import streamlit as st 
from utils import *

def jason_3pt_confidence(main):
    main['3 Point Confidence'] = ""
    for index, row in main.iterrows():
        main.loc[index, '3 Point Confidence'] = float(row['3FG%'])*float(row['3PAr'])
    return main

def bentaylor_stats(main):
    main["3 Point Proficiency"] = ""
    main['Box Score Creation'] = ""
    main['Offensive Load'] = ""
    main['Adjusted TOV%'] = ""
    for index, row in main.iterrows():
        if not pd.isna(row['3FGA/100Poss']):
            _3PA = -abs(float(row['3FGA/100Poss']))
            _3P = float(row['3FG%'])
            _3PP = (((2/(1+math.pow(math.e, _3PA))-1)*_3P)+(float(row['3FG%'])*float(row['3PAr'])))/2
            main.loc[index, '3 Point Proficiency'] = round(_3PP, 3)
            _AST = float(row['AST/100Poss'])
            _PTS = float(row['PTS/100Poss'])
            _TOV = float(row['TOV/100Poss'])
            _BSC = _AST*0.1843+(_PTS+_TOV)*0.0969-2.3021*(_3PP)+0.0582*(_AST*(_PTS+_TOV)*_3PP)-1.1942
            main.loc[index, 'Box Score Creation'] = round(_BSC, 3)
            _FGA = float(row['FGA/100Poss'])
            _FTA = float(row['FTA/100Poss'])
            _OL = ((_AST-(0.38*_BSC))*0.75)+_FGA+_FTA*0.44+_BSC+_TOV
            main.loc[index, 'Offensive Load'] = round(_OL, 3)
            _cTOV = _TOV / _OL
            main.loc[index, 'Adjusted TOV%'] = round(_cTOV, 3)
        else:
            print(f"{row['Name']}") 
    return main
    
def reorder_final_columns(main):
    return main[['RealGM ID','Season','Name',
                'Position 1','Position 2',
                'School','Wins','Losses','SOS',
                'Class','Birthday','Draft Day Age',
                'Height','Weight','Height w/o Shoes','Height w/ Shoes','Wingspan','Standing Reach','Body Fat %','Hand Length','Hand Width',
                'RSCI','G','GS','MP','PER','TS%','eFG%','3PAr','FTr','PProd','ORB%','DRB%','TRB%','AST%','STL%','BLK%','TOV%','USG%','OWS','DWS','WS','WS/40','OBPM','DBPM','BPM','ATS/TOV','OFF RTG','DEF RTG','Hands-On Buckets','Pure Point Rating',
                'FG/40','FGA/40','FG%','2FGM/40','2FGA/40','2FG%','3FGM/40','3FGA/40','3FG%','FT/40','FTA/40','FT%','TRB/40','AST/40','STL/40','BLK/40','TOV/40','PF/40','PTS/40',
                'FGM/100Poss','FGA/100Poss','2FGM/100Poss','2FGA/100Poss','3FGM/100Poss','3FGA/100Poss','FT/100Poss','FTA/100Poss','TRB/100Poss','AST/100Poss','STL/100Poss','BLK/100Poss','TOV/100Poss','PF/100Poss','PTS/100Poss','FGA/100Poss',
                '# Dunks','% Shots @ Rim','FG% @ Rim','%Astd @ Rim','% Shots @ Mid','FG% @ Mid','%Astd @ Mid','% Shots @ 3','%Astd @ 3',
                'AAU Season','AAU Team','AAU League','AAU GP','AAU GS','AAU MIN','AAU PTS','AAU FGM','AAU FGA','AAU FG%','AAU 3PM','AAU 3PA','AAU 3P%','AAU FTM','AAU FTA','AAU FT%','AAU ORB','AAU DRB','AAU TRB','AAU AST','AAU STL','AAU BLK','AAU TOV','AAU PF',
                'Event Year','Event Name','Event GP','Event MIN','Event PTS','Event FGM','Event FGA','Event FG%','Event 3PM','Event 3PA','Event 3P%','Event FTM','Event FTA','Event FT%','Event TRB','Event AST','Event STL','Event BLK','Event TOV','Event PF','Event Placement'
                ]]

def set_up_streamlit(main):
    st.set_page_config(page_title="NBA Draft Model", page_icon=":bar_chart:", layout="wide")

    st.sidebar.header("Please Filter Here:")
    position = st.sidebar.multiselect(
        "Select the primary position:",
        options=main["Position 1"].unique(),
        default=main["Position 1"].unique()
    )

    season = st.sidebar.multiselect(
        "Select the season:",
        options=main["Season"].unique(),
        default=main["Season"].unique()
    )

    classification = st.sidebar.multiselect(
        "Select the class/year:",
        options=main["Class"].unique(),
        default=main["Class"].unique()
    )
    st.sidebar.text("Class 1 = Freshmen, Class 2 = Sophomore, etc.")

    main_selection = main.query(
        "'Position 1' == @position & Season == @season & Class == @classification"
    )
    main['Position 2'] = main['Position 2'].fillna('')
    main = main.round({'PER': 1})
    st.dataframe(main)

    bsc = (
        main_selection.groupby(by=["Class"]).mean()[["Box Score Creation"]].sort_values(by="Box Score Creation")
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

    offensive_load_by_position = main_selection.groupby(by=["Position 1"]).mean()[["Offensive Load"]]
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
    #main.to_csv('temp_master.csv', index=False)
    hide_st_style = """
                <style>
                #MainMenu {visibility: hidden;}
                footer {visibility: hidden;}
                header {visibility: hidden;}
                </style>
                """
    st.markdown(hide_st_style, unsafe_allow_html=True)
    
def play_styles(main):
    # df = main[main['Position 1'] == 'PG']
    # df['Floor General%'] = df['Pure Point Rating'].rank(na_option='bottom', pct=True)
    # df['Athletic%'] = df['% Shots @ Rim'].rank(na_option='keep', pct=True)
    # df['Scorer%'] = df['PTS/40'].rank(na_option='bottom', pct=True)
    # df['Shooter%'] = df['3FG%'].rank(na_option='bottom', pct=True)
    # df['Play Style'] = df[['Floor General%','Athletic%','Scorer%','Shooter%']].idxmax(axis=1)
    # df.to_csv('PG.csv', index=False)
    
    # df = main[main['Position 1'] == 'C']
    # df['Stretch%'] = df['3FGM/40'].rank(na_option='keep', pct=True)
    # for index, row in df.iterrows():
    #     if row['3FGM/40'] <= 1:
    #         df.loc[index, 'Stretch%'] = 0
    # df['OREB%'] = df['ORB%'].rank(na_option='keep', pct=True)
    # df['PlayFinisher%'] = df['2FG%'].rank(na_option='keep', pct=True)
    # df['ShortRoll%'] = df['AST%'].rank(na_option='keep', pct=True)
    # df['PostUp%'] = df['%Astd @ Rim'].rank(na_option='keep', ascending=False, pct=True)
    # df['Play Style'] = df[['Stretch%','OREB%','PlayFinisher%','ShortRoll%', 'PostUp%']].idxmax(axis=1)
    # df.to_csv('C.csv', index=False)
    
    # df = main[main['Position 1'] in ['SF', 'SG']]
    # df['Creator%'] = df['Hands-On Buckets'].rank(na_option='keep', pct=True)
    # df['Scorer%'] = df['PTS/40'].rank(na_option='keep', pct=True)
    # df['Shooter%'] = df['% Shots @ 3'].rank(na_option='keep', pct=True)
    # df['Slasher%'] = df['% Shots @ Rim'].rank(na_option='keep', pct=True)
    # df['Play Style'] = df[['Creator%','Scorer%','Shooter%','Slasher%']].idxmax(axis=1)
    # for index, row in df.iterrows():
    #     if row['Scorer%'] <= 0.675 and row['Creator%'] <= 0.675 and row['Slasher%'] <= 0.675 and row['Shooter%'] <= 0.675:
    #         df.loc[index, 'Play Style'] = 'Connector'
    # # Creator, Scorer, Secondary, Connector, Shooter, Slasher, Off-Ball
    # df.to_csv('SF.csv', index=False)
    
        # df = main[main['Position 1'] == 'C']
    # df['Stretch%'] = df['3FGM/40'].rank(na_option='keep', pct=True)
    # for index, row in df.iterrows():
    #     if row['3FGM/40'] <= 1:
    #         df.loc[index, 'Stretch%'] = 0
    # df['OREB%'] = df['ORB%'].rank(na_option='keep', pct=True)
    # df['PlayFinisher%'] = df['2FG%'].rank(na_option='keep', pct=True)
    # df['ShortRoll%'] = df['AST%'].rank(na_option='keep', pct=True)
    # df['PostUp%'] = df['%Astd @ Rim'].rank(na_option='keep', ascending=False, pct=True)
    # df['Play Style'] = df[['Stretch%','OREB%','PlayFinisher%','ShortRoll%', 'PostUp%']].idxmax(axis=1)
    # df.to_csv('C.csv', index=False)
    
    df = main[main['Position 1'] == 'PF']
    df['Stretch%'] = df['3FGM/40'].rank(na_option='keep', pct=True)
    for index, row in df.iterrows():
        if row['3FGM/40'] <= 1.75:
            df.loc[index, 'Stretch%'] = 0
    df['Energy'] = df['ORB%'].rank(na_option='keep', pct=True)
    df['Playmaker%'] = df['AST%'].rank(na_option='keep', pct=True)
    df['Scorer%'] = df['PTS/40'].rank(na_option='keep', pct=True)
    df['Creator%'] = df['Hands-On Buckets'].rank(na_option='keep', pct=True)
    df['Play Style'] = df[['Stretch%','Energy','Playmaker%','Scorer%', 'Creator%']].idxmax(axis=1)
    for index, row in df.iterrows():
        if row['Scorer%'] <= 0.675 and row['Creator%'] <= 0.675 and row['Playmaker%'] <= 0.675 and row['Stretch%'] <= 0.675 and row['Energy'] <= 0.675:
            df.loc[index, 'Play Style'] = 'Connector'
    df.to_csv('PF.csv', index=False)
    
def add_aux_columns(main):
    main = jason_3pt_confidence(main)
    main = bentaylor_stats(main)
    df = play_styles(main)
    
main = pd.read_csv('data/main.csv')
add_aux_columns(main)
play_styles(main)
#df = main[main['Position 1'] == 'PG']
