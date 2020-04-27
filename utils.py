import requests
import re
from bs4 import BeautifulSoup
from googlesearch import search
import urllib

comm = re.compile("<!--|-->")

playerExceptions = {
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
    "moe-harkless" : "maurice-harkless",
	"gary-trent" : "gary-trentjr",
	"cameron-reddish" : "cam-reddish",
	"simi-shittu" : "simisola-shittu",
	"kira-lewis" : "kira-lewisjr",
	"rob-gray" : "robert-grayjr",
	"vernon-carey" : "vernon-careyjr",
	"zach-norvell" : "zach-norvelljr",
	"kevin-porter" : "kevin-porterjr",
	"kz-okpala" : "kezie-okpala",
	"ja-morant" : "temetrius-morant",
	"jo-lual-acuil" : "jo-acuil",
	"shake-milton" : "malik-milton",
	"andrew-white" : "andrew-whiteiii",
	"cam-oliver" : "cameron-oliver",
	"bam-adebayo" : "edrice-adebayo",
	"dennis-smith" : "dennis-smithjr",
	"yogi-ferrell" : "kevin-farrell",
	"anthony-barber" : "anthony-cat-barber"
}

indexExceptions = {
    "gary-payton" : 2,
    "kyle-anderson" : 3,
    "thomas-robinson" : 2,
	"josh-green" : 2,
	"nick-richards" : 2,
	"aj-lawson" : 12,
	"reggie-perry" : 2,
	"lonnie-walker" : 2,
	"eric-mika" : 2
}

advancedColumnIDs = ['g','gs','mp','per','ts_pct','efg_pct','fg3a_per_fga_pct','fta_per_fga_pct','pprod','orb_pct','drb_pct','trb_pct','ast_pct',
    'stl_pct','blk_pct','tov_pct','usg_pct','ws-dum','ows','dws','ws','ws_per_40','bpm-dum','obpm','dbpm','bpm']  
    

def findSite(url):
	"""Use BeautifulSoup to head to designated URL and return BeautifulSoup object.
	It's very important to decode + sub out all comments! (Basketball-Reference's HTML comments throw everything out of wack)"""
	
	headers = { 'User-Agent': 'NBA Draft Model Scraper' }
	response = requests.get(url, headers=headers)
	html = response.content.decode("utf-8")
	return BeautifulSoup(re.sub("<!--|-->","", html), "html.parser")

def searchGoogle(query, waitTime):
	"""Go to Google and make a basic search for the provided query, returning the first provided result.
	This is used primarily for searching from Basketball-Reference"""

	try:
		for j in search(query, num=1, stop=1, pause=waitTime, user_agent='NBA Draft Model Scraper'):
			url = j
	except urllib.error.HTTPError:
		return searchGoogle(query, 10)
	return url