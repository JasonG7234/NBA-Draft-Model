import sys
sys.path.append("./src")

from utils import *

from nbadraftcombine import measurements_fetch
from nbadraftnet import nbadraftnet_scrape
from basketballreference import basketballreference_scrape
from barttorvik import torvik_fetch
from hoopmath import hoopmath_scrape
from rsci import rsci_scrape
from realgm import realgm_scrape

def invalid_season_format(season):
    try:
        if (int(season[:4])+1 == int(season[-2:])+2000) and (season[4] == '-'):
            return False
        else:
            return True
    except Exception:
        return True
    
player_name = input("Enter the name of the player you would want to add. Please include normal capitalization: ")
while True: 
    season = input(f"Enter the season you would want the stats for {player_name} in the format of 20XX-XX: ")
    if invalid_season_format(season):
        print("ERROR: Invalid season format. Please try again in the format of 20XX-XX")
    else:
        break
school = input(f"Enter the school {player_name} played for in {season}: ")

df = pd.DataFrame([[season, player_name, school]], columns=['Season', 'Name', 'School'])
df.set_index(['Season', 'Name', 'School'])
df = nbadraftnet_scrape.add_all_college_basketball_prospects(df, True)
if ('Height' not in df.columns):
    df = realgm_scrape.get_realgm_stats(df, True, True)
    df = convert_class_to_number(df)
    df = convert_height_to_inches(df)
else:
    df = realgm_scrape.get_realgm_stats(df, True, False)
df = basketballreference_scrape.add_college_stats_from_basketball_reference(df)
df = rsci_scrape.add_rsci_rank_as_column(df, True)
if (df.at[0, 'RSCI'] == ""):
    df.loc[0, 'RSCI'] = 400
df = measurements_fetch.get_NBA_Combine_measurements(df)
df = torvik_fetch.get_torvik_dunks(df)
df = hoopmath_scrape.add_college_stats_from_hoopmath(df)
df = update_position_columns(df)
df = reorder_final_columns(df)
df.to_csv('temp.csv', index=False)
#def fix_percents(df):
#    df[]