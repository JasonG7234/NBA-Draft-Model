import pandas as pd
from utils import *

# Read the CSV file into a dataframe
df = pd.read_csv('data/draft_db.csv')

# Filter the dataframe to only include rows where the 'Season' column has a value of '2023-24'
fdf = df[(df['ORB%'] <= 7) & (df['DRB%'] <= 11) & (df['Height'] >= 80)]

# Output the filtered dataframe to a CSV file called 'temp.csv'
draw_conclusions_on_column(fdf, 'Draft Score')
