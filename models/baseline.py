# predict the same win rate for every deck (task 4b)
import numpy as np


def fit(train):
    # average win rate over all training games = total wins / total games
    return train.wins.sum() / train.games.sum()


def predict(rate, df):
    return np.full(len(df), rate)
