import sys
sys.path.insert(0, '../../')
from utils import *

HOOP_MATH_TABLE_COLUMN_COUNT = 15
HOOP_MATH_COLUMN_INDEXES = [4, 5, 6, 7, 8, 9, 10, 12]
HOOP_MATH_COLUMN_NAMES = ['% Shots @ Rim', 'FG% @ Rim', '%Astd @ Rim', '% Shots @ Mid', 'FG% @ Mid', '%Astd @ Mid', '% Shots @ 3', '%Astd @ 3']

HOOP_MATH_NAME_EXCEPTIONS = {
	"Kenneth Jr. Lofton" : "Kenneth Lofton Jr.",
    "Patrick Jr. Baldwin" : "Patrick Baldwin Jr.",
	"Herbert Jones" : "Herb Jones",
	"Barry Jr. Brown" : "Barry Brown",
	"Vincent Edwards" : "Vince Edwards",
	"Wendell Jr. Carter" : "Wendell Carter",
	"Gary Jr. Trent" : "Gary Trent Jr",
	"Ray Spalding" : "Raymond Spalding",
	"Edrice Adebayo" : "Bam Adebayo",
	"Anthony 'Cat' Barber" : "Anthony Barber",
	"McAdoo,James" : "James Michael McAdoo",
	"Amath M'Baye" : "Amath Mbaye",
	"Phl Pressey" : "Phil Pressey",
	"Edward Daniel" : "Ed Daniel",
	"Moe Harkless" : "Maurice Harkless",
	"KEVIN JONES" : "Kevin Jones",
    "Kam Jones" : "Kameron Jones"
}

HOOP_MATH_SCHOOL_EXCEPTIONS = {
	"UNC" : "NorthCarolina",
	"SaintMary's" : "SaintMary's(CA)",
	"Pitt" : "Pittsburgh",
	"Wisconsin-Milwaukee" : "Milwaukee",
	"St.Joseph's" : "SaintJoseph's",
	"NCSt." : "NCState",
	"USC" : "SouthernCalifornia",
	"WesternKentucky" : "WesternKy.",
	"Charleston" : "Col.ofCharleston",
	"CalSt.Northridge" : "CSUN",
	"Miami" : "Miami(FL)",
	"CentralFlorida" : "UCF",
	"WesternMichigan" : "WesternMich.",
	"Illinois-Chicago" : "UIC",
    "Purdue-FortWayne" : "PurdueFortWayne",
	"TexasArlington" : "UTArlington",
	"EasternWashington" : "EasternWash.",
	"LouisianaLafayette" : "Louisiana",
	"UMass" : "Massachusetts",
    "UNCWilmington" : "UNCW",
    "StephenF.Austin" : "SFA",
    "St. John's" : "St. John's (NY)",
    "UCSB" : "UCSantaBarbara",
    "FloridaGulfCoast" : "FGCU",
    "Seattle": "SeattleU",
    "St.Peter's" : "SaintPeter's",
    "Loyola(MD)" : "LoyolaMaryland"
}

def add_college_stats_from_hoopmath(df, is_same_team=False):

    hoop_math_stats = []
    
    if is_same_team:
        soup_html = fetch_hoop_math_page_url(df.iloc[0])
        
    for _, row in df.iterrows():
        if (row['Season'] in ['2008-09', '2009-10', '2010-11']):
            hoop_math_stats.append(['']*len(HOOP_MATH_COLUMN_INDEXES))
            continue
        # print("Getting most recent hoop-math stats for " + row['Name'])
        if not is_same_team:
            soup_html = fetch_hoop_math_page_url(row)
        if not soup_html:
            print("ERROR: Unable to connect to hoop-math. Stats will have to be entered in manually.")
            continue
        hoop_math_stats.append(get_hoop_math_data(soup_html, row))
    df = pd.concat([df, pd.DataFrame(hoop_math_stats,index=df.index,columns=HOOP_MATH_COLUMN_NAMES)], axis=1)
    return df

def fetch_hoop_math_page_url(row):
    """Fetches the 247 recruiting rankings for a given dataframe row.

    Args:
        row (int): The DataFrame row, as long as that row has a 'School' and 'Season' column.

    Returns:
        The html of the hoop-math team page for that season.
    """

    team_name_in_url = get_hoop_math_formatted_school(row['School'])
    season_in_url = '20' + row['Season'].split('-')[-1]
    if (int(season_in_url) < 2018 and team_name_in_url == "NCState"):
        team_name_in_url = "NorthCarolinaSt."
    elif (int(season_in_url) < 2018 and team_name_in_url == "SaintMary's(CA)"):
        team_name_in_url = "St.Mary's(CA)"
    elif (int(season_in_url) < 2015 and team_name_in_url == "Louisiana"):
        team_name_in_url = "La.-Lafayette"
    elif (int(season_in_url) < 2019 and team_name_in_url == "UIC"):
        team_name_in_url = "Ill.-Chicago"
    url = 'https://hoop-math.com/' + team_name_in_url + season_in_url + '.php'
    return find_site(url)[0]

def get_hoop_math_formatted_school(name):
    url_name = name.replace(" State", "St.").replace(" ", "")
    return check_value_in_dictionary_of_exceptions(url_name, HOOP_MATH_SCHOOL_EXCEPTIONS, url_name)

def get_hoop_math_data(soup_html, row):
    
    pbp_table = soup_html.find('table', {'id': 'OffTable1'})
    if (pbp_table):
        player_stats = []
        player_found = False
        items = pbp_table.find_all('td')
        for i in range(int(len(items) / HOOP_MATH_TABLE_COLUMN_COUNT)):
            hoop_math_row = items[i*HOOP_MATH_TABLE_COLUMN_COUNT:(i+1)*HOOP_MATH_TABLE_COLUMN_COUNT]
            hoop_math_name = ' '.join(reversed(hoop_math_row[0].getText().strip().split(', ')))
            if(is_fuzzy_name_match(hoop_math_name, row['Name'], HOOP_MATH_NAME_EXCEPTIONS)):
                for i in HOOP_MATH_COLUMN_INDEXES:
                    val = hoop_math_row[i].getText() 
                    if (val == '---'):
                        player_stats.append(0)
                    else:
                        player_stats.append(val.replace('%', ''))
                player_found = True
                break
        if not player_found:
            print(f"ERROR: Could not find hoop-math data for player {row['Name']}")
            return ['']*len(HOOP_MATH_COLUMN_INDEXES)
        else:
            return player_stats
    else:
        print(f"ERROR: Could not find hoop-math site for player {row['Name']}")
        return ['']*len(HOOP_MATH_COLUMN_INDEXES)
