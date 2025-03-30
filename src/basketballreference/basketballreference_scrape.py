import sys
sys.path.insert(0, '../../')
from utils import *

INDEX_OF_POSSESSION_STATS_IN_TABLE = 25
MAX_PROFILES_TO_SEARCH_BY_NAME = 6

BASKETBALL_REFERENCE_PLAYER_NAME_EXCEPTIONS = {
    "eric-hunter" : "eric-hunterjr",
    "roy-dixon" : "roy-dixoniii",
    "julian-roper-ii" : "julian-roperii",
    "eugene-brown" : "eugene-browniii",
    "alonzo-verge" : "alonzo-vergejr",
    "brandon-johns-jr" : "brandon-johnsjr",
    "terrance-williams" : "terrance-williamsii",
    "lorne-bowman" : "lorne-bowmanii",
    "ron-harper" : "ron-harperjr",
    "keion-brooks" : "keion-brooksjr",
    "kim-aiken" : "kim-aikenjr",
    "juan-toscano-anderson" : "juan-anderson",
    "wendell-carter" : "wendell-carterjr",
    "marvin-bagley" : "marvin-bagleyiii",
    "trey-murphy" : "trey-murphyiii",
    "fuquan-edwin" : "edwin-fuquan",
    "derrick-jones" : "derrick-jonesjr",
    "brandon-boston" : "brandon-bostonjr",
    "jaren-jackson" : "jaren-jacksonjr",
    "james-mcadoo" : "james-michael-mcadoo",
    "glen-rice" : "glen-rice-jr",
    "tim-hardaway" : "tim-hardaway-jr",
    "tu-holloway" : "terrell-holloway",
    "bernard-james" : "bernard-james-",
    "simi-shittu" : "simisola-shittu",
    "kira-lewis" : "kira-lewisjr",
    "stephen-zimmerman" : "stephen-zimmermanjr",
    "roy-devyn" : "roy-devyn-marble",
    "rob-gray" : "robert-grayjr",
    "vernon-carey" : "vernon-careyjr",
    "zach-norvell" : "zach-norvelljr",
    "kz-okpala" : "kezie-okpala",
    "ja-morant" : "temetrius-morant",
    "jo-lual-acuil" : "jo-acuil",
    "michael-porter" : "michael-porterjr",
    "shake-milton" : "malik-milton",
    "andrew-white" : "andrew-whiteiii",
    "wesley-johnson" : "wes-johnson",
    "cam-oliver" : "cameron-oliver",
    "bam-adebayo" : "edrice-adebayo",
    "dennis-smith" : "dennis-smithjr",
    "yogi-ferrell" : "kevin-ferrell",
    "anthony-barber" : "anthony-cat-barber",
    "christ-koumadje" : "jeanmarc-koumadje",
    "dewan-hernandez" : "dewan-huell",
    "dez-wells" : "dezmine-wells",
    "bryce-dejean-jones" : "bryce-jones",
    "ronald-roberts" : "ronald-roberts-",
    "ed-daniel" : "edward-daniel",
    "cam-long" : "cameron-long",
    "art-parakhouski" : "artsiom-parakhouski",
    "landers-nolley" : "landers-nolleyii",
    "terrence-shannon" : "terrence-shannonjr",
    "obi-toppin" : "obadiah-toppin",
    "duane-washington" : "duane-washingtonjr",
    "mac-mcclung" : "matthew-mcclung",
    "mckinley-wright" : "mckinley-wrightiv",
    "oscar-da-silva" : "oscar-dasilva",
    "johnny-davis" : "jonathan-davis",
    "tyty-washington" : "tyty-washingtonjr",
    "wendell-moore" : "wendell-moorejr",
    "kenneth-lofton" : "kenneth-loftonjr",
    "joe-harris" : "joe-harris-",
    "garrison-mathews" : "garrison-matthews",
    "kc-ndefo" : "kenechukwu-ndefo",
    "hunter-tyson" : "tyson-hunter",
    "gg-jackson" : "gregory-jackson-ii",
    "ricky-council-iv" : "ricky-counciliv",
    "craig-porter-jr" : "craig-porterjr",
    "daron-holmes" : "daron-holmesii",
    "tristan-da-silva": "tristan-dasilva",
    "terrence-shannon-jr": "terrence-shannonjr",
    "ace-bailey": "airious-bailey",
}

BASKETBALL_REFERENCE_INDEX_EXCEPTIONS = {
    "ryan-young" : 2,
    "jordan-davis" : 24,
    "ian-burns" : 3,
    "brandon-williams" : 8,
    "anthony-lamb" : 2,
    "kristian-doolittle" : 2,
    "paul-reed" : 5,
    "gary-payton" : 2,
    "kyle-anderson" : 3,
    "thomas-robinson" : 2,
    "josh-green" : 2,
    "nick-richards" : 2,
    "aj-lawson" : 12,
    "reggie-perry" : 2,
    "robert-woodard" : 2,
    "greg-brown" : 9,
    "lonnie-walker" : 2,
    "anthony-davis" : 5,
    "chris-walker" : 6,
    "eric-mika" : 2,
    "troy-brown" : 5,
    "charlie-brown" : 2,
    "rodney-williams" : 3,
    "cameron-johnson" : 4,
    "mark-williams" : 7,
    "chris-smith" : 19,
    "tyler-davis" : 5,
    "jalen-johnson" : 24,
    "david-johnson" : 13,
    "jalen-williams" : 13,
    "donovan-williams" : 3,
    "jonathan-davis" : 3,
    "jared-harper" : 12,
    "keith-williams" : 10,
    "nate-johnson" : 6,
    "andre-jackson" : 8,
    "brandon-johnson" : 56,
    "david-jones" : 10,
    "terrell-brown" : 55,
    "marcus-hammond" : 4,
    "justin-edwards": 4,
}

BASKETBALL_REFERENCE_SCHOOL_NAME_EXCEPTIONS = {
    "Illinois-Chicago" : "UIC",
    "Louisiana Lafayette" : "Louisiana",
    "Southern Miss." : "Southern Miss",
    "Tennessee-Martin" : "UT-Martin",
    "Texas A&M Corpus Christi" : "Texas A&M-Corpus Christi",
    "Texas Arlington" : "UT Arlington",
    "USC" : "Southern California",
    "BYU" : "Brigham Young",
}

def add_college_stats_from_basketball_reference(df):
    """Get all advanced college stats for each player's most recent year by scraping the relevant table from basketballreference.
    I also add on ORTG, DRTG, and AST/TOV% because I think they are really relevant stats for projecting NBA prospects.
    """
    college_stats = []
    for index, row in df.iterrows():
        player_stats = []
        print("Getting most recent college stats for " + row['Name'])
        soup_html = get_players_basketball_reference_page(row)
        if (soup_html):
            player_stats.extend(get_advanced_stats(soup_html))
            player_stats.extend(get_per_40_stats(soup_html))
            player_stats.extend(get_per_100_stats(soup_html))
            player_stats.append(get_ast_to_tov_ratio(soup_html))
            player_stats.append(get_sos(soup_html))
            player_stats.append(get_conference(soup_html))
        else:
            df.drop(index, inplace=True)
            continue
        college_stats.append(player_stats)
    basketball_reference_df = pd.DataFrame(college_stats,index=df.index,columns=COLUMN_NAMES)
    df = pd.concat([df, basketball_reference_df], axis=1)
    return df

def get_players_basketball_reference_page(row):
    """Get the player's Basketall-Reference page. This includes pulling the right name and index from the respective dictionaries.
    Once we have the URL, we check if it is right by checking the player's quick info.
    """

    player_name_in_url = get_basketball_reference_formatted_url(row['Name'])
    index_value_in_url = check_value_in_dictionary_of_exceptions(player_name_in_url, BASKETBALL_REFERENCE_INDEX_EXCEPTIONS, 1)
    if (index_value_in_url == 1):
        while index_value_in_url in range(1, MAX_PROFILES_TO_SEARCH_BY_NAME): 
            url = "https://www.sports-reference.com/cbb/players/" + player_name_in_url + "-" + str(index_value_in_url) + ".html"
            soup_html, _ = find_site(url)
            if ((not soup_html) and (player_name_in_url[-3:] == '-jr')):
                player_name_in_url = player_name_in_url[:-3] + 'jr'
                url = "https://www.sports-reference.com/cbb/players/" + player_name_in_url + "-" + str(index_value_in_url) + ".html"
                soup_html, _ = find_site(url)
            if not soup_html:
                url = input(f"Cannot find basketball-reference player page for {row['Name']}. Can you try manually inputting the URL? ")
                soup_html, _ = find_site(url)
            if (soup_html.find('table', {'id':'players_advanced'})):
                quick_player_info = get_basketball_reference_player_info(soup_html)
                expected_school_name = get_basketball_reference_formatted_school(row['School'], BASKETBALL_REFERENCE_SCHOOL_NAME_EXCEPTIONS, row['School'])
                if (quick_player_info and expected_school_name in quick_player_info):
                    return soup_html
                else:
                    print(row['Name'] + " might be a common name - trying again at next profile index")
                    if (player_name_in_url[-3:] == '-jr'):
                        player_name_in_url = player_name_in_url[:-3] + 'jr'
                    else:
                        index_value_in_url = index_value_in_url + 1
            else:
                if (player_name_in_url[-3:] == '-jr'):
                    player_name_in_url = player_name_in_url[:-3] + 'jr'
                    url = "https://www.sports-reference.com/cbb/players/" + player_name_in_url + "-" + str(index_value_in_url) + ".html"
                    soup_html, _ = find_site(url)
                    return soup_html
                if (index_value_in_url == 1):
                    index_value_in_url = 2
                    url = "https://www.sports-reference.com/cbb/players/" + player_name_in_url + "-" + str(index_value_in_url) + ".html"
                    soup_html, _ = find_site(url)
                    return soup_html
                print("Sorry, we couldn't find the correct player page for : " +row['Name'])
                return None
    else:
        url = "https://www.sports-reference.com/cbb/players/" + player_name_in_url + "-" + str(index_value_in_url) + ".html"
        soup_html, _ = find_site(url)
        return soup_html
    print("Sorry, we couldn't find any college stats for : " + row['Name'])
    return None

def get_advanced_stats(soup_html):
    """Get the player's advanced stats from their table. This is a complicated process because of the differences in the format 
    of the advanced table through the years, along with some dummy columns that are always blank for some reason.
    """
    player_advanced_stats = [] 
    last_season_stats = get_last_season_stat_row(soup_html, 'players_advanced')
    stats = last_season_stats.findChildren('td')[4:] # Slicing
    stats_index = 0 # Index of which stat we are on in the player's Advanced table
    all_index = 0 # Index of which stat we SHOULD be on, according to all possible stats in the Advanced table
    while all_index in range(0, len(ADVANCED_COLUMN_IDS)):
        try:
            stat_at_index = stats[stats_index]
            if (stat_at_index.getText()):
                if (is_expected_advanced_stat_in_table(stat_at_index, all_index)):
                    player_advanced_stats.append(stat_at_index.getText()) 
                    stats_index = stats_index + 1
                else: 
                    player_advanced_stats.append("")
            else:
                if (is_empty_dummy_column(stat_at_index)):
                    stats_index = stats_index + 1
                else:
                    player_advanced_stats.append("")
                    stats_index = stats_index + 1
        except IndexError: ### As of 2025 this blank dummy column no longer exists, it did from at least 2013 -> 2024
        #    if (ADVANCED_COLUMN_IDS[all_index] != 'bpm-dum'):
        #        player_advanced_stats.append("") 
            continue
        all_index = all_index + 1
    return player_advanced_stats

def get_per_40_stats(soup_html):
    """Get the player's per 40 minute stats from their table.
    """
    
    last_season_stats = get_last_season_stat_row(soup_html, 'players_per_min')
    return [last_season_stats.find('td', {'data-stat' : col}).getText() for col in PER_40_COLUMN_IDS]
    
def get_per_100_stats(soup_html):
    """Get the player's per 100 possession stats from their table.
    """

    last_season_stats = get_last_season_stat_row(soup_html, 'players_per_poss')
    if (last_season_stats): 
        return [last_season_stats.find('td', {'data-stat' : col}).getText() for col in PER_100_COLUMN_IDS]
    else: 
        return [""] * len(PER_100_COLUMN_IDS)

# HELPER METHODS
def get_last_season_stat_row(soup_html, table_id):
    table = soup_html.find('table', {'id':table_id})
    if (table):
        table_body = table.find('tbody')
        return table_body('tr')[-1] 
    return None

def get_possession_stats(season_row):
    stats = season_row.findChildren('td', {'data-stat':True})[INDEX_OF_POSSESSION_STATS_IN_TABLE:] # Slicing
    return [ stat.getText() for stat in stats ]

def get_ast_to_tov_ratio(soup_html):
    last_season = get_last_season_stat_row(soup_html, 'players_totals')
    ast = (last_season.find('td', {'data-stat':'ast'})).getText()
    tov = (last_season.find('td', {'data-stat':'tov'})).getText()
    if (int(tov) == 0):
        return ast
    return str(round(int(ast)/int(tov), 2))

def get_sos(soup_html):
    last_season = get_last_season_stat_row(soup_html, 'players_per_game')
    sos = last_season.find('td', {'data-stat':'sos'})
    return sos.getText() if sos else ""

def get_conference(soup_html):
    last_season = get_last_season_stat_row(soup_html, 'players_per_game')
    conf = last_season.find('td', {'data-stat':'conf_abbr'})
    return conf.getText() if conf else ""

def is_expected_advanced_stat_in_table(stat, index):
    return stat['data-stat'].strip() == ADVANCED_COLUMN_IDS[index]

def is_empty_dummy_column(stat):
    return stat['data-stat'] == 'ws-dum' or stat['data-stat'] == 'bpm-dum'

def get_basketball_reference_formatted_url(name):
    url_name = name.replace("'", "").replace(".", "").replace(" ", "-").lower()
    return check_value_in_dictionary_of_exceptions(url_name, BASKETBALL_REFERENCE_PLAYER_NAME_EXCEPTIONS, url_name)
