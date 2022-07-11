import sys
sys.path.insert(0, '../../')
from utils import *

from nba_api.stats.endpoints import draftcombineplayeranthro
import numpy as np
import time

DRAFT_COMBINE_ANTHRO_COLUMNS = ["POSITION", "HEIGHT_WO_SHOES", "HEIGHT_W_SHOES", "WEIGHT", "WINGSPAN", "STANDING_REACH", "BODY_FAT_PCT", "HAND_LENGTH", "HAND_WIDTH"]

DRAFT_COMBINE_DATAFRAME_COLUMN_NAMES = ["Position", "Height w/o Shoes", "Height w/ Shoes", "Weight", "Wingspan", "Standing Reach", "Body Fat %", "Hand Length", "Hand Width"]

NBA_DRAFT_COMBINE_NAME_EXCEPTIONS = {
    "Edrice Adebayo" : "Bam Adebayo",
    "Byron Mullens" : "BJ Mullens",
    "Patrick Mills" : "Patty Mills",
    "Jeff Ayres" : "Jeff Pendergraph",
    "Keith Gallon" : "Tiny Gallon",
    "Artsiom Parakhouski" : "Art Parakhouski",
    "E'Twaun Moore" : "Etwaun Moore",
    "Jeff Taylor" : "Jeffrey Taylor",
    "James McAdoo" : "James Michael McAdoo",
    "Devyn Marble" : "Roy Devyn",
    "Kay Felder" : "Kahlil Felder",
    "Cat Barber" : "Anthony Barber",
    "Ray Spalding" : "Raymond Spalding",
    "Cameron Reddish" : "Cam Reddish",
    "Herbert Jones" : "Herb Jones",
    "Matt Hurt" : "Matthew Hurt"
    }

def get_NBA_Combine_measurements(df):
    """Takes in a dataframe, adds columns for each nba combine measurement, and then returns the dataframe with the new data.

    Args:
        df (dataframe): Any DataFrame with a "Name" and "Season" column

    Returns:
        dataframe: The dataframe with the new data
    """
    seasons = df.Season.unique()
    for col in DRAFT_COMBINE_DATAFRAME_COLUMN_NAMES:
        if col not in df:
            df[col] = ""
            
    for season in seasons:
        print(season)
        combine_data = fetch_NBA_combine_data(season)
        for _, combine_player in combine_data.iterrows():
            for i, df_player in df[df['Season'] == season].iterrows():
                if (is_fuzzy_name_match(combine_player['PLAYER_NAME'], df_player['Name'], NBA_DRAFT_COMBINE_NAME_EXCEPTIONS)):
                    print(f"Found match for {df_player['Name']}")
                    populate_NBA_combine_measurements(df, i, combine_player)
                    break
    return df

def populate_NBA_combine_measurements(df, index, combine_values):
    print(index)
    for i in range(len(DRAFT_COMBINE_DATAFRAME_COLUMN_NAMES)):
        combine_value = combine_values[DRAFT_COMBINE_ANTHRO_COLUMNS[i]]
        if (combine_value in ERROR_VALUES):
            print("Not adding a value for " + DRAFT_COMBINE_ANTHRO_COLUMNS[i])
        else:
            df.loc[index, DRAFT_COMBINE_DATAFRAME_COLUMN_NAMES[i]] = combine_value
        
def fetch_NBA_combine_data(season):
    """Fetches the NBA Combine measurement data for a specific season.
    NOTE: This function takes in the collegiate season as a parameter, not the NBA season. 

    Args:
        season (string): The collegiate season to fetch the data for.
        
    Returns: 
        DataFrame: The NBA Combine data for that season.
    """
    season = str(int(season[:4])+1) + '-' + str(int(season[-2:])+1)
    time.sleep(2)
    count = 0
    while count < 3:
        try:
            combine_data = draftcombineplayeranthro.DraftCombinePlayerAnthro(
            league_id='00', 
            season_year=season,
            headers={'Accept': 'application/json, text/plain, */*',
'Accept-Encoding': 'gzip, deflate, br',
'Accept-Language': 'en-US,en;q=0.5',
'Connection': 'keep-alive',
'Host': 'stats.nba.com',
'Origin': 'https://www.stats.nba.com',
'Referer': 'https://www.stats.nba.com/',
'sec-ch-ua': '"Google Chrome";v="87", "\"Not;A\\Brand";v="99", "Chromium";v="87"',
'sec-ch-ua-mobile': '?1',
'Sec-Fetch-Dest': 'empty',
'Sec-Fetch-Mode': 'cors',
'Sec-Fetch-Site': 'same-site',
'User-Agent': 'Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Mobile Safari/537.36',
'x-nba-stats-origin': 'stats',
'x-nba-stats-token': 'true'}).results.get_data_frame()
            return combine_data
        except requests.exceptions.ConnectionError:
            print("Yup connection error, giving it 10 and retrying")
            time.sleep(10)
            count += 1
        except Exception:
            print("Other error, giving it 10 and retrying")
            time.sleep(10)
            count += 1
    return None