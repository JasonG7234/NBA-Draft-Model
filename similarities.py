import pandas as pd
from utils import *

TARGET_PLAYER_NAME = "Ryan Dunn"
COMPARISON_COLUMN_NAME = "Rim Shot Creation"
            
def get_specific_column_similarities(df: pd.DataFrame):
    
    # Filter by position? 
    target_player = df.loc[df['Name'] == TARGET_PLAYER_NAME].iloc[0]
    df = df[(df['Class'] == target_player['Class']+1)]
    cols = ['Draft Day Age']

    for col in cols:
        #get_value_at_column_by_player_name(df, TARGET_PLAYER_NAME, col, to_find_similar=True, num_find_similar=20)
        #get_top_values(df, col, num_values=10)
        draw_conclusions_on_column(df, col)
        
def main():
    df = pd.read_csv("data/draft_db.csv")
    #get_overall_player_comparisons(df)
    get_specific_column_similarities(df)

main()

# TODO:
# Add Dalton Knecht and make a thread on him / other players
# Add hoop-explorer support

