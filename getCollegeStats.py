from utils import *
import datetime
import pandas as pd
import numpy as np
import os.path

master = pd.DataFrame()

def main():
    global master
    current_year = datetime.datetime.now().year
    if not(os.path.isfile('temp_master.csv')):
        year_counter = 2009
        print("Getting all college basketball prospects since " + str(year_counter))
        while year_counter <= current_year:
            getCollegePlayersOfGivenYear(str(year_counter))
            year_counter = year_counter + 1
    else:
        master = pd.read_csv('temp_master.csv')
    addRSCIRankAsColumn(current_year)
    # After adding RSCI rank, might be beneficial to do some manual data cleaning in the CSV... took me like ~30 minutes to add fix the names
    # and add missing RSCI ranks... could probably be easier to use 247's recruiting rankings but TOO LATE NOW
    fixMasterBeforeExporting()


def getCollegePlayersOfGivenYear(year):
    global master
    top100 = []
    season = str(int(year)-1) + "-" + year[0:2]
    print("Getting players from the " + season + "season")
    soup = findSite("https://www.nbadraft.net/ranking/bigboard/?year-ranking=" + year)
    table_body = soup.find("tbody")
    if (table_body):
        players = table_body.findChildren("tr")
        for player in players:
            stat = player.find_all("td")
            row = [player.text for player in stat]
            top100.append(row)
        year_dataframe = pd.DataFrame(top100, columns=["Rank", "Change", "Name", "Height", "Weight", "Position", "School", "Class"])
        year_dataframe = year_dataframe.insert(0, 'Season', season)
    master = master.append(year_dataframe)

def addRSCIRankAsColumn(current_year):
    global master
    print("Now getting RSCI rank for each player")
    year_counter = 2004
    master["RSCI"] = ""
    while year_counter < current_year:
        soup = findSite("http://www.draftexpress.com/RSCI/" + str(year_counter))
        players = soup.findChildren("tr")
        print("There are " + str(len(players)) + " players in this year's RSCI rankings")
        for player in players:
            booleanVal = False
            real_name = player.find("td", {"class":"text key"})
            if (real_name):
                real_name = real_name.getText().strip()
                print("Searching for a match in CSV file for player: " + real_name)
                for index, row in master.iterrows():
                    if (real_name.replace(" ", "") == row["Name"]):
                        rank = player.find("td").getText()
                        print("Found a match for " + real_name + ": " + rank)
                        master.at[index, 'RSCI'] = rank
                        master.at[index, 'Name'] = real_name
                        booleanVal = True
                if not(booleanVal):
                    print("Could not find a match for " + real_name)
            else:
                print("Could not find a name for " + str(real_name))
        year_counter = year_counter + 1


                
    

def fixMasterBeforeExporting():
    class_list = ["Fr.", "So.", "Jr.", "Sr."]
    global master
    # master = master.drop(["Rank", "Change"], axis=1)
    # master = master[np.equal(master.Class, class_list[0])
    # | np.equal(master.Class, class_list[1])
    #  | np.equal(master.Class, class_list[2])
    #   | np.equal(master.Class, class_list[3])]
    master.to_csv("temp.csv", index=False)

if __name__ == "__main__":
    main()