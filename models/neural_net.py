# a small neural network (MLP)
from sklearn.neural_network import MLPRegressor
from .common import SEED
from .trees import make_X_trees


def fit(train, hidden=(16, 8), seed=SEED):
    X = make_X_trees(train)
    mean, sd = X.mean(), X.std()
    Z = (X - mean) / sd
    y = train.wins / train.games
    model = MLPRegressor(
        hidden_layer_sizes=hidden, max_iter=500, early_stopping=True, random_state=seed
    )
    model.fit(Z, y)
    return {"model": model, "cols": list(X.columns), "mean": mean, "sd": sd}


def predict(fitted, df):
    X = make_X_trees(df, fitted["cols"])
    return fitted["model"].predict((X - fitted["mean"]) / fitted["sd"]).clip(0, 1)
