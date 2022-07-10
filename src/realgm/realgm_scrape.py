class RealGM:
    
    RELEVANT_TABLES = {key: None for key in [
        "NCAA Season Stats - Misc Stats",
        "NCAA Season Stats - Advanced Stats",
        "AAU Stats - Per Game",
        "FIBA Junior Team Events Stats",
        "Non-FIBA Events Stats"
    ]}
    HOB_INDEX = 10
    WIN_INDEX = 14
    LOSS_INDEX = 15
    PPR_INDEX = 15

    def __init__(self, soup):
        profile_box = soup.find('div', {"class": "half-column-left"})
        if not profile_box:
            raise ReferenceError("Page not found.")
        for item in profile_box.find_all('p'):
            info_category = item.text.split(" ")[0]
            if "Born:" in info_category:
                self.birthday = item.text
    
        sections = soup.find('div', {"class": "profile-wrap"})
        for section in sections:
            header = section.find('h2')
            if header in self.RELEVANT_TABLES.keys():
                self.RELEVANT_TABLES[header] = section

    
    def get_birthday(self):
        return self.birthday.split(" ")[1:4] if hasattr(self, 'birthday') else None

    def get_ncaa_hob(self):
        table = self.RELEVANT_TABLES.get("NCAA Season Stats - Misc Stats")
        if not table:
            return None
        
        row = table.find('tbody').find_all('tr')[-1]
        hob = row.find_all('td')[self.HOB_INDEX].text
        try:
            return float(hob)
        except Exception:
            return None
    
    def get_ncaa_win_loss(self):
        table = self.RELEVANT_TABLES.get("NCAA Season Stats - Misc Stats")
        if not table:
            return None, None
        row = table.find('tbody').find_all('tr')[-1]
        win = row.find_all('td')[self.WIN_INDEX].text
        loss = row.find_all('td')[self.LOSS_INDEX].text
        try:
            return int(win), int(loss)
        except Exception:
            return None, None
    
    def get_ncaa_ppr(self):
        table = self.RELEVANT_TABLES.get("NCAA Season Stats - Advanced Stats")
        if not table:
            return None
        
        row = table.find('tbody').find_all('tr')[-1]
        ppr = row.find_all('td')[self.PPR_INDEX].text
        try:
            return float(ppr)
        except Exception:
            return None
    
    def get_aau_stats(self):
        table = self.RELEVANT_TABLES.get("AAU Stats - Per Game")
        if not table:
            return ['' * 24]
        
        row = table.find('tbody').find_all('tr')[-1]
        aau_stats = []
        for elem in row.find_all('td'):
            aau_stats.append(elem.text if elem else "")
        return aau_stats
    
    def get_international_stats(self):
        num_elems = 21
        table = self.RELEVANT_TABLES.get("FIBA Junior Team Events Stats")
        if not table:
            table = self.RELEVANT_TABLES.get("Non-FIBA Events Stats")
            if not table:
                return ['' * num_elems]
        
        stats_row = table.find('tfoot').find('tr').find_all('td')
        info_row = table.find('tbody').find('tr').find_all('td')
        international_stats = []
        for i in range(num_elems):
            if i in [0, 1, 20]:
                international_stats.append(info_row[i].text)
            else:
                international_stats.append(stats_row[i].text)
        return international_stats

import sys
sys.path.insert(0, '../../')
from utils import *

def get_realgm_stats(df):
    
    for index, row in df.iterrows():
        summary_index = row['RealGM ID']
        url_name = get_matchable_name(row['Name'])
        print("PLAYER NAME: " + row['Name'])
        if (np.isnan(summary_index)):
            realgm_url = "https://basketball.realgm.com/search?q=" + url_name.replace(" ", "+")
        else:
            print(summary_index)
            continue
        try:
            site, url = find_site(realgm_url)
            summary_id = url[url.rindex('/')+1:]
            print("RealGM ID: " + str(int(summary_id)))
            df.loc[index, 'RealGM ID'] = summary_id
        except Exception:
            print("CANNOT FIND PLAYER PAGE FOR " + row['Name'] + " TRY AGAIN")
    df.to_csv('temp_master', index=False)
    