import sys
sys.path.insert(0, '../../')
from utils import *

MAX_LENGTH_OF_PROSPECT_CAREER = 5
PAGE_OF_RSCI_RANK_CUTOFF = 8

OVERALL_RSCI_EXCEPTIONS = {
    "Hasheem Thabeet": 64,
    "Sam Young": 52,
    "Jeff Pendergraph" : 161,
    "Leo Lyons" : 66,
    "Hassan Whiteside" : 96,
    "Jordan Crawford" : 239,
	"Dar Tucker" : 46,
	"DeSean Butler" : 107,
	"Tiny Gallon" : 10,
	"Manny Harris" : 37,
	"Darington Hobson" : 146,
	"AJ Ogilvy" : 100,
	"Justin Brownlee" : 351,
	"Jeff Allen" : 83,
	"Jacob Pullen" : 88,
	"Jeremy Hazell" : 182,
	"Jeffery Taylor" : 48,
    "Fab Melo": 14,
    "Dee Bost" : 84,
	"Tu Holloway" : 181,
	"Ricardo Ratcliffe" : 154,
	"Alex Len" : 250,
	"Kelly Olynyk" : 200,
	"Arsalan Kazemi" : 143,
	"Cleanthony Early" : 193,
	"Andre Dawkins" : 31,
	"Kendall Williams" : 149,
	"Marcus Johnson" : 51,
	"Zach Norvell" : 103,
	"Vince Edwards" : 121,
	"James Blackmon" : 20,
	"Gary Payton" : 123,
	"Andrew White" : 54,
	"Justin Jackson" : 9,
	"Darius Johnson-Odom": 329,
	"Caris LeVert" : 239,
	"Anthony Davis" : 1,
	"Raymond Spalding" : 42,
	"Roy Devyn" : 200,
	"Geron Johnson" : 154,
	"Scottie Wilbekin" : 250,
	"Delon Wright" : 159,
	"Michael Frazier" : 86,
	"Bryce Dejean-Jones" : 82,
	"Michael Porter" : 2,
	"Jakob Poeltl" : 100,
	"Kadeem Allen" : 83,
	"Chris Boucher" : 100,
	"Jock Landale" : 343,
	"Ja Morant" : 328,
	"Dylan Windler" : 377,
	"Cameron Johnson" : 224,
	"Obi Toppin" : 343,
	"Desmond Bane" : 343,
	"Joshua Primo" : 62,
	"Joel Ayayi" : 100,
	"Herb Jones" : 148,
	"Mark Williams" : 28,
	"Jake Laravia" : 250,
	"Julian Champagnie" : 162,
	"Kenneth Lofton" : 250,
	"Keon Ellis" : 169,
	"JD Notae" : 343,
	"Quenton Jackson": 242,
    "Shaq Buchanan" : 400,
    "Daeqwon Plowden" : 400,
    "Dakota Mathias" : 218,
    "Kevon Harris" : 400,
    "DeAnthony Melton" : 134
}

def add_rsci_rank_as_column(df, find_single_player=False):
    """Get the RSCI rank from 247Sports (not rivals) and add it as a column to the main DataFrame.
    
    Args:
        df (dataframe): Any DataFrame with a "Name" and "School" column

    Returns:
        dataframe: The dataframe with the new data
    """
    df['RSCI'] = ""
    df = add_initial_rsci_rankings(df)
    if (find_single_player and df.at[0, 'RSCI']):
        return df
    if (find_single_player):
        year_counter = get_year_from_season(df.at[0, 'Season']) - df.at[0, 'Class']-1
        end_year = get_year_from_season(df.at[0, 'Season'])
    else:
        year_counter = FIRST_YEAR_OF_DRAFT_RANKINGS - MAX_LENGTH_OF_PROSPECT_CAREER
        end_year = get_current_year()
    while year_counter < end_year:
        print("Getting RSCI rank for players from the class of " + str(year_counter))
        page = 1
        while page <= PAGE_OF_RSCI_RANK_CUTOFF: 
            soup_html = fetch_247_html(year_counter, page)
            trs = soup_html.find_all('li', {'class':'rankings-page__list-item'})
            for player in trs:
                name = remove_non_alphabetic_characters(player.find('a').getText()).lower()
                for index, row in df.iterrows():
                    if (name in row['Name'].lower() and row['RSCI'] == ""):
                        if (name in COMMON_NAMES):
                            college = player.find('div', {'class':'status'}).find('img')['alt']
                            if (college != row['School']):
                                continue
                        rank = player.find('div', {'class':'primary'}).getText().split()[0]
                        print("Found a match for " + row['Name'] + ": " + rank)
                        df.at[index, 'RSCI'] = rank
                        if find_single_player:
                            return df
                        else:
                            break
            page = page + 1
        year_counter = year_counter + 1
    df.apply(set_remaining_rsci_rankings, axis=1)
    return df
    
def fetch_247_html(year_counter, page):
    """Fetches the 247 recruiting rankings for a given year & page.

    Args:
        year_counter (int): The year of the recruiting rankings.
        page (int): The page of the recruiting rankings. A page has 50 results, so page 7 is players with ranks between 300-350.
    
    Returns:
        List: The html of the 247 rankings page.
    """
    base_url = "http://247sports.com/Season/" + str(year_counter) + "-Basketball/CompositeRecruitRankings"
    params = "?InstitutionGroup=HighSchool&Page=" + str(page)
    return find_site(base_url + params)[0]
    
def add_initial_rsci_rankings(df):
    for index, row in df.iterrows():
        rank_in_dictionary = OVERALL_RSCI_EXCEPTIONS.get(row['Name'], 0)
        if (rank_in_dictionary != 0):
            df.loc[index, 'RSCI'] = rank_in_dictionary
    return df
    
def set_remaining_rsci_rankings(row):
    """For every player not found on 247 year pages, we want to add their RSCI rank if it we have it saved as an exception."""
	
    if (pd.isna(row['RSCI'])):
        row['RSCI'] = 400
    return row