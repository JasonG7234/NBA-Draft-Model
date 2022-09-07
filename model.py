import numpy as np
import pandas as pd
import tensorflow.compat.v1 as tf
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, log_loss, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.python.keras.backend import set_session

from utils import *

MACHINE_LEARNING_COLUMNS = ['Height','Draft Day Age','RSCI','SOS','BLK%','STL%','TRB%','FTr','3PAr','AST%','USG%','WS/40','BPM','AST/TOV', 'OFF RTG','DEF RTG','Hands-On Buckets','Pure Point Rating', '# Dunks', 'TS%']
CURRENT_YEAR = "2021-22"

TENSORFLOW_EPOCHS = 25
NODE_COUNT = 64
LOGREG_ITER = 500

def main():
    master = pd.read_csv("main.csv")
    sum_list = [0.0] * len(master.loc[master['Season'] == CURRENT_YEAR])
    for _ in range(10):
        x_train, x_test, y_train, y_test, prospects, norm_x_train, norm_x_test = get_train_test_split(master)
        gbm = perform_gradient_boosting(x_train, x_test, y_train, y_test, prospects)
        lr = perform_log_reg(norm_x_train, norm_x_test, y_train, y_test, prospects)
        tf = perform_tensorflow_log_reg(norm_x_train, norm_x_test, y_train, y_test, prospects)
        for i in range(len(prospects)):
            sum_list[i] = round(sum_list[i]+tf[i][0]+gbm[i]+lr[i], 3)
    prospects['Result'] = sum_list
    prospects.sort_values(by=['Result'], ascending=False)
    prospects.to_csv('modelv1.0.csv', index=False)

def get_train_test_split(master):
    master = master['Draft Pick'].replace('', 0)
    
    Y = pd.DataFrame(index=np.arange(len(master)), columns=['Result'])
    
    prospects = master.loc[master['Season'] == CURRENT_YEAR]
    for index, row in master.iterrows():
        if (row['Season'] == CURRENT_YEAR):
            master = master.drop(index)
            Y = Y.drop(index)
            continue
        Y.loc[index, 'Result'] = 1 if row['Draft Pick'] != 0 else 0
    
    print("# prospects: " + str(len(prospects)))
    X = master[MACHINE_LEARNING_COLUMNS]
    print_dataframe(X)
    Y=Y.astype('int')
    x_train, x_test, y_train, y_test = train_test_split(X, Y, test_size=0.25, shuffle=True)
    norm_x_train = normalize(x_train, x_train.describe().transpose())
    norm_x_test = normalize(x_test, x_test.describe().transpose())
    return x_train, x_test, y_train, y_test, prospects, norm_x_train, norm_x_test

def perform_tensorflow_log_reg(x_train, x_test, y_train, y_test, prospects):
    """Creates the logistic regression model and tests accuracy using tensorflow"""

    sess = tf.Session()
    set_session(sess)

    model = build_model(x_train.shape[1])
    
    model.fit(
    x_train, y_train,
    epochs=TENSORFLOW_EPOCHS, validation_split = 0.25)

    loss, accuracy, precision, recall = model.evaluate(x_test, y_test, verbose=2)

    y_pred = model.predict(x_test)

    l = make_predictions_for_upcoming_nba_prospects(model, prospects, "Tensorflow", False)
    print_accuracy_metrics(accuracy, precision, recall, loss)
    print_confusion_matrix(y_test, y_pred)
    print("\n")
    
    return l

def normalize(val, stats):
    val = (val - stats['mean']) / stats['std']
    return val
    
def build_model(n_cols):
    model = keras.Sequential([
        layers.Dense(NODE_COUNT, activation='relu', input_shape=(n_cols,)),
        layers.Dense(NODE_COUNT, activation='relu'),
        layers.Dense(1, activation='sigmoid')
    ])

    model.compile(loss='mse',
                optimizer='adam',
                metrics=['accuracy', tf.keras.metrics.Precision(), tf.keras.metrics.Recall()])

    return model

def perform_log_reg(x_train, x_test, y_train, y_test, prospects):
    """Creates the logistic regression model and tests accuracy"""

    logreg = LogisticRegression(solver='liblinear', max_iter=LOGREG_ITER)
    logreg.fit(x_train, y_train.values.ravel())
    y_pred = logreg.predict(x_test)
    
    l = make_predictions_for_upcoming_nba_prospects(logreg, prospects, "LogReg", False)
    print_coefficient_information(logreg)
    print_accuracy_metrics(accuracy_score(y_test, y_pred), precision_score(y_test, y_pred), recall_score(y_test, y_pred), log_loss(y_test, y_pred))
    print_confusion_matrix(y_test, y_pred)
    return l

def perform_gradient_boosting(x_train, x_test, y_train, y_test, prospects):
    """Creates the Gradient Boosting Machine and tests accuracy"""

    print("\n\n")
    print("----------------------------------")
    classifier = GradientBoostingClassifier()
    classifier.fit(x_train, y_train.values.ravel())
    print("GBM Training score: ", classifier.score(x_train, y_train))
    print("GBM Testing score: ", classifier.score(x_test, y_test))
    y_pred = classifier.predict(x_test)

    l = make_predictions_for_upcoming_nba_prospects(classifier, prospects, "GBM", False)
    print(l)
    print_confusion_matrix(y_test, y_pred)
    print(classification_report(y_test, y_pred))
    return l


def print_coefficient_information(logreg):
    print("----------------------------------")
    print("Coefficient Information:")

    for i in range(len(MACHINE_LEARNING_COLUMNS)):

        logreg_coefficients = logreg.coef_

        current_feature = MACHINE_LEARNING_COLUMNS[i]
        current_coefficient = logreg_coefficients[0][i]

        print(current_feature + ': ' + str(current_coefficient))

def print_confusion_matrix(labels, predictions):
    
    print("----------------------------------")
    print("Confusion Matrix: ")
    
    print(confusion_matrix(labels, predictions.round()))

def print_accuracy_metrics(accuracy, precision, recall, loss):
    print("----------------------------------")

    print("Accuracy:", accuracy)
    print("Precision:", precision)
    print("Recall:", recall)
    print("Loss:", loss)
    
def make_predictions_for_upcoming_nba_prospects(logreg, prospects, row_name, is_round):
    predictions = logreg.predict(prospects[MACHINE_LEARNING_COLUMNS])
    return predictions.tolist() if is_round else predictions

if __name__ == "__main__":
    tf.compat.v1.disable_eager_execution()
    main()
