import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.patches import FancyBboxPatch

import os
#import sys
#sys.path.insert(0, '../')
#from utils import *

TARGET_PLAYER_NAME="Ryan Dunn"

def calculate_text_yval(y: int):
    if (y < 0):
        return 0
    else: return -0.7

def main():
        # Given inputs
    y = [8, -16, 0, -1, 2, 15, 16, -9]
    x = ['Finishing','Shooting','Shot Creation','Passing','Rebounding','Athleticism','Defense','Intangibles']
    
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

    plt.figure(figsize=(2.5, 1.25), facecolor='none')
# or)

    # Create a bar chart with the custom colormap
    bars = plt.bar(x, y, color=bar_colors)

    
    # Add the values on the bars
    for bar in bars:
        yval = bar.get_height()
        if (yval != 0):
            plt.text(bar.get_x() + bar.get_width()/2, calculate_text_yval(yval), int(yval), 
                    va='top' if (yval > 0) else 'bottom', ha='center', color='black', fontsize=12)


    # Center the plot around y=0
    max_y_value = max(abs(max(y)), abs(min(y)))
    plt.ylim(-max_y_value, max_y_value)

    # Hide the axes
    plt.gca().xaxis.set_visible(False)
    plt.gca().yaxis.set_visible(False)
    for spine in plt.gca().spines.values():
        spine.set_visible(False)
    plt.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=0, hspace=0)


    plt.show()
    
    #    new_patches = []
    #for patch in reversed(ax.patches):
    #    bb = patch.get_bbox()
    #    color = patch.get_facecolor()
    #    p_bbox = FancyBboxPatch((bb.xmin, bb.ymin),
    #                            abs(bb.width), abs(bb.height),
    #                            boxstyle="round,pad=-0.0040,rounding_size=0.015",
    #                            ec="none", fc=color,
    #                            mutation_aspect=4
    #                            )
    #    patch.remove()
    #    new_patches.append(p_bbox)
    #for patch in new_patches:
    #    ax.add_patch(patch)
    #plt.show()

    #df = pd.read_csv("data/draft_db.csv")
    # Specify the file path
    file_path = "./figs/my_plot.jpg"

    # Check if the file exists and remove it if it does
    if os.path.isfile(file_path):
        os.remove(file_path)

    # Save the figure
    plt.savefig(file_path)
    
    #get_top_values(df, TARGET_PLAYER_NAME)
    
main()