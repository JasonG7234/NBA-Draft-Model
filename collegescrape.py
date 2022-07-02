import os.path
import sys

import pandas as pd
import numpy as np

from utils import *
from collegeutils import *

master = pd.DataFrame()

def main():
    global master
    master = pd.read_csv('main_2012.csv')
    add_college_stats_from_basketball_reference()
    #add_college_stats_from_hoopmath()
        
    export_master(master)

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

def add_rsci_rank_as_column():
    """Get the RSCI rank from 247Sports and add it as a column to the master DataFrame."""

    global master

    print("----------------------------------")
    print("STEP 2 - Getting the RSCI ranks of all the prospects")
    print("----------------------------------")
    
    year_counter = FIRST_YEAR_OF_DRAFT_RANKINGS - MAX_LENGTH_OF_PROSPECT_CAREER
    master['RSCI'] = ""
    while year_counter < get_current_year():
        print("Getting RSCI rank for players from the class of " + str(year_counter))
        page = 1
        while page <= PAGE_OF_RSCI_RANK_CUTOFF: 
            base_url = "http://247sports.com/Season/" + str(year_counter) + "-Basketball/CompositeRecruitRankings"
            params = "?View=Detailed&InstitutionGroup=HighSchool&Page=" + str(page)
            soup_html = find_site(base_url + params)
            trs = soup_html.find_all('li', {'class':'rankings-page__list-item'})
            for player in trs:
                name = remove_non_alphabetic_characters(player.find('a').getText()).lower()
                for index, row in master.iterrows():
                    if (name in row['Name'].lower() and row['RSCI'] == ""):
                        if (name in COMMON_NAMES):
                            college = player.find('div', {'class':'status'}).find('img')['alt']
                            if (college != row['School']):
                                continue
                        rank = player.find('div', {'class':'primary'}).getText().split()[0]
                        print("Found a match for " + row['Name'] + ": " + rank)
                        master.at[index, 'RSCI'] = rank
                        break
            page = page + 1
        year_counter = year_counter + 1
    master.apply(add_remaining_rsci_rankings)
    
def add_remaining_rsci_rankings(row):
    """For every player not found on 247 year pages, we want to add their RSCI rank if it we have it saved as an exception."""

    rank_in_dictionary = get_rsci_rank_from_dictionary(row['Name'])
    if (rank_in_dictionary != 0):
        row['RSCI'] = rank_in_dictionary
    if (pd.isna(row['RSCI'])):
        row['RSCI'] = 400
    return row

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

def get_players_hoop_math_page(row):
    """Get the player's Hoop-Math team page.
    """
    
    team_name_in_url = get_hoop_math_formatted_school(row['School'])
    season_in_url = '20' + row['Season'].split('-')[-1]
    if (int(season_in_url) < 2018 and team_name_in_url == 'NCState'):
        team_name_in_url = "NorthCarolinaSt."
    url = 'https://hoop-math.com/' + team_name_in_url + season_in_url + '.php'
    return find_site(url)

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

def add_college_stats_from_hoopmath():
    print("----------------------------------")
    print("STEP 4 - Getting the last year's Hoop-Math data for all the prospects")
    print("----------------------------------")
    # TODO: Is it necessary to add these stats from Hoop-Math? 
    
    global master

    hoop_math_stats = []
    
    for _, row in master.iterrows():
        if (row['Season'] in ['2008-09', '2009-10', '2010-11']):
            hoop_math_stats.append(['']*len(INDEXES_OF_HOOP_MATH_COLUMNS))
            continue
        player_stats = []
        print("Getting most recent hoop-math stats for " + row['Name'])
        soup_html = get_players_hoop_math_page(row)
        pbp_table = soup_html.find('table', {'id': 'OffTable1'})
        if (pbp_table):
            player_found = False
            items = pbp_table.find_all('td')
            for i in range(int(len(items) / HOOP_MATH_TABLE_COLUMN_COUNT)):
                hoop_math_row = items[i*HOOP_MATH_TABLE_COLUMN_COUNT:(i+1)*HOOP_MATH_TABLE_COLUMN_COUNT]
                hoop_math_name = ' '.join(reversed(hoop_math_row[0].getText().strip().split(', ')))
                if(is_fuzzy_name_match(hoop_math_name, row['Name'])):
                    for i in INDEXES_OF_HOOP_MATH_COLUMNS:
                        val = hoop_math_row[i].getText() 
                        if (val == '---'):
                            player_stats.append(0)
                        else:
                            player_stats.append(val.replace('%', ''))
                    player_found = True
                    break
            if not player_found:
                print(f"ERROR: Could not find hoop-math data for player {row['Name']}")
                hoop_math_stats.append(['']*len(INDEXES_OF_HOOP_MATH_COLUMNS))
            else:
                print(player_stats)
                hoop_math_stats.append(player_stats)
        else:
            print(f"ERROR: Could not find hoop-math site for player {row['Name']}")
            hoop_math_stats.append(['']*len(INDEXES_OF_HOOP_MATH_COLUMNS))
    master = pd.concat([master, pd.DataFrame(hoop_math_stats,index=master.index,columns=HOOP_MATH_COLUMN_NAMES)], axis=1)
        

def export_master(master):
    temp_master = reorder_columns(master)
    temp_master.to_csv('temp_master.csv', index=False)

if __name__ == "__main__":
    main()
