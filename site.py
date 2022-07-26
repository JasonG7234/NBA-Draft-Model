
from distutils.command.config import dump_file
import pandas as pd
import plotly.express as px  
import streamlit as st
from utils import *

def set_up_streamlit(df):
    st.set_page_config(page_title="NBA Draft Model", page_icon=":bar_chart:", layout="wide")

    st.sidebar.header("Please Filter Here:")
    position = st.sidebar.multiselect(
        "Select the primary position:",
        options=df["Position"].unique(),
        default=df["Position"].unique()
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
    df_selection = df.query("Position == @position & Season == @season & Class == @classification")
    
    st.markdown("##")
    num_prospects = len(df_selection.index)
    best_3pt_shooter = df_selection.loc[df_selection['3 Point Proficiency'].idxmax()]
    best_finisher = df_selection.loc[df_selection['Rim Shot Creation'].idxmax()]
    
    left_column, middle_column, right_column = st.columns(3)
    with left_column:
        st.subheader("Number of prospects:")
        st.subheader(f"{num_prospects}")
    with middle_column:
        st.subheader("Best shooter:")
        st.subheader(f"{best_3pt_shooter['Name']}")
    with right_column:
        st.subheader("Best finisher:")
        st.subheader(f"{best_finisher['Name']}")
        
    st.dataframe(df_selection)
    
    creation_scatter = px.scatter(
        df_selection,
        x="% Assisted",
        y="Height",
        orientation="h",
        title="<b>Test Scatter</b>",
        hover_data=['% Assisted', 'Height', 'Name'],
        color_discrete_sequence=["#0083B8"] * len(df_selection),
        template="plotly_white",
    )
    creation_scatter.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=(dict(showgrid=False))
    )
    
    three_pt_shooting_by_season = (
        df_selection.groupby(by=["Season"]).mean()[["3 Point Confidence"]].sort_values(by="Season")
    )
    fig_three_pt_shooting = px.bar(
        three_pt_shooting_by_season,
        x="3 Point Confidence",
        y=three_pt_shooting_by_season.index,
        orientation="h",
        title="<b>Has 3 point shooting improved by season?</b>",
        color_discrete_sequence=["#0083B8"] * len(three_pt_shooting_by_season),
        template="plotly_white"
    )
    
    fig_three_pt_shooting.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=(dict(showgrid=False))
    )
    
    col1, col2 = st.columns(2)
    col1.plotly_chart(creation_scatter, use_container_width=True)
    col2.plotly_chart(fig_three_pt_shooting, use_container_width=True)

    hide_st_style = """
                <style>
                #dfMenu
                footer
                header
                </style>
                """
    st.markdown(hide_st_style, unsafe_allow_html=True)

float_column_names = {
    'Height w/ Shoes' : 2, 
    'Height w/o Shoes' : 2, 
    'Wingspan' : 2,
    'Standing Reach': 2, 
    'Body Fat %' : 2, 
    'Hand Length' : 2, 
    'Hand Width' : 2,
    'SOS' : 2, 
    'Draft Day Age': 2, 
    'Weight' : 2, 
    'PER': 1,
    'TS%' : 1,
    'eFG%' : 1,
    '3PAr' : 1,
    'FTr' : 1,
    'ORB%' : 1,
    'DRB%': 1,
    'TRB%': 1,
    'AST%' : 1,
    'STL%' : 1,
    'BLK%' : 1,
    'Stock%' : 1,
    'TOV%' : 1,
    'Adjusted TOV%' : 1,
    'USG%' : 1,
    'Offensive Load': 2,
    'OWS': 1,
    'DWS': 1,
    'WS': 1,
    'WS/40': 3,
    'OBPM': 1,
    'DBPM': 1,
    'BPM': 1,
    'AST/TOV': 2,
    'OFF RTG': 1,
    'DEF RTG': 1,
    'Hands-On Buckets': 1,
    'Pure Point Rating': 1,
    'FG/40' : 1,
    'FGA/40' : 1,
    'FG%' : 1,
    '2FGM/40' : 1,
    '2FGA/40' : 1,
    '2FG%' : 1,
    '3FGM/40' : 1,
    '3FGA/40' : 1,
    '3FG%' : 1,
    'FT/40' : 1,
    'FTA/40' : 1,
    'FT%' : 1,
    'TRB/40' : 1,
    'AST/40' : 1,
    'STL/40' : 1,
    'BLK/40' : 1,
    'TOV/40' : 1,
    'PF/40' : 1,
    'PTS/40' : 1
}
    
def set_up_dataframe(df):

    df.rename(columns={"Position 1": "Position"}, inplace=True) 
    percents = ['TS%', 'eFG%', '3PAr', 'FTr', 'Adjusted TOV%', 'Hands-On Buckets', 'FG%', '2FG%', '3FG%', 'FT%', '3 Point Proficiency', '3 Point Confidence']
    for col_name in percents:
        df[col_name] = df[col_name]*100
    
    for col_name, decimal_places in float_column_names.items():
        df[col_name] = df[col_name].round(decimals=decimal_places).astype(float)
        if (decimal_places == 2):
            df[col_name] = df[col_name].apply('{:0<2}'.format)
        elif (decimal_places == 1):
            df[col_name] = df[col_name].apply('{:0<1}'.format)
        elif (decimal_places == 3):
            df[col_name] = df[col_name].apply('{:0<3}'.format)
    
    int_column_names = ['Wins', 'Losses', 'Class', 'RSCI', 'MP', 'PProd']
    for col_name in int_column_names:
        df[col_name] = df[col_name].astype(str).apply(lambda x: x.replace('.0',''))
        
    column_names_with_na_values = ['Position 2', 'Height w/ Shoes', 'Height w/o Shoes', 'Wingspan', 'Standing Reach', 'Body Fat %', 'Hand Length', 'Hand Width', 'PER', 'PProd', 'ORB%', 'DRB%', 'TRB%', 'AST%', 'STL%', 'BLK%', 'Stock%', 'Adjusted TOV%', 'USG%', 'Offensive Load', 'OBPM', 'DBPM', 'BPM', 'OFF RTG','DEF RTG']
    for col_name in column_names_with_na_values:
        df[col_name] = df[col_name].fillna('')
        df[col_name] = df[col_name].replace('nan', '')
    return df

df = set_up_dataframe(pd.read_csv('data/jason_db.csv'))
set_up_streamlit(df)