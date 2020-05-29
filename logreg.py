from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn import metrics, preprocessing
from utils import *
import pandas as pd
import numpy as np

def main():
    master = getCSVFile("perform logistic regression on? ")
    performLogReg(master)

# Creates the logistic regression model and tests accuracy
def performLogReg(dataframe):

    X = pd.DataFrame() # Create main dataframe
    Y = pd.DataFrame(index=np.arange(len(dataframe)), columns=['Result']) # Create result dataframe
    
    dataframe = populateDataFrameWithAverageValues(dataframe)

    prospectsForUpcomingNBADraft = dataframe.loc[dataframe['NBA GP'] == '?'] # Create prospect dataframe
    for index, row in dataframe.iterrows():
        if (row['NBA GP'] == '?'):
            dataframe = dataframe.drop(index)
            Y = Y.drop(index)
            continue
        Y.loc[index, 'Result'] = isNBAPlayer(row)

    X = dataframe[LOG_REG_COLUMNS] # Tie only necessary stats to algorithm
    prospectStatsForUpcomingNBADraft = prospectsForUpcomingNBADraft[LOG_REG_COLUMNS]

    Y = Y.astype('int') # Cast all of Y to be an integer (0 or 1)

    X_train, X_test, Y_train, Y_test = getTrainTestSplit(X, Y) # Run train/test split
    
    logreg = LogisticRegression(max_iter=500)
    logreg.fit(X_train, Y_train.values.ravel())  # Fits model with data
    Y_pred = logreg.predict(X_test) # Make predictions on test data to get baseline accuracy
    
    makePredictionsForUpcomingNBAProspects(logreg, prospectStatsForUpcomingNBADraft, prospectsForUpcomingNBADraft)
    printCoefficientInformation(logreg)
    printConfusionMatrixForTestData(Y_test, Y_pred)

    return logreg

def populateDataFrameWithAverageValues(df):
    df = df.replace('', np.nan)
    return df.fillna(df.mean())

def getTrainTestSplit(X, Y):
    X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.5, shuffle=False)
    return X_train, X_test, Y_train, Y_test

def makePredictionsForUpcomingNBAProspects(logreg, prospectStats, prospects):
    predictions = logreg.predict(prospectStats)
    prospects['NBA Player?'] = predictions
    prospects.to_csv('upcomingProspects.csv', index=False)

def printCoefficientInformation(logreg):
    print('Coefficient Information:')

    for i in range(len(LOG_REG_COLUMNS)):  # Prints each feature next to its corresponding coefficient in the model

        logregCoefficients = logreg.coef_

        currentFeature = LOG_REG_COLUMNS[i]
        currentCoefficient = logregCoefficients[0][i]

        print(currentFeature + ': ' + str(currentCoefficient))

def printConfusionMatrixForTestData(test, pred):
    confusionMatrix = metrics.confusion_matrix(test, pred)  # Diagonals tell you correct predictions
    
    print('----------------------------------')

    print("Accuracy:", metrics.accuracy_score(test, pred))
    print("Precision:", metrics.precision_score(test, pred))
    print("Recall:", metrics.recall_score(test, pred))

    print('----------------------------------')

    print('Confusion Matrix:')
    print(confusionMatrix)

if __name__ == "__main__":
    main()