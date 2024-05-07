import pandas as pd
import numpy as np

import sys
sys.path.append("./src")

from realgm import realgm_scrape

import math
from utils import *


df = pd.read_csv('data/draft_db_nba.csv')
df.to_csv('data/draft_db_nba.csv', index = False)
df = df[(df['3FGA/40']*df['MP']) >= 50]
get_top_values(df, '3PAr')

# correlations = []
# for value in ['AST/TOV', 'FG% @ Mid', '3PAr', '3FG%', 'FT%', '%Astd @ 3', 'TS%']:
#     t = df.dropna(subset=[value])
#     correlation = np.corrcoef(t[value], t['NBA 3P%'])[0, 1]
#     correlations.append((value, correlation))

# # Sort the correlations by absolute value to find the most correlated value
# sorted_correlations = sorted(correlations, key=lambda x: abs(x[1]), reverse=True)

# print(sorted_correlations)
# # Print the most correlated value
# print(f"The value that correlates most with 'NBA 3P%' is '{sorted_correlations[0][0]}' with a correlation coefficient of {sorted_correlations[0][1]}")

# # CORRELATIING TO NBA 3P%:
# # 179 Guards: [('3PAr', 0.3126832759252265), ('3FG%', 0.28356500403010027), ('TS%', 0.27005614052435484), ('FG% @ Mid', 0.2525728570865721), ('FT%', 0.16470192325318922), ('%Astd @ 3', 0.09570079488288226), ('AST/TOV', 0.00725223673530722)]
# # 71 Centers: [('%Astd @ 3', 0.42339370420705197), ('FT%', 0.3778054415410404), ('3PAr', 0.32642321010196623), ('3FG%', 0.2988643546959436), ('AST/TOV', 0.17018978697435075), ('FG% @ Mid', 0.11614101223352839), ('TS%', -0.030677590121022745)]
# # 389 Wings: [('3PAr', 0.24083648154861195), ('3FG%', 0.20614102086745256), ('FT%', 0.18902436471816803), ('TS%', 0.14620622654351367), ('FG% @ Mid', 0.11036695039407084), ('%Astd @ 3', 0.04342983980322431), ('AST/TOV', -0.020508000859267895)]   

# # CORRELATING TO NBA 3 POINT CONFIDENCE:
# # [('3PAr', 0.6960056596032334), ('FT%', 0.41104619507228823), ('3FG%', 0.334483738842485), ('%Astd @ 3', 0.29524616224177525), ('AST/TOV', 0.18834651552625004), ('FG% @ Mid', 0.01883135511166908), ('TS%', 0.011494706671979531)]       