import traceback

class RealGM:
    
    RELEVANT_TABLES = {key: None for key in [
        "NCAA Season Stats - Misc Stats",
        "NCAA Season Stats - Advanced Stats",
        "AAU Stats - Per Game",
        "FIBA Junior Team Events Stats",
        "Non-FIBA Events Stats",
        "NBA Regular Season Stats - Per Game"
    ]}

    RELEVANT_PROFILE_INFO = {key: None for key in [
        "Born:",
        "Height:",
        "Weight:",
        "Pre-Draft",
        "Drafted:"
    ]}
    
    NBA_MIN_INDEX = 4
    HOB_INDEX = 11
    WIN_INDEX = 15
    LOSS_INDEX = 16
    PPR_INDEX = 16

    def __init__(self, soup, url=""):
        self.reset_relevant_info()
        profile_box = soup.find('div', {"class": "profile-box"})
        if not profile_box:
            print(url)
            raise ReferenceError("Page not found.")
        self.position = profile_box.find('h2').find('span').text
        for item in profile_box.find_all('p'):
            info_category = item.text.split(" ")
            if info_category[0] in self.RELEVANT_PROFILE_INFO.keys():
                self.RELEVANT_PROFILE_INFO[info_category[0]] = info_category
        self.image = profile_box.find('img')['src']
        content = soup.find('div', {"class": "profile-wrap"}).find('div', {"class": "section_tabs_content"})
        for div in content.find_all('div', id=lambda x: x and x.startswith("tabs_profile-")):
            h3_elements = div.find_all('h3')
            for i in range(len(h3_elements)):
                h3_text = h3_elements[i].text
                if h3_text == "NCAA Season Stats":
                    self.RELEVANT_TABLES["NCAA Season Stats - Misc Stats"] = div.find('div', {"id": "tabs_ncaa_reg-5"}).find('table')
                    self.RELEVANT_TABLES["NCAA Season Stats - Advanced Stats"] = div.find('div', {"id": "tabs_ncaa_reg-4"}).find('table')
                elif h3_text in self.RELEVANT_TABLES:
                    self.RELEVANT_TABLES[h3_text] = div.find_all('table')[i]

    def get_position(self):
        if self.position == 'G':
            return 'SG/PG'
        if self.position == 'F':
            return 'PF/SF'
        if self.position == 'GF':
            return 'SG/SF'
        if self.position == 'FC':
            return 'PF/C'
        return self.position
    
    def get_birthday(self):
        birthday = self.RELEVANT_PROFILE_INFO.get('Born:')
        if not birthday:
            return None
        return birthday[1:4]
    
    def get_height(self):
        return self.RELEVANT_PROFILE_INFO.get('Height:')[1]
    
    def get_weight(self):
        return self.RELEVANT_PROFILE_INFO.get('Weight:')[1]
    
    def get_class(self):
        grade = self.RELEVANT_PROFILE_INFO.get('Pre-Draft')
        if not grade:
            return None
        return grade[-1].strip('()') + '.'
    
    def get_draft_pick(self):
        pick = self.RELEVANT_PROFILE_INFO.get('Drafted:')
        if (not pick) or (pick[1] == "Undrafted"):
            return 100
        draft_round = int(pick[2].replace(',', ''))
        draft_pick = int(pick[4].replace(',', ''))
        return int((draft_round-1)*30+draft_pick)

    def get_ncaa_hob(self, row_to_get=-1):
        table = self.RELEVANT_TABLES.get("NCAA Season Stats - Misc Stats")
        if not table:
            return None
        
        row = table.find('tbody').find_all('tr')[row_to_get]
        hob = row.find_all('td')[self.HOB_INDEX].text
        try:
            return float(hob)
        except Exception:
            return None
    
    def get_ncaa_win_loss(self, row_to_get=-1):
        table = self.RELEVANT_TABLES.get("NCAA Season Stats - Misc Stats")
        if not table:
            return None, None
        row = table.find('tbody').find_all('tr')[row_to_get]
        win = row.find_all('td')[self.WIN_INDEX].text
        loss = row.find_all('td')[self.LOSS_INDEX].text
        try:
            return int(win), int(loss)
        except Exception as e:
            return None, None
    
    def get_ncaa_ppr(self, row_to_get=-1):
        table = self.RELEVANT_TABLES.get("NCAA Season Stats - Advanced Stats")
        if not table:
            return None
        row = table.find('tbody').find_all('tr')[row_to_get]
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
        num_elems = 22
        table = self.RELEVANT_TABLES.get("FIBA Junior Team Events Stats")
        if not table:
            table = self.RELEVANT_TABLES.get("Non-FIBA Events Stats")
            if not table:
                return None
        
        stats_row = table.find('tfoot').find('tr').find_all('th')
        info_row = table.find('tbody').find('tr').find_all('td')
        international_stats = []
        for i in range(num_elems):
            if i in [0, 2, 21]: # Represents year, event name, place
                international_stats.append(info_row[i].text)
            elif i == 1:
                continue
            else:
                international_stats.append(stats_row[i].text)
        return international_stats
    
    def get_nba_stats(self, row_to_get=-1):
        table = self.RELEVANT_TABLES.get("NBA Regular Season Stats - Per Game")
        if not table:
            return 0
        row = table.find('tfoot').find_all('tr')[row_to_get]
        try:
            return float(row.find_all('td')[self.NBA_MIN_INDEX].text)
        except Exception:
            return 0
        
    def get_image_url(self):
        return "https://basketball.realgm.com" + self.image
    
    def reset_relevant_info(self):
        self.RELEVANT_TABLES = {key: None for key in [
        "NCAA Season Stats - Misc Stats",
        "NCAA Season Stats - Advanced Stats",
        "AAU Stats - Per Game",
        "FIBA Junior Team Events Stats",
        "Non-FIBA Events Stats",
        "NBA Regular Season Stats - Per Game"
    ]}
        self.RELEVANT_PROFILE_INFO = {key: None for key in [
        "Born:",
        "Height:",
        "Weight:",
        "Pre-Draft",
        "Drafted:"
    ]}

import sys
sys.path.insert(0, '../../')
from utils import *

AAU_STATS_TABLE_COLUMNS = ['AAU Season', 'AAU Team', 'AAU League', 'AAU GP', 'AAU GS', 'AAU MIN', 'AAU PTS', 'AAU FGM', 'AAU FGA', 'AAU FG%', 'AAU 3PM', 'AAU 3PA', 'AAU 3P%', 
        'AAU FTM', 'AAU FTA', 'AAU FT%', 'AAU ORB', 'AAU DRB', 'AAU TRB', 'AAU AST', 'AAU STL', 'AAU BLK', 'AAU TOV', 'AAU PF']
    
INTERNATIONAL_STATS_TABLE_COLUMNS = ['Event Year', 'Event Name', 'Event GP', 'Event MIN', 'Event PTS', 'Event FGM', 'Event FGA', 'Event FG%', 'Event 3PM', 'Event 3PA', 'Event 3P%', 
        'Event FTM', 'Event FTA', 'Event FT%', 'Event TRB', 'Event AST', 'Event STL', 'Event BLK', 'Event TOV', 'Event PF', 'Event Placement']

def get_realgm_stats(df, need_profile_info=False, realgm_id=None):
    
    df["RealGM ID"] = ''
    df["Birthday"] = ''
    df["Draft Day Age"] = ''
    df["Draft Pick"] = ''
    df["Hands-On Buckets"] = ''
    df["Wins"] = ''
    df["Losses"] = ''
    df["Pure Point Rating"] = ''
    df["Image Link"] = ""
    
    for col in AAU_STATS_TABLE_COLUMNS:
        df[col] = ''
    for col in INTERNATIONAL_STATS_TABLE_COLUMNS:
        df[col] = ''
        
    for index, row in df.iterrows():
        is_row_data_populated = False
        while not is_row_data_populated:
            summary_index = realgm_id if realgm_id is not None else df.at[index, 'RealGM ID']
            realgm_url = get_url_from_name(row['Name'], summary_index)
            try:
                site, url = find_site(realgm_url)
                player_page = RealGM(site, url)
                df.loc[index, 'RealGM ID'] = url.split("/")[-1]
                populate_stats(df, player_page, index, row)
                if (need_profile_info):
                    populate_profile_info(df, player_page, index)
                is_row_data_populated = True
            except IndexError:
                traceback.print_exc()
                print(f"Dropping {row['Name']}")
                df.drop(index, inplace=True)
                is_row_data_populated = True
            except Exception as e:
                traceback.print_exc()
                print(e)
                realgm_id = input(f"Cannot find player page for {row['Name']}. Can you try manually inputting the RealGM ID? ")
                df.loc[index, 'RealGM ID'] = realgm_id
    return df

def populate_stats(df, player_page, index, row):

    df.loc[index, 'Draft Pick'] = player_page.get_draft_pick()
    birthday = player_page.get_birthday()
    if (birthday):
        df.loc[index, 'Birthday'] = " ".join(birthday)
        draft_day_age = birthday_to_draft_day_age(birthday, get_year_from_season(row['Season']))
        df.loc[index, 'Draft Day Age'] = draft_day_age
    hob = player_page.get_ncaa_hob()
    wins, losses = player_page.get_ncaa_win_loss()
    ppr = player_page.get_ncaa_ppr()
    if (wins == losses == hob == ppr == None): #If last season data is missing, get previous season
        hob = player_page.get_ncaa_hob(-2)
        wins, losses = player_page.get_ncaa_win_loss(-2)
        ppr = player_page.get_ncaa_ppr(-2)
    df.loc[index, 'Hands-On Buckets'] = hob
    df.loc[index, 'Wins'] = wins
    df.loc[index, 'Losses'] = losses
    df.loc[index, 'Pure Point Rating'] = ppr
    aau_stats = player_page.get_aau_stats()
    if aau_stats:
        for i in range(len(aau_stats)):
            df.loc[index, AAU_STATS_TABLE_COLUMNS[i]] = aau_stats[i]
    event_stats = player_page.get_international_stats()
    if event_stats:
        for i in range(len(event_stats)):
            df.loc[index, INTERNATIONAL_STATS_TABLE_COLUMNS[i]] = event_stats[i]   

def populate_profile_info(df, player_page, index):
    df.loc[index, "Position"] = player_page.get_position()
    df.loc[index, "Height"] = player_page.get_height()
    df.loc[index, "Weight"] = player_page.get_weight()
    df.loc[index, "Class"] = player_page.get_class()
    df.loc[index, "Image Link"] = player_page.get_image_url()

def populate_draft_picks(df):
    df["Draft Pick"] = ""
    df["NBA MPG"] = ""
    
    for index, row in df.iterrows():
        summary_index = df.at[index, 'RealGM ID']
        realgm_url = get_url_from_name(row['Name'], summary_index)
        try:
            site, _ = find_site(realgm_url)
            player_page = RealGM(site)
            df.loc[index, 'NBA Draft Pick'] = player_page.get_draft_pick()
            nba_mpg = player_page.get_nba_stats()
            df.loc[index, 'NBA MPG'] = nba_mpg
            print(f"{row['Name']} played {nba_mpg} minutes per game in the NBA.")
        except Exception as e:
            print(e)
    return df

def get_url_from_name(name, summary_index):
    url_name = get_matchable_name(name)
    try: 
        if (not summary_index or summary_index in ERROR_VALUES):
            realgm_url = "https://basketball.realgm.com/search?q=" + url_name.replace(" ", "+")
        else:
            realgm_url = "https://basketball.realgm.com/player/" + url_name.replace(" ", "-") + "/Summary/" + str(summary_index)
    except KeyError:
        realgm_url = "https://basketball.realgm.com/search?q=" + url_name.replace(" ", "+")
    return realgm_url

def populate_image_links(df):
    df["Image Link"] = ""
    
    for index, row in df.iterrows():
        summary_index = df.at[index, 'RealGM ID']
        realgm_url = get_url_from_name(row['Name'], summary_index)
        try:
            site, _ = find_site(realgm_url)
            player_page = RealGM(site)
            img_link = player_page.get_image_url()
            print(img_link)
            df.loc[index, 'Image Link'] = img_link
        except Exception as e:
            print(e)
    
    return df