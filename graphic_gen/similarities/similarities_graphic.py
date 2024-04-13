import pandas as pd
import matplotlib.colors as mcolors
from flask import Flask, render_template, url_for

import sys
sys.path.insert(0, './')
from utils import *

sys.path.insert(0, './graphic_gen/')
from graphic_utils import *

TARGET_PLAYER_NAME= "Reed Sheppard"
SUMMARY_SCORE_LABELS = ['Finishing Score','Shooting Score','Shot Creation Score','Passing Score','Rebounding Score','Athleticism Score','Defense Score','College Productivity Score']
NUM_TO_COMPARE = 4

def create_target_graph(target_row):
    # Populate summary score values for target player
    y = []
    for label in SUMMARY_SCORE_LABELS:
        val = round(100*target_row[label], 0)
        y.append(val)
    
    # Create two colormaps
    cmap_neg = mcolors.LinearSegmentedColormap.from_list('red_gray', ['red', 'gray'], N=100)
    cmap_pos = mcolors.LinearSegmentedColormap.from_list('gray_green', ['gray', 'green'], N=100)

    # Normalize the y-values to the range [0, 1] for colormap scaling
    norm_neg = mcolors.Normalize(vmin=0, vmax=50)
    norm_pos = mcolors.Normalize(vmin=50, vmax=100)

    # Assign colors based on the value of each bar
    bar_colors = [cmap_neg(norm_neg(val)) if val < 50 else cmap_pos(norm_pos(val)) for val in y]
    
    #        plt.text(bar.get_x() + bar.get_width()/2, 15, int(yval), 
    #                va='top', ha='center', color='black', fontsize=12)
            
    return create_summary_graph(y, bar_colors, False, to_print=False, file_path = f"./graphic_gen/similarities/static/gt.png")

def get_comparison_graph(target_row, comp_row, count: int):
    
    # Populate summary score differences
    y = []
    for label in SUMMARY_SCORE_LABELS:
        val = round(100*(comp_row[label] - target_row[label]), 0)
        y.append(val)
    
    # Create two colormaps: one for negative values and one for positive values
    cmap_neg = mcolors.LinearSegmentedColormap.from_list('red_gray', ['red', 'gray'], N=100)
    cmap_pos = mcolors.LinearSegmentedColormap.from_list('gray_green', ['gray', 'green'], N=100)

    # Normalize the y-values to the range [0, 1] for colormap scaling
    # We find the maximum absolute value to scale negative and positive values proportionally
    max_abs_value = max(abs(min(y)), abs(max(y)))
    norm_neg = mcolors.Normalize(vmin=-max_abs_value, vmax=0)
    norm_pos = mcolors.Normalize(vmin=0, vmax=max_abs_value)

    # Assign colors based on the value of each bar
    bar_colors = [cmap_neg(norm_neg(val)) if val < 0 else cmap_pos(norm_pos(val)) for val in y]

    #        plt.text(bar.get_x() + bar.get_width()/2, calculate_text_yval(yval), int(yval), 
    #                va='top' if (yval > 0) else 'bottom', ha='center', color='black', fontsize=12)

    return create_summary_graph(y, bar_colors, True, to_print=False, file_path = f"./graphic_gen/similarities/static/g{str(count)}.png")
    
app = Flask(__name__, static_folder='static')

@app.route('/')
def home():
    
    df = pd.read_csv("data/draft_db.csv")
    # Get player
    target_row = get_row_from_player_name(df, TARGET_PLAYER_NAME)
    
    # Get comparisons
    top_comparisons = get_overall_player_comparisons(df, TARGET_PLAYER_NAME, num_to_compare=NUM_TO_COMPARE)
    
    comparisons = []
    comparisons_scores = []
    # Generate graphs for comparisons
    for i in range(0, NUM_TO_COMPARE):
        comp = top_comparisons[i]
        comp_row = get_row_from_player_name(df, comp[0])
        comparisons.append(comp_row)
        comparisons_scores.append(round(100*(1-comp[1]), 2))
        get_comparison_graph(target_row, comp_row, i)
        
    # Generate HTML for image
    return render_template('index.html', 
            target=target_row, 
            comparisons=comparisons, 
            scores=comparisons_scores, 
            colors=get_colors_from_school(target_row['School']),
            int=int
    )

if __name__ == '__main__':
    df = pd.read_csv("data/draft_db.csv")
    # Get player
    target_row = get_row_from_player_name(df, TARGET_PLAYER_NAME)
    create_target_graph(target_row)
    app.run(host="localhost", port=8000)