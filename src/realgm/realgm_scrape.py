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
        self.reset_relevant_tables()
        profile_box = soup.find('div', {"class": "half-column-left"})
        if not profile_box:
            raise ReferenceError("Page not found.")
        for item in profile_box.find_all('p'):
            info_category = item.text.split(" ")[0]
            if "Born:" in info_category:
                self.birthday = item.text
        content = soup.find('div', {"class": "profile-wrap"})
        headers = content.find_all('h2')
        for i, header in enumerate(headers):
            if header.text in self.RELEVANT_TABLES.keys():
                table = content.find_all('table')[i]
                self.RELEVANT_TABLES[header.text] = table

    
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
        except Exception as e:
            print(e)
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
            return None
        
        rows = table.find('tbody').find_all('tr')
        aau_stats = []
        for i, elem in enumerate(rows[0].find_all('td')):
            if (i == 1 and elem.text == 'All Teams'):
                # When the player played for multiple AAU teams, make sure to add a name for one of them
                aau_stats.append(rows[-1].find_all('td')[1].text)
            else:
                aau_stats.append(elem.text if elem else "")
        return aau_stats
    
    def get_international_stats(self):
        num_elems = 21
        table = self.RELEVANT_TABLES.get("FIBA Junior Team Events Stats")
        if not table:
            table = self.RELEVANT_TABLES.get("Non-FIBA Events Stats")
            if not table:
                return None
        
        stats_row = table.find('tfoot').find('tr').find_all('td')
        info_row = table.find('tbody').find('tr').find_all('td')
        international_stats = []
        for i in range(num_elems):
            if i in [0, 1, 20]:
                international_stats.append(info_row[i].text)
            else:
                international_stats.append(stats_row[i].text)
        return international_stats
    
    def reset_relevant_tables(self):
        self.RELEVANT_TABLES = {key: None for key in [
        "NCAA Season Stats - Misc Stats",
        "NCAA Season Stats - Advanced Stats",
        "AAU Stats - Per Game",
        "FIBA Junior Team Events Stats",
        "Non-FIBA Events Stats"
    ]}

import sys
sys.path.insert(0, '../../')
from utils import *

def get_realgm_stats(df):
    
    AAU_STATS_TABLE_COLUMNS = ['AAU Season', 'AAU Team', 'AAU League', 'AAU GP', 'AAU GS', 'AAU MIN', 'AAU PTS', 'AAU FGM', 'AAU FGA', 'AAU FG%', 'AAU 3PM', 'AAU 3PA', 'AAU 3P%', 
        'AAU FTM', 'AAU FTA', 'AAU FT%', 'AAU ORB', 'AAU DRB', 'AAU TRB', 'AAU AST', 'AAU STL', 'AAU BLK', 'AAU TOV', 'AAU PF']
    
    INTERNATIONAL_STATS_TABLE_COLUMNS = ['Event Year', 'Event Name', 'Event GP', 'Event MIN', 'Event PTS', 'Event FGM', 'Event FGA', 'Event FG%', 'Event 3PM', 'Event 3PA', 'Event 3P%', 
        'Event FTM', 'Event FTA', 'Event FT%', 'Event TRB', 'Event AST', 'Event STL', 'Event BLK', 'Event TOV', 'Event PF', 'Event Placement']
    
    df["Birthday"] = ''
    df["Draft Day Age"] = ''
    df["Hands-On Buckets"] = ''
    df["Wins"] = ''
    df["Losses"] = ''
    df["Pure Point Rating"] = ''
    for index, row in df.iterrows():
        summary_index = row['RealGM ID']
        url_name = get_matchable_name(row['Name'])
        print("PLAYER NAME: " + row['Name'])
        if (np.isnan(summary_index)):
            realgm_url = "https://basketball.realgm.com/search?q=" + url_name.replace(" ", "+")
        else:
            realgm_url = "https://basketball.realgm.com/player/" + url_name.replace(" ", "-") + "/Summary/" + str(summary_index)
        try:
            site, url = find_site(realgm_url)
            player_page = RealGM(site)
            birthday = player_page.get_birthday()
            if (birthday):
                print(birthday)
                df.loc[index, 'Birthday'] = " ".join(birthday)
                draft_day_age = birthday_to_draft_day_age(birthday, get_year_from_season(row['Season']))
                print(draft_day_age)
                df.loc[index, 'Draft Day Age'] = draft_day_age
            hob = player_page.get_ncaa_hob()
            print(hob)
            df.loc[index, 'Hands-On Buckets'] = hob
            wins, losses = player_page.get_ncaa_win_loss()
            print(f"{str(wins)}/{str(losses)}")
            df.loc[index, 'Wins'] = wins
            df.loc[index, 'Losses'] = losses
            ppr = player_page.get_ncaa_ppr()
            print(ppr)
            df.loc[index, 'Pure Point Rating'] = ppr
            aau_stats = player_page.get_aau_stats()
            if aau_stats:
                print(aau_stats)
                for i in range(len(aau_stats)):
                    df.loc[index, AAU_STATS_TABLE_COLUMNS[i]] = aau_stats[i]
            event_stats = player_page.get_international_stats()
            if event_stats:
                print(event_stats)
                for i in range(len(event_stats)):
                    df.loc[index, INTERNATIONAL_STATS_TABLE_COLUMNS[i]] = event_stats[i]
        except Exception as e:
            print(e)
        
    df.to_csv('temp_master.csv', index=False)
    