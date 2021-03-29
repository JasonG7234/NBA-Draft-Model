import datetime
import re
import requests
import string
import urllib

import unidecode
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from sklearn import metrics

comm = re.compile("<!--|-->")
pattern = re.compile('[\W_]+')

OVERALL_PLAYER_NAME_EXCEPTIONS = {
	"Moe Harkless" : "Maurice Harkless",
	"TyShon Alexander" : "Ty-Shon Alexander",
	"BJ Boston" : "Brandon Boston",
	"Chris Johnsonn" : "Chris Johnson",
	"Cameron Reddish" : "Cam Reddish",
	"James McAdoo" : "James Michael McAdoo",
	"Cam Long" : "Cameron Long",
	"Simi Shittu" : "Simisola Shittu",
	"Kevin Porter" : "Kevin Porter Jr.",
	"Herbert Jones" : "Herb Jones",
	"Ron Harper" : "Ron Harper Jr.",
	"Gary Trent" : "Gary Trent Jr.",
	"Dennis Smith" : "Dennis Smith Jr.",
	"Tashawn Thomas" : "TaShawn Thomas",
	"DeShaun Thomas" : "Deshaun Thomas",
	"Glen Rice" : "Glen Rice Jr."
}

OVERALL_PLAYER_SCHOOL_EXCEPTIONS = {
	"PJ Hairston" : "UNC",
    "Glen Rice" : "Georgia Tech",
    "Nick Barbour" : "High Point",
	"Charlie Westbrook" : "South Dakota"
}

OVERALL_SCHOOL_NAME_EXCEPTIONS = {
	"St. Mary's" : "Saint Mary's", 
	"Massachusetts" : "UMass",
	"North Carolina" : "UNC",
	"Pittsburgh" : "Pitt",
	"St. Johns" : "St. John's (NY)",
	"Cal St. Northridge" : "Cal State Northridge",
	"Mississippi" : "Ole Miss"
}

COMMON_NAMES = [
	"Tony Mitchell",
	"Justin Jackson",
	"Mike Davis",
	"Michael Porter",
	"Chris Johnson",
	"Anthony Davis",
	"Marcus Johnson",
	"Josh Carter",
	"Mike Scott",
	"Chris Wright",
	"Gary Clark",
	"Chris Smith",
	"James Johnson",
	"Marcus Thornton"
]

OVERALL_RSCI_EXCEPTIONS = {
	"Marcus Johnson" : 51,
	"Zach Norvell" : 103,
	"Vince Edwards" : 121,
	"James Blackmon" : 20,
	"Andrew White" : 54,
	"Justin Jackson" : 9,
	"Caris LeVert" : 239,
	"Tu Holloway" : 181,
	"Jeff Allen" : 83,
	"Anthony Davis" : 1,
	"Darington Hobson" : 146,
	"Manny Harris" : 37,
	"DeSean Butler" : 107,
	"Tiny Gallon" : 10,
	"Dar Tucker" : 46,
	"Jeffery Taylor" : 48,
	"Raymond Spalding" : 42
}

COLLEGE_PLAYER_NAME_EXCEPTIONS = {
    "wendell-carter" : "wendell-carterjr",
    "marvin-bagley" : "marvin-bagleyiii",
	"trey-murphy" : "trey-murphyiii",
    "fuquan-edwin" : "edwin-fuquan",
    "derrick-jones" : "derrick-jonesjr",
	"brandon-boston" : "brandon-bostonjr",
    "jaren-jackson" : "jaren-jacksonjr",
    "james-mcadoo" : "james-michael-mcadoo",
    "glen-rice" : "glen-rice-jr",
    "tim-hardaway" : "tim-hardaway-jr",
    "tu-holloway" : "terrell-holloway",
    "bernard-james" : "bernard-james-",
	"gary-trent-jr" : "gary-trentjr",
	"simi-shittu" : "simisola-shittu",
	"kira-lewis" : "kira-lewisjr",
	"stephen-zimmerman" : "stephen-zimmermanjr",
	"roy-devyn" : "roy-devyn-marble",
	"rob-gray" : "robert-grayjr",
	"vernon-carey" : "vernon-careyjr",
	"zach-norvell" : "zach-norvelljr",
	"kevin-porter-jr" : "kevin-porterjr",
	"kz-okpala" : "kezie-okpala",
	"ja-morant" : "temetrius-morant",
	"jo-lual-acuil" : "jo-acuil",
	"shake-milton" : "malik-milton",
	"andrew-white" : "andrew-whiteiii",
	"wesley-johnson" : "wes-johnson",
	"cam-oliver" : "cameron-oliver",
	"bam-adebayo" : "edrice-adebayo",
	"dennis-smith" : "dennis-smithjr",
	"yogi-ferrell" : "kevin-ferrell",
	"anthony-barber" : "anthony-cat-barber",
	"christ-koumadje" : "jeanmarc-koumadje",
	"dewan-hernandez" : "dewan-huell",
	"dez-wells" : "dezmine-wells",
	"bryce-dejean-jones" : "bryce-jones",
	"ronald-roberts" : "ronald-roberts-",
	"ed-daniel" : "edward-daniel",
	"cam-long" : "cameron-long",
	"art-parakhouski" : "artsiom-parakhouski",
	"landers-nolley" : "landers-nolleyii",
	"terrence-shannon" : "terrence-shannonjr",
	"obi-toppin" : "obadiah-toppin"
}

COLLEGE_INDEX_EXCEPTIONS = {
	"anthony-lamb" : 2,
	"kristian-doolittle" : 2,
	"paul-reed" : 5,
    "gary-payton" : 2,
    "kyle-anderson" : 3,
    "thomas-robinson" : 2,
	"josh-green" : 2,
	"nick-richards" : 2,
	"aj-lawson" : 12,
	"reggie-perry" : 2,
	"robert-woodard" : 2,
	"greg-brown" : 9,
	"lonnie-walker" : 2,
	"anthony-davis" : 5,
	"chris-walker" : 6,
  	"eric-mika" : 2,
	"troy-brown" : 5,
	"charlie-brown" : 2,
	"rodney-williams" : 3,
	"mark-williams" : 7,
	"chris-smith" : 19,
	"jalen-johnson" : 24
}

COLLEGE_SCHOOL_NAME_EXCEPTIONS = {
	"Central Florida" : "UCF",
	"Illinois-Chicago" : "UIC",
	"Louisiana Lafayette" : "Louisiana",
	"UAB" : "Alabama-Birmingham",
	"Southern Miss." : "Southern Miss",
	"Tennessee-Martin" : "UT-Martin",
	"Texas A&M Corpus Christi" : "Texas A&M-Corpus Christi",
}

NBA_PLAYER_NAME_EXCEPTIONS = {
	"BJ Mullens" : "Byron Mullens",
	"Patrick Mills" : "Patty Mills",
	"Jeffery Taylor" : "Jeff Taylor",
	"Jahmius Ramsey" : "Jahmi'us Ramsey",
	"Simi Shittu" : "Simisola Shittu",
	"Mohamed Bamba" : "Mo Bamba",
	"Raymond Spalding" : "Ray Spalding",
	"Joseph Young" : "Joe Young",
	"Kahlil Felder" : "Kay Felder"
}

NBA_INDEX_EXCEPTIONS = {
	"Alan Williams" : 3,
	"Derrick Brown" : 4,
	"Darius Johnson-Odom" : 3,
	"Brandon Knight" : 3,
	"Marcus Morris" : 3,
	"Dennis Smith Jr" : 3,
	"Chris Johnson" : 3,
	"Robert Williams" : 4,
	"Jeff Taylor" : 3,
	"Kenrich Williams" : 4,
	"Johnathan Williams" : 4,
	"Keldon Johnson" : 4,
	"Andre Roberson" : 3,
	"Damian Jones" : 3,
	"Stanley Johnson" : 4
}

NBA_SCHOOL_NAME_EXCEPTIONS = {
	"Louisiana Lafayette" : "LA-Lafayette",
	"VCU" : "Virginia Commonwealth",
	"Long Beach State" : "Cal State Long Beach",
	"Tennessee-Martin" : "University of Tennessee at Martin",
	"UCSB" : "UC Santa Barbara",
	"Illinois-Chicago" : "University of Illinois at Chicago",
	"UAB" : "University of Alabama at Birmingham",
	"Southern Miss." : "University of Southern Mississippi",
	"St. Johns" : "St. John's"
}

ADVANCED_COLUMN_IDS = ['g','gs','mp','per','ts_pct','efg_pct','fg3a_per_fga_pct','fta_per_fga_pct','pprod','orb_pct','drb_pct','trb_pct','ast_pct',
    'stl_pct','blk_pct','tov_pct','usg_pct','ws-dum','ows','dws','ws','ws_per_40','bpm-dum','obpm','dbpm','bpm']  
    
COLUMN_NAMES = ['G','GS','MP','PER','TS%','eFG%','3PAr','FTr','PProd','ORB%','DRB%','TRB%','AST%',
                    'STL%','BLK%','TOV%','USG%','OWS','DWS','WS','WS/40','OBPM','DBPM','BPM', 'ORTG', 'DRTG', 'AST/TOV']

LOG_REG_COLUMNS = ['Height','RSCI','Class','TS%','3PAr','TRB%','AST%','BLK%','STL%','WS/40','AST/TOV']

USER_AGENT = "Mozilla/5.0 (Android 4.4; Mobile; rv:41.0) Gecko/41.0 Firefox/41.0"
HEADERS = { 'User-Agent': USER_AGENT}

def find_site(url):
	"""Use BeautifulSoup to head to designated URL and return BeautifulSoup object.
	It's very important to decode + sub out all comments! (Basketball-Reference's HTML comments throw everything out of wack)"""
	
	response = requests.get(url, headers=HEADERS)
	try: 
		html = response.content.decode("utf-8")
	except UnicodeDecodeError:
		html = response.content.decode("latin-1")
	return BeautifulSoup(re.sub("<!--|-->","", html), "html.parser")

def check_value_in_dictionary_of_exceptions(name, exceptions_dict, default):
    """Performs a dictionary lookup to try to map the player's name/school to the correct Basketball-Reference page."""
    return exceptions_dict.get(name, default)

def get_csv_file(objective):
    while True:
        file_name = input("What csv file would you like to " + objective).strip()
        try:
            master = pd.read_csv(file_name)
        except FileNotFoundError:
            print("ERROR - File not found. Please try again.")
            continue
        return master

def get_basketball_reference_player_info(soup):
	player_info =  soup.find('div', {'itemtype': 'https://schema.org/Person'})
	if (not player_info): return None
	return unidecode.unidecode(player_info.getText())
		
def get_basketball_reference_formatted_school(school, exceptions, default):
	return check_value_in_dictionary_of_exceptions(school, exceptions, default)

def get_basketball_reference_formatted_name(name, exceptions):
	return remove_non_alphabetic_characters(check_value_in_dictionary_of_exceptions(name, exceptions, name))

def get_basketball_reference_formatted_url(name):
	url_name = name.replace("'", "").replace(".", "").replace(" ", "-").lower()
	return check_value_in_dictionary_of_exceptions(url_name, COLLEGE_PLAYER_NAME_EXCEPTIONS, url_name)

def remove_non_alphabetic_characters(name):
	return unidecode.unidecode(re.sub(r'[^A-Za-z- ]+', '', name))

def get_current_year():
	return datetime.datetime.now().year

def get_season_from_year(year):
	return str(year-1) + "-" + str(year)[2:4]

def reorder_columns(master):
    cols_to_order = ['Name', 'Season']
    new_columns = cols_to_order + (master.columns.drop(cols_to_order).tolist())
    return master[new_columns]

def populate_dataframe_with_average_values(df):
    df = df.replace('', np.nan)
    return df.fillna(df.mean())

def is_nba_player(player):
	is_recent_season = int(player['Season'][0:4]) >= get_current_year() - 3
	games_played = int(player['NBA GP'])
	minutes_played = float(player['NBA MPG'])
	if (is_recent_season):
		if (games_played >= 82): 
			return float(1)
		if (games_played >= 41 and minutes_played >= 12): 
			return float(1)
		return float(0)
	else:
		if (games_played >= 123): 
			return float(1)
		if (games_played >= 82 and minutes_played >= 18): 
			return float(1)
		return float(0)

def make_predictions_for_upcoming_nba_prospects(logreg, prospects, row_name, is_round):
    predictions = logreg.predict(prospects[LOG_REG_COLUMNS])
    prospects[row_name] = predictions.tolist() if is_round else predictions
