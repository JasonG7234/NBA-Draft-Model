import NBACombinePage

NBA_COMBINE_MEASUREMENT_COLUMNS = {'Position':1, 'Body Fat %':2, 'Hand Length (In.)':3, 'Hand Width (In.)':4, 'Height W/O Shoes':5,
    'Height W/ Shoes':6, 'Standing Reach':7, 'Weight':8, 'Wingspan':9}

def get_NBA_Combine_page(season, short_season_year=False):
    season = str(int(season[:4])+1) + '-' + str(int(season[-2:])+1)
    if (short_season_year):
        season = season + '-' + str(int(season[-2:])+2)
    url = f"https://www.nba.com/stats/draft/combine-anthro/?SeasonYear={season}"
    return NBACombinePage(url)

def get_NBA_Combine_measurements(df):
    tmp = df.sort_values(by=['Season'])
    for col in NBA_COMBINE_MEASUREMENT_COLUMNS.keys():
        if col not in tmp:
            tmp = df.assign(col='')
    for season in tmp['Season'].tolist():
        season_players = tmp[tmp['Season'] == season]
        nba_combine_page = get_NBA_Combine_page(season)
        for row in nba_combine_page.get_rows():
            row_index = tmp.index[tmp['Name'] == row[0].getText()]
            if (row_index):
                print(f"Found match for {row[0].getText()}")
                populate_NBA_combine_measurements(df, row_index, row)
            else:
                print(f"Could not find easy match for {row[0].getText()}")
                
def populate_NBA_combine_measurements(df, index, row_values):
    row = df.iloc(index)
    for pair in NBA_COMBINE_MEASUREMENT_COLUMNS.items():
        if (pair[1] == 2): # Body Fat
            row_values[pair[1]].getText
        row[pair[0]] = row_values[pair[1]].getText()