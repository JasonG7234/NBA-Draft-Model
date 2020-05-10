from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn import metrics
from utils import *
import pandas as pd
import numpy as np

def main():
    master = getCSVFile("perform logistic regression on? ")
    performLogReg(master)

# Creates the logistic regression model and tests accuracy
def performLogReg(dataframe):
    X = pd.DataFrame()
    # Update if new stats are added
    dataframe = dataframe[LOG_REG_COLUMNS] # Features
    dataframe = dataframe.replace('', np.nan)
    for index, row in dataframe.iterrows():
        if (row.isnull().values.all()):
            dataframe = dataframe.drop(index)
        elif (row.isnull().values.any()):
            dataframe = dataframe.fillna(dataframe.mean())
    X = dataframe
    Y = pd.DataFrame(index=np.arange(len(X)), columns=np.arange(0))
    Y['Result'] = '' # Target Variable

    printEveryElement(X)

    X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, shuffle=True)
    logreg = LogisticRegression()

    logreg.fit(X_train, Y_train.values.ravel())  # Fits model with data
    Y_pred = logreg.predict(X_test)

    confusionMatrix = metrics.confusion_matrix(Y_test, Y_pred)  # Diagonals tell you correct predictions

    # Code below prints model accuracy information
    print('Coefficient Information:')

    for i in range(len(LOG_REG_COLUMNS)):  # Prints each feature next to its corresponding coefficient in the model

        logregCoefficients = logreg.coef_

        currentFeature = LOG_REG_COLUMNS[i]
        currentCoefficient = logregCoefficients[0][i]

        print(currentFeature + ': ' + str(currentCoefficient))

    print('----------------------------------')

    print("Accuracy:", metrics.accuracy_score(Y_test, Y_pred))
    print("Precision:", metrics.precision_score(Y_test, Y_pred))
    print("Recall:", metrics.recall_score(Y_test, Y_pred))

    print('----------------------------------')

    print('Confusion Matrix:')
    print(confusionMatrix)

    return logreg

def printEveryElement(dataframe):
    for index, row in dataframe.iterrows():
        for col in LOG_REG_COLUMNS:
            if(row[col] == ''):
                print("Here is a possible culprit! Index " + str(index) + " Column " + col)

if __name__ == "__main__":
    main()