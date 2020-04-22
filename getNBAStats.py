from utils import *
from googlesearch import search
import pandas as pd
import csv

CUR_YEAR = "2019-20"
MPG = []
WSP48 = []
BPM = []
VORP = []
PLUSMINUS = []
NBA_STATS = [MPG, WSP48, BPM, VORP, PLUSMINUS]

def main():
    all = createPlayerListFromCSVs()
    nba = pd.read_csv('all_nba_stats.csv')
    if (nba.empty):
        nba = populateNBAStatistics(all)
    addNBAStatsToMasterList(all, nba)

# Import all necessary players to create one player DataFrame to work with
def createPlayerListFromCSVs():
    all = pd.DataFrame()
    while True:
        file_name = input("Enter a CSV file with player information. If you have entered all of them, enter 'stop' ").strip()
        if (file_name == 'stop'):
            break
        try:
            csv = pd.read_csv(file_name)
            all = all.append(csv, sort=False)
        except FileNotFoundError:
            print("ERROR - File not found. Please try again.")
            continue
    return all

# For each player in supplied panda dataframe, parse data through BasketballReference page
def populateNBAStatistics(all):
    nba_stats = all[['First Name', 'Last Name']].copy()
    for index, row in all.iterrows():
        player_name = row["First Name"] + " " + row["Last Name"]
        if(row["Season"] == CUR_YEAR):
            print(player_name + " is still in college.")
            appendValuesToNBALists(["?", "?", "?", "?", "?"])
            continue
        url = searchGoogle("bkref " + player_name)
        if("basketball-reference.com/players" not in url):
            print(player_name + " has yet to record any NBA stats. Adding all zeros.")
            appendValuesToNBALists(["0", "0", "0", "0", "0"])
            continue
        soup = findSite(url)
        print("Checking " + player_name + "'s stats now...")
        statValueList = []
        statValueList.extend(findGivenStatOnPlayerPage(soup, "all_per_game", ["mp_per_g"]))
        statValueList.extend(findGivenStatOnPlayerPage(soup, "all_advanced", ["ws_per_48", "bpm", "vorp"]))
        statValueList.extend(findGivenStatOnPlayerPage(soup, "all_pbp", ["plus_minus_net"]))
        appendValuesToNBALists(statValueList)
    nba_stats['NBA MPG'] = MPG
    nba_stats['NBA WSP48'] = WSP48
    nba_stats['NBA BPM'] = BPM
    nba_stats['NBA VORP'] = VORP
    nba_stats['NBA PLUSMINUS'] = PLUSMINUS
    nba_stats.to_csv('all_nba_stats.csv')

# Go to Google and make a basic search for "bkref + " player_name
# Figured this was more accurate than going to bkref's page directly bc their searching is not as direct
def searchGoogle(query):
	for j in search(query, num=1, stop=1):
			url = j
	return url

# Check the designated table for the designated datastat
def findGivenStatOnPlayerPage(soup, table_ID, datastat_IDs):
    table = soup.find("div", {"id": table_ID})
    list = []
    if table:
        career_stats = table("tfoot")[0] #Guarantees first row in the footer (career)
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
    all['NBA MPG'] = nba['NBA MPG']
    all['NBA WSP48'] = nba['NBA WSP48']
    all['NBA BPM'] = nba['NBA BPM']
    all['NBA VORP'] = nba['NBA VORP']
    all['NBA PLUSMINUS'] = nba['NBA PLUSMINUS']
    #all.drop(all.columns[[0, 1]], axis = 1, inplace = True) might be necessary? 
    all.to_csv("master.csv", index=False)

if __name__ == "__main__":
    main()