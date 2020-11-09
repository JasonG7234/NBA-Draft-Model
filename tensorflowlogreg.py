from utils import *
import numpy as np
import pandas as pd
import tensorflow.compat.v1 as tf
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import train_test_split
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.python.keras.backend import set_session

def main():
    master = get_csv_file("perform logistic regression on? ")
    perform_tensorflow_log_reg(master)

def perform_tensorflow_log_reg(master):
    '''Creates the logistic regression model and tests accuracy using tensorflow'''

    X = pd.DataFrame() 
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

    X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.25, shuffle=True)

    #normed_X_train = normalize(X_train, X_train.describe().transpose())
    #normed_X_test = normalize(X_test, X_test.describe().transpose())

    sess = tf.Session()
    set_session(sess)

    model = build_model(X_train.shape[1])
    
    model.fit(
    X_train, Y_train,
    epochs=100, validation_split = 0.25)

    loss, accuracy, precision, recall = model.evaluate(X_test, Y_test, verbose=2)

    Y_pred = model.predict(X_test)

    make_predictions_for_upcoming_nba_prospects(model, prospects, False)
    print_accuracy_metrics_with_tensorflow(accuracy, precision, recall, loss)
    print_confusion_matrix_with_tensorflow(sess, Y_test, Y_pred)

def normalize(val, stats):
    val = (val - stats['mean']) / stats['std']
    return val
    
def build_model(n_cols):
    model = keras.Sequential([
        layers.Dense(64, activation='relu', input_shape=(n_cols,)),
        layers.Dense(64, activation='relu'),
        layers.Dense(1, activation='sigmoid')
    ])

    model.compile(loss='mse',
                optimizer='adam',
                metrics=['accuracy', tf.keras.metrics.Precision(), tf.keras.metrics.Recall()])

    return model

def print_coefficient_information_with_tensorflow(sess, model):
    vars = tf.trainable_variables()
    vars_vals = sess.run(vars)
    for var, val in zip(vars, vars_vals):
        print("var: {}, value: {}".format(var.name, val))

def print_confusion_matrix_with_tensorflow(sess, labels, predictions):
    
    print("----------------------------------")

    print(confusion_matrix(labels, predictions.round()))

def print_accuracy_metrics_with_tensorflow(accuracy, precision, recall, loss):
    print("----------------------------------")

    print("Accuracy:", accuracy)
    print("Precision:", precision)
    print("Recall:", recall)
    print("Loss:", loss)

if __name__ == "__main__":
    tf.compat.v1.disable_eager_execution()
    main()