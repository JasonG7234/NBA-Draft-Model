import sys
sys.path.append("./src")

from utils import *

from nbadraftcombine import measurements_fetch
from basketballreference import basketballreference_scrape
from barttorvik import torvik_fetch
from hoopmath import hoopmath_scrape
from rsci import rsci_scrape
from realgm import realgm_scrape



def add_team():
    df_players = []
    season = "2021-22"
    team = " ".join(sys.argv[1:])
    url = f"https://www.sports-reference.com/cbb/schools/{team.replace(' ', '-').lower()}/2022.html"
    #team = "SMU"
    soup_html, _ = find_site(url)
    table = soup_html.find('table', {'id':'roster'}).find('tbody')
    players = table.find_all('tr')
    for player in players:
        name = player.find('th').text
        df_players.append([season, name, team])

    df = pd.DataFrame(df_players, columns=['Season', 'Name', 'School'])

    df = realgm_scrape.get_realgm_stats(df, True)
    df = convert_class_to_number(df)
    df = convert_height_to_inches(df)
    df = basketballreference_scrape.add_college_stats_from_basketball_reference(df)
    df = torvik_fetch.get_torvik_dunks(df)
    df = hoopmath_scrape.add_college_stats_from_hoopmath(df)
    df = rsci_scrape.add_rsci_rank_as_column(df, starting_year=2021)
    df = update_position_columns(df)
    df = reorder_final_season_db_columns(df)
    df.to_csv('temp.csv', index=False)

from utils import *
if __name__ == "__main__":
    add_team()
    #df = pd.read_csv("data/db_2022.csv")
    #get_percentile_rank(df, 'FTr', player_name, to_print=False, to_drop_column=False, rank_col_name="FTr Rank")
