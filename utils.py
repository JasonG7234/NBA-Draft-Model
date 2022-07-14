import datetime
import re
import requests

import unidecode
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from fuzzywuzzy import fuzz

FIRST_YEAR_OF_DRAFT_RANKINGS = 2009



OVERALL_PLAYER_NAME_EXCEPTIONS = {
	"Moe Harkless" : "Maurice Harkless",
	"TyShon Alexander" : "Ty-Shon Alexander",
	"BJ Boston" : "Brandon Boston Jr.",
	"Chris Johnsonn" : "Chris Johnson",
	"Cameron Reddish" : "Cam Reddish",
	"Cam Oliver" : "Cameron Oliver",
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
	"Khalil Whitney" : "Kahlil Whitney",
	"Oscar da" : "Oscar da Silva",
	"Patrick Baldwin" : "Patrick Baldwin Jr.",
	"Scotty Pippen" : "Scotty Pippen Jr"
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
	"simi-shittu" : "simisola-shittu",
	"kira-lewis" : "kira-lewisjr",
	"stephen-zimmerman" : "stephen-zimmermanjr",
	"roy-devyn" : "roy-devyn-marble",
	"rob-gray" : "robert-grayjr",
	"vernon-carey" : "vernon-careyjr",
	"zach-norvell" : "zach-norvelljr",
	"kz-okpala" : "kezie-okpala",
	"ja-morant" : "temetrius-morant",
	"jo-lual-acuil" : "jo-acuil",
	"michael-porter" : "michael-porterjr",
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
	"obi-toppin" : "obadiah-toppin",
	"duane-washington" : "duane-washingtonjr",
	"mac-mcclung" : "matthew-mcclung",
	"mckinley-wright" : "mckinley-wrightiv",
	"oscar-da-silva" : "oscar-dasilva",
	"johnny-davis" : "jonathan-davis",
	"tyty-washington" : "tyty-washingtonjr",
	"wendell-moore" : "wendell-moorejr",
	"kenneth-lofton" : "kenneth-loftonjr"
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
	"cameron-johnson" : 4,
	"mark-williams" : 7,
	"chris-smith" : 19,
	"tyler-davis" : 5,
	"jalen-johnson" : 24,
	"david-johnson" : 13,
	"jalen-williams" : 13,
	"donovan-williams" : 3,
	"jonathan-davis" : 3
}

COLLEGE_SCHOOL_NAME_EXCEPTIONS = {
	"Central Florida" : "UCF",
	"Illinois-Chicago" : "UIC",
	"Louisiana Lafayette" : "Louisiana",
	"UAB" : "Alabama-Birmingham",
	"Southern Miss." : "Southern Miss",
	"Tennessee-Martin" : "UT-Martin",
	"Texas A&M Corpus Christi" : "Texas A&M-Corpus Christi",
	"UC Santa Barbara" : "UCSB",
	"Texas Arlington" : "UT Arlington"
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

PER_40_COLUMN_IDS = ['fg_per_min', 'fga_per_min', 'fg_pct', 'fg2_per_min', 'fg2a_per_min', 'fg2_pct', 'fg3_per_min', 'fg3a_per_min', 'fg3_pct',
    'ft_per_min','fta_per_min','ft_pct', 'trb_per_min', 'ast_per_min', 'stl_per_min', 'blk_per_min', 'tov_per_min', 'pf_per_min', 'pts_per_min']

PER_100_COLUMN_IDS = ['fg_per_poss', 'fga_per_poss', 'fg2_per_poss', 'fg2a_per_poss', 'fg3_per_poss', 'fg3a_per_poss','ft_per_poss','fta_per_poss',
    'trb_per_poss', 'ast_per_poss', 'stl_per_poss', 'blk_per_poss', 'tov_per_poss', 'pf_per_poss', 'pts_per_poss', 'off_rtg', 'def_rtg']

ADVANCED_COLUMN_IDS = ['g','gs','mp','per','ts_pct','efg_pct','fg3a_per_fga_pct','fta_per_fga_pct','pprod','orb_pct','drb_pct','trb_pct','ast_pct',
    'stl_pct','blk_pct','tov_pct','usg_pct','ws-dum','ows','dws','ws','ws_per_40','bpm-dum','obpm','dbpm','bpm']  
    
COLUMN_NAMES = ['G','GS','MP','PER','TS%','eFG%','3PAr','FTr','PProd','ORB%','DRB%','TRB%','AST%',
    'STL%','BLK%','TOV%','USG%','OWS','DWS','WS','WS/40','OBPM','DBPM','BPM','FG/40', 'FGA/40', 'FG%', '2FGM/40', '2FGA/40', '2FG%', '3FGM/40', '3FGA/40', '3FG%',
    'FT/40','FTA/40','FT%', 'TRB/40', 'AST/40', 'STL/40', 'BLK/40', 'TOV/40', 'PF/40', 'PTS/40', 'FGM/100Poss', 'FGA/100Poss', '2FGM/100Poss', '2FGA/100Poss', '3FGM/100Poss', '3FGA/100Poss','FT/100Poss','FTA/100Poss',
    'TRB/100Poss', 'AST/100Poss', 'STL/100Poss', 'BLK/100Poss', 'TOV/100Poss', 'PF/100Poss', 'PTS/100Poss', 'OFF RTG', 'DEF RTG', 'ATS/TOV', 'SOS', 'Conference']

HOOP_MATH_COLUMN_NAMES = ['% Shots @ Rim', 'FG% @ Rim', '%Astd @ Rim', '% Shots @ Mid', 'FG% @ Mid', '%Astd @ Mid', '% Shots @ 3', '%Astd @ 3']

LOG_REG_COLUMNS = ['Height','RSCI','Class','TS%','3PAr','TRB%','AST%','BLK%','STL%','WS/40','AST/TOV']

USER_AGENT = "Mozilla/5.0 (Android 4.4; Mobile; rv:41.0) Gecko/41.0 Firefox/41.0"
HEADERS = { 'User-Agent': USER_AGENT}

ERROR_VALUES = [None, np.nan, '', '-', '-%']

def find_site(url):
	"""Use BeautifulSoup to head to designated URL and return BeautifulSoup object.
	It's very important to decode + sub out all comments! (Basketball-Reference's HTML comments throw everything out of wack)"""
	
	response = requests.get(url, headers=HEADERS)
	try: 
		html = response.content.decode("utf-8")
	except UnicodeDecodeError:
		html = response.content.decode("latin-1")
	return BeautifulSoup(re.sub("<!--|-->","", html), "html.parser"), response.url

def birthday_to_draft_day_age(birthday, season):
	dt = datetime.datetime.strptime(' '.join(birthday), "%b %d, %Y")
	draft_date = datetime.datetime.strptime(f"Jun 25, {season}", "%b %d, %Y")
	return round((draft_date - dt).days / 365, 2)

def check_value_in_dictionary_of_exceptions(name, exceptions_dict, default):
    """Performs a dictionary lookup to try to map the player's name/school to the correct Basketball-Reference page."""
    return exceptions_dict.get(name, default)

def get_basketball_reference_player_info(soup):
	player_info =  soup.find('div', {'id': 'meta'})
	if (not player_info): return None
	return unidecode.unidecode(player_info.getText())

def is_fuzzy_name_match(data_name, csv_name, name_exception_dict, name_match_percentage=90):
    exception_name = check_value_in_dictionary_of_exceptions(data_name, name_exception_dict, data_name)
    ratio = fuzz.partial_ratio(csv_name, exception_name.replace('.', '').replace("'", ''), )
    return True if ratio >= name_match_percentage else False
		
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

def get_matchable_name(name):
    return name.replace("'", '').replace('.', '').replace('-', ' ').lower()

def get_season_from_year(year):
	return str(year-1) + "-" + str(year)[2:4]

def get_year_from_season(season):
    return int(season[:4])+1

def update_position_columns(df):
    if 'Position 1' in df and 'Position 2' in df:
        return df
    else:
        df['Position 2'] = ''
        for index, row in df.iterrows():
            positions = re.split('/|-', df.at[index, 'Position'])
            df.loc[index, 'Position'] = positions[0]
            if (len(positions) == 2):
                df.loc[index, 'Position 2'] = positions[1]
        df = df.rename(columns = {'Position' : 'Position 1'})
    return df

def reorder_final_columns(main):
    return main[['RealGM ID','Season','Name',
                'Position 1','Position 2',
                'School','Conference','Wins','Losses','SOS',
                'Class','Birthday','Draft Day Age',
                'Height','Weight','Height w/o Shoes','Height w/ Shoes','Wingspan','Standing Reach','Body Fat %','Hand Length','Hand Width',
                'RSCI','G','GS','MP','PER','TS%','eFG%','3PAr','FTr','PProd','ORB%','DRB%','TRB%','AST%','STL%','BLK%','TOV%','USG%','OWS','DWS','WS','WS/40','OBPM','DBPM','BPM','ATS/TOV','OFF RTG','DEF RTG','Hands-On Buckets','Pure Point Rating',
                'FG/40','FGA/40','FG%','2FGM/40','2FGA/40','2FG%','3FGM/40','3FGA/40','3FG%','FT/40','FTA/40','FT%','TRB/40','AST/40','STL/40','BLK/40','TOV/40','PF/40','PTS/40',
                'FGM/100Poss','FGA/100Poss','2FGM/100Poss','2FGA/100Poss','3FGM/100Poss','3FGA/100Poss','FT/100Poss','FTA/100Poss','TRB/100Poss','AST/100Poss','STL/100Poss','BLK/100Poss','TOV/100Poss','PF/100Poss','PTS/100Poss','FGA/100Poss',
                '# Dunks','% Shots @ Rim','FG% @ Rim','%Astd @ Rim','% Shots @ Mid','FG% @ Mid','%Astd @ Mid','% Shots @ 3','%Astd @ 3',
                'AAU Season','AAU Team','AAU League','AAU GP','AAU GS','AAU MIN','AAU PTS','AAU FGM','AAU FGA','AAU FG%','AAU 3PM','AAU 3PA','AAU 3P%','AAU FTM','AAU FTA','AAU FT%','AAU ORB','AAU DRB','AAU TRB','AAU AST','AAU STL','AAU BLK','AAU TOV','AAU PF',
                'Event Year','Event Name','Event GP','Event MIN','Event PTS','Event FGM','Event FGA','Event FG%','Event 3PM','Event 3PA','Event 3P%','Event FTM','Event FTA','Event FT%','Event TRB','Event AST','Event STL','Event BLK','Event TOV','Event PF','Event Placement'
                ]]

def draw_conclusions_on_column(df, col_name, num_top=5):
    print(f"The top {str(num_top)} highest values of column {col_name} are: ")
    for _, row in df.nlargest(num_top, [col_name]).iterrows():
        print(f"{row['Name']}: {row[col_name]}")
    
    print('=========================================')
    print(f"The top {str(num_top)} lowest values of column {col_name} are: ")
    for _, row in df.nsmallest(num_top, [col_name]).iterrows():
        print(f"{row['Name']}: {row[col_name]}")
    
    print('=========================================')    
    print(f"The average value of column {col_name} is: {df[col_name].mean()}")
    print(f"The median value of column {col_name} is: {df[col_name].median()}")

def print_dataframe(df):
	with pd.option_context('display.max_rows', None, 'display.max_columns', None):
		print(df)

def populate_dataframe_with_average_values(df):
    df = df.replace('', np.nan)
    return df.fillna(df.mean())