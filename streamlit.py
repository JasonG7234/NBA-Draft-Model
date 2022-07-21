import plotly.express as px  
import streamlit as st 

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