from utils import *
import pandas as pd
import csv

CUR_YEAR = "2019-20"
GP = []
MPG = []
WS = []
WSP48 = []
BPM = []
VORP = []
PLUSMINUS = []
NBA_STATS = [GP, MPG, WS, WSP48, BPM, VORP, PLUSMINUS]

def main():
    all = getCSVFile("add NBA stats? ")
    populateNBAAllStatistics(all)

# Import all necessary players to create one player DataFrame to work with
def createPlayerListFromCSVs():
    all = pd.DataFrame()
    while True:
        file_name = input("Enter a CSV file with player information.").strip()
        if (file_name == 'stop'):
            break
        try:
            csv = pd.read_csv(file_name)
            all = all.append(csv, sort=False)
        except FileNotFoundError:
            print("ERROR - File not found. Please try again.")
            continue
    return all

def populateNBAAllStatistics(all):
    couldNotFindList = []
    nba_stats = all[['Name']].copy()
    base_url = "https://www.basketball-reference.com/players"
    for index, row in all.iterrows():
        if(row['Season'] == CUR_YEAR):
            print(row['Name'] + " is still in college.")
            appendValuesToNBALists(["?", "?", "?", "?", "?"])
            continue
        bkrefIdentifier, bkrefIndex, bkrefName = getBKRefIdentifierAndIndex(row['Name'])
        while True:
            url = base_url + bkrefIdentifier + "0" + str(bkrefIndex) + ".html"
            print(url)
            soup = findSite(url)   
            if (soup):
                if (soup.find('div', {'class': 'index reading'}) or not soup.find('table')):
                    print("Reached 404 page - assuming there are no stats for " + row['Name'])
                    appendValuesToNBALists(["0", "0", "0", "0", "0"])
                    break
                quickBKRefPlayerInfoDiv = getBasketballReferencePlayerInfo(soup)
                if (quickBKRefPlayerInfoDiv):
                    if (isOnCorrectPlayerPage(bkrefName, row['School'], quickBKRefPlayerInfoDiv)):
                        if (soup.find('table')['id'] == 'all_college_stats'):
                            print("Could not find an NBA Basketball Reference page for " + row['Name'])
                            bkrefIndex = bkrefIndex + 1
                            continue
                        else:
                            print("Found NBA player page for " + row['Name'])
                            populateNBAPlayerStatistics(soup)
                            break
                    else:
                        if (bkrefIndex == 1):
                            bkrefIndex = bkrefIndex + 1
                            continue
                        else: 
                            print("Could not find a correct NBA player page for " + row['Name'])
                            couldNotFindList.append(index)
                            appendValuesToNBALists(["0", "0", "0", "0", "0"])
                            bkrefIndex = bkrefIndex + 1
                            break
                else:
                    print("Could not find player info div for " + url)    
            else: 
                    print("Could not find page for url: " + url)

    nba_stats['NBA GP'] = GP
    nba_stats['NBA MPG'] = MPG
    nba_stats['NBA WS'] = WS
    nba_stats['NBA WSP48'] = WSP48
    nba_stats['NBA BPM'] = BPM
    nba_stats['NBA VORP'] = VORP
    nba_stats['NBA PLUSMINUS'] = PLUSMINUS
    nba_stats.to_csv('all_nba_stats.csv')
    print(couldNotFindList)

def getBKRefIdentifierAndIndex(name):
    bkrefName = getBasketballReferenceFormattedName(name, NBA_NAME_EXCEPTIONS)
    print(bkrefName)
    firstName, lastName = bkrefName.rsplit(' ', 1)
    bkrefIdentifier = ("/" + lastName[0] + "/" + lastName[:5] + firstName[:2]).lower()
    bkrefIndex = checkValueInDictOfExceptions(bkrefName, NBA_INDEX_EXCEPTIONS, 1)
    return bkrefIdentifier, bkrefIndex, bkrefName

def isOnCorrectPlayerPage(name, school, playerInfo):
    school = getBasketballReferenceFormattedSchool(school, NBA_SCHOOL_EXCEPTIONS)
    playerInfoText = playerInfo.getText().replace(".", "")
    return name in playerInfoText and school in playerInfoText       

def populateNBAPlayerStatistics(soup):
    statValueList = []
    statValueList.extend(findGivenStatOnPlayerPage(soup, 'all_per_game', ['g','mp_per_g']))
    statValueList.extend(findGivenStatOnPlayerPage(soup, 'all_advanced', ['ws', 'ws_per_48', 'bpm', 'vorp']))
    statValueList.extend(findGivenStatOnPlayerPage(soup, 'all_pbp', ['plus_minus_net']))
    appendValuesToNBALists(statValueList)

# Check the designated table for the designated datastat
def findGivenStatOnPlayerPage(soup, table_ID, datastat_IDs):
    table = soup.find('div', {'id': table_ID})
    list = []
    if table:
        career_stats = table('tfoot')[0] #Guarantees first row in the footer (career)
        for datastat_ID in datastat_IDs:
            stat = (career_stats.find("td", {"data-stat": datastat_ID})).getText()
            print("Found stat for " + datastat_ID + ": " + stat)
            list.append(stat)
    else:
        for datastat_ID in datastat_IDs:
            print("Did not find a stat for " + datastat_ID + " - adding zero.")
            list.append("0")
    return list

# For each player, add an entry to the NBA stats lists
def appendValuesToNBALists(l):
    for i in range(0,5):
        NBA_STATS[i].append(l[i])

# Final step, add NBA stats to master list and export to CSV
def addNBAStatsToMasterList(all, nba):
    all['NBA GP'] = nba['NBA GP']
    all['NBA MPG'] = nba['NBA MPG']
    all['NBA WS'] = nba ['NBA WS']
    all['NBA WSP48'] = nba['NBA WSP48']
    all['NBA BPM'] = nba['NBA BPM']
    all['NBA VORP'] = nba['NBA VORP']
    all['NBA PLUSMINUS'] = nba['NBA PLUSMINUS']
    all.to_csv("master.csv", index=False)

if __name__ == "__main__":
    main()