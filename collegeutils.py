from utils import *

# Constants are declared with capital letters and underscores
FIRST_YEAR_OF_DRAFT_RANKINGS = 2009
MAX_LENGTH_OF_PROSPECT_CAREER = 5
INDEX_SEPERATING_FIRST_AND_LAST_NAME = 2
PAGE_OF_RSCI_RANK_CUTOFF = 8
INDEX_OF_POSSESSION_STATS_IN_TABLE = 25
MAX_PROFILES_TO_SEARCH_BY_NAME = 5

def remove_non_college_basketball_prospects(master):
    master = remove_international_prospects(master)
    master = remove_non_d1_prospects(master)
    master = remove_individual_prospects(master)

def remove_international_prospects(master):
    return master[(master.Class == "Fr.")
     | (master.Class == "So.")
      | (master.Class == "Jr.")
       | (master.Class == "Sr.")]

def remove_non_d1_prospects(master):
    return master[(master.School != "JUCO")
     & (master.School != "USA") 
       & (master.School != "")]

def remove_individual_prospects(master):
    return master[(master.Name != "Enes Kanter")
     & (master.Name != "Garrett Siler")
      & (master.Name != "Ricardo Ledo")]

def reformat_remaining_college_basketball_prospects(master):
    for index, row in master.iterrows():
        row['Name'] = get_basketball_reference_formatted_name(row['Name'], OVERALL_PLAYER_NAME_EXCEPTIONS)
        school = get_basketball_reference_formatted_school(row['School'], OVERALL_SCHOOL_NAME_EXCEPTIONS, row['School'])
        row['School'] = get_basketball_reference_formatted_school(row['Name'], OVERALL_PLAYER_SCHOOL_EXCEPTIONS, school)
        if (row['School'][-3:] == "St."):
            row['School'] = row['School'][:-1] + "ate"

def get_rsci_rank_from_dictionary(name):
    return check_value_in_dictionary_of_exceptions(name, OVERALL_RSCI_EXCEPTIONS, 0) 

def get_last_season_stat_row(soup_html, tableID):
    table = soup_html.find('table', {'id':tableID})
    if (table):
        tableBody = table.find('tbody')
        return tableBody('tr')[-1] 
    return None

def get_possession_stats(season_row):
    stats = season_row.findChildren('td', {'data-stat':True})[INDEX_OF_POSSESSION_STATS_IN_TABLE:]
    return [ stat.getText() for stat in stats ]

def get_ast_to_tov_ratio(soup_html):
    lastSeason = get_last_season_stat_row(soup_html, 'players_totals')
    ast = (lastSeason.find('td', {'data-stat':'ast'})).getText()
    tov = (lastSeason.find('td', {'data-stat':'tov'})).getText()
    if (int(tov) == 0):
        return ast
    return str(round(int(ast)/int(tov), 2))

def is_expected_advanced_stat_in_table(stat, index):
    return stat['data-stat'] == ADVANCED_COLUMN_IDS[index]

def is_empty_dummy_column(stat):
    return stat['data-stat'] == 'ws-dum' or stat['data-stat'] == 'bpm-dum'