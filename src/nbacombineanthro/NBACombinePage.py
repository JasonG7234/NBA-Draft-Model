import re
import requests
from bs4 import BeautifulSoup

class NBACombinePage:
    
    def __init__(self, url):
        html = self.find_site(url)
        self.table = html.find('table')
        self.rows = self.table.find_all('tr')
        self.values = [elem.getText() for elem in [row for row in self.rows]]
        
    def get_table(self):
        return self.table
    
    def get_rows(self):
        return self.rows
    
    def get_table_values(self):
        print(self.values)
        return self.values
        
    def find_site(self, url):
        """Use BeautifulSoup to head to designated URL and return BeautifulSoup object.
        It's very important to decode + sub out all comments! (Basketball-Reference's HTML comments throw everything out of wack)"""
	
        response = requests.get(url)
        try: 
            html = response.content.decode("utf-8")
        except UnicodeDecodeError:
            html = response.content.decode("latin-1")
        return BeautifulSoup(re.sub("<!--|-->","", html), "html.parser")
    
    