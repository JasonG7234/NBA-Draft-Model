
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

    #left_column, right_column = st.columns(2)
    hide_st_style = """
                <style>
                #dfMenu {visibility: hidden;}
                footer {visibility: hidden;}
                header {visibility: hidden;}
                </style>
                """
    st.markdown(hide_st_style, unsafe_allow_html=True)

def set_up_dataframe(df):
    df['SOS'] = df['SOS'].round(decimals=2).astype(float)
    df['SOS'] = df['SOS'].apply('{:0<2}'.format)
    df.rename(columns={"Position 1": "Position"}, inplace=True)
    df['Position 2'] = df['Position 2'].fillna('')
    
    df['Wins'] = df['Wins'].astype(str).apply(lambda x: x.replace('.0',''))
    df['Losses'] = df['Losses'].astype(str).apply(lambda x: x.replace('.0',''))
    df['Class'] = df['Class'].astype(str).apply(lambda x: x.replace('.0',''))
    #print(df.at[0, 'SOS'])
    return df

df = set_up_dataframe(pd.read_csv('data/main.csv'))
set_up_streamlit(df)