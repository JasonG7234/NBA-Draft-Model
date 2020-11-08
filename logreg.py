from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from utils import *
import pandas as pd
import numpy as np

def main():
    master = get_csv_file("perform logistic regression on? ")
    perform_log_reg(master)

def perform_log_reg(master):

    X = pd.DataFrame() 
    Y = pd.DataFrame(index=np.arange(len(master)), columns=['Result'])
    
    master = populate_dataframe_with_average_values(master)

    prospects_for_upcoming_nba_draft = master.loc[master['NBA GP'] == '?']
    for index, row in master.iterrows():
        if (row['NBA GP'] == '?'):
            master = master.drop(index)
            Y = Y.drop(index)
            continue
        Y.loc[index, 'Result'] = is_nba_player(row)

    X = master[LOG_REG_COLUMNS]
    prospect_stats_for_upcoming_nba_draft = prospects_for_upcoming_nba_draft[LOG_REG_COLUMNS]

    Y = Y.astype('int')
    Y.to_csv('isNBA.csv', index=False)

    X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.25, shuffle=True)
    
    logreg = LogisticRegression(solver='liblinear', max_iter=250)
    logreg.fit(X_train, Y_train.values.ravel())
    Y_pred = logreg.predict(X_test)
    
    make_predictions_for_upcoming_nba_prospects(logreg, prospect_stats_for_upcoming_nba_draft, prospects_for_upcoming_nba_draft, False)
    print_coefficient_information(logreg)
    print_confusion_matrix_for_test_data(Y_test, Y_pred)

    return logreg

def print_coefficient_information(logreg):
    print("----------------------------------")
    print("Coefficient Information:")

    for i in range(len(LOG_REG_COLUMNS)):

        logregCoefficients = logreg.coef_

        currentFeature = LOG_REG_COLUMNS[i]
        currentCoefficient = logregCoefficients[0][i]

        print(currentFeature + ': ' + str(currentCoefficient))

def print_confusion_matrix_for_test_data(test, pred):
    
    print("----------------------------------")

    print("Accuracy:", metrics.accuracy_score(test, pred))
    print("Precision:", metrics.precision_score(test, pred))
    print("Recall:", metrics.recall_score(test, pred))

    print("----------------------------------")

    print("Confusion Matrix: ")
    print(metrics.confusion_matrix(test, pred))

if __name__ == "__main__":
    main()