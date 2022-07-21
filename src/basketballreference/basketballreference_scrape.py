import sys
sys.path.insert(0, '../../')
from utils import *

INDEX_OF_POSSESSION_STATS_IN_TABLE = 25
MAX_PROFILES_TO_SEARCH_BY_NAME = 6

def add_college_stats_from_basketball_reference(df):
    """Get all advanced college stats for each player's most recent year by scraping the relevant table from basketballreference.
    I also add on ORTG, DRTG, and AST/TOV% because I think they are really relevant stats for projecting NBA prospects.
    """

    college_stats = []
    for index, row in df.iterrows():
        player_stats = []
        print("Getting most recent college stats for " + row['Name'])
        soup_html = get_players_basketball_reference_page(row)
        if (soup_html):
            player_stats.extend(get_advanced_stats(soup_html))
            player_stats.extend(get_per_40_stats(soup_html))
            player_stats.extend(get_per_100_stats(soup_html))
            player_stats.append(get_ast_to_tov_ratio(soup_html))
            player_stats.append(get_sos(soup_html))
            player_stats.append(get_conference(soup_html))
        else:
            df.drop(index, inplace=True)
            continue
        print(player_stats)
        college_stats.append(player_stats)

    df = pd.concat([df, pd.DataFrame(college_stats,index=df.index,columns=COLUMN_NAMES)], axis=1)
    return df

def get_players_basketball_reference_page(row):
    """Get the player's Basketall-Reference page. This includes pulling the right name and index from the respective dictionaries.
    Once we have the URL, we check if it is right by checking the player's quick info.
    """

    player_name_in_url = get_basketball_reference_formatted_url(row['Name'])
    index_value_in_url = check_value_in_dictionary_of_exceptions(player_name_in_url, COLLEGE_INDEX_EXCEPTIONS, 1)
    if (index_value_in_url == 1):
        while index_value_in_url in range(1, MAX_PROFILES_TO_SEARCH_BY_NAME): 
            url = "https://www.sports-reference.com/cbb/players/" + player_name_in_url + "-" + str(index_value_in_url) + ".html"
            print(url)
            soup_html, _ = find_site(url)
            if (soup_html.find('table', {'id':'players_advanced'})):
                quick_player_info = get_basketball_reference_player_info(soup_html)
                expected_school_name = get_basketball_reference_formatted_school(row['School'], COLLEGE_SCHOOL_NAME_EXCEPTIONS, row['School'])
                if (quick_player_info and expected_school_name in quick_player_info):
                    return soup_html
                else:
                    print(row['Name'] + " might be a common name - trying again at next profile index")
                    if (player_name_in_url[-3:] == '-jr'):
                        player_name_in_url = player_name_in_url[:-3] + 'jr'
                        print(player_name_in_url)
                    else:
                        index_value_in_url = index_value_in_url + 1
            else:
                print("Sorry, we couldn't find the correct player page for : " +row['Name'])
                if (player_name_in_url[-3:] == '-jr'):
                    player_name_in_url = player_name_in_url[:-3] + 'jr'
                    url = "https://www.sports-reference.com/cbb/players/" + player_name_in_url + "-" + str(index_value_in_url) + ".html"
                    soup_html, _ = find_site(url)
                    return soup_html
                return None
    else:
        url = "https://www.sports-reference.com/cbb/players/" + player_name_in_url + "-" + str(index_value_in_url) + ".html"
        soup_html, _ = find_site(url)
        return soup_html
    print("Sorry, we couldn't find any college stats for : " + row['Name'])
    return None

def get_advanced_stats(soup_html):
    """Get the player's advanced stats from their table. This is a complicated process because of the differences in the format 
    of the advanced table through the years, along with some dummy columns that are always blank for some reason.
    """
    player_advanced_stats = [] 
    last_season_stats = get_last_season_stat_row(soup_html, 'players_advanced')
    stats = last_season_stats.findChildren('td')[2:] # Slicing
    stats_index = 0 # Index of which stat we are on in the player's Advanced table
    all_index = 0 # Index of which stat we SHOULD be on, according to all possible stats in the Advanced table
    while all_index in range(0, len(ADVANCED_COLUMN_IDS)):
        try:
            stat_at_index = stats[stats_index] 
            if (stat_at_index.getText()):
                if (is_expected_advanced_stat_in_table(stat_at_index, all_index)):
                    player_advanced_stats.append(stat_at_index.getText()) 
                    stats_index = stats_index + 1
                else: 
                    player_advanced_stats.append("")
            else:
                if (is_empty_dummy_column(stat_at_index)):
                    stats_index = stats_index + 1
                else:
                    player_advanced_stats.append("")
                    stats_index = stats_index + 1
        except IndexError:
            if (ADVANCED_COLUMN_IDS[all_index] != 'bpm-dum'):
                player_advanced_stats.append("") 
        all_index = all_index + 1
    return player_advanced_stats

def get_per_40_stats(soup_html):
    """Get the player's per 40 minute stats from their table.
    """
    
    last_season_stats = get_last_season_stat_row(soup_html, 'players_per_min')
    return [last_season_stats.find('td', {'data-stat' : col}).getText() for col in PER_40_COLUMN_IDS]
    
def get_per_100_stats(soup_html):
    """Get the player's per 100 possession stats from their table.
    """

    last_season_stats = get_last_season_stat_row(soup_html, 'players_per_poss')
    if (last_season_stats): 
        return [last_season_stats.find('td', {'data-stat' : col}).getText() for col in PER_100_COLUMN_IDS]
    else: 
        return [""] * len(PER_100_COLUMN_IDS)

# HELPER METHODS
def get_last_season_stat_row(soup_html, table_id):
    table = soup_html.find('table', {'id':table_id})
    if (table):
        table_body = table.find('tbody')
        return table_body('tr')[-1] 
    return None

def get_possession_stats(season_row):
    stats = season_row.findChildren('td', {'data-stat':True})[INDEX_OF_POSSESSION_STATS_IN_TABLE:] # Slicing
    return [ stat.getText() for stat in stats ]

def get_ast_to_tov_ratio(soup_html):
    last_season = get_last_season_stat_row(soup_html, 'players_totals')
    ast = (last_season.find('td', {'data-stat':'ast'})).getText()
    tov = (last_season.find('td', {'data-stat':'tov'})).getText()
    if (int(tov) == 0):
        return ast
    return str(round(int(ast)/int(tov), 2))

def get_sos(soup_html):
    last_season = get_last_season_stat_row(soup_html, 'players_per_game')
    sos = last_season.find('td', {'data-stat':'sos'})
    return sos.getText() if sos else ""

def get_conference(soup_html):
    last_season = get_last_season_stat_row(soup_html, 'players_per_game')
    conf = last_season.find('td', {'data-stat':'conf_abbr'})
    return conf.getText() if conf else ""

def is_expected_advanced_stat_in_table(stat, index):
    return stat['data-stat'].strip() == ADVANCED_COLUMN_IDS[index]

def is_empty_dummy_column(stat):
    return stat['data-stat'] == 'ws-dum' or stat['data-stat'] == 'bpm-dum'


