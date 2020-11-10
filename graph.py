import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from utils import *

GRAPH_FIELD_NAMES = ['label', 'x-axis', 'y-axis']

def main():
    master = get_csv_file("graph? ")
    column_count = 0
    for col in master.columns:
        print("At index " + str(column_count) + ", the column name is " + col)
        column_count += 1
    column_indexes = []
    for graph_field_name in GRAPH_FIELD_NAMES:
        column_indexes.append(get_index_of_column(graph_field_name, column_count))
    graph(master, column_indexes)


def get_index_of_column(graph_part, column_count):
    '''Get the index of the column being requested to pass into the graphing method'''
    while True:
        try:
            column_index = int(input("What column index would you like to be the " + graph_part + "? "))
        except ValueError:
            print("ERROR - That is not a valid column index. Please try again.")
            continue
        if (int(column_index) > column_count or int(column_index) < 0):
            print("ERROR - That column index is not within the bounds of the CSV. Please try again.")
            continue
        return column_index


def graph(table_name, column_indexes):
    '''Produce the scatter plot using matplotlib.pyplot'''

    x_axis_row_index = int(column_indexes[1])
    y_axis_row_index = int(column_indexes[2])

    plt.figure()

    plt.scatter(table_name.iloc[:, x_axis_row_index], table_name.iloc[:, y_axis_row_index])
    plt.xlabel(table_name.columns[column_indexes[1]])
    plt.ylabel(table_name.columns[column_indexes[2]])
    for index,row in table_name.iterrows():
        plt.annotate(row[column_indexes[0]], (row[column_indexes[1]], row[column_indexes[2]]))
    plt.show()

if __name__ == "__main__":
    main()