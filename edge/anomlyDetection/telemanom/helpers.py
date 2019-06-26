import sys
import numpy as np
from .globals import Config
import time
import pandas as pd

def load_train( config):
    """Load train data.

    Args:
        config (Config): configuration object

    Returns:
        X_train (np array): array of train inputs with dimensions [timesteps, l_s, input dimensions]
        y_train (np array): array of train outputs corresponding to true values following each sequence
    """
    try:
        data = np.load( config.trainFile)
    except IOError or ValueError:
        print( "Training File '%s' not found" % (config.trainFile, ))
        sys.exit(1)

    # shape, split data
    X_train, y_train = shape_data( config, data, shuffle=True)

    return X_train, y_train


def load_test( config):
    """Load test data.

    Args:
        config (Config): configuration object
        testFile (str): path of testing file

    Returns:
        X_test (np array): array of test inputs with dimensions [timesteps, l_s, input dimensions)
        y_test (np array): array of test outputs corresponding to true values following each sequence
    """
    try:
        data = np.load(config.testFile)
    except IOError or ValueError:
        print( "Testing File '%s' not found" % (config.testFile, ))
        sys.exit(1)

    # shape, split data
    X_test, y_test = shape_data( config, data)

    return X_test, y_test


def shape_data( config, arr, shuffle=False):
    """Shape raw input streams for ingestion into LSTM.
    `config.l_s` specifies the sequence length of prior timesteps fed into the model at each timestep t.

    Args:
        config (Config): configuration object
        arr (np.ndarray): array of input streams with dimensions [timesteps, input dimensions]
        shuffle (bool): this indicates data can be shuffled

    Returns:
        X (np.ndarray): array of inputs with dimensions [timesteps, l_s, input dimensions)
        y (np.ndarray): array of outputs corresponding to true values following each sequence.
            shape = [timesteps, n_predictions, 1)
    """

    d2 = config.l_s + config.n_predictions
    d1 = len( arr) - d2 + 1
    print( 'shape_data 预期产生大小:', (d1, d2, arr.shape[1]))
    data = np.empty( (d1, d2, arr.shape[1]), dtype=arr.dtype)
    for i in range( d1):
        data[i] = arr[i:i+d2]

    if shuffle:
        np.random.shuffle(data)

    X = data[:, :-config.n_predictions, :]
    y = data[:, -config.n_predictions:, 0]  # telemetry value is at position 0

    return X, y


def anom_stats(stats, anom, logger):
    """Log stats after processing of each stream.

    Args:
        stats (dict): Count of true positives, false positives, and false negatives from experiment
        anom (dict): contains all anomaly information for a given input stream
        logger (obj): logging object
    """

    logger.info("TP: %s  FP: %s  FN: %s" % (anom["true_positives"], anom["false_positives"], anom["false_negatives"]))
    logger.info('Total true positives: %s' % stats["true_positives"])
    logger.info('Total false positives: %s' % stats["false_positives"])
    logger.info('Total false negatives: %s\n' % stats["false_negatives"])


def final_stats( stats, logger):
    """Log final stats at end of experiment.

    Args:
        stats (dict): Count of true positives, false positives, and false negatives from experiment
        logger (obj): logging object
    """

    logger.info("Final Totals:")
    logger.info("-----------------")
    logger.info("True Positives: %s " % stats["true_positives"])
    logger.info("False Positives: %s " % stats["false_positives"])
    logger.info("False Negatives: %s\n" % stats["false_negatives"])
    try:
        logger.info("Precision: %s" % (float(stats["true_positives"]) /
                                        float(stats["true_positives"]+stats["false_positives"])))
        logger.info("Recall: %s" % (float(stats["true_positives"]) /
                                    float(stats["true_positives"]+stats["false_negatives"])))
    except ZeroDivisionError:
        logger.info("Precision: NaN")
        logger.info("Recall: NaN")
