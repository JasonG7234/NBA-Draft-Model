from utils import *
import numpy as np
import pandas as pd
import seaborn as sns
import sklearn as sk
import tensorflow.compat.v1 as tf
import tensorflow_docs as tfdocs
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.python.keras.backend import set_session

def main():
    master = get_csv_file("perform logistic regression on? ")
    perform_tensorflow_log_reg(master)

def perform_tensorflow_log_reg(dataframe):
    '''Creates the logistic regression model and tests accuracy using tensorflow'''

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

    sess = tf.Session()
    set_session(sess)
    model = build_model(train)
    
    model.fit(
    normed_train_data, train_labels,
    epochs=1000, validation_split = 0.25, verbose=0)

    loss, accuracy, precision, recall = model.evaluate(normed_test_data, test_labels, verbose=2)

    test_predictions = model.predict(normed_test_data)
    
    make_predictions_for_upcoming_nba_prospects(model, prospects, prospectsForUpcomingNBADraft, False)
    #print_coefficient_information_with_tensorflow(sess, model)
    print_accuracy_metrics_with_tensorflow(accuracy, precision, recall, loss)
    #printConfusionMatrixWithTensorflow(test_labels, test_predictions)

def normalize(val, stats):
    val = (val - stats['mean']) / stats['std']
    return val
    
def build_model(train):
  model = keras.Sequential([
    layers.Dense(64, activation='relu', input_shape=[len(train.keys())]),
    layers.Dense(64, activation='relu'),
    layers.Dense(1)
  ])

  model.compile(loss='mse',
                optimizer=tf.keras.optimizers.RMSprop(0.001),
                metrics=[tf.keras.metrics.Accuracy(), tf.keras.metrics.Precision(), tf.keras.metrics.Recall()])

  return model

def print_coefficient_information_with_tensorflow(sess, model):
    vars = tf.trainable_variables()
    vars_vals = sess.run(vars)
    for var, val in zip(vars, vars_vals):
        print("var: {}, value: {}".format(var.name, val))

def printConfusionMatrixWithTensorflow(labels, predictions):
    v1 = tf.compat.v1
    con = v1.confusion_matrix(labels = labels, predictions = predictions)
    sess = v1.Session()
    with sess.as_default():
        print(sess.run(con))

def print_accuracy_metrics_with_tensorflow(accuracy, precision, recall, loss):
    print("----------------------------------")

    print("Accuracy:", tf.keras.metrics.Accuracy().result())
    print("Precision:", tf.keras.metrics.Precision().result())
    print("Recall:", recall)
    print("Loss:", loss)

    print("----------------------------------")

if __name__ == "__main__":
    tf.compat.v1.disable_eager_execution()
    main()