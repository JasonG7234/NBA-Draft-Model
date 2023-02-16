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
    
# Open the file in read mode
with open("temp.txt", "r") as file:
  # Create an empty list
  lines = []
  
  # Iterate over the lines of the file
  for line in file:
    # Strip leading and trailing whitespace
    line = line.strip()

    # Add the line to the list
    lines.append(line)

df = pd.DataFrame([[lines[1], lines[0], lines[2]]], columns=['Season', 'Name', 'School'])
df.set_index(['Season', 'Name', 'School'])
df = realgm_scrape.get_realgm_stats(df, True)
df = convert_class_to_number(df)
df = convert_height_to_inches(df)
df = basketballreference_scrape.add_college_stats_from_basketball_reference(df)
df = rsci_scrape.add_rsci_rank_as_column(df, True)
if (df.at[0, 'RSCI'] == ""):
    df.loc[0, 'RSCI'] = 400
df = torvik_fetch.get_torvik_dunks(df)
df = hoopmath_scrape.add_college_stats_from_hoopmath(df)
df = update_position_columns(df)
if (lines[3] == 'Draft'):
    df = measurements_fetch.get_NBA_Combine_measurements(df)
    df = reorder_final_draft_db_columns(df)
else:
    df = reorder_final_season_db_columns(df)
df.to_csv('temp.csv', index=False)
#def fix_percents(df):
#    df[]