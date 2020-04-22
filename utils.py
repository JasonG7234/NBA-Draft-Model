import requests
import re
from bs4 import BeautifulSoup

comm = re.compile("<!--|-->")

# Use BeautifulSoup to head to designated URL
# It's very important to decode + sub out all comments! (BasketballReferences' HTML comments throw everything out of wack)
def findSite(url):
	response = requests.get(url)
	html = response.content.decode("utf-8")
	return BeautifulSoup(re.sub("<!--|-->","", html), "html.parser")