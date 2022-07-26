
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

    st.dataframe(df_selection)
    
    st.markdown("##")
    num_prospects = len(df_selection.index)
    best_3pt_shooter = df_selection.loc[df_selection['3 Point Confidence'].idxmax()]
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

    hide_st_style = """
                <style>
                #dfMenu {visibility: hidden;}
                footer {visibility: hidden;}
                header {visibility: hidden;}
                </style>
                """
    st.markdown(hide_st_style, unsafe_allow_html=True)

def set_up_dataframe(df):

    df.rename(columns={"Position 1": "Position"}, inplace=True)
    column_names_with_na_values = ['Position 2', 'Height w/o Shoes', 'Height w/ Shoes', 'Wingspan']
    df['Position 2'] = df['Position 2'].fillna('')
    
    float_column_names = ['SOS', 'Draft Day Age', 'Weight']
    for col_name in float_column_names:
        df[col_name] = df[col_name].round(decimals=2).astype(float)
        df[col_name] = df[col_name].apply('{:0<2}'.format)
    
    int_column_names = ['Wins', 'Losses', 'Class']
    for col_name in int_column_names:
        df[col_name] = df[col_name].astype(str).apply(lambda x: x.replace('.0',''))
    return df

df = set_up_dataframe(pd.read_csv('data/jason_db.csv'))
set_up_streamlit(df)