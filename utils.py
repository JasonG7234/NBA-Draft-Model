import datetime
import re
import requests
import time
import unidecode
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from fuzzywuzzy import fuzz

FIRST_YEAR_OF_DRAFT_RANKINGS = 2009

OVERALL_PLAYER_NAME_EXCEPTIONS = {
    "Moe Harkless" : "Maurice Harkless",
    "TyShon Alexander" : "Ty-Shon Alexander",
    "BJ Boston" : "Brandon Boston Jr.",
    "Chris Johnsonn" : "Chris Johnson",
    "Cameron Reddish" : "Cam Reddish",
    "Cam Oliver" : "Cameron Oliver",
    "James McAdoo" : "James Michael McAdoo",
    "Cam Long" : "Cameron Long",
    "Simi Shittu" : "Simisola Shittu",
    "Kevin Porter" : "Kevin Porter Jr.",
    "Herbert Jones" : "Herb Jones",
    "Ron Harper" : "Ron Harper Jr.",
    "Gary Trent" : "Gary Trent Jr.",
    "Dennis Smith" : "Dennis Smith Jr.",
    "Tashawn Thomas" : "TaShawn Thomas",
    "DeShaun Thomas" : "Deshaun Thomas",
    "Khalil Whitney" : "Kahlil Whitney",
    "Oscar da" : "Oscar da Silva",
    "Patrick Baldwin" : "Patrick Baldwin Jr.",
    "Scotty Pippen" : "Scotty Pippen Jr"
}

OVERALL_PLAYER_SCHOOL_EXCEPTIONS = {
    "PJ Hairston" : "UNC",
    "Glen Rice" : "Georgia Tech",
    "Nick Barbour" : "High Point",
    "Charlie Westbrook" : "South Dakota"
}

OVERALL_SCHOOL_NAME_EXCEPTIONS = {
    "St. Mary's" : "Saint Mary's", 
    "Massachusetts" : "UMass",
    "North Carolina" : "UNC",
    "Pittsburgh" : "Pitt",
    "St. Johns" : "St. John's (NY)",
    "Cal St. Northridge" : "Cal State Northridge",
    "Mississippi" : "Ole Miss"
}

COMMON_NAMES = [
    "Tony Mitchell",
    "Justin Jackson",
    "Mike Davis",
    "Michael Porter",
    "Chris Johnson",
    "Anthony Davis",
    "Marcus Johnson",
    "Josh Carter",
    "Mike Scott",
    "Chris Wright",
    "Gary Clark",
    "Chris Smith",
    "James Johnson",
    "Marcus Thornton"
]

NBA_PLAYER_NAME_EXCEPTIONS = {
    "BJ Mullens" : "Byron Mullens",
    "Patrick Mills" : "Patty Mills",
    "Jeffery Taylor" : "Jeff Taylor",
    "Jahmius Ramsey" : "Jahmi'us Ramsey",
    "Simi Shittu" : "Simisola Shittu",
    "Mohamed Bamba" : "Mo Bamba",
    "Raymond Spalding" : "Ray Spalding",
    "Joseph Young" : "Joe Young",
    "Kahlil Felder" : "Kay Felder"
}

NBA_INDEX_EXCEPTIONS = {
    "Alan Williams" : 3,
    "Derrick Brown" : 4,
    "Darius Johnson-Odom" : 3,
    "Brandon Knight" : 3,
    "Marcus Morris" : 3,
    "Dennis Smith Jr" : 3,
    "Chris Johnson" : 3,
    "Robert Williams" : 4,
    "Jeff Taylor" : 3,
    "Kenrich Williams" : 4,
    "Johnathan Williams" : 4,
    "Keldon Johnson" : 4,
    "Andre Roberson" : 3,
    "Damian Jones" : 3,
    "Stanley Johnson" : 4
}

NBA_SCHOOL_NAME_EXCEPTIONS = {
    "Louisiana Lafayette" : "LA-Lafayette",
    "VCU" : "Virginia Commonwealth",
    "Long Beach State" : "Cal State Long Beach",
    "Tennessee-Martin" : "University of Tennessee at Martin",
    "UCSB" : "UC Santa Barbara",
    "Illinois-Chicago" : "University of Illinois at Chicago",
    "UAB" : "University of Alabama at Birmingham",
    "Southern Miss." : "University of Southern Mississippi",
    "St. Johns" : "St. John's"
}

HIGH_MAJOR_CONFERENCES = ['Big Ten', 'SEC', 'ACC', 'Big East', 'Big 12', 'Pac-12']
MID_MAJOR_CONFERENCES = ['A-10', 'AAC', 'WCC', 'MWC']

PER_40_COLUMN_IDS = ['fg_per_min', 'fga_per_min', 'fg_pct', 'fg2_per_min', 'fg2a_per_min', 'fg2_pct', 'fg3_per_min', 'fg3a_per_min', 'fg3_pct',
    'ft_per_min','fta_per_min','ft_pct', 'trb_per_min', 'ast_per_min', 'stl_per_min', 'blk_per_min', 'tov_per_min', 'pf_per_min', 'pts_per_min']

PER_100_COLUMN_IDS = ['fg_per_poss', 'fga_per_poss', 'fg2_per_poss', 'fg2a_per_poss', 'fg3_per_poss', 'fg3a_per_poss','ft_per_poss','fta_per_poss',
    'trb_per_poss', 'ast_per_poss', 'stl_per_poss', 'blk_per_poss', 'tov_per_poss', 'pf_per_poss', 'pts_per_poss', 'off_rtg', 'def_rtg']

ADVANCED_COLUMN_IDS = ['games','games_started','mp','per','ts_pct','efg_pct','fg3a_per_fga_pct','fta_per_fga_pct','pprod','orb_pct','drb_pct','trb_pct','ast_pct',
    'stl_pct','blk_pct','tov_pct','usg_pct','ows','dws','ws','ws_per_40','obpm','dbpm','bpm']  
    
COLUMN_NAMES = ['G','GS','MP','PER','TS%','eFG%','3PAr','FTr','PProd','ORB%','DRB%','TRB%','AST%',
    'STL%','BLK%','TOV%','USG%','OWS','DWS','WS','WS/40','OBPM','DBPM','BPM','FG/40', 'FGA/40', 'FG%', '2FGM/40', '2FGA/40', '2FG%', '3FGM/40', '3FGA/40', '3FG%',
    'FT/40','FTA/40','FT%', 'TRB/40', 'AST/40', 'STL/40', 'BLK/40', 'TOV/40', 'PF/40', 'PTS/40', 'FGM/100Poss', 'FGA/100Poss', '2FGM/100Poss', '2FGA/100Poss', '3FGM/100Poss', '3FGA/100Poss','FT/100Poss','FTA/100Poss',
    'TRB/100Poss', 'AST/100Poss', 'STL/100Poss', 'BLK/100Poss', 'TOV/100Poss', 'PF/100Poss', 'PTS/100Poss', 'OFF RTG', 'DEF RTG', 'AST/TOV', 'SOS', 'Conference']

LOG_REG_COLUMNS = ['Height','RSCI','Class','TS%','3PAr','TRB%','AST%','BLK%','STL%','WS/40','AST/TOV']

ERROR_VALUES = [None, np.nan, '', '-', '-%']
COLUMNS_TO_CAST = ['MP', 'STL%', 'BLK%','TOV%','USG%','OWS','DWS','WS', '# Dunks', '% Shots @ Rim', 'FG% @ Rim', '%Astd @ Rim', '% Shots @ Mid', 'FG% @ Mid', 'FGA/100Poss']

def find_site(url, max_retry_count=3):
    """Use BeautifulSoup to head to designated URL and return BeautifulSoup object.
    It's very important to decode + sub out all comments! (Basketball-Reference's HTML comments throw everything out of wack)"""
    count = 0
    req_headers = { 'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36",
                   'referer': "https://www.sports-reference.com/cbb/schools/pepperdine/2022.html",
                   'accept-language': "en-US,en;q=0.6"}
    response = None
    while count < max_retry_count:
        try:
            response = requests.get(url, headers=req_headers, timeout=30)
            break
        except requests.exceptions.ConnectionError:
            print("Connection error, giving it 10 and retrying")
            time.sleep(10)
            count += 1
        except requests.exceptions.TooManyRedirects:
            print("Redirect error, giving it 10 and then retrying")
            req_headers = { 'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0"}
            time.sleep(10)
            count += 1
    if not response:
        print('NO RESPONSE')
        return None, None
    html = response.text
    return BeautifulSoup(re.sub("<!--|-->","", html), "html.parser"), response.url

def read_csv_and_cast_columns(file_name):
    df = pd.read_csv(file_name)
    for col in COLUMNS_TO_CAST:
        df = cast_column_to_type(df, col)
    return df

def get_draft_db_df():
    return pd.read_csv("data/draft_db.csv")
    
def cast_column_to_type(df, col_name):
    df[col_name].replace('', np.nan, inplace=True)
    df[col_name].astype(float)
    return df

def birthday_to_draft_day_age(birthday, season):
    dt = datetime.datetime.strptime(' '.join(birthday), "%b %d, %Y")
    draft_date = datetime.datetime.strptime(f"Jun 25, {season}", "%b %d, %Y")
    return round((draft_date - dt).days / 365, 2)

def check_value_in_dictionary_of_exceptions(name, exceptions_dict, default):
    """Performs a dictionary lookup to try to map the player's name/school to the correct Basketball-Reference page."""
    return exceptions_dict.get(name, default)

def get_row_from_player_name(df: pd.DataFrame, player_name: str, idx: int = 0):
    return df.loc[df['Name'] == player_name].iloc[idx]

def get_basketball_reference_player_info(soup):
    player_info =  soup.find('div', {'id': 'meta'})
    if (not player_info): return None
    return unidecode.unidecode(player_info.getText())

def is_fuzzy_name_match(data_name, csv_name, name_exception_dict, name_match_percentage=90):
    exception_name = check_value_in_dictionary_of_exceptions(data_name, name_exception_dict, data_name)
    ratio = fuzz.partial_ratio(csv_name, exception_name.replace('.', '').replace("'", ''), )
    if ratio >= name_match_percentage:
        print(ratio)
        return True
    else:
        return False
        
def get_basketball_reference_formatted_school(school, exceptions, default):
    return check_value_in_dictionary_of_exceptions(school, exceptions, default)

def get_basketball_reference_formatted_name(name, exceptions):
    return remove_non_alphabetic_characters(check_value_in_dictionary_of_exceptions(name, exceptions, name))

def remove_non_alphabetic_characters(name):
    return unidecode.unidecode(re.sub(r'[^A-Za-z- ]+', '', name))

def convert_class_to_number(df):
    class_to_number = {'Fr.':1, 'RS-Fr': 1, 'So.':2, 'Jr.':3, 'Sr.':4, 'RS-Sr.': 4}
    df.replace(to_replace=class_to_number, inplace=True)
    return df

def convert_number_to_class(df):
    number_to_class = {1:'Freshman', 2:'Sophomore', 3:'Junior', 4:'Senior'}
    df['Class'] = df['Class'].replace(to_replace=number_to_class)
    return df

def convert_height_to_inches(df):
    df['Height'] = df['Height'].apply(lambda x: int(x[0])*12 + int(x[2:].replace('-', '')))
    return df

def get_current_year():
    return datetime.datetime.now().year

def get_matchable_name(name):
    return name.replace("'", '').replace('.', '').replace('-', ' ').lower()

def get_season_from_year(year):
    return str(year-1) + "-" + str(year)[2:4]

def get_year_from_season(season):
    return int(season[:4])+1

def reverse_name(name):
    return ' '.join(reversed(name.strip().split(', ')))

def update_position_columns(df):
    if 'Position 1' in df and 'Position 2' in df:
        return df
    else:
        df['Position 2'] = ''
        for index, row in df.iterrows():
            positions = re.split('/|-', df.at[index, 'Position'])
            df.loc[index, 'Position'] = positions[0]
            if (len(positions) == 2):
                df.loc[index, 'Position 2'] = positions[1]
        df = df.rename(columns = {'Position' : 'Position 1'})
    return df

def normalize(df, col_name, is_inverse_normalization=False, lower_bound=None):
    if (df[col_name] == "").all():
        df[f'{col_name} Normalized'] = 0
        return df
    max_value = df[col_name].max()
    min_value = df[col_name].min()
    if (is_inverse_normalization):
        df.loc[:, f'{col_name} Normalized'] = 1 - (df[col_name] - min_value) / (max_value - min_value)
    else:
        df.loc[:, f'{col_name} Normalized'] = (df[col_name] - min_value) / (max_value - min_value)
    if (lower_bound):
        df.loc[df[col_name] < 0.05, col_name] = 0.05
    df.loc[:, f'{col_name} Normalized'] = df[f'{col_name} Normalized'].astype(float, errors='raise')
    df.loc[:, f'{col_name} Normalized'] = df[f'{col_name} Normalized'].fillna(df[f'{col_name} Normalized'].mean())
    return df

def reorder_final_draft_db_columns(df):
    
    df = df.reindex(columns = df.columns.tolist() + 
        ['Play Style', 'Stock%', 'Adjusted TOV%', 'Offensive Load', '3 Point Proficiency', '3 Point Confidence', 'Dunk vs Rim Shot Percentage', '% Dunks Unassisted', 'Dunks per Minute Played', 'Unassisted Shots @ Rim /100Poss', '% Assisted', 'Finishing Score', 'Shooting Score', 'Shot Creation Score', 'Passing Score', 'Rebounding Score', 'Athleticism Score', 'Defense Score', 'College Productivity Score', 'Percentile Score', 'Box Score Creation', 'Rim Shot Creation', 'Helio Score', 'Draft Score']
    )
    
    return df[['RealGM ID','Season','Name',
                'Position 1','Position 2','Play Style','Height','Weight',
                'School','Conference','Wins','Losses','SOS',
                'Class','Birthday','Draft Day Age',
                'RSCI','G','GS','MP','PER','TS%','eFG%','3PAr','FTr','PProd','ORB%','DRB%','TRB%','AST%','STL%','BLK%','Stock%','TOV%','Adjusted TOV%','USG%','Offensive Load','OWS','DWS','WS','WS/40','OBPM','DBPM','BPM','AST/TOV','OFF RTG','DEF RTG','Hands-On Buckets','Pure Point Rating',
                'FG/40','FGA/40','FG%','2FGM/40','2FGA/40','2FG%','3FGM/40','3FGA/40','3FG%',"3 Point Proficiency",'3 Point Confidence','FT/40','FTA/40','FT%','TRB/40','AST/40','STL/40','BLK/40','TOV/40','PF/40','PTS/40',
                'FGM/100Poss','FGA/100Poss','2FGM/100Poss','2FGA/100Poss','3FGM/100Poss','3FGA/100Poss','FT/100Poss','FTA/100Poss','TRB/100Poss','AST/100Poss','STL/100Poss','BLK/100Poss','TOV/100Poss','PF/100Poss','PTS/100Poss',
                '# Dunks',"Dunk vs Rim Shot Percentage","% Dunks Unassisted","Dunks per Minute Played","Unassisted Shots @ Rim /100Poss",
                '% Shots @ Rim','FG% @ Rim','%Astd @ Rim','% Shots @ Mid','FG% @ Mid','%Astd @ Mid','% Shots @ 3','%Astd @ 3','% Assisted',
                'AAU Season','AAU Team','AAU League','AAU GP','AAU GS','AAU MIN','AAU PTS','AAU FGM','AAU FGA','AAU FG%','AAU 3PM','AAU 3PA','AAU 3P%','AAU FTM','AAU FTA','AAU FT%','AAU ORB','AAU DRB','AAU TRB','AAU AST','AAU STL','AAU BLK','AAU TOV','AAU PF',
                'Event Year','Event Name','Event GP','Event MIN','Event PTS','Event FGM','Event FGA','Event FG%','Event 3PM','Event 3PA','Event 3P%','Event FTM','Event FTA','Event FT%','Event TRB','Event AST','Event STL','Event BLK','Event TOV','Event PF','Event Placement',
                'Finishing Score','Shooting Score','Shot Creation Score','Passing Score','Rebounding Score','Athleticism Score','Defense Score','College Productivity Score','Percentile Score',
                'Box Score Creation','Rim Shot Creation','Helio Score','Draft Score', 'Image Link']]
    
def reorder_final_season_db_columns(df):
    return df[['RealGM ID','Season','Name',
                'Position 1','Position 2',
                'School','Conference','Wins','Losses','SOS',
                'Class','Birthday','Draft Day Age',
                'Height','Weight',
                'RSCI','G','GS','MP','PER','TS%','eFG%','3PAr','FTr','PProd','ORB%','DRB%','TRB%','AST%','STL%','BLK%','TOV%','USG%','OWS','DWS','WS','WS/40','OBPM','DBPM','BPM','AST/TOV','OFF RTG','DEF RTG','Hands-On Buckets','Pure Point Rating',
                'FG/40','FGA/40','FG%','2FGM/40','2FGA/40','2FG%','3FGM/40','3FGA/40','3FG%','FT/40','FTA/40','FT%','TRB/40','AST/40','STL/40','BLK/40','TOV/40','PF/40','PTS/40',
                'FGM/100Poss','FGA/100Poss','2FGM/100Poss','2FGA/100Poss','3FGM/100Poss','3FGA/100Poss','FT/100Poss','FTA/100Poss','TRB/100Poss','AST/100Poss','STL/100Poss','BLK/100Poss','TOV/100Poss','PF/100Poss','PTS/100Poss',
                '# Dunks','% Shots @ Rim','FG% @ Rim','%Astd @ Rim','% Shots @ Mid','FG% @ Mid','%Astd @ Mid','% Shots @ 3','%Astd @ 3',
                'AAU Season','AAU Team','AAU League','AAU GP','AAU GS','AAU MIN','AAU PTS','AAU FGM','AAU FGA','AAU FG%','AAU 3PM','AAU 3PA','AAU 3P%','AAU FTM','AAU FTA','AAU FT%','AAU ORB','AAU DRB','AAU TRB','AAU AST','AAU STL','AAU BLK','AAU TOV','AAU PF',
                'Event Year','Event Name','Event GP','Event MIN','Event PTS','Event FGM','Event FGA','Event FG%','Event 3PM','Event 3PA','Event 3P%','Event FTM','Event FTA','Event FT%','Event TRB','Event AST','Event STL','Event BLK','Event TOV','Event PF','Event Placement', 
                'Image Link'
                ]]

def get_value_at_column_by_player_name(df, player_name, col_name, is_inverse_percentile=False, to_print_percentile=True, to_find_similar=False, num_find_similar=0):
    print('=========================================')
    try:
        val = df.loc[df['Name'] == player_name].iloc[0][col_name]
    except IndexError:
        print(f"ERROR: The name {player_name} has no exact match.")
        return
    print(f"{player_name}'s value for column '{col_name}' is: {val}")
    if to_find_similar:
        # Calculate the absolute difference between each row and the target value
        df['difference'] = df[col_name].apply(lambda x: abs(x - val))

        # Sort the dataframe by the 'difference' column to find the closest rows
        df_sorted = df.sort_values(by='difference')

        # Get the rows with the smallest difference (closest to the target value)
        closest_rows = df_sorted.head(num_find_similar)  # You can specify the number of rows you want

        print(closest_rows[['Name', col_name]])
    if to_print_percentile:
        get_percentile_rank(df, col_name, player_name, is_inverse_percentile)

def get_top_values(df, col_name, num_values=10):
    # Sort the dataframe by 'column_name' in descending order (highest to lowest)
    df_sorted = df.sort_values(by=col_name, ascending=False)

    # Print the top 10 rows
    print(df_sorted[['Name', col_name]].head(num_values))   

def get_percentile_rank(df, col_name, player_name, is_inverse_percentile=False, to_print=True, rank_col_name="Rank", to_drop_column=True):
    df[col_name] = df[col_name].fillna(df[col_name].mean())
    df[rank_col_name] = df[col_name].rank(pct=True, ascending=(not is_inverse_percentile))
    try:
        percentile = round(df.loc[df['Name'] == player_name].iloc[0][rank_col_name]*100)
        percentile = 100-percentile if is_inverse_percentile else percentile
    except:
        percentile = 1
    if to_print:
        d = {1 : 'st', 2 : 'nd', 3 : 'rd'}
        print(f"This value for {col_name} is in the {percentile}{d.get(percentile % 10, 'th')} percentile.")
        print('=========================================')
    if to_drop_column:
        df = df.drop([rank_col_name], axis=1)
    return percentile
    
def cast_column_to_float(df, col_name):
    df[col_name].astype(float)
    return df

def draw_conclusions_on_column(df, col_name, num_top=10, position="all", show_bottom=True):
    if (position != "all"):
        df = df[df['Position 1'] == position]
    df[col_name].replace('', np.nan, inplace=True)
    df[col_name].astype(float)
    print(f"The top {str(num_top)} highest values of column {col_name} are: ")
    for _, row in df.nlargest(num_top, [col_name]).iterrows():
        print(f"{row['Name']}: {row[col_name]}")
    
    print('=========================================')
    if (show_bottom):
        print(f"The top {str(num_top)} lowest values of column {col_name} are: ")
        for _, row in df.nsmallest(num_top, [col_name]).iterrows():
            print(f"{row['Name']}: {row[col_name]}")
        print('=========================================')    
    print(f"The average value of column {col_name} is: {df[col_name].mean()}")
    print(f"The median value of column {col_name} is: {df[col_name].median()}")

def get_player_comparisons(df: pd.DataFrame, player_name: str, num_to_compare: int = 4, categories = None, include_draft_score=False):
    if (categories is None):
        categories = ['Finishing Score','Shooting Score','Shot Creation Score','Passing Score','Rebounding Score','Athleticism Score','Defense Score','College Productivity Score']
        
    leaderboard = {}
    target_player = df.loc[df['Name'] == player_name].iloc[0]
    
    
    # Filter out to same primary or secondary position
    df = filter_by_position(df, target_player)
    for _, row in df.iterrows():
        player_summary_score_diff = 0
        summary_score_count = 0
        for summary_label in categories:
            summary_value = row[summary_label]
            if (summary_value not in ERROR_VALUES):
                #if (summary_value < 1): summary_value *= 100
                    
                player_summary_score_diff += abs(target_player[summary_label] - summary_value)
                summary_score_count += 1
        if (include_draft_score):
            draft_score_value = row['Draft Score']
            player_summary_score_diff += (abs(target_player['Draft Score'] - draft_score_value)*3) # Magnitude of 3. We want the Draft Score comp to be about 33% of the comparison
            leaderboard[row['Name']] = (player_summary_score_diff/(summary_score_count+3))
        else:
            leaderboard[row['Name']] = (player_summary_score_diff/summary_score_count)
        
    top_leaderboard = []
    for key, value in leaderboard.items():
        if (value < 100):
            top_leaderboard.append([key, value])
    return sorted(top_leaderboard, key=lambda x: x[1])[1:num_to_compare+1]

def filter_by_position(df, target_row):
    return df[(df['Position 1'] == target_row['Position 1']) | (df['Position 2'] == target_row['Position 1'])]

def print_dataframe(df):
    
    with pd.option_context('display.max_rows', 100, 'display.max_columns', None):
        print(df)

def populate_dataframe_with_average_values(df):
    df = df.replace('', np.nan)
    return df.fillna(df.mean())

def delete_duplicates(df):
    df_unique = df.drop_duplicates(subset='RealGM ID', keep='first')
    return df_unique
    
df = pd.read_csv("data/draft_db.csv")
df = delete_duplicates(df)
df.to_csv("data/draft_db.csv", index=False)
