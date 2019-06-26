import math

import numpy as np
from keras.models import Sequential, load_model
from keras.callbacks import History, EarlyStopping
from keras.layers.recurrent import LSTM
from keras.layers.core import Dense, Activation, Dropout

from .globals import Config

# os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # suppress tensorflow CPU speedup warnings


def get_model( config, X_train = None, y_train = None) -> Sequential:
    """Train LSTM model according to specifications in config.yaml or load pre-trained model.

    Args:
        config (Config): configuration object
        X_train (np array): numpy array of training inputs with dimensions [timesteps, l_s, input dimensions)
        y_train (np array): numpy array of training outputs corresponding to true values following each sequence

    Returns:
        model (Sequential): Trained Keras LSTM model
    """

    if not config.train:
        config.info.logger.info("Loading pre-trained model")
        return load_model( config.info.modelPath)

    else:
        config.info.logger.info("Training new model from scratch.")

        cbs = [ History(), EarlyStopping(monitor='val_loss', patience=config.patience,
                min_delta=config.min_delta, verbose=0)]

        model = Sequential()

        model.add(LSTM(
            config.layers[0],
            input_shape=(None, X_train.shape[2]),
            return_sequences=True))
        model.add(Dropout(config.dropout))

        model.add(LSTM(
            config.layers[1],
            return_sequences=False))
        model.add(Dropout(config.dropout))

        model.add(Dense(config.n_predictions))
        model.add(Activation("linear"))

        model.compile(loss=config.loss_metric, optimizer=config.optimizer)

        model.fit( X_train, y_train, batch_size=config.lstm_batch_size, epochs=config.epochs,
            validation_split=config.validation_split, callbacks=cbs, verbose=True)

        return model


def predict_in_batches( config, model, X_test):
    """Used trained LSTM model to predict test data arriving in batches (designed to
    mimic a spacecraft downlinking schedule).

    Args:
        config (Config): configuration object
        model (obj): trained Keras model
        X_test (np.ndarray): numpy array of test inputs with dimensions [timesteps, l_s, input dimensions)

    Returns:
        y_hat (np array): predicted test values for each timestep in y_test
    """

    y_hat = np.array([])

    num_batches = int( math.floor( X_test.shape[0] / config.batch_size))
    if num_batches < 0:
        raise ValueError( "l_s (%s) too large for stream with length %s."
                          % ( config.l_s, X_test.shape[0]))

    # simulate data arriving in batches
    for i in range(1, num_batches+2):
        prior_idx = (i-1) * config.batch_size
        idx = i * config.batch_size
        if i == num_batches+1:
            idx = X_test.shape[0]  # remaining values won't necessarily equal batch size

        X_test_period = X_test[prior_idx:idx]
        y_hat_period = model.predict(X_test_period)
        y_hat = np.append(y_hat, y_hat_period[:, 0])

    return y_hat
