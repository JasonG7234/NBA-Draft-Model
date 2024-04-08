import pandas as pd
from utils import *

TARGET_PLAYER_NAME = "Reed Sheppard"
COMPARISON_COLUMN_NAME = "Unassisted Shots @ Rim /100Poss"

def get_overall_player_comparisons(df: pd.DataFrame):
    SUMMARY_SCORE_LABELS = ['Finishing Score','Shooting Score','Shot Creation Score','Passing Score','Rebounding Score','Athleticism Score','Defense Score','College Productivity Score']

    leaderboard = {}
    df = pd.read_csv("data/draft_db_2023_special.csv")

    target_player = df.loc[df['Name'] == TARGET_PLAYER_NAME].iloc[0]

    # Filter out to same primary or secondary position
    df = df[(df['Position 1'] == target_player['Position 1']) | (df['Position 2'] == target_player['Position 2'])]
    for _, row in df.iterrows():
        player_summary_score_diff = 0
        summary_score_count = 0
        for summary_label in SUMMARY_SCORE_LABELS:
            summary_value = row[summary_label]
            if (summary_value not in ERROR_VALUES):
                player_summary_score_diff += abs(target_player[summary_label] - summary_value)
                summary_score_count += 1
        leaderboard[row['Name']] = (player_summary_score_diff/summary_score_count)
        
    for key, value in leaderboard.items():
        if (value < 20):
            print(key + ": " + str(100-value))
            
def get_specific_column_similarities(df: pd.DataFrame):
    # Filter by position? 
    target_player = df.loc[df['Name'] == TARGET_PLAYER_NAME].iloc[0]
    df = df[(df['Position 1'] == target_player['Position 1']) | (df['Position 2'] == target_player['Position 2'])]

    get_value_at_column_by_player_name(df, TARGET_PLAYER_NAME,  COMPARISON_COLUMN_NAME, to_find_similar=True)
    
def main():
    df = pd.read_csv("data/draft_db_2023_special.csv")
    get_specific_column_similarities(df)
    
main()

