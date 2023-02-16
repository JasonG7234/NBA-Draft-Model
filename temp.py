import pandas as pd
import sys
sys.path.append("./src")

from utils import *
from realgm import realgm_scrape

df = pd.read_csv("data/draft_db_2022_special.csv")
df = realgm_scrape.populate_image_links(df)
df.to_csv("dadsa.csv", index=False)

