import pandas as pd
import matplotlib.colors as mcolors
from flask import Flask, render_template, url_for

import sys
sys.path.insert(0, './')
from utils import *

sys.path.insert(0, './graphic_gen/')
from graphic_utils import *

TARGET_PLAYER_NAME = 'Dylan Harper'
SUMMARY_SCORE_LABELS = ['Finishing Score','Shooting Score','Shot Creation Score','Passing Score','Rebounding Score','Athleticism Score','Defense Score','College Productivity Score']
NUM_TO_COMPARE = 4

def create_target_summary_graph(target_row):
    # Populate summary score values for target player
    y = []
    for label in SUMMARY_SCORE_LABELS:
        print(label, str(100*target_row[label]))
        val = round(100*target_row[label], 0)
        y.append(val)
            
    return create_summary_graph(y, get_colors_from_ranks(y), False, to_print=False, file_path = f"./graphic_gen/similarities/static/gt.png")

def create_comparison_summary_graph(target_row, comp_row, count: int):
    
    # Populate summary score differences
    y = []
    for label in SUMMARY_SCORE_LABELS:
        val = round(100*(comp_row[label] - target_row[label]), 0)
        y.append(val)

    return create_summary_graph(y, get_colors_from_ranks(y, True), True, to_print=False, file_path = f"./graphic_gen/similarities/static/g{str(count)}.png")
    
app = Flask(__name__, static_folder='static')

@app.route('/')
def home(create_graphs: bool = False):
    df = pd.read_csv("data/draft_db.csv")
    # Get player
    target_row = get_row_from_player_name(df, TARGET_PLAYER_NAME)
    if (create_graphs):
        create_target_summary_graph(target_row)
    
    # Get comparisons
    top_comparisons = get_player_comparisons(df, TARGET_PLAYER_NAME, num_to_compare=NUM_TO_COMPARE, include_draft_score=False)
    
    comparisons = []
    comparisons_scores = []
    # Generate graphs for comparisons
    for i in range(0, NUM_TO_COMPARE):
        comp = top_comparisons[i]
        comp_row = get_row_from_player_name(df, comp[0])
        comparisons.append(comp_row)
        comparisons_scores.append(round(100*(1-comp[1]), 2))
        if (create_graphs):
            create_comparison_summary_graph(target_row, comp_row, i)
        
    # Generate HTML for image
    if (not create_graphs):
        school_colors = get_colors_from_school(target_row['School'])
        return render_template('index.html', 
                target=target_row, 
                comparisons=comparisons, 
                scores=comparisons_scores, 
                colors=school_colors,
                text_colors =[c for c in get_a11y_text_color_from_hex(school_colors)],
                int=int
        )

if __name__ == '__main__':
    if '-g' in sys.argv:
        home(True)
    else:
        app.run(host="localhost", port=8000)