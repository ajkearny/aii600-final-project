# sgd_logit.py: the same logistic regression, fitted by stochastic gradient descent
# the way the class slides write it: theta <- theta - alpha * gradient, on a random batch B.
import numpy as np
from .common import make_X, SEED


def sigmoid(z):
    return 1 / (1 + np.exp(-z))


def design(X, mean, sd):
    # standardise each column (so one learning rate suits all of them),
    # then add a column of ones for the intercept theta_0, as in the slides' design matrix
    Z = ((X - mean) / sd).to_numpy()
    return np.column_stack([np.ones(len(Z)), Z])


def fit(train, alpha=0.5, epochs=200, batch_size=256, seed=SEED):
    rng = np.random.default_rng(seed)
    X = make_X(train)
    cols, mean, sd = (
        list(X.columns),
        X.mean(),
        X.std(),
    )  # learned from training data only
    Z = design(X, mean, sd)
    wins, games = train.wins.to_numpy(), train.games.to_numpy()
    theta = np.zeros(Z.shape[1])  # start with all parameters at 0
    n = len(Z)

    for epoch in range(epochs):  # one epoch = one pass over the data
        order = rng.permutation(n)  # shuffle first (the slides say to)
        for start in range(0, n, batch_size):
            b = order[start : start + batch_size]  # the batch B
            p = sigmoid(Z[b] @ theta)  # predicted win chance per deck
            # slides: gradient = -X^T (y - p). Here y -> wins and p -> games * p.
            # dividing by the games in the batch gives the average over games
            gradient = -Z[b].T @ (wins[b] - games[b] * p) / games[b].sum()
            theta = theta - alpha * gradient  # alpha = learning rate
    return {"theta": theta, "cols": cols, "mean": mean, "sd": sd}


def predict(fitted, df):
    X = make_X(df, fitted["cols"])
    return sigmoid(design(X, fitted["mean"], fitted["sd"]) @ fitted["theta"])
