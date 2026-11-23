from pathlib import Path

import numpy as np
import pandas as pd

SEED = 0  # one number to make sure the random draw is the same each time

# the project's data folder (one level up from this models/ folder)
DATA = Path(__file__).parent.parent / "data"


# one row per deck. first column in the csv is just the old row number
def load_decks(filename="mtg_data_clean.csv"):
    return pd.read_csv(DATA / filename, index_col=0)


# fake decks where we set the answer ourselves, to check the model can find it
# win chance peaks at 2.9 mana value and 17 lands, +0.05 logit per creature
# colour pair does nothing here
def fake_decks(n=20000, seed=SEED):
    rng = np.random.default_rng(seed)

    avg_mana_value = rng.normal(2.9, 0.4, n)
    num_creatures = rng.integers(10, 18, n)  # 10 to 17
    num_lands = rng.integers(15, 19, n)  # 15 to 18

    logit = (
        0.3
        - 1.7 * (avg_mana_value - 2.9) ** 2
        - 0.1 * (num_lands - 17) ** 2
        + 0.05 * (num_creatures - 14)
    )

    games = rng.integers(3, 8, n)  # 3 to 7
    wins = rng.binomial(games, 1 / (1 + np.exp(-logit)))

    return pd.DataFrame(
        {
            "draft_id": np.arange(n),
            "avg_mana_value": avg_mana_value,
            "num_creatures": num_creatures,
            "num_lands": num_lands,
            "games": games,
            "wins": wins,
            "main_colors": rng.choice(["BG", "WG", "UG", "WB", "WR"], n),
        }
    )


# random 25% of drafts go to test. split on draft_id not rows, because one draft
# can have a few builds and they all need to be on the same side
def split_by_draft(decks, test_fraction=0.25, seed=SEED):
    rng = np.random.default_rng(seed)
    drafts = decks.draft_id.unique()
    test_drafts = rng.choice(
        drafts, size=round(test_fraction * len(drafts)), replace=False
    )
    is_test = decks.draft_id.isin(test_drafts)
    return decks[~is_test], decks[is_test]


# feature table for the SGD model: the three deck numbers, their squares,
# and 0/1 columns for colour pair
def make_X(df, columns=None):
    X = pd.DataFrame(
        {
            "avg_mana_value": df.avg_mana_value,
            "avg_mana_value_sq": df.avg_mana_value**2,
            "num_creatures": df.num_creatures,
            "num_creatures_sq": df.num_creatures**2,
            "num_lands": df.num_lands,
            "num_lands_sq": df.num_lands**2,
        }
    )
    # first pair is dropped as the reference
    dummies = pd.get_dummies(
        df["main_colors"], prefix="main_colors", drop_first=True, dtype=float
    )
    X = pd.concat([X, dummies], axis=1)
    if columns is not None:
        # make the test table have exactly the training columns, in the same order
        X = X.reindex(columns=columns, fill_value=0.0)
    return X


# how far off the predicted win rate is on average, in wins per 100 games
# weighted by games since a deck with 7 games is less noisy than one with 3
def error_per_100(test, pred):
    return 100 * np.average(np.abs(test.wins / test.games - pred), weights=test.games)


# how close a deck must be to a "peak" value to count as following the advice
PEAK_TOLERANCE = {"avg_mana_value": 0.2, "num_creatures": 1, "num_lands": 0}


# True/False per deck: does it follow the advice on all three choices
# peak -> within the tolerance of the best value
# lower/higher is better -> in the bottom/top quarter of the training decks
def follows_advice(decks, best, train):
    ok = pd.Series(True, index=decks.index)
    for col, b in best.items():
        if b["shape"] == "peak":
            ok &= (decks[col] - b["best"]).abs() <= PEAK_TOLERANCE[col]
        elif b["shape"] == "lower is better":
            ok &= decks[col] <= train[col].quantile(0.25)
        else:
            ok &= decks[col] >= train[col].quantile(0.75)
    return ok


# win rate of test decks that follow the advice vs test decks on 17 lands
def value_per_100(test, follows):
    near = test[follows]
    base = test[test.num_lands == 17]
    near_rate = 100 * near.wins.sum() / near.games.sum()
    base_rate = 100 * base.wins.sum() / base.games.sum()
    return {
        "follows_advice": near_rate,
        "baseline": base_rate,
        "gain": near_rate - base_rate,
        "n_follow": len(near),
        "n_base": len(base),
    }
