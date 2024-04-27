import matplotlib.pyplot as plt
import cv2
import os
import csv
from typing import List, Optional

import matplotlib.colors as mcolors
import matplotlib.font_manager

# Set the font globally
#prop = matplotlib.font_manager.FontProperties(fname="C:/Users/Owner/Documents/Projects/NBA-Draft-Model/fonts/Roboto-Regular.ttf")
#matplotlib.rcParams['font.family'] = prop.get_name()


SUMMARY_SCORE_LABELS = ['Finishing Score','Shooting Score','Shot Creation Score','Passing Score','Rebounding Score','Athleticism Score','Defense Score','College Productivity Score']
PATH_TO_COLORS = 'data/colors.csv'

def get_colors_from_ranks(vals, is_negative_vals_accepted=False):
    
    # Create two colormaps
    cmap_neg = mcolors.LinearSegmentedColormap.from_list('red_gray', ['red', 'gray'], N=100)
    cmap_pos = mcolors.LinearSegmentedColormap.from_list('gray_green', ['gray', 'green'], N=100)

    # Normalize the y-values to the range [0, 1] for colormap scaling
    if (is_negative_vals_accepted):
        max_abs_value = max(abs(min(vals)), abs(max(vals)))
        norm_neg = mcolors.Normalize(vmin=-max_abs_value, vmax=0)
        norm_pos = mcolors.Normalize(vmin=0, vmax=max_abs_value)
    else: 
        norm_neg = mcolors.Normalize(vmin=0, vmax=50)
        norm_pos = mcolors.Normalize(vmin=50, vmax=100)

    # Assign colors based on the value of each bar
    return [cmap_neg(norm_neg(val)) if val < (0 if is_negative_vals_accepted else 50) else cmap_pos(norm_pos(val)) for val in vals]

def get_colors_from_school(school_name: str) -> List[str]:
    colors = []  # List to store the colors corresponding to the team
    
    with open(PATH_TO_COLORS, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['Team'] == school_name:
                # Iterate through the columns to find non-empty color values
                for color_key in ['Color 1', 'Color 2', 'Color 3', 'Color 4']:
                    color_value = row[color_key].strip()
                    if color_value:
                        colors.append(color_value)
                break  # Stop searching once the team is found

    return colors

def get_a11y_text_color_from_hex(hex_colors) -> str:
    text_colors = []
    for hex in hex_colors:
        rgb = []
        for i in (1, 3, 5):
            unit = hex[i:i+2]
            unit_int = int(unit, 16)
            rgb.append(unit_int)
        intensity = (rgb[0] * 0.299) + (rgb[1] * 0.587) + (rgb[2] * 0.114)
        text_colors.append("black" if intensity > 186 else "white")
    return text_colors

def create_summary_graph(
    y: List[float],  # List of values for the Summary Scores
    bar_colors: List[str],  # List of colors for the bars in the graph
    is_negative: bool = True,  # Flag indicating whether this graph includes negative values. 
    to_print: bool = True,  # Flag indicating whether to print the graph to console
    file_path: Optional[str] = None  # Optional file path to save the graph image
) -> None:
    """
    Creates a summary graph based on the provided data.

    Parameters:
    - y (List[float]): List of values for the y-axis.
    - bar_colors (List[str]): List of colors for the bars in the graph.
    - is_negative (bool, optional): Flag indicating whether negative values should be highlighted.
      Defaults to True.
    - to_print (bool, optional): Flag indicating whether to print the graph. Defaults to True.
    - file_path (Optional[str], optional): Optional file path to save the graph image.
      Defaults to None.

    Returns:
    - None
    """
    
    # Change to ideal size
    plt.figure(figsize=(2.5, 1.25), facecolor='none')

    # Create a bar chart with the custom colormap
    bars = plt.bar(SUMMARY_SCORE_LABELS, y, color=bar_colors)
    
    # Add the values on the bars
    for bar in bars:
        yval = bar.get_height()
        #text_color = __get_a11y_text_color_from_hex(bar.get_facecolor())
        if (yval != 0):
            plt.text(bar.get_x() + bar.get_width()/2, __calculate_text_yval(yval, is_negative), int(yval), 
                    va='bottom' if (yval < 0 and is_negative) else 'top', ha='center', color='black', fontsize=12)

    # Hide the axes
    plt.gca().xaxis.set_visible(False)
    plt.gca().yaxis.set_visible(False)
    for spine in plt.gca().spines.values():
        spine.set_visible(False)
    plt.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=0, hspace=0)
    
    if (is_negative):
        # Center the plot around y=0
        max_y_value = max(abs(max(y)), abs(min(y)))
        plt.ylim(-max_y_value, max_y_value)
    
    if (to_print):
        plt.show()
    
    else:
        __remove_file_if_exists(file_path)

        # Save the figure
        plt.savefig(file_path)
        
        set_img_transparent_background(file_path)
    
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

import numpy as np

def set_img_transparent_background(file_path: str) -> None:
    """
    Sets the background of an image file to be transparent and saves it.

    Parameters:
    - file_path (str): Path to the image file.

    Returns:
    - None
    """
    src = cv2.imread(file_path, 1)
    
    # Convert the image to RGBA format
    rgba_image = cv2.cvtColor(src, cv2.COLOR_BGR2BGRA)

    # Set Alpha channel values of white pixels to 0 (fully transparent)
    white_pixels = np.all(rgba_image[:, :, :3] == [255, 255, 255], axis=-1)
    rgba_image[white_pixels, -1] = 0  # Set Alpha channel to 0 for white pixels

    __remove_file_if_exists(file_path)
    cv2.imwrite(file_path, rgba_image)
    
# HELPER METHODS (PRIVATE)

def __calculate_text_yval(y: int, is_negative: bool) -> int:
    if (is_negative):
        if (y < 0):
            return 0
        else: return -0.7
    else:
        return 15

def __remove_file_if_exists(file_path: str):
    if os.path.isfile(file_path):
        os.remove(file_path)
