import sys
sys.path.insert(0, '../../')
from utils import *

from nba_api.stats.endpoints import draftcombineplayeranthro
import time

DRAFT_COMBINE_ANTHRO_COLUMNS = ["POSITION", "HEIGHT_WO_SHOES", "HEIGHT_W_SHOES", "HEIGHT_W_SHOES", "WEIGHT", "WINGSPAN", "STANDING_REACH", "BODY_FAT_PCT", "HAND_LENGTH", "HAND_WIDTH"]

DRAFT_COMBINE_DATAFRAME_COLUMN_NAMES = ["Position", "Height w/o Shoes", "Height w/ Shoes", "Wingspan", "Weight", "Standing Reach", "Body Fat %", "Hand Length", "Hand Width"]

NBA_DRAFT_COMBINE_NAME_EXCEPTIONS = {
    "Edrice Adebayo" : "Bam Adebayo"
    }

def get_NBA_Combine_measurements(df):
    tmp = df.sort_values(by=['Season'])
    for col in DRAFT_COMBINE_DATAFRAME_COLUMN_NAMES:
        if col not in tmp: # FIX THIS
            tmp[col] = ""
    
    season = '2008-09'
    season_players = tmp[tmp['Season'] == season]
    combine_data = get_NBA_combine_data(season)

    for _, combine_player in combine_data.iterrows():
        print(combine_player['PLAYER_NAME'])
        for _, df_player in season_players.iterrows():
            combine_player_name = check_value_in_dictionary_of_exceptions(combine_player['PLAYER_NAME'], NBA_DRAFT_COMBINE_NAME_EXCEPTIONS, combine_player['PLAYER_NAME'])
            if (is_fuzzy_name_match(df_player['Name'], combine_player_name)):
                print(f"Found match for {combine_player['PLAYER_NAME']}")
                populate_NBA_combine_measurements(tmp, df.loc[(df['Name'] == df_player['Name']) & (df['School'] == df_player['School'])], combine_player)
                break
    return tmp
                
def populate_NBA_combine_measurements(df, row, combine_values):
    print(row.index[0])
    print(combine_values)
    for i in range(len(DRAFT_COMBINE_DATAFRAME_COLUMN_NAMES)):
        col_index = df.columns.get_loc(DRAFT_COMBINE_DATAFRAME_COLUMN_NAMES[i])
        print(row.index[0]+1, col_index)
        df.loc[row.index[0]+1, col_index] = combine_values[DRAFT_COMBINE_ANTHRO_COLUMNS[i]]
        
def get_NBA_combine_data(season):
    season = str(int(season[:4])+1) + '-' + str(int(season[-2:])+1)
    time.sleep(2)
    return draftcombineplayeranthro.DraftCombinePlayerAnthro(
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