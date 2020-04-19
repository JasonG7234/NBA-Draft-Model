import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
#import statsmodels.api as sm

def graph(tableName, labelRowIndex, xAxisRowIndex, yAxisRowIndex):
    plt.figure()
    plt.scatter(tableName.iloc[:, xAxisRowIndex], tableName.iloc[:, yAxisRowIndex])
    plt.xlabel(tableName.columns[xAxisRowIndex])
    plt.ylabel(tableName.columns[yAxisRowIndex])
    for index,row in tableName.iterrows():
        plt.annotate(row[labelRowIndex], (row[xAxisRowIndex], row[yAxisRowIndex]))
    plt.show()
    
master = pd.read_csv("master.csv")
i = 0
for (columnName, columnData) in master.iteritems():
    print("At index " + str(i) + ", the column name is " + columnName)
    i += 1
graph(master, 4, 2, 45)