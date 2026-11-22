# trees.py: gradient boosted trees on the same decks
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
from .common import SEED


def make_X_trees(df, columns=None):
    # raw columns only: trees choose their own split points, so no squared terms
    X = df[["avg_mana_value", "num_creatures", "num_lands"]].copy()
    dummies = pd.get_dummies(df["main_colors"], prefix="main_colors", dtype=float)
    X = pd.concat([X, dummies], axis=1)
    if columns is not None:
        X = X.reindex(columns=columns, fill_value=0.0)
    return X


def fit(train, max_depth=3, learning_rate=0.05, max_iter=300, seed=SEED):
    X = make_X_trees(train)
    y = train.wins / train.games  # win rate per deck
    model = HistGradientBoostingRegressor(
        max_depth=max_depth,
        learning_rate=learning_rate,
        max_iter=max_iter,
        random_state=seed,
    )
    model.fit(X, y, sample_weight=train.games)  # decks with more games count more
    return {"model": model, "cols": list(X.columns)}


def predict(fitted, df):
    X = make_X_trees(df, fitted["cols"])
    return fitted["model"].predict(X)
