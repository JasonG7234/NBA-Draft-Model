import pandas as pd
from utils import *

TARGET_PLAYER_NAME = "Dalton Knecht"
COMPARISON_COLUMN_NAME = "3 Point Proficiency"
            
def get_specific_column_similarities(df: pd.DataFrame):
    
    # Filter by position? 
    target_player = df.loc[df['Name'] == TARGET_PLAYER_NAME].iloc[0]
    df = df[(df['Position 1'] == target_player['Position 1']) | (df['Position 2'] == target_player['Position 1'])]
    cols = ['FG% @ Rim']

    #print(get_player_comparisons(df, TARGET_PLAYER_NAME, num_to_compare=10, categories=cols))

    for col in cols:
        get_value_at_column_by_player_name(df, TARGET_PLAYER_NAME, col, to_find_similar=True, num_find_similar=20)
        get_top_values(df, col, num_values=10)
    #     draw_conclusions_on_column(df, col)
        
def main():
    df = pd.read_csv("data/draft_db.csv")
    get_specific_column_similarities(df)
    #df = df.drop_duplicates(subset='RealGM ID', keep='first')
    #df.to_csv('data/draft_db.csv', index=False)

main()

# TODO:
# Add Dalton Knecht and make a thread on him / other players
# Add hoop-explorer support

