import datetime
import re
import requests
import string
import unidecode
import urllib
import pandas as pd
from bs4 import BeautifulSoup
from googlesearch import search

comm = re.compile("<!--|-->")
pattern = re.compile('[\W_]+')

OVERALL_NAME_EXCEPTIONS = {
	"Moe Harkless" : "Maurice Harkless",
	"Cameron Reddish" : "Cam Reddish",
	"James McAdoo" : "James Michael McAdoo",
	"Cam Long" : "Cameron Long",
	"Simi Shittu" : "Simisola Shittu",
	"Kevin Porter" : "Kevin Porter Jr.",
	"Gary Trent" : "Gary Trent Jr.",
	"Dennis Smith" : "Dennis Smith Jr.",
	"Tashawn Thomas" : "TaShawn Thomas",
	"DeShaun Thomas" : "Deshaun Thomas",
	"Glen Rice" : "Glen Rice Jr."
}

OVERALL_COLLEGE_EXCEPTIONS = {
	"PJ Hairston" : "UNC",
    "Glen Rice" : "Georgia Tech",
    "Nick Barbour" : "High Point",
	"Charlie Westbrook" : "South Dakota"
}

OVERALL_SCHOOL_EXCEPTIONS = {
	"St. Mary's" : "Saint Mary's", 
	"Massachusetts" : "UMass",
	"North Carolina" : "UNC",
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
	"Darington Hobson" : 146,
	"Manny Harris" : 37,
	"DeSean Butler" : 107,
	"Tiny Gallon" : 10,
	"Dar Tucker" : 46,
	"Jeffery Taylor" : 48,
	"Raymond Spalding" : 42
}

COLLEGE_NAME_EXCEPTIONS = {
    "wendell-carter" : "wendell-carterjr",
    "marvin-bagley" : "marvin-bagleyiii",
    "fuquan-edwin" : "edwin-fuquan",
    "derrick-jones" : "derrick-jonesjr",
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
	"yogi-ferrell" : "kevin-farrell",
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
    "gary-payton" : 2,
    "kyle-anderson" : 3,
    "thomas-robinson" : 2,
	"josh-green" : 2,
	"nick-richards" : 2,
	"aj-lawson" : 12,
	"reggie-perry" : 2,
	"lonnie-walker" : 2,
	"chris-walker" : 6,
  	"eric-mika" : 2,
	"charlie-brown" : 2,
	"rodney-williams" : 3,
	"chris-smith" : 19
}

COLLEGE_SCHOOL_EXCEPTIONS = {
	"Central Florida" : "UCF",
	"Illinois-Chicago" : "UIC",
	"Louisiana Lafayette" : "Louisiana",
	"UAB" : "Alabama-Birmingham",
	"Southern Miss." : "Southern Miss",
	"Tennessee-Martin" : "UT-Martin",
	"Texas A&M Corpus Christi" : "Texas A&M-Corpus Christi",
}

NBA_NAME_EXCEPTIONS = {
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

NBA_SCHOOL_EXCEPTIONS = {
	"Louisiana Lafayette" : "LA-Lafayette",
	"VCU" : "Virginia Commonwealth",
	"Long Beach State" : "Cal State Long Beach",
	"Tennessee-Martin" : "University of Tennessee at Martin",
	"UCSB" : "UC Santa Barbara",
	"Illinois-Chicago" : "University of Illinois at Chicago",
	"UAB" : "University of Alabama at Birmingham",
	"Southern Miss." : "University of Southern Mississippi",
	"Pittsburgh" : "Pitt",
	"St. Johns" : "St. John's"
}

ADVANCED_COLUMN_IDS = ['g','gs','mp','per','ts_pct','efg_pct','fg3a_per_fga_pct','fta_per_fga_pct','pprod','orb_pct','drb_pct','trb_pct','ast_pct',
    'stl_pct','blk_pct','tov_pct','usg_pct','ws-dum','ows','dws','ws','ws_per_40','bpm-dum','obpm','dbpm','bpm']  
    
COLUMN_NAMES = ['G','GS','MP','PER','TS%','eFG%','3PAr','FTr','PProd','ORB%','DRB%','TRB%','AST%',
                    'STL%','BLK%','TOV%','USG%','OWS','DWS','WS','WS/40','OBPM','DBPM','BPM', 'ORTG', 'DRTG', 'AST/TOV']

LOG_REG_COLUMNS = ['TS%','eFG%','3PAr','FTr','TRB%','AST%','BLK%','TOV%','USG%','OWS','DWS','WS','WS/40','AST/TOV']

USER_AGENT = "Mozilla/5.0 (Android 4.4; Mobile; rv:41.0) Gecko/41.0 Firefox/41.0"
HEADERS = { 'User-Agent': USER_AGENT}

def findSite(url):
	"""Use BeautifulSoup to head to designated URL and return BeautifulSoup object.
	It's very important to decode + sub out all comments! (Basketball-Reference's HTML comments throw everything out of wack)"""
	
	response = requests.get(url, headers=HEADERS)
	html = response.content.decode("utf-8")
	return BeautifulSoup(re.sub("<!--|-->","", html), "html.parser")

def searchGoogle(query, waitTime, index):
	"""Go to Google and make a basic search for the provided query, returning the first provided result.
	This is used primarily for replacing bad site-specific search bars"""
	
	try:
		for j in search(query, num=1, stop=1, pause=waitTime, user_agent=USER_AGENT):
			return j
	except urllib.error.HTTPError:
		return searchGoogle(query, 10 * (index + 1))

def checkValueInDictOfExceptions(name, exceptionsDict, default):
    """Performs a dictionary lookup to try to map the player's name/school to the correct Basketball-Reference page."""
    return exceptionsDict.get(name, default)

def getCSVFile(objective):
    while True:
        file_name = input("What csv file would you like to " + objective).strip()
        try:
            master = pd.read_csv(file_name)
        except FileNotFoundError:
            print("ERROR - File not found. Please try again.")
            continue
        return master

def getBasketballReferencePlayerInfo(soup):
	playerInfo =  soup.find('div', {'itemtype': 'https://schema.org/Person'})
	if (not playerInfo): return None
	return unidecode.unidecode(playerInfo.getText())
		
def getBasketballReferenceFormattedSchool(school, exceptions, default):
	return checkValueInDictOfExceptions(school, exceptions, default)

def getBasketballReferenceFormattedName(name, exceptions):
	return removeCharactersThatWouldNotBeInAName(checkValueInDictOfExceptions(name, exceptions, name))

def getBasketballReferenceFormattedURL(name):
	urlName = name.replace("'", "").replace(".", "").replace(" ", "-").lower() # Translate player name to how it would appear in the URL
	return checkValueInDictOfExceptions(urlName, COLLEGE_NAME_EXCEPTIONS, urlName)

def removeCharactersThatWouldNotBeInAName(name):
	return unidecode.unidecode(re.sub(r'[^A-Za-z- ]+', '', name))

def getCurrentYear():
	return datetime.datetime.now().year

def getSeasonFromYear(year):
	return str(year-1) + "-" + str(year)[2:4]

def isNBAPlayer(player):
	isRecentSeason = int(player['Season'][0:4]) >= getCurrentYear() - 3
	gamesPlayed = int(player['NBA GP'])
	minutesPlayed = float(player['NBA MPG'])
	if (isRecentSeason):
		if (gamesPlayed >= 82): 
			return 1
		if (gamesPlayed >= 41 and minutesPlayed >= 12): 
			return 1
		return 0
	else:
		if (gamesPlayed >= 123): 
			return 1
		if (gamesPlayed >= 82 and minutesPlayed >= 18): 
			return 1
		return 0
