from utils import *
import numpy as np
import pandas as pd
import seaborn as sns
import sklearn as sk
import tensorflow.compat.v1 as tf
import tensorflow_docs as tfdocs
from tensorflow import keras
from tensorflow.keras import layers


def main():
    master = get_csv_file("perform logistic regression on? ")
    performLogReg(master)

# Creates the logistic regression model and tests accuracy using tensorflow
def performLogReg(dataframe):
    dataframe['Result'] = ""

    prospectsForUpcomingNBADraft = dataframe.loc[dataframe['NBA GP'] == '?'] # Create prospect dataframe
    dataframe = dataframe.drop(prospectsForUpcomingNBADraft.index)
    for index, row in dataframe.iterrows():
        dataframe.loc[index, 'Result'] = is_nba_player(row)

    dataframe = dataframe.astype({'Result': float})
    dataframe = dataframe.select_dtypes(include=[np.float])
    prospects = prospectsForUpcomingNBADraft.select_dtypes(include=[np.float])

    print(dataframe)

    dataframe = populate_dataframe_with_average_values(dataframe)
    prospects = populate_dataframe_with_average_values(prospects)

    train = dataframe.sample(frac = 0.75, random_state = 0)
    test = dataframe.drop(train.index)

    train_stats = train.describe()
    train_stats.pop('Result')
    train_stats = train_stats.transpose()
    print(train_stats)

    train_labels = train.pop('Result')
    test_labels = test.pop('Result')
    #prospects_labels = prospects.pop('Result')

    normed_train_data = normalize(train, train_stats)
    normed_test_data = normalize(test, train_stats)
    normed_prospect_data = normalize(prospects, train_stats)

    model = build_model(train)
    
    history = model.fit(
    normed_train_data, train_labels,
    epochs=1000, validation_split = 0.2, verbose=0)

    loss, mae, mse = model.evaluate(normed_test_data, test_labels, verbose=2)

    test_predictions = model.predict(normed_test_data).flatten()
    
    make_predictions_for_upcoming_nba_prospects(model, prospects, prospectsForUpcomingNBADraft, True)
    #printCoefficientInformationWithTensorflow(model)
    printAccuracyMetricsWithTensorflow(test_labels, test_predictions)
    printConfusionMatrixWithTensorflow(test_labels, test_predictions)
    

def printCoefficientInformationWithTensorflow(model):
    vars = tf.trainable_variables()
    print(vars) 
    sess = tf.Session()
    with sess.as_default():
        vars_vals = sess.run(vars)
        for var, val in zip(vars, vars_vals):
            print("var: {}, value: {}".format(var.name, val))

def printConfusionMatrixWithTensorflow(labels, predictions):
    con = tf.confusion_matrix(labels = labels, predictions = predictions)
    sess = tf.Session()
    with sess.as_default():
        print(sess.run(con))

def printAccuracyMetricsWithTensorflow(labels, predictions):
    print(tf.metrics.accuracy(labels, predictions))
    print(sk.metrics.accuracy())

def normalize(val, stats):
    val = (val - stats['mean']) / stats['std']
    return val

def build_model(train):
  model = keras.Sequential([
    layers.Dense(64, activation='relu', input_shape=[len(train.keys())]),
    layers.Dense(64, activation='relu'),
    layers.Dense(1)
  ])

  optimizer = tf.keras.optimizers.RMSprop(0.001)

  model.compile(loss='mse',
                optimizer=optimizer,
                metrics=['mae', 'mse'])

  return model

if __name__ == "__main__":
    main()