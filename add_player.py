import sys
sys.path.append("./src")

from utils import *
from aux_stats import *

from nbadraftcombine import measurements_fetch
from nbadraftnet import nbadraftnet_scrape
from hoop_explorer import hoop_explorer_fetch
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
    
# NAME, SEASON, SCHOOL, REALGM_ID
with open("temp.txt", "r") as file:
  lines = []
  
  for line in file:
    line = line.strip()

    lines.append(line)

df = pd.DataFrame([[lines[1], lines[0], lines[2]]], columns=['Season', 'Name', 'School'])
df.set_index(['Season', 'Name', 'School'])
df = realgm_scrape.get_realgm_stats(df, True, realgm_id=lines[3])
df = convert_class_to_number(df)
df = convert_height_to_inches(df)
df = basketballreference_scrape.add_college_stats_from_basketball_reference(df)
df = rsci_scrape.add_rsci_rank_as_column(df, True)
if (not df["RSCI"].all()):
    df['RSCI'] = 400
df = torvik_fetch.get_torvik_dunks(df)
df = hoop_explorer_fetch.get_hoop_explorer_plus_minus_single_player(df)
df = hoopmath_scrape.add_college_stats_from_hoopmath(df)
df = update_position_columns(df)
if (len(lines) == 5 and lines[4] == 'Draft'):
    df = measurements_fetch.get_NBA_Combine_measurements(df)
    df = add_aux_columns(df)
    # Let's do something here to just append to aux_stats and then call the main method
else:
    df = reorder_final_season_db_columns(df)
df.to_csv('temp.csv', index=False)
#def fix_percents(df):
#    df[]