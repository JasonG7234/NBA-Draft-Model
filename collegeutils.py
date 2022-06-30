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
    master = convert_class_to_number(master)
    master = convert_height_to_inches(master)
    return master

def remove_international_prospects(master):
    return master[master['Class'].isin(['Fr.','So.','Jr.','Sr.'])]

def remove_non_d1_prospects(master):
    return master[~master['School'].isin(["JUCO",'USA',''])]

def remove_individual_prospects(master):
    return master[~master['Name'].isin(["Enes Kanter","Garrett Siler","Ricardo Ledo"])]

def reformat_remaining_college_basketball_prospects(master):
    master['Name'] = master['Name'].apply(lambda name: get_basketball_reference_formatted_name(name, OVERALL_PLAYER_NAME_EXCEPTIONS))
    for index, row in master.iterrows():
        school = get_basketball_reference_formatted_school(row['School'], OVERALL_SCHOOL_NAME_EXCEPTIONS, row['School'])
        school = get_basketball_reference_formatted_school(row['Name'], OVERALL_PLAYER_SCHOOL_EXCEPTIONS, school)
        if (school.endswith("St.")):
            school = school[:-1] + "ate"
        master.at[index, 'School'] = school
    return master

def convert_class_to_number(master):
    class_to_number = {'Fr.':1, 'So.':2, 'Jr.':3, 'Sr.':4}
    master.replace(to_replace=class_to_number, inplace=True)
    return master

def convert_height_to_inches(master):
    master['Height'] = master['Height'].apply(lambda x: int(x[0])*12 + int(x[2:].replace('-', '')))
    return master

def get_rsci_rank_from_dictionary(name):
    return check_value_in_dictionary_of_exceptions(name, OVERALL_RSCI_EXCEPTIONS, 0) 

def get_last_season_stat_row(soup_html, table_id):
    table = soup_html.find('table', {'id':table_id})
    if (table):
        table_body = table.find('tbody')
        return table_body('tr')[-1] 
    return None

def get_possession_stats(season_row):
    stats = season_row.findChildren('td', {'data-stat':True})[INDEX_OF_POSSESSION_STATS_IN_TABLE:] # Slicing
    return [ stat.getText() for stat in stats ] # List comprehension

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

def is_expected_advanced_stat_in_table(stat, index):
    return stat['data-stat'].strip() == ADVANCED_COLUMN_IDS[index]

def is_empty_dummy_column(stat):
    return stat['data-stat'] == 'ws-dum' or stat['data-stat'] == 'bpm-dum'
