
import pandas as pd
from flask import Flask, render_template, url_for

import sys
sys.path.insert(0, './')
from utils import *

sys.path.insert(0, './graphic_gen/')
from graphic_utils import *

TARGET_PLAYER_NAME = 'Dalton Knecht'

LABELS = [
    ['3FG%', '3PAr', 'FG% @ Mid'], # Shooting
    ['FG% @ Rim', '% Shots @ Rim', '%Astd @ Rim'], # Finishing
    ['AST%', 'AST/TOV'], # Passing
    ['ORB%', 'DRB%'], # Rebounding
    ['STL%', 'BLK%', 'Adj DEF +/-'], # Defense
    ['WS', 'SOS', 'Draft Day Age', 'Adj OFF +/-'] # Production
]

FILE_NAMES = ['gshoot', 'gfinish', 'gpass', 'grebound', 'gdefense', 'gprod']

NEGATIVE_COLS = ['%Astd @ Rim', 'Draft Day Age']

def __create_rank_column(df, col_name):
    df[col_name + ' Rank'] = df[col_name].rank(pct=True, ascending=False if col_name in NEGATIVE_COLS else True)
    return df

def __calculate_text_position(bar):
    if (bar.get_height() > 2):
        return bar.get_y() + bar.get_height()/1.3
    else:
        return bar.get_y() + bar.get_height()/0.8

def create_prospect_graphs(df, to_filter_by_position=True):
    
    if (to_filter_by_position):
        df = filter_by_position(df, get_row_from_player_name(df, TARGET_PLAYER_NAME))
    
    for labels in LABELS:
        for label in labels:
            # Create ranked column for the label, for the coloring
            # Doing this outside of the main loop for performance and ease of access
            df = __create_rank_column(df, label)

    new_row = get_row_from_player_name(df, TARGET_PLAYER_NAME)  
    
    # For each list of labels 
    for label_i in range(0, len(LABELS)): 
        
        # Change to ideal size
        plt.figure(figsize=(3, 1.25), facecolor='none')
        
        plt.gca().xaxis.set_visible(False)
        plt.gca().yaxis.set_visible(False)
        for spine in plt.gca().spines.values():
            spine.set_visible(False)
        
        plt.tight_layout()
        
        y = []
        ranks = []
        # For each label in the master spreadsheet list
        for label in LABELS[label_i]:
            y.append(round(new_row[label], 1))
            print(new_row[label + ' Rank'])
            ranks.append(100*new_row[label + ' Rank'])
        
        # Create a bar chart with the desired labels on the graph, not the spreadsheet
        bars = plt.bar(LABELS[label_i], ranks, color=get_colors_from_ranks(ranks))
    
        # Add the values on the bars
        for bar_i in range(0, len(bars)):
            bar = bars[bar_i]
            #text_color = __get_a11y_text_color_from_hex(bar.get_facecolor())
            if (bar.get_height() != 0):
                plt.text(bar.get_x() + bar.get_width()/2, __calculate_text_position(bar), y[bar_i], 
                        va='top', ha='center', color='black', fontsize=12)
            

        
        file_path = f"./graphic_gen/overall/static/{FILE_NAMES[label_i]}.png"
        if os.path.isfile(file_path):
            os.remove(file_path)

        # Save the figure
        plt.savefig(file_path)
        
        set_img_transparent_background(file_path)
        
        plt.clf()

app = Flask(__name__, static_folder='static')

@app.route('/')
def home(create_graphs = False):
    df = pd.read_csv("data/draft_db.csv")
    
    target_row = get_row_from_player_name(df, TARGET_PLAYER_NAME)
    if (create_graphs):
        create_prospect_graphs(df)
    else: 
        school_colors = get_colors_from_school(target_row['School'])
        return render_template('index.html', 
                row=target_row, 
                colors=school_colors,
                text_colors =[c for c in get_a11y_text_color_from_hex(school_colors)],
                int=int, float=float
            )

if __name__ == '__main__':
    if '-g' in sys.argv:
        home(True)
    else:
        app.run(host="localhost", port=8000)