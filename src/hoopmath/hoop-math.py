import sys
sys.path.insert(0, '../../')
from utils import *

HOOP_MATH_TABLE_COLUMN_COUNT = 15
INDEXES_OF_HOOP_MATH_COLUMNS = [4, 5, 6, 7, 8, 9, 10, 12]

HOOP_MATH_NAME_EXCEPTIONS = {
	"Kenneth Jr. Lofton" : "Kenneth Lofton Jr.",
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
	"KEVIN JONES" : "Kevin Jones"}

def add_college_stats_from_hoopmath(df):

    hoop_math_stats = []
    
    for _, row in df.iterrows():
        if (row['Season'] in ['2008-09', '2009-10', '2010-11']):
            hoop_math_stats.append(['']*len(INDEXES_OF_HOOP_MATH_COLUMNS))
            continue
        player_stats = []
        print("Getting most recent hoop-math stats for " + row['Name'])
        soup_html = fetch_hoop_math_page_url(row)
        pbp_table = soup_html.find('table', {'id': 'OffTable1'})
        if (pbp_table):
            player_found = False
            items = pbp_table.find_all('td')
            for i in range(int(len(items) / HOOP_MATH_TABLE_COLUMN_COUNT)):
                hoop_math_row = items[i*HOOP_MATH_TABLE_COLUMN_COUNT:(i+1)*HOOP_MATH_TABLE_COLUMN_COUNT]
                hoop_math_name = ' '.join(reversed(hoop_math_row[0].getText().strip().split(', ')))
                if(is_fuzzy_name_match(hoop_math_name, row['Name'], HOOP_MATH_NAME_EXCEPTIONS)):
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
    df = pd.concat([df, pd.DataFrame(hoop_math_stats,index=df.index,columns=HOOP_MATH_COLUMN_NAMES)], axis=1)
        
def fetch_hoop_math_page_url(row):
    """Fetches the 247 recruiting rankings for a given dataframe row.

    Args:
        row (int): The DataFrame row, as long as that row has a 'School' and 'Season' column.

    Returns:
        The html of the hoop-math team page for that season.
    """
    
    team_name_in_url = get_hoop_math_formatted_school(row['School'])
    season_in_url = '20' + row['Season'].split('-')[-1]
    if (int(season_in_url) < 2018 and team_name_in_url == 'NCState'):
        team_name_in_url = "NorthCarolinaSt."
    url = 'https://hoop-math.com/' + team_name_in_url + season_in_url + '.php'
    return find_site(url)