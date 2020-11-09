from utils import *
import numpy as np
import pandas as pd
import tensorflow.compat.v1 as tf
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import train_test_split
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.python.keras.backend import set_session

TENSORFLOW_EPOCHS = 50
NODE_COUNT = 32
LOGREG_ITER = 500

def main():
    master = get_csv_file("perform logistic regression on? ")
    x_train, x_test, y_train, y_test, prospects = get_train_test_split(master)
    while True:
        is_tensorflow = input("Do you want to utilize tensorflow with this model? Enter 'yes' or 'no': ").strip()
        if (is_tensorflow == 'yes'):
                perform_tensorflow_log_reg(x_train, x_test, y_train, y_test, prospects)
                break
        elif (is_tensorflow == 'no'):
                perform_log_reg(x_train, x_test, y_train, y_test, prospects)
                break
        else:
                print("ERROR - That is not a valid input. Please try again.")

def get_train_test_split(master):
    
    Y = pd.DataFrame(index=np.arange(len(master)), columns=['Result'])
    
    master = populate_dataframe_with_average_values(master)

    prospects = master.loc[master['NBA GP'] == '?']
    for index, row in master.iterrows():
        if (row['NBA GP'] == '?'):
            master = master.drop(index)
            Y = Y.drop(index)
            continue
        Y.loc[index, 'Result'] = is_nba_player(row)
        
    X = master[LOG_REG_COLUMNS]
    Y = Y.astype('int')

    x_train, x_test, y_train, y_test = train_test_split(X, Y, test_size=0.25, shuffle=True)

    return x_train, x_test, y_train, y_test, prospects

def perform_tensorflow_log_reg(x_train, x_test, y_train, y_test, prospects):
    """Creates the logistic regression model and tests accuracy using tensorflow"""

    normed_x_train = normalize(x_train, x_train.describe().transpose())
    normed_x_test = normalize(x_test, x_test.describe().transpose())

    sess = tf.Session()
    set_session(sess)

    model = build_model(x_train.shape[1])
    
    model.fit(
    normed_x_train, y_train,
    epochs=TENSORFLOW_EPOCHS, validation_split = 0.25)

    loss, accuracy, precision, recall = model.evaluate(normed_x_test, y_test, verbose=2)

    y_pred = model.predict(normed_x_test)

    make_predictions_for_upcoming_nba_prospects(model, prospects, False)
    print_accuracy_metrics(accuracy, precision, recall, loss)
    print_confusion_matrix(y_test, y_pred)

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
    
    make_predictions_for_upcoming_nba_prospects(logreg, prospects, False)
    print_coefficient_information(logreg)
    print_accuracy_metrics(metrics.accuracy_score(y_test, y_pred), metrics.precision_score(y_test, y_pred), metrics.recall_score(y_test, y_pred), metrics.log_loss(y_test, y_pred))
    print_confusion_matrix(y_test, y_pred)


def print_coefficient_information(logreg):
    print("----------------------------------")
    print("Coefficient Information:")

    for i in range(len(LOG_REG_COLUMNS)):

        logreg_coefficients = logreg.coef_

        current_feature = LOG_REG_COLUMNS[i]
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

if __name__ == "__main__":
    tf.compat.v1.disable_eager_execution()
    main()
