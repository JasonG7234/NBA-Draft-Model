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
    
main = pd.read_csv('data/jason_db.csv')
#draw_conclusions_on_column(main, 'USG%')
#draw_conclusions_on_column(main, 'Offensive Load')
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
