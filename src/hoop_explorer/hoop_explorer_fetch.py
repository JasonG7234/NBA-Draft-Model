import sys
sys.path.insert(0, './')
from utils import *

HOOP_EXPLORER_NAME_EXCEPTIONS = {
	"Kenneth Jr. Lofton" : "Kenneth Lofton Jr.",
}

def __get_url_from_season_and_tier(year, tier):
    if (int(year) < 2023):
        return f"https://hoop-explorer.com/leaderboards/lineups/players_all_Men_{year}_{tier}.json"
    else:
        return f"https://hoop-explorer.com/api/getLeaderboard?src=players&oppo=all&gender=Men&year={year}&tier={tier}"

def fetch(season, tier='High'):
    time.sleep(2)
    count = 0
    while count < 3:
        try:
            url = __get_url_from_season_and_tier(season, tier)
            response = requests.get(url, timeout=30)
            #print(response.json())
            return response.json()['players']
        except requests.exceptions.ConnectionError:
            print("Connection error, giving it 10 and retrying")
            time.sleep(10)
            count += 1
        except requests.exceptions.TooManyRedirects:
            print("Redirect error, giving it 10 and then retrying")
            time.sleep(10)
            count += 1
    if not response:
        print('NO RESPONSE')
        return None, None
    return None

def get_hoop_explorer_plus_minus_single_player(df):
    
    df['Adj OFF +/-'] = ""
    df['Adj DEF +/-'] = ""
    
    for index, row in df.iterrows():
        year = row['Season'][:4]
        hoop_explorer_player_data = fetch(year, 'High') + fetch(year, 'Medium') + fetch(year, 'Low')
        for he_player in hoop_explorer_player_data:
            he_player_name = reverse_name(he_player['key'])
            if is_fuzzy_name_match(he_player_name, row['Name'], HOOP_EXPLORER_NAME_EXCEPTIONS, name_match_percentage=95):
                o = he_player['off_adj_rapm']['value']
                d = he_player['def_adj_rapm']['value']
                # pos = player['posFreqs'] While this is probably the best single source of positional data, it still differs from what I'd consider correct NBA positional predictions
                print(f"Found +/- match for {he_player_name}")
                df.loc[index, 'Adj OFF +/-'] = o
                df.loc[index, 'Adj DEF +/-'] = -d
                break
    
    return df
    
def get_hoop_explorer_plus_minus_dataframe():
        
    # Fetch all data from hoop-explorer, so we minimize number of calls made
    data_18 = fetch('2018')
    data_19 = fetch('2019')
    data_20 = fetch('2020', 'High') + fetch('2020', 'Medium') + fetch('2020', 'Low')
    data_21 = fetch('2021', 'High') + fetch('2021', 'Medium') + fetch('2021', 'Low')
    data_22 = fetch('2022', 'High') + fetch('2022', 'Medium') + fetch('2022', 'Low')
    data_23 = fetch('2023', 'High') + fetch('2023', 'Medium') + fetch('2023', 'Low')

    df = get_draft_db_df()

    df['Adj OFF +/-'] = ""
    df['Adj DEF +/-'] = ""

    for index, row in df.iterrows():
        year = row['Season'][:4]
        if int(year) < 2018: # Prior to first year of hoop-explorer data
            continue
        else:
            if int(year) == 2018:
                hoop_explorer_player_data = data_18
            elif int(year) == 2019:
                hoop_explorer_player_data = data_19
            elif int(year) == 2020:
                hoop_explorer_player_data = data_20
            elif int(year) == 2021:
                hoop_explorer_player_data = data_21
            elif int(year) == 2022:
                hoop_explorer_player_data = data_22
            else:
                hoop_explorer_player_data = data_23
                
            for he_player in hoop_explorer_player_data:
                he_player_name = reverse_name(he_player['key'])
                if is_fuzzy_name_match(he_player_name, row['Name'], HOOP_EXPLORER_NAME_EXCEPTIONS, name_match_percentage=95):
                    o = he_player['off_adj_rapm']['value']
                    d = he_player['def_adj_rapm']['value']
                    # pos = player['posFreqs'] While this is probably the best single source of positional data, it still differs from what I'd consider correct NBA positional predictions
                    print(f"Found +/- match for {he_player_name}")
                    df.loc[index, 'Adj OFF +/-'] = o
                    df.loc[index, 'Adj DEF +/-'] = -d
                    break

    df.to_csv('data/draft_db.csv', index=False)

#get_hoop_explorer_plus_minus_dataframe()

