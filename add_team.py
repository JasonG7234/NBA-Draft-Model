import sys
sys.path.append("./src")

from utils import *

from nbadraftcombine import measurements_fetch
from basketballreference import basketballreference_scrape
from barttorvik import torvik_fetch
from hoopmath import hoopmath_scrape
from rsci import rsci_scrape
from realgm import realgm_scrape

def reorder_final_team_columns(df):
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
                'Event Year','Event Name','Event GP','Event MIN','Event PTS','Event FGM','Event FGA','Event FG%','Event 3PM','Event 3PA','Event 3P%','Event FTM','Event FTA','Event FT%','Event TRB','Event AST','Event STL','Event BLK','Event TOV','Event PF','Event Placement'
                ]]

df_players = []
season = "2021-22"
team = " ".join(sys.argv[1:])
url = f"https://www.sports-reference.com/cbb/schools/{team.replace(' ', '-').lower()}/2022.html"
#team = "USC"
soup_html, _ = find_site(url)
table = soup_html.find('table', {'id':'roster'}).find('tbody')
players = table.find_all('tr')
for player in players:
    name = player.find('th').text
    df_players.append([season, name, team])

df = pd.DataFrame(df_players, columns=['Season', 'Name', 'School'])

df = realgm_scrape.get_realgm_stats(df, False, True)
df = convert_class_to_number(df)
df = convert_height_to_inches(df)
df = basketballreference_scrape.add_college_stats_from_basketball_reference(df)
df = torvik_fetch.get_torvik_dunks(df)
df = hoopmath_scrape.add_college_stats_from_hoopmath(df)
df = rsci_scrape.add_rsci_rank_as_column(df, starting_year=2021)
df = update_position_columns(df)
df = reorder_final_team_columns(df)
df.to_csv('temp.csv', index=False)

