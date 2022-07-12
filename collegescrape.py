import sys
sys.path.append("./src")
from nbadraftcombine import measurements

import pandas as pd
import numpy as np

from utils import *
from collegeutils import *

master = pd.DataFrame()

def main():
    global master
    master = pd.read_csv('data/main.csv')
    #add_college_stats_from_basketball_reference()
    #add_college_stats_from_hoopmath()
    
    export_master(measurements.get_NBA_Combine_measurements(master))

def add_all_college_basketball_prospects():
    """Get the top 100 prospects each year from NBADraft.net, and add each year's top 100 to a master DataFrame.
    Found NBADraft.net to be the simplest to scrape and the most consistent from year-to-year, 
    their rankings are generally questionable but I'm dropping their rankings anyway.
    """
    
    global master

    print("----------------------------------")
    print("STEP 1 - Getting the names of all the prospects")
    print("----------------------------------")
    year_counter = FIRST_YEAR_OF_DRAFT_RANKINGS
    current_year = get_current_year()
    while year_counter <= current_year:
        top100 = []
        season = get_season_from_year(year_counter)
        print("Getting players from the " + season + " season")
        soup_html = find_site("https://www.nbadraft.net/ranking/bigboard/?year-ranking=" + str(year_counter))
        if (soup_html):
            players = soup_html.find('tbody').findChildren('tr')
            for player in players:
                stats = player.find_all('td')
                index = INDEX_SEPERATING_FIRST_AND_LAST_NAME
                row = []
                while index < len(stats):
                    stat_text = stats[index].getText()
                    if (index == INDEX_SEPERATING_FIRST_AND_LAST_NAME):
                        stat_text = " ".join(name.text for name in stats[index].findChildren('span')) # Example of list comprehension
                    row.append(stat_text)
                    index = index + 1
                row.insert(0, season)
                top100.append(row)
            year_dataframe = pd.DataFrame(top100, columns=['Season', 'Name', 'Height', 'Weight', 'Position', 'School', 'Class'])
        master = pd.concat([master, year_dataframe], ignore_index=True)
        year_counter = year_counter + 1
    master = remove_non_college_basketball_prospects(master)
    master = reformat_remaining_college_basketball_prospects(master)

def add_college_stats_from_basketball_reference():
    """Get all advanced college stats for each player's most recent year by scraping the relevant table from basketballreference.
    I also add on ORTG, DRTG, and AST/TOV% because I think they are really relevant stats for projecting NBA prospects.
    """

    global master

    print("----------------------------------")
    print("STEP 3 - Getting the last year's advanced stats of all of the prospects")
    print("----------------------------------")

    college_stats = []
    for index, row in master.iterrows():
        player_stats = []
        print("Getting most recent college stats for " + row['Name'])
        soup_html = get_players_basketball_reference_page(row)
        if (soup_html):
            player_stats.extend(get_advanced_stats(soup_html))
            player_stats.extend(get_per_40_stats(soup_html))
            player_stats.extend(get_per_100_stats(soup_html))
            player_stats.append(get_ast_to_tov_ratio(soup_html))
            player_stats.append(get_sos(soup_html))
        else:
            master.drop(index, inplace=True)
            continue
        print(player_stats)
        college_stats.append(player_stats)

    master = pd.concat([master, pd.DataFrame(college_stats,index=master.index,columns=COLUMN_NAMES)], axis=1)

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
            soup_html = find_site(url)
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
                    return(find_site(url))
                return None
    else:
        url = "https://www.sports-reference.com/cbb/players/" + player_name_in_url + "-" + str(index_value_in_url) + ".html"
        return(find_site(url))
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

def export_master(master):
    temp_master = reorder_columns(master)
    temp_master.to_csv('temp_master.csv', index=False)

if __name__ == "__main__":
    main()
