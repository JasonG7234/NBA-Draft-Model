import sys
from utils import *

def draw_conclusions_on_player(df, player_name, by_position=True):
    row = df.loc[df['Name'] == player_name].iloc[0]
    pos2 = row['Position 2']
    df = df.append(row, ignore_index = True)
    if by_position:
        df = df[df['Position 1'] == row['Position 1']]
        if (pos2):
            df = pd.concat([df, df[df['Position 2'] == pos2]], axis=0)
    print(f"================ {player_name} ==================")
    # Measurables
    get_value_at_column_by_player_name(df, player_name, 'Position 1', to_print_percentile=False)
    get_value_at_column_by_player_name(df, player_name, 'Position 2', to_print_percentile=False)
    get_value_at_column_by_player_name(df, player_name, 'Draft Day Age', to_print_percentile=False)
    get_value_at_column_by_player_name(df, player_name, 'Height', to_print_percentile=False)
    get_value_at_column_by_player_name(df, player_name, 'Weight', to_print_percentile=False)
    # Athleticism 
    get_percentile_rank(df, 'FTr', player_name, to_print=False, to_drop_column=False, rank_col_name="FTr Rank")
    get_percentile_rank(df, 'Stock%', player_name, to_print=False, to_drop_column=False, rank_col_name="Stock% Rank")
    get_percentile_rank(df, '%Astd @ Rim', player_name, is_inverse_percentile=True, to_print=False, to_drop_column=False, rank_col_name='%Astd @ Rim Rank')
    get_percentile_rank(df, '# Dunks', player_name, to_print=False, to_drop_column=False, rank_col_name="# Dunks Rank")

    df['Athleticism Score'] = round((df['FTr Rank']+df['# Dunks Rank'])/2, 1)
    print("Athleticism Score: " + str(get_percentile_rank(df, 'Athleticism Score', player_name, to_print=False)))
    df.drop(['FTr Rank', '# Dunks Rank', "Stock% Rank", '%Astd @ Rim Rank'], axis=1, inplace=True)
    # Passing
    get_percentile_rank(df, 'Pure Point Rating', player_name, to_print=False, to_drop_column=False, rank_col_name="PPR Rank")
    get_percentile_rank(df, 'AST/40', player_name, to_print=False, to_drop_column=False, rank_col_name="AST/40 Rank")
    get_percentile_rank(df, 'AST/TOV', player_name, to_print=False, to_drop_column=False, rank_col_name="AST/TOV Rank")
    df['Passing Score'] = round((df['PPR Rank']+df['AST/40 Rank']+df['AST/TOV Rank'])/3, 1)
    print(f"Passing Score: " + str(get_percentile_rank(df, 'Passing Score', player_name, to_print=False)))
    df = df.drop('PPR Rank', axis=1)
    df = df.drop('AST/40', axis=1)
    df = df.drop('AST/TOV Rank', axis=1)
    # Rebounding
    p1 = get_percentile_rank(df, 'TRB%', player_name, to_print=False)
    print(f"Rebounding Score: " + str(float(p1)))
    # Shooting
    get_percentile_rank(df, '3PAr', player_name, to_print=False, to_drop_column=False, rank_col_name="3PAr Rank")
    get_percentile_rank(df, '3FG%', player_name, to_print=False, to_drop_column=False, rank_col_name="3FG% Rank")
    get_percentile_rank(df, 'FG% @ Mid', player_name, to_print=False, to_drop_column=False, rank_col_name="FG% @ Mid Rank")
    df['Shooting Score'] = round((df['3PAr Rank']+df['3FG% Rank']+df['FG% @ Mid Rank'])/3, 1)
    #print(get_value_at_column_by_player_name(df, player_name, "3PAr Rank"))
    #print(get_value_at_column_by_player_name(df, player_name, "Shooting Score"))
    #print(get_value_at_column_by_player_name(df, player_name, "FG% @ Mid Rank"))
    print(f"Shooting Score: " + str(get_percentile_rank(df, 'Shooting Score', player_name, to_print=False)))
    df = df.drop('3PAr Rank', axis=1)
    df = df.drop('3FG% Rank', axis=1)
    df = df.drop('FG% @ Mid Rank', axis=1)
    # Finishing
    get_percentile_rank(df, 'FG% @ Rim', player_name, to_print=False, to_drop_column=False, rank_col_name="FG% @ Rim Rank")
    get_percentile_rank(df, '% Shots @ Rim', player_name, to_print=False, to_drop_column=False, rank_col_name="% Shots @ Rim Rank")
    df['Finishing Score'] = round((df['% Shots @ Rim Rank']+df['FG% @ Rim Rank'])/2, 1)
    get_value_at_column_by_player_name(df, player_name, "FG% @ Rim")
    get_value_at_column_by_player_name(df, player_name, "% Shots @ Rim")
    print(f"Finishing Score: " + str(get_percentile_rank(df, 'Finishing Score', player_name, to_print=False)))
    df = df.drop('FG% @ Rim Rank', axis=1)
    df = df.drop('% Shots @ Rim Rank', axis=1)
    # Defense
    get_percentile_rank(df, 'STL%', player_name, to_print=False, to_drop_column=False, rank_col_name="STL% Rank")
    get_percentile_rank(df, 'BLK%', player_name, to_print=False, to_drop_column=False, rank_col_name="BLK% Rank")
    get_percentile_rank(df, 'DEF RTG', player_name, is_inverse_percentile=True, to_print=False, to_drop_column=False, rank_col_name="DEF RTG Rank")
    print(get_value_at_column_by_player_name(df, player_name, "STL%"))
    print(get_value_at_column_by_player_name(df, player_name, "BLK%"))
    print(get_value_at_column_by_player_name(df, player_name, "DEF RTG"))
    df['Defense Score'] = round((df['STL% Rank']+df['BLK% Rank']+df['DEF RTG Rank'])/3, 1)
    print(f"Defense Score: " + str(get_percentile_rank(df, 'Defense Score', player_name, to_print=False)))
    df = df.drop('STL% Rank', axis=1)
    df = df.drop('BLK% Rank', axis=1)
    df = df.drop('DEF RTG Rank', axis=1)
    # Shot Creator
    get_percentile_rank(df, '%Astd @ Mid', player_name, to_print=False, is_inverse_percentile=True, to_drop_column=False, rank_col_name="%Astd @ Mid Rank")
    get_percentile_rank(df, 'Hands-On Buckets', player_name, to_print=False, to_drop_column=False, rank_col_name="HOB Rank")
    get_percentile_rank(df, 'USG%', player_name, to_print=False, to_drop_column=False, rank_col_name="USG% Rank")
    get_percentile_rank(df, '%Astd @ Rim', player_name, is_inverse_percentile=True, to_print=False, to_drop_column=False, rank_col_name="%Astd @ Rim Rank")
    get_percentile_rank(df, '%Astd @ 3', player_name, is_inverse_percentile=True, to_print=False, to_drop_column=False, rank_col_name="%Astd @ 3 Rank")
    df['Shot Creation Score'] = round((df['%Astd @ Mid Rank']+df['HOB Rank']+df['USG% Rank']+df['%Astd @ Rim Rank']+df['%Astd @ 3 Rank'])/5, 1)
    print(f"Shot Creation Score: " + str(get_percentile_rank(df, 'Shot Creation Score', player_name, to_print=False)))
    df = df.drop('%Astd @ Mid Rank', axis=1)
    df = df.drop('HOB Rank', axis=1)
    df = df.drop('USG% Rank', axis=1)
    df = df.drop('%Astd @ Rim Rank', axis=1)
    df = df.drop('%Astd @ 3 Rank', axis=1)
    # College Productivity
    get_percentile_rank(df, 'SOS', player_name, to_print=False, to_drop_column=False, rank_col_name="SOS Rank")
    get_percentile_rank(df, 'WS/40', player_name, to_print=False, to_drop_column=False, rank_col_name="WS/40 Rank")
    get_percentile_rank(df, 'BPM', player_name, to_print=False, to_drop_column=False, rank_col_name="BPM Rank")
    df['College Productivity Score'] = round((df['SOS Rank']+df['WS/40 Rank']+df['BPM Rank'])/3, 1)
    print(f"College Productivity Score: " + str(get_percentile_rank(df, 'College Productivity Score', player_name, to_print=False)))
    df = df.drop('SOS Rank', axis=1)
    df = df.drop('WS/40 Rank', axis=1)
    df = df.drop('BPM Rank', axis=1)
    # AAU Success?
    
df = read_csv_and_cast_columns('data/db_2022_special.csv')
name = " ".join(sys.argv[1:])
draw_conclusions_on_player(df, name)
