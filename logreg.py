from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from utils import *
import pandas as pd
import numpy as np

def main():
    master = get_csv_file("perform logistic regression on? ")
    performLogReg(master)

# Creates the logistic regression model and tests accuracy
def performLogReg(dataframe):

    X = pd.DataFrame() # Create main dataframe
    Y = pd.DataFrame(index=np.arange(len(dataframe)), columns=['Result']) # Create result dataframe
    
    dataframe = populate_dataframe_with_average_values(dataframe)

    prospectsForUpcomingNBADraft = dataframe.loc[dataframe['NBA GP'] == '?'] # Create prospect dataframe
    for index, row in dataframe.iterrows():
        if (row['NBA GP'] == '?'):
            dataframe = dataframe.drop(index)
            Y = Y.drop(index)
            continue
        Y.loc[index, 'Result'] = is_nba_player(row)

    X = dataframe[LOG_REG_COLUMNS] # Tie only necessary stats to algorithm
    prospectStatsForUpcomingNBADraft = prospectsForUpcomingNBADraft[LOG_REG_COLUMNS]

    Y = Y.astype('int') # Cast all of Y to be an integer (0 or 1)

    X_train, X_test, Y_train, Y_test = getTrainTestSplit(X, Y) # Run train/test split
    
    logreg = LogisticRegression(max_iter=500)
    logreg.fit(X_train, Y_train.values.ravel())  # Fits model with data
    Y_pred = logreg.predict(X_test) # Make predictions on test data to get baseline accuracy
    
    makePredictionsForUpcomingNBAProspects(logreg, prospectStatsForUpcomingNBADraft, prospectsForUpcomingNBADraft, False)
    printCoefficientInformation(logreg)
    printConfusionMatrixForTestData(Y_test, Y_pred)

    return logreg

def getTrainTestSplit(X, Y):
    X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.8, shuffle=False)
    return X_train, X_test, Y_train, Y_test

if __name__ == "__main__":
    main()