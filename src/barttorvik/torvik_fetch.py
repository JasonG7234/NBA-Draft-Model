import sys
sys.path.insert(0, '../../')
from utils import *

import json
import requests

BART_TORVIK_NAME_EXCEPTIONS = {
    "Wes Johnson" : "Wesley Johnson",
    "Artsiom Parakhouski" : "Art Parakhouski",
    "Howard Thompkins III" : "Trey Thompkins",
    "Moe Harkless" : "Maurice Harkless",
    "Amath M'Baye" : "Amath Mbaye",
    "Phl Pressey" : "Phil Pressey",
    "Edward Daniel" : "Ed Daniel",
    "Deandre Daniels" : "DeAndre Daniels",
    "Deandre Kane" : "DeAndre Kane",
    "Laquinton Ross" : "LaQuinton Ross",
    "Tashawn Thomas" : "TaShawn Thomas",
    "Ladontae Henton" : "LaDontae Henton",
    "Dennis Smith, Jr." : "Dennis Smith Jr",
    "Edrice Adebayo" : "Bam Adebayo",
    "Vincent Edwards" : "Vince Edwards",
    "Simi Shittu" : "Simisola Shittu",
    "Tyty Washington Jr." : "TyTy Washington",
    "Jeenathan Williams" : "JeeNathan Williams",
    "E'Twaun Moore" : "Etwaun Moore",
    "Jeff Taylor" : "Jeffrey Taylor",
    "Devyn Marble" : "Roy Devyn",
    "Kay Felder" : "Kahlil Felder",
    "Ray Spalding" : "Raymond Spalding",
    "Herbert Jones" : "Herb Jones",
    "Tyrn Flowers" : "Ty Flowers",
    "JaKarr Sampson" : "Jakarr Sampson",
    "Tristan Da Silva" : "Tristan da Silva",
    }

BART_TORVIK_VALUE_EXCEPTIONS = {
    "Derrick Williams2009-10" : "40",
    "Tyler Harris2015-16" : "6",
    "Donovan Mitchell2016-17" : "9",
    "Jordan Bell2016-17" : "50",
    "Donovan Williams2021-22" : "9",
    "Jae'Sean Tate2017-18" : "17"
}

def fetch_bart_torvik_data(year):
    """Fetches the bart torvik player data for a given year.

    Args:
        year (string): Represents the end year of the college basketball season. 
    
    Returns:
        List: The torvik data.
    """
    
    torvik_season_url = f"https://barttorvik.com/getadvstats.php?year={year}&top=400&page=playerstat"
    response = requests.get(url = torvik_season_url).text
    return json.loads(response)

def get_torvik_dunks(df):
    """Takes in a DataFrame, adds a '# Dunks' column, and adds the value according to the prospect's name.

    Args:
        df (DataFrame): Any DataFrame that uses a "Name" column
        
    Returns:
        DataFrame: The DataFrame with the new data
    """
    
    df['# Dunks'] = ""
    seasons = df.Season.unique()
    for season in seasons:
        if season == '2008-09': continue # Bart Torvik doesn't have dunk data for this season 
        torvik_json = fetch_bart_torvik_data(get_year_from_season(season))
        for index, df_player in df[df['Season'] == season].iterrows():
            manual_dunks = BART_TORVIK_VALUE_EXCEPTIONS.get(df_player['Name'] + df_player['Season'], None)
            if (manual_dunks):
                df.loc[index, '# Dunks'] = manual_dunks
            else:
                for player in torvik_json:
                    if (is_fuzzy_name_match(player[0], df_player['Name'], BART_TORVIK_NAME_EXCEPTIONS, 93)):
                        dunk_count = player[42]
                        print(f"Found # Dunks for {df_player['Name']}: {dunk_count}")
                        df.loc[index, '# Dunks'] = dunk_count
                        break
    return df

