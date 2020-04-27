from utils import *
import datetime
import pandas as pd
import numpy as np
import os.path
import sys

master = pd.DataFrame()
currentYear = datetime.datetime.now().year

def main():
    global master
    if not(os.path.isfile('master.csv')):
        addAllCollegeBasketballProspects()
        addRSCIRankAsColumn()
        while True:
            stopScript = input("We completed Step 2 - do you want to pause the script to do some manual data cleanup? It is recommended. Enter 'yes' or 'no': ").strip()
            if (stopScript == 'yes'):
                print("Okay, we recommend fixing all of the names and adding missing RSCI ranks from 247sports.")
                fixMasterBeforeExporting()
                sys.exit("Exiting the program to do manual data cleanup.")
            elif (stopScript == 'no'):
                print("Okay! Continuing with the script.")
                break
            else:
                print("ERROR - That is not a valid input. Please try again.")    
    else:
        while True:
            continueScript = input("Seems like you already have a master.csv file. Do you want to pick up from step 3? Enter 'yes' or 'no': ").strip()
            if (continueScript == 'yes'):
                print("Okay, picking up from Step 3 - adding college stats from Basketball Reference.")
                master = pd.read_csv('master.csv')
                break
            elif (continueScript == 'no'):
                print("Okay, exiting the program. You can delete the master.csv file if you want to try again.")
                sys.exit("Exiting the program.")
            else:
                print("ERROR - That is not a valid input. Please try again.")    
    addCollegeStatsFromBasketballReference()
    fixMasterBeforeExporting()


def addAllCollegeBasketballProspects():
    """Get the top 100 prospects each year from NBADraft.net, and add each year's top 100 to a master DataFrame.
    Found NBADraft.net to be the simplest to scrape and the most consistent from year-to-year, 
    their rankings are generally questionable but I'm dropping their rankings anyway."""
    
    global master
    global currentYear

    print("==============================================")
    print("STEP 1 - Getting the names of all the prospects")
    print("==============================================")
    yearCounter = 2009 # The first year nbadraft.net has their top100
    while yearCounter <= currentYear:
        top100 = []
        season = str(yearCounter-1) + "-" + str(yearCounter)[2:4] # Turn the year 
        print("Getting players from the " + season + " season")
        soup = findSite("https://www.nbadraft.net/ranking/bigboard/?year-ranking=" + str(yearCounter))
        if (soup):
            tableBody = soup.find('tbody')
            players = tableBody.findChildren('tr')
            for player in players:
                stat = player.find_all('td')
                row = [player.text for player in stat] # Get all the stats for that player
                row.insert(0, season)
                top100.append(row)
            yearDataFrame = pd.DataFrame(top100, columns=['Season', 'Rank', 'Change', 'Name', 'Height', 'Weight', 'Position', 'School', 'Class'])
        master = master.append(yearDataFrame, ignore_index=True)
        yearCounter = yearCounter + 1
    master = master.drop(['Rank', 'Change'], axis=1) # Remove the two unnecessary columns from the NBADraft table 
    print("Done! Moving onto step 2.")

def addRSCIRankAsColumn():
    """Get the RSCI rank from DraftExpress and add it as a column to the master DataFrame.
    I chose to use DraftExpress because 247sports only loads the top 50, and makes you press 'Load More'.
    Also, might be beneficial to do some manual data cleaning in the CSV... took me like ~30 minutes to fix the names of the prospects
    who were unranked, and also add some rankings if 247sports had them as like composite 435 or whatever..."""

    global master
    global currentYear

    print("==============================================")
    print("STEP 2 - Getting the RSCI ranks of all the prospects")
    print("==============================================")
    
    yearCounter = 2004
    master['RSCI'] = ""
    while yearCounter < currentYear:
        print("Getting RSCI rank for players from the class of " + str(yearCounter))
        soup = findSite("http://www.draftexpress.com/RSCI/" + str(yearCounter))
        players = soup.findChildren('tr')
        for player in players:
            booleanVal = False
            realName = player.find('td', {'class':'text key'})
            if (realName):
                realName = realName.getText().strip() # Go from column -> player name
                print("Searching for a match in CSV file for player: " + realName)
                for index, row in master.iterrows():
                    if (realName.replace(" ", "") == row['Name']):
                        rank = player.find('td').getText() # Get first column in row, which is the RSCI rank
                        print("Found a match for " + realName + ": " + rank)
                        master.at[index, 'RSCI'] = rank
                        master.at[index, 'Name'] = realName
                        booleanVal = True
                        break
                if not(booleanVal):
                    print("Could not find a match for " + realName)
        yearCounter = yearCounter + 1

def addCollegeStatsFromBasketballReference():
    """Get all advanced college stats for each player by scraping the relevant table from basketballreference.
    I also add on ORTG, DRTG, and AST/TOV% because I think they are really relevant stats for projecting NBA prospects."""

    global master

    print("==============================================")
    print("STEP 3 - Getting the last year's advanced stats of all of the prospects")
    print("==============================================")

    collegeStats = []
    for index, row in master.iterrows():
        playerStats = []
        print("Getting senior year college stats for " + row['Name'])
        soup = getPlayersBasketballReferencePage(row)
        if (soup):
            # Step 1 -> Get advanced stats, depending on what is null
            playerStats.extend(getAdvancedStats(soup, advancedColumnIDs))
            #Step 2 -> Get ORTG and DRTG, if it exists
            lastSeason = getLastSeasonForTable(soup, 'players_per_poss')
            if (lastSeason): playerStats = getRelevantStats(lastSeason, 25, playerStats)
            else: playerStats.extend(["", ""])
            
            # Step 3 -> Add on AST/TOV%
            playerStats.append(getASTtoTOVratio(soup))
        else:
            playerStats = [""] * 27
        print(len(playerStats))
        collegeStats.append(playerStats)
    master = pd.concat(
        [
            master,
            pd.DataFrame(
                collegeStats,
                index=master.index,
                columns=['G','GS','MP','PER','TS%','eFG%','3PAr','FTr','PProd','ORB%','DRB%','TRB%','AST%',
                    'STL%','BLK%','TOV%','USG%','OWS','DWS','WS','WS/40','OBPM','DBPM','BPM', 'ORTG', 'DRTG', 'AST/TOV']
            )
        ], axis=1
    )

def getPlayersBasketballReferencePage(row):
    name = row['Name'].replace("'", "").replace(" ", "-").lower()
    playerNameInURL = checkValueInDictOfExceptions(name, playerExceptions, name)
    index = checkValueInDictOfExceptions(name, indexExceptions, 1)
    while index in range(1,6):
        url = "https://www.sports-reference.com/cbb/players/" + playerNameInURL + "-" + str(index) + ".html"
        soup = findSite(url)
        if (soup.find('table', {'id':'players_advanced'})):
            school = soup.find('div', {'itemtype': 'https://schema.org/Person'})
            if (school and row['School'] in school.getText()):
                    return soup
            else:
                print("Common name?")
                index = index + 1
        else:
            break # Cannot find player
    print("Sorry, we couldn't find any college stats for : " +row['Name'])
    return None

def checkValueInDictOfExceptions(name, exceptionsDict, default):
    if (name in exceptionsDict):
        return exceptionsDict.get(name)
    return default

def getAdvancedStats(soup, advancedColumnIDs):
    playerAdvancedStats = [] #Initialize empty table to store stats
    lastSeason = getLastSeasonForTable(soup, 'players_advanced')
    stats = lastSeason.findChildren('td')[2:]
    statsIndex = 0 # Index of which stat we are on in the player's Advanced table
    allIndex = 0 # Index of which stat we SHOULD be on, according to all possible stats in the Advanced table
    while allIndex in range(0, len(advancedColumnIDs)): 
        try:
            td = stats[statsIndex] # Get the stat from the given index in the player's Advanced table
            if (td.getText()): # If the stat we are at (the td element) has content and is not blank...
                if (td['data-stat'] == advancedColumnIDs[allIndex]): # Check if that is the stat we are expecting to see!
                    # This is because in Basketball-Reference, for older players some columns won't even show up, like PER
                    playerAdvancedStats.append(td.getText()) 
                    statsIndex = statsIndex + 1
                else: # If this isn't the stat we are expecting to see, that means that there should be a blank value for that stat
                    playerAdvancedStats.append("")
            else: # If there is no data for the stat (td) we are at...
                if (td['data-stat'] == 'ws-dum' or td['data-stat'] == 'bpm-dum'): # Check if this is the default blank column that Basketball-Reference always has!
                    # For some reason those two columns exists solely to bother web scrapers like me
                    statsIndex = statsIndex + 1
                else: # If it is not one of those dumb columns, add it.
                    playerAdvancedStats.append("")
                    statsIndex = statsIndex + 1
        except IndexError: # However, if we finish indexing through the table but there are still advanced stats to be added...
           if not(advancedColumnIDs[allIndex] == 'bpm-dum'):
                playerAdvancedStats.append("") # Just add a blank stat
        allIndex = allIndex + 1 # Iterate the index to pull the next stat we expect to see 
    return playerAdvancedStats

def getASTtoTOVratio(soup):
    lastSeason = getLastSeasonForTable(soup, 'players_totals')
    ast = (lastSeason.find('td', {'data-stat': 'ast'})).getText()
    tov = (lastSeason.find('td', {'data-stat': 'tov'})).getText()
    if (int(tov) == 0):
        return ast
    return str(round(int(ast)/int(tov), 2))

def getLastSeasonForTable(soup, tableID):
    table = soup.find('table', {'id': tableID})
    if (table):
        tableBody = table.find('tbody')
        return tableBody('tr')[-1] 
    return None

def getRelevantStats(seasonRow, columnIndex, playerStats):
    stats = seasonRow.findChildren('td', {'data-stat': True})[columnIndex:]
    for stat in stats:
        playerStats.append(stat.getText())
    return playerStats

def addCollegeStatsFromHoopMath():
    print("Here is where we will add stats from hoopmath")

def fixMasterBeforeExporting():
    class_list = ["Fr.", "So.", "Jr.", "Sr."]
    global master

    master = master[np.equal(master.Class, class_list[0])
    | np.equal(master.Class, class_list[1])
     | np.equal(master.Class, class_list[2])
      | np.equal(master.Class, class_list[3])]
    master.to_csv('temp_master.csv', index=False)


if __name__ == "__main__":
    main()