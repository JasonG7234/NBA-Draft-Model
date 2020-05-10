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
    if not(os.path.isfile('temp_master.csv')):
        addAllCollegeBasketballProspects()
        addRSCIRankAsColumn()
        while True:
            stopScript = input("We completed Step 2 - do you want to pause the script to do some manual data cleanup? It is recommended. Enter 'yes' or 'no': ").strip()
            if (stopScript == 'yes'):
                print("Okay, we recommend fixing all of the names and adding missing RSCI ranks from 247sports.")
                exportMaster()
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
                master = pd.read_csv('temp_master.csv')
                break
            elif (continueScript == 'no'):
                print("Okay, exiting the program. You can delete the master.csv file if you want to try again.")
                sys.exit("Exiting the program.")
            else:
                print("ERROR - That is not a valid input. Please try again.")    
    addCollegeStatsFromBasketballReference()
    exportMaster()


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
                stats = player.find_all('td')
                index = 2
                row = []
                while index < len(stats):
                    statText = stats[index].getText()
                    if (index == 2): #If at the name element, separate first and last name
                        statText = " ".join(name.text for name in stats[index].findChildren('span'))
                    row.append(statText)
                    index = index + 1
                row.insert(0, season)
                top100.append(row)
            yearDataFrame = pd.DataFrame(top100, columns=['Season', 'Name', 'Height', 'Weight', 'Position', 'School', 'Class'])
        master = master.append(yearDataFrame, ignore_index=True)
        yearCounter = yearCounter + 1
    removeNonCollegeBasketballProspects()
    reformatRemainingCollegeBasketballProspects()
    
def removeNonCollegeBasketballProspects():
    global master
    
    master = master[(master.Class == "Fr.")
     | (master.Class == "So.")
      | (master.Class == "Jr.")
       | (master.Class == "Sr.")] # Remove all international players
    master = master[(master.School != "JUCO")
     & (master.Class != "USA") 
      & (master.Class != "Augusta St.")] # Remove all players without any affiliation to a D1 school 

def reformatRemainingCollegeBasketballProspects():
    global master
    
    for index, row in master.iterrows():
        row['Name'] = getBasketballReferenceFormattedName(row['Name'], OVERALL_NAME_EXCEPTIONS)
        row['School'] = getBasketballReferenceFormattedSchool(row['School'], OVERALL_SCHOOL_EXCEPTIONS)
        if (row['School'][-3:] == "St."):
            row['School'] = row['School'][:-1] + "ate"

def addRSCIRankAsColumn():
    """Get the RSCI rank from 247Sports and add it as a column to the master DataFrame."""

    global master
    global currentYear

    print("==============================================")
    print("STEP 2 - Getting the RSCI ranks of all the prospects")
    print("==============================================")
    
    yearCounter = 2004
    master['RSCI'] = ""
    while yearCounter < currentYear:
        print("Getting RSCI rank for players from the class of " + str(yearCounter))
        page = 1
        while page <= 8: # Stopping at 8 pages because I think RSCI rank 400 is a good maximum value
            base_url = "http://247sports.com/Season/" + str(yearCounter) + "-Basketball/CompositeRecruitRankings"
            params = "?View=Detailed&InstitutionGroup=HighSchool&Page=" + str(page)
            soup = findSite(base_url + params)
            trs = soup.find_all('li', {'class':'rankings-page__list-item'})
            for player in trs:
                name = player.find('a').getText()
                for index, row in master.iterrows():
                    if (name == row['Name'] and row['RSCI'] == ""):
                        if (name in COMMON_NAMES):
                             college = player.find('div', {'class':'status'}).find('img')['alt']
                             if (college != row['School']):
                                 continue
                        rank = player.find('div', {'class':'primary'}).getText().split()[0]
                        print("Found a match for " + name + ": " + rank)
                        master.at[index, 'RSCI'] = rank
                        break
            page = page + 1
        yearCounter = yearCounter + 1
    addRemainingRSCIRankings()
    
def addRemainingRSCIRankings():
    """For every player not found on 247 year pages."""
    
    global master
    
    print("==============================================")
    print("STEP 2.5 - Getting the RSCI ranks of all of the remaining prospects")
    print("==============================================")
    
    for index, row in master.iterrows():
        rankInDictionary = RSCIRankInDictionary(row['Name'])
        if (pd.isna(row['RSCI']) and rankInDictionary != 0):
            print('yessir')
            row['RSCI'] = rankInDictionary

def RSCIRankInDictionary(name):
    return checkValueInDictOfExceptions(name, OVERALL_RSCI_EXCEPTIONS, 0) 

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
            playerStats.extend(getAdvancedStats(soup))
            # Step 2 -> Get ORTG and DRTG, if it exists
            lastSeason = getLastSeasonForTable(soup, 'players_per_poss')
            if (lastSeason): playerStats = getRelevantStats(lastSeason, 25, playerStats)
            else: playerStats.extend(["", ""])
            # Step 3 -> Add on AST/TOV%
            playerStats.append(getASTtoTOVratio(soup))
        else:
            # If there is no Basketball-Reference page, assume there is no page and delete the player from the csv
            master.drop(index, inplace=True)
            break
        collegeStats.append(playerStats)
    # Add the new DataFrame to the master list
    master = pd.concat([master, pd.DataFrame(collegeStats,index=master.index,columns=COLUMN_NAMES)], axis=1)

def getPlayersBasketballReferencePage(row):
    """Get the players Basketall-Reference page. This includes pulling the right name and index from the respective dictionaries.
    Once we have the URL, we check if it is right by checking the player's quick info."""

    playerNameInURL = getBasketballReferenceFormattedURL(row['Name'])
    indexValueInURL = checkValueInDictOfExceptions(playerNameInURL, COLLEGE_INDEX_EXCEPTIONS, 1)
    if(indexValueInURL == 1):
        while indexValueInURL in range(1,5): # We check first five profiles of each name
            url = "https://www.sports-reference.com/cbb/players/" + playerNameInURL + "-" + str(indexValueInURL) + ".html"
            soup = findSite(url)
            if (soup.find('table', {'id':'players_advanced'})): # If there is an advanced table (some older profiles don't have them)
                quickBKRefPlayerInfoDiv = getBasketballReferencePlayerInfo(soup)
                expectedSchoolNameInInfoDiv = getBasketballReferenceFormattedSchool(row['School'], COLLEGE_SCHOOL_EXCEPTIONS)
                if (quickBKRefPlayerInfoDiv and expectedSchoolNameInInfoDiv in quickBKRefPlayerInfoDiv.getText()): # If the expected school name is in the school div
                    return soup # We found the right player and can return
                else: # Otherwise, we found the wrong player, let's try again with the next player
                    print("Common name?")
                    index = index + 1
    else:
        url = "https://www.sports-reference.com/cbb/players/" + playerNameInURL + "-" + str(indexValueInURL) + ".html"
        return findSite(url)
    print("Sorry, we couldn't find any college stats for : " +row['Name'])
    return None

def getAdvancedStats(soup):
    playerAdvancedStats = [] #Initialize empty table to store stats
    lastSeason = getLastSeasonForTable(soup, 'players_advanced')
    stats = lastSeason.findChildren('td')[2:]
    statsIndex = 0 # Index of which stat we are on in the player's Advanced table
    allIndex = 0 # Index of which stat we SHOULD be on, according to all possible stats in the Advanced table
    while allIndex in range(0, len(ADVANCED_COLUMN_IDS)): 
        try:
            td = stats[statsIndex] # Get the stat from the given index in the player's Advanced table
            if (td.getText()): # If the stat we are at (the td element) has content and is not blank...
                if (td['data-stat'] == ADVANCED_COLUMN_IDS[allIndex]): # Check if that is the stat we are expecting to see!
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
           if not(ADVANCED_COLUMN_IDS[allIndex] == 'bpm-dum'):
                playerAdvancedStats.append("") # Just add a blank stat
        allIndex = allIndex + 1 # Iterate the index to pull the next stat we expect to see 
    return playerAdvancedStats

def getASTtoTOVratio(soup):
    lastSeason = getLastSeasonForTable(soup, 'players_totals')
    ast = (lastSeason.find('td', {'data-stat':'ast'})).getText()
    tov = (lastSeason.find('td', {'data-stat':'tov'})).getText()
    if (int(tov) == 0):
        return ast
    return str(round(int(ast)/int(tov), 2))

def getLastSeasonForTable(soup, tableID):
    table = soup.find('table', {'id':tableID})
    if (table):
        tableBody = table.find('tbody')
        return tableBody('tr')[-1] 
    return None

def getRelevantStats(seasonRow, columnIndex, playerStats):
    stats = seasonRow.findChildren('td', {'data-stat':True})[columnIndex:]
    for stat in stats:
        playerStats.append(stat.getText())
    return playerStats

def addCollegeStatsFromHoopMath():
    print("==============================================")
    print("STEP 4 - Getting the last year's Hoop-Math data for all the prospects")
    print("==============================================")
    #Still a work in progress... wondering if this is necessary... right now leaning towards no

def exportMaster():
    global master
    master.to_csv('temp_master.csv', index=False)

if __name__ == "__main__":
    main()
