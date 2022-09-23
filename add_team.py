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

def add_team():
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

from utils import *
def divide_by_positions(df):
    
    #Pure points
    temp = df[(df['Position 1'] == 'PG') & (df['Position 2'] != 'SG')]
    pg = create_percentile_ranks_by_position_group(temp)
    #Combos
    temp = df[((df['Position 1'] == 'PG') & (df['Position 2'] == 'SG')) | ((df['Position 1'] == 'SG') & (df['Position 2'] == 'PG'))]
    g = create_percentile_ranks_by_position_group(temp)
    #Pure 2s
    temp = df[(df['Position 1'] == 'SG') & ((df['Position 2'] != 'PG') & (df['Position 2'] != 'SF'))]
    sg = create_percentile_ranks_by_position_group(temp)
    #Wings
    temp = df[((df['Position 1'] == 'SG') & (df['Position 2'] == 'SF')) | ((df['Position 1'] == 'SF') & (df['Position 2'] == 'SG'))]
    gf = create_percentile_ranks_by_position_group(temp)
    #Pure 3s
    temp = df[(df['Position 1'] == 'SF') & ((df['Position 2'] != 'SG') & (df['Position 2'] != 'PF'))]
    sf = create_percentile_ranks_by_position_group(temp)
    #Forwards
    temp = df[((df['Position 1'] == 'SF') & (df['Position 2'] == 'PF')) | ((df['Position 1'] == 'PF') & (df['Position 2'] == 'SF'))]
    f = create_percentile_ranks_by_position_group(temp)
    #Pure 4s
    temp = df[(df['Position 1'] == 'PF') & ((df['Position 2'] != 'SF') & (df['Position 2'] != 'C'))]
    pf = create_percentile_ranks_by_position_group(temp)
    #Bigs
    temp = df[((df['Position 1'] == 'PF') & (df['Position 2'] == 'C')) | ((df['Position 1'] == 'C') & (df['Position 2'] == 'PF'))]
    b = create_percentile_ranks_by_position_group(temp)
    #Pure 5s
    temp = df[(df['Position 1'] == 'C') & (df['Position 2'] != 'PF')]
    c = create_percentile_ranks_by_position_group(temp)
    
    df = pd.concat([pg, g, sg, gf, sf, f, pf, b, c], axis=0)
    draw_conclusions_on_column(df, "Overall Score")

def create_percentile_ranks_by_position_group(temp):
    temp['FTr Rank'] = temp['FTr'].rank(pct=True, ascending=True)
    temp['STK% Rank'] = temp['Stock%'].rank(pct=True, ascending=True)
    temp['%A@R Rank'] = temp['%Astd @ Rim'].rank(pct=True, ascending=False)
    temp['#D Rank'] = temp['# Dunks'].rank(pct=True, ascending=True)
    temp['PPR Rank'] = temp['Pure Point Rating'].rank(pct=True, ascending=True)
    temp['AST/40 Rank'] = temp['AST/40'].rank(pct=True, ascending=True)
    temp['A/V Rank'] = temp['AST/TOV'].rank(pct=True, ascending=True)
    temp['TRB% Rank'] = temp['TRB%'].rank(pct=True, ascending=True)
    temp['3PP Rank'] = temp['3 Point Proficiency'].rank(pct=True, ascending=True)
    temp['F%@M Rank'] = temp['FG% @ Mid'].rank(pct=True, ascending=True)
    temp['F%@R Rank'] = temp['FG% @ Rim'].rank(pct=True, ascending=True)
    temp['%S@R Rank'] = temp['% Shots @ Rim'].rank(pct=True, ascending=True)
    temp['DR Rank'] = temp['DEF RTG'].rank(pct=True, ascending=False)
    temp['HOB Rank'] = temp['Hands-On Buckets'].rank(pct=True, ascending=True)
    temp['%A@M Rank'] = temp['%Astd @ Mid'].rank(pct=True, ascending=False)
    temp['OL Rank'] = temp['Offensive Load'].rank(pct=True, ascending=True)
    temp['%A@3 Rank'] = temp['%Astd @ 3'].rank(pct=True, ascending=False)
    temp['SOS Rank'] = temp['SOS'].rank(pct=True, ascending=True)
    temp['WS/40 Rank'] = temp['WS/40'].rank(pct=True, ascending=True)
    temp['BPM Rank'] = temp['BPM'].rank(pct=True, ascending=True)
    # -----------------------------------------------------------------------
    temp['Athleticism Score'] = round((temp['FTr Rank']+temp['#D Rank']+temp['STK% Rank']+temp['%A@R Rank'])/4, 1)
    temp['Passing Score'] = round((temp['PPR Rank']+temp['AST/40 Rank']+temp['A/V Rank'])/3, 1)
    temp['Rebounding Score'] = temp['TRB% Rank']
    temp['Shooting Score'] = round((temp['3PP Rank']+temp['F%@M Rank'])/2, 1)
    temp['Finishing Score'] = round((temp['F%@R Rank']+temp['%S@R Rank'])/2, 1)
    temp['Defense Score'] = round((temp['STK% Rank']+temp['DR Rank'])/2, 1)
    temp['Shot Creation Score'] = round((temp['HOB Rank']+temp['%A@M Rank']+temp['OL Rank']+temp['%A@3 Rank'])/4, 1)
    temp['College Productivity Score'] = round((temp['SOS Rank']+temp['WS/40 Rank']+temp['BPM Rank'])/3, 1)
    # -----------------------------------------------------------------------
    temp['Athleticism Score'] = temp['Athleticism Score'].rank(pct=True, ascending=True)
    temp['Passing Score'] = temp['Passing Score'].rank(pct=True, ascending=True)
    temp['Shooting Score'] = temp['Shooting Score'].rank(pct=True, ascending=True)
    temp['Finishing Score'] = temp['Finishing Score'].rank(pct=True, ascending=True)
    temp['Defense Score'] = temp['Defense Score'].rank(pct=True, ascending=True)
    temp['Shot Creation Score'] = temp['Shot Creation Score'].rank(pct=True, ascending=True)
    temp['College Productivity Score'] = temp['College Productivity Score'].rank(pct=True, ascending=True)
    # -----------------------------------------------------------------------
    temp['Overall Score'] = round((temp['Athleticism Score']+temp['Passing Score']+temp['Shooting Score']+temp['Finishing Score']+temp['Defense Score']+temp['Shot Creation Score']+temp['College Productivity Score']+temp['Rebounding Score'])/8, 3)*100
    # -----------------------------------------------------------------------------
    temp.drop(['BPM Rank', 'WS/40 Rank', 'SOS Rank', '%A@3 Rank', 'OL Rank', '%A@M Rank', 'HOB Rank', 'DR Rank', '%S@R Rank', 'F%@R Rank', 'F%@M Rank', 
               '3PP Rank', 'TRB% Rank', 'A/V Rank', 'AST/40 Rank', 'PPR Rank', '#D Rank', '%A@R Rank', 'STK% Rank', 'FTr Rank'], axis=1, inplace=True)
    return temp

if __name__ == "__main__":
    add_team()
    #df = pd.read_csv("data/db_2022_special.csv")
    #get_percentile_rank(df, 'FTr', player_name, to_print=False, to_drop_column=False, rank_col_name="FTr Rank")
