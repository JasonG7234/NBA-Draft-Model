import sys
sys.path.insert(0, '../../')
from utils import *

INDEX_SEPERATING_FIRST_AND_LAST_NAME = 2

def add_all_college_basketball_prospects(df, find_single_player=False):
    """Get the top 100 prospects each year from NBADraft.net, and add each year's top 100 to a df DataFrame.
    Found NBADraft.net to be the simplest to scrape and the most consistent from year-to-year, 
    their rankings are generally questionable but I'm dropping their rankings anyway.
    """

    year_counter = FIRST_YEAR_OF_DRAFT_RANKINGS if not find_single_player else get_year_from_season(df.at[0, 'Season'])
    current_year = get_current_year()
    while year_counter <= current_year:
        season = get_season_from_year(year_counter)
        #print("Getting players from the " + season + " season")
        soup_html, _ = find_site("https://www.nbadraft.net/ranking/bigboard/?year-ranking=" + str(year_counter))
        if (soup_html):
            players = soup_html.find('tbody').findChildren('tr')
            if (find_single_player):
                df = find_single_player_info(df, players)
                df = convert_class_to_number(df)
                print(df)
                df = convert_height_to_inches(df)
                df = reformat_remaining_college_basketball_prospects(df)
                return df
            else:
                year_dataframe = add_all_prospects_to_df(season, players)
                df = pd.concat([df, year_dataframe], ignore_index=True)
        year_counter = year_counter + 1
    df = remove_non_college_basketball_prospects(df)
    return reformat_remaining_college_basketball_prospects(df)
    
def find_single_player_info(df, players):
    for player in players:
        stats = player.find_all('td')
        name_elem = stats[INDEX_SEPERATING_FIRST_AND_LAST_NAME]
        name = " ".join(name.text for name in name_elem.findChildren('span'))
        if (is_fuzzy_name_match(name, df.at[0, 'Name'], OVERALL_PLAYER_NAME_EXCEPTIONS)):
            df.loc[0, 'Height'] = stats[3].text
            df.loc[0, 'Weight'] = stats[4].text
            df.loc[0, 'Position'] = stats[5].text
            df.loc[0, 'Class'] = stats[7].text
            return df
    print("ERROR: Could not find single player info from nbadraft.net.")
    return df

def add_all_prospects_to_df(season, players):
    top100 = []
    for player in players:
        stats = player.find_all('td')
        index = INDEX_SEPERATING_FIRST_AND_LAST_NAME
        row = []
        while index < len(stats):
            stat_text = stats[index].getText()
            if (index == INDEX_SEPERATING_FIRST_AND_LAST_NAME):
                stat_text = " ".join(name.text for name in stats[index].findChildren('span'))
            row.append(stat_text)
            index = index + 1
        row.insert(0, season)
        top100.append(row)
    return pd.DataFrame(top100, columns=['Season', 'Name', 'Height', 'Weight', 'Position', 'School', 'Class'])

def remove_non_college_basketball_prospects(df):
    df = remove_international_prospects(df)
    df = remove_non_d1_prospects(df)
    df = remove_individual_prospects(df)
    df = convert_class_to_number(df)
    df = convert_height_to_inches(df)
    return df

def remove_international_prospects(df):
    return df[df['Class'].isin(['Fr.','So.','Jr.','Sr.'])]

def remove_non_d1_prospects(df):
    return df[~df['School'].isin(["JUCO",'USA','Canada','G-League',''])]

def remove_individual_prospects(df):
    """Remove individual prospects who didn't play, and therefore throw off some of the code.

    Args:
        df (DataFrame): Any DataFrame with a 'Name' column

    Returns:
        DataFrame: The same DataFrame
    """
    return df[~df['Name'].isin(["Enes Kanter","Garrett Siler","Ricardo Ledo","Shaedon Sharpe"])]

def reformat_remaining_college_basketball_prospects(df):
    df['Name'] = df['Name'].apply(lambda name: get_basketball_reference_formatted_name(name, OVERALL_PLAYER_NAME_EXCEPTIONS))
    for index, row in df.iterrows():
        school = get_basketball_reference_formatted_school(row['School'], OVERALL_SCHOOL_NAME_EXCEPTIONS, row['School'])
        school = get_basketball_reference_formatted_school(row['Name'], OVERALL_PLAYER_SCHOOL_EXCEPTIONS, school)
        if (school.endswith("St.")):
            school = school[:-1] + "ate"
        df.at[index, 'School'] = school
    return df

def convert_class_to_number(df):
    class_to_number = {'Fr.':1, 'So.':2, 'Jr.':3, 'Sr.':4}
    df.replace(to_replace=class_to_number, inplace=True)
    return df

def convert_height_to_inches(df):
    df['Height'] = df['Height'].apply(lambda x: int(x[0])*12 + int(x[2:].replace('-', '')))
    return df
