import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
#import statsmodels.api as sm

graphFieldNames = ['label', 'x-axis', 'y-axis']

def main():
    master = getCSVFile()
    columnCount = 0
    for col in master.columns:
        print("At index " + str(columnCount) + ", the column name is " + col)
        columnCount += 1
    columnIndexes = []
    for graphFieldName in graphFieldNames:
        columnIndexes.append(getIndexOfColumn(graphFieldName, columnCount))
    graph(master, columnIndexes)

def getCSVFile():
    while True:
        file_name = input("What csv file would you like to graph? ").strip()
        try:
            master = pd.read_csv(file_name)
        except FileNotFoundError:
            print("ERROR - File not found. Please try again.")
            continue
        return master

def getIndexOfColumn(graph_part, columnCount):
    while True:
        try:
            columnIndex = int(input("What column index would you like to be the " + graph_part + "? "))
        except ValueError:
            print("ERROR - That is not a valid column index. Please try again.")
            continue
        if (int(columnIndex) > columnCount or int(columnIndex) < 0):
            print("ERROR - That column index is not within the bounds of the CSV. Please try again.")
            continue
        return columnIndex

def graph(tableName, columnIndexes):
    xAxisRowIndex = int(columnIndexes[1])
    yAxisRowIndex = int(columnIndexes[2])
    plt.figure()
    plt.scatter(tableName.iloc[:, xAxisRowIndex], tableName.iloc[:, yAxisRowIndex])
    plt.xlabel(tableName.columns[columnIndexes[1]])
    plt.ylabel(tableName.columns[columnIndexes[2]])
    for index,row in tableName.iterrows():
        plt.annotate(row[columnIndexes[0]], (row[columnIndexes[1]], row[columnIndexes[2]]))
    plt.show()

if __name__ == "__main__":
    main()