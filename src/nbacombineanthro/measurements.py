from nba_api.stats.endpoints import draftcombineplayeranthro

from fuzzywuzzy import fuzz

def get_NBA_Combine_measurements(df):
    tmp = df.sort_values(by=['Season'])
    for season in set(tmp['Season']):
        combine_data = draftcombineplayeranthro.DraftCombinePlayerAnthro(
            league_id='00', 
            season_year=season,
            headers={'Accept': 'application/json, text/plain, */*',
'Accept-Encoding': 'gzip, deflate, br',
'Accept-Language': 'en-US,en;q=0.9',
'Connection': 'keep-alive',
'Host': 'stats.nba.com',
'Origin': 'https://www.nba.com',
'Referer': 'https://www.nba.com/',
'sec-ch-ua': '"Google Chrome";v="87", "\"Not;A\\Brand";v="99", "Chromium";v="87"',
'sec-ch-ua-mobile': '?1',
'Sec-Fetch-Dest': 'empty',
'Sec-Fetch-Mode': 'cors',
'Sec-Fetch-Site': 'same-site',
'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Mobile Safari/537.36',
'x-nba-stats-origin': 'stats',
'x-nba-stats-token': 'true'}).results.get_data_frame()

        season_players = tmp[tmp['Season'] == season]
        for index, row in season_players.iterrows():
            row_index = tmp.index[season_players['Name'] == row_name]
        #     if (row_index):
        #         print(f"Found match for {row[0].getText()}")
        #         populate_NBA_combine_measurements(df, row_index, row)
        #     else:
        #         mapped_name = nba_combine_page.get_mapped_name(row_name)
        #         tmp.index[utils.is_fuzzy_name_match(season_players['Name'], mapped_name)]
        #         if (row_index):
        #             populate_NBA_combine_measurements(df, row_index, row)
        #         else:
        #             print(f"ERROR: Unable to find match for {mapped_name}")
    return tmp
                
def populate_NBA_combine_measurements(df, index, row_values):
    row = df.iloc(index)
    for pair in NBA_COMBINE_MEASUREMENT_COLUMNS.items():
        if (pair[1] == 1): # Position
            row[pair[0]] = row_values[pair[1]].getText()
        if (pair[1] == 2): # Body Fat
            row[pair[0]] = float(row_values[pair[1]].getText()[:-1])
        if (pair[1] in [5, 6, 7, 9]): # Height in feet/inches
            row[pair[0]] = translate_measurements_to_inches(row_values[pair[1]].getText())
        else:
            row[pair[0]] = float(row_values[pair[1]].getText())
            
def translate_measurements_to_inches(measurement):
    feet = int(measurement.split("'")[0])
    inches = float(measurement.split("'")[1].replace(' ','').replace('"', ''))
    return feet*12+inches