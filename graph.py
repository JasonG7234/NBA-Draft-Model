import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from matplotlib.lines import Line2D # for the legend
from adjustText import adjust_text

# Position colors
COLORS = {"PG": "yellow", "SG": "orange", "SF": "red", "PF": "purple", "C": "blue"}
POSITIONS = ['PG', 'SG', 'SF', 'PF', 'C']
PLAYER_TO_LABEL = "Reed Sheppard"
X_AXIS = "STL/100Poss"
Y_AXIS = "BLK/100Poss"

'''
Get the dataframe from the file, filter out unnecessary players from the corresponding graph.
'''
def get_filtered_dataframe() -> pd.DataFrame:
    df = pd.read_csv("data/draft_db_2023_special.csv")
    
    # Games played filter
    df = df[(df['G'] > 10)]
    
    # Position filter
    df = df[(df['Position 1'] == 'PG') | (df['Position 1'] == 'SG')]
    
    return df[(df[X_AXIS] > 1) & (df[Y_AXIS] > 1)]

'''
Create the legend for the graph
'''
def add_legend(fig: plt.figure) -> None:
    handles = [
        Line2D(
            [], [], label=label, 
            lw=0, # there's no line added, just the marker
            marker="o", # circle marker
            markersize=10, 
            markerfacecolor=COLORS[label], # marker fill color
        )
        for _, label in enumerate(POSITIONS)
    ]
    fig.legend(
        handles=handles,
        bbox_to_anchor=[0.5, 0.95], # Located in the top-mid of the figure.
        fontsize=12,
        handletextpad=0.6, # Space between text and marker/line
        handlelength=1.4, 
        columnspacing=1.4,
        loc="center", 
        ncol=6,
        frameon=False
    )
    
'''
Gets the list of players to label in the graph
'''
def get_players_to_label(df: pd.DataFrame) -> list:
    return df[(df[Y_AXIS] > 2) | (df[X_AXIS] > 4)]['Name'].tolist()


# ================================================================

df = get_filtered_dataframe()

# Select colors for each region according to its category.
colors = []
for id, row in df.iterrows():
    c = COLORS[row['Position 1']]
    colors.append(c)

three_rate = df[Y_AXIS].values
three_pct = df[X_AXIS].values

fig, ax = plt.subplots(figsize=(12, 8))
add_legend(fig)

ax.scatter(three_rate, three_pct, color=colors, s=80, alpha=0.5)

TEXTS = []
for idx, player in df.iterrows():
    # Only append selected countries
    if player['Name'] in get_players_to_label(df):
        x, y = player[Y_AXIS], player[X_AXIS]
        if (player['Name'] == PLAYER_TO_LABEL):
            TEXTS.append(ax.text(x, y, player['Name'], fontsize=14))
        else:
            TEXTS.append(ax.text(x, y, player['Name'], fontsize=10))

adjust_text(
    TEXTS, 
    arrowprops=dict(arrowstyle="-", lw=1),
    ax=ax
)

ax.set_xlabel(Y_AXIS)
ax.set_ylabel(X_AXIS)
plt.show()