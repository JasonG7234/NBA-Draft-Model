
import pandas as pd
from flask import Flask, render_template, url_for

import sys
sys.path.insert(0, './')
from utils import *

sys.path.insert(0, './graphic_gen/')
from graphic_utils import *

TARGET_PLAYER_NAME = 'Jalen Brunson'

SHEET_LABELS = [
    ['3FG%', '3PAr', 'FG% @ Mid'], # Shooting
    ['FG% @ Rim', '% Shots @ Rim', '%Astd @ Rim'], # Finishing
    ['AST%', 'AST/TOV'], # Passing
    ['ORB%', 'DRB%'], # Rebounding
    ['STL%', 'BLK%', 'Adj DEF +/-'], # Defense
    ['WS', 'SOS', 'Draft Day Age', 'Adj OFF +/-'] # Production
]

GRAPH_LABELS = [
    ['3FG%', '3PAr', 'Mid FG%'], # Shooting
    ['FG%@Rim', 'Freq@Rim', '%Astd@Rim'], # Finishing
    ['AST%', 'AST/TOV'], # Passing
    ['ORB%', 'DRB%'], # Rebounding
    ['STL%', 'BLK%', 'DEF+/-'], # Defense
    ['WS', 'SOS', 'Age', 'OFF+/-'] # Production
]

FILE_NAMES = ['gshoot', 'gfinish', 'gpass', 'grebound', 'gdefense', 'gprod']

NEGATIVE_COLS = ['%Astd @ Rim', 'Draft Day Age', '% Assisted']

def __create_rank_column(df, col_name):
    df[col_name + ' Rank'] = df[col_name].rank(pct=True, ascending=False if col_name in NEGATIVE_COLS else True)
    return df

def __calculate_text_position(bar, bars):
    print(bar.get_height())
    if (bar.get_height() > 10):
        return bar.get_height()/1.3
    else:
        max_height = max(b.get_height() for b in bars)
        return bar.get_height()*(1/20*max_height)
    
def __get_defensive_projection_score(df):
    new_row = get_row_from_player_name(df, TARGET_PLAYER_NAME)
    a = new_row['Athleticism Score']
    d = new_row['Defense Score']
    if (a > 0.95 and d > 0.95):
        return 5
    elif (a > 0.9 and d > 0.9):
        return 4
    elif ((a > 0.8 and d > 0.8) or (d > 0.9)): 
        return 3
    elif ((a > 0.67 and d > 0.67) or (d > 0.8)):
        return 2
    elif ((a > 0.55 and d > 0.55) or (d > 0.75) or (a > 0.9)):
        return 1
    elif ((a > 0.4 and d > 0.4) or (d > 0.6) or (a > 0.8)):
        return 0
    elif (d > 0.5 or a > 0.7):
        return -1
    elif (d > 0.4 or a > 0.6):
        return -2
    elif (d > 0.3 or a > 0.5):
        return -3
    elif (d > 0.2 or a > 0.4):
        return -4
    else:
        return -5
    
def __get_offensive_projection_score(df):
    new_row = get_row_from_player_name(df, TARGET_PLAYER_NAME)
    sh = new_row['Shooting Score']
    f = new_row['Finishing Score']
    sc = new_row['Shot Creation Score']
    p = new_row['Passing Score']
    avg = (sh+f+sc+p)/4
    if (avg > 0.85):
        return 5
    elif (avg > 0.77):
        return 4
    elif (avg > 0.7 or sh > 0.95 or f > 0.95 or sc > 0.95 or p > 0.95): 
        return 3
    elif (avg > 0.6):
        return 2
    elif (avg > 0.5 or sh > 0.9 or f > 0.9 or sc > 0.9 or p > 0.9):
        return 1
    elif (avg > 0.4):
        return 0
    elif (sh > 0.8 or f > 0.8 or sc > 0.8 or p > 0.8):
        return -1
    elif (avg > 0.3):
        return -2
    elif (avg > 0.2):
        return -3
    elif (sh > 0.5 and f > 0.5 and sc > 0.5 and p > 0.5):
        return -4
    else:
        return -5
    
def __get_draft_projection_text(df):
    df = __create_rank_column(df, 'Draft Score')
    new_row = get_row_from_player_name(df, TARGET_PLAYER_NAME)
    r = new_row['Draft Score Rank']*100
    print(str(r))
    if(r > 95):
        return "Top 5"
    elif(r > 90):
        return "Lottery"
    elif(r > 75):
        return "First Round"
    elif(r > 50):
        return "Second Round"
    elif(r > 25):
        return "G-Leaguer"
    else:
        return "Undrafted"
    
def __get_offensive_role_text(df):
    df = __create_rank_column(df, 'AST%')
    df = __create_rank_column(df, '% Assisted')
    # Hands-On Buckets, % Assisted
    new_row = get_row_from_player_name(df, TARGET_PLAYER_NAME)
    p = new_row['AST% Rank']
    a = new_row['% Assisted Rank']
    print(p, a)
    if (p > 0.8 and a > 0.8):
        return "Primary"
    elif (p > 0.5 and a > 0.5):
        return "Secondary"
    elif (p > 0.5 or a > 0.5):
        return "Tertiary"
    else:
        return "Off-Ball"
    
def __get_defensive_role_text(df):
    def_role = ""
    new_row = get_row_from_player_name(df, TARGET_PLAYER_NAME)
    a = new_row['Athleticism Score']
    d = new_row['Defense Score']
    if (a > 0.8):
        def_role = "Versatile "
    elif (a < 0.2):
        def_role = "Single-positional " # Include height here! PGs can only guard PGs if short
    
    if (d > 0.8):
        def_role += "PoA "
    elif (d < 0.2):
        def_role += "Weak "
    else:
        def_role += "Secondary "
        
    return def_role
    
def __get_position_text(df):
    d = get_row_from_player_name(df, TARGET_PLAYER_NAME)
    if ((d['Position 1'] == 'SG' and d['Position 2'] == 'PG') or 
        (d['Position 1'] == 'PG' and d['Position 2'] == 'SG')):
        return "Guard"
    elif ((d['Position 1'] == 'SG' and d['Position 2'] == 'SF') or 
        (d['Position 1'] == 'SF' and d['Position 2'] == 'SG')):
        return "Wing"
    elif ((d['Position 1'] == 'SF' and d['Position 2'] == 'PF') or 
        (d['Position 1'] == 'PF' and d['Position 2'] == 'SF')):
        return "Forward"
    elif ((d['Position 1'] == 'PF' and d['Position 2'] == 'C') or 
        (d['Position 1'] == 'C' and d['Position 2'] == 'PF')):
        return "Big"
    elif (d['Position 1'] == 'C'):
        return "Center"
    else:
        return d['Position 1']


def create_prospect_graphs(df):
    
    for labels in SHEET_LABELS:
        for label in labels:
            # Create ranked column for the label, for the coloring
            # Doing this outside of the main loop for performance and ease of access
            df = __create_rank_column(df, label)

    new_row = get_row_from_player_name(df, TARGET_PLAYER_NAME)  
    
    # For each list of labels 
    for label_i in range(0, len(GRAPH_LABELS)): 
        
        # Change to ideal size
        plt.figure(figsize=(30, 12.5), facecolor='none')
        
        plt.gca().xaxis.set_visible(True)
        plt.gca().yaxis.set_visible(False)
        for spine in plt.gca().spines.values():
            spine.set_visible(False)
            
        plt.gca().tick_params(labelsize=98)
        
        plt.tight_layout()
        
        y = []
        ranks = []
        # For each label in the master spreadsheet list
        for label in SHEET_LABELS[label_i]:
            if (new_row[label] in ERROR_VALUES or pd.isna(new_row[label])):
                GRAPH_LABELS[label_i].remove(label.replace(" ", "")[3:])
                continue
            y.append(round(new_row[label], 1))
            ranks.append(100*new_row[label + ' Rank'])
        
        # Create a bar chart with the desired labels on the graph, not the spreadsheet
        bars = plt.bar(GRAPH_LABELS[label_i], ranks, color=get_colors_from_ranks(ranks))
    
        # Add the values on the bars
        for bar_i in range(0, len(bars)):
            bar = bars[bar_i]
            print(GRAPH_LABELS[label_i][bar_i])
            if (bar.get_height() != 0):
                plt.text(bar.get_x() + bar.get_width()/2, __calculate_text_position(bar, bars), y[bar_i], 
                        va='top', ha='center', color='black', fontsize=120)
            

        
        file_path = f"./graphic_gen/overall/static/{FILE_NAMES[label_i]}.png"
        if os.path.isfile(file_path):
            os.remove(file_path)

        # Save the figure
        plt.savefig(file_path)
        
        set_img_transparent_background(file_path)
        
        plt.clf()

app = Flask(__name__, static_folder='static')

@app.route('/')
def home(create_graphs = False, to_filter_by_position=True):
    df = pd.read_csv("data/draft_db.csv")
    if (to_filter_by_position):
        df = filter_by_position(df, get_row_from_player_name(df, TARGET_PLAYER_NAME))
    
    target_row = get_row_from_player_name(df, TARGET_PLAYER_NAME)
    if (create_graphs):
        create_prospect_graphs(df)
    else: 
        school_colors = get_colors_from_school(target_row['School'])
        return render_template('index.html', 
                row=target_row, 
                colors=school_colors,
                text_colors =[c for c in get_a11y_text_color_from_hex(school_colors)],
                int=int, float=float,
                pos=__get_position_text(df),
                ovr_proj=__get_draft_projection_text(df),
                off_role=__get_offensive_role_text(df),
                def_role=__get_defensive_role_text(df),
                off_proj=__get_offensive_projection_score(df),
                def_proj=__get_defensive_projection_score(df),
                comps=get_player_comparisons(df, TARGET_PLAYER_NAME, num_to_compare=2, include_draft_score=True)
            )

if __name__ == '__main__':
    if '-g' in sys.argv:
        home(True)
    else:
        app.run(host="localhost", port=8000)