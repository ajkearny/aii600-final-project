from pathlib import Path

import numpy as np
import pandas as pd

SEED = 0  # one number to make sure the random draw is the same each time

# the project's data folder (one level up from this models/ folder)
DATA = Path(__file__).parent.parent / "data"

# column names, exactly as they appear in data/mtg_data_clean.csv:
#   avg_mana_value  average mana value of the nonland cards
#   num_creatures   number of creatures
#   num_lands       number of lands
#   main_colors     the deck's colour pair, e.g. "BG"
#   wins, games     games won and games played by the deck
#   draft_id        the draft the deck came from (one draft can have several builds)


def load_decks(filename="mtg_data_clean.csv"):
    """Read the cleaned deck table: one row per deck."""
    # index_col=0: the first column in the file is only a row number (0, 1, 2, ...)
    # that pandas wrote when the file was saved, so we use it as the index, not as data
    return pd.read_csv(DATA / filename, index_col=0)


def fake_decks(n=20000, seed=SEED):
    """Made-up decks where we know the right answer, to test that the code finds it.

    The built-in "truth" is: win chance peaks at average mana value 2.9 and 17 lands,
    and each extra creature adds 0.05 on the logit scale.
    Columns have the same names as the real table.
    """
    rng = np.random.default_rng(seed)  # random number generator with a fixed seed

    # average mana value: normally distributed around 2.9 with a standard deviation of 0.4
    avg_mana_value = rng.normal(2.9, 0.4, n)
    # creatures: a whole number from 10 to 17 (the upper bound 18 is left out)
    num_creatures = rng.integers(10, 18, n)
    # lands: a whole number from 15 to 18 (the upper bound 19 is left out)
    num_lands = rng.integers(15, 19, n)

    # the true win chance on a logit scale: bump peaks at 2.9 mana value and 17 lands,
    # plus 0.05 per creature above or below 14
    logit = (0.3
             - 1.7 * (avg_mana_value - 2.9) ** 2
             - 0.1 * (num_lands - 17) ** 2
             + 0.05 * (num_creatures - 14))

    games = rng.integers(3, 8, n)  # games played by each deck (3 to 7)
    wins = rng.binomial(games, 1 / (1 + np.exp(-logit)))  # games won, drawn from the true win chance

    return pd.DataFrame({
        "draft_id": np.arange(n),
        "avg_mana_value": avg_mana_value,
        "num_creatures": num_creatures,
        "num_lands": num_lands,
        "games": games,
        "wins": wins,
        # not used in the truth, so models should find ~no effect
        "main_colors": rng.choice(["BG", "WG", "UG", "WB", "WR"], n),
    })


def split_by_draft(decks, test_fraction=0.25, seed=SEED):
    """Hold out a random 25% of drafts for testing; train on the rest.

    The table has no dates, so we split at random. We pick whole drafts, not single rows,
    so every build of the same draft is on the same side and the test stays unseen.
    The seed and the fraction go in decisions.md.
    """
    rng = np.random.default_rng(seed)
    drafts = decks.draft_id.unique()
    test_drafts = rng.choice(drafts, size=round(test_fraction * len(drafts)), replace=False)
    is_test = decks.draft_id.isin(test_drafts)
    return decks[~is_test], decks[is_test]


def make_X(df, columns=None):
    """Turn decks into a table of numbers: mana value, mana value squared, creatures,
    lands, lands squared, and 0/1 columns for colour pair.
    The squared terms let the curve rise and then fall."""
    X = pd.DataFrame({
        "avg_mana_value": df.avg_mana_value,
        "avg_mana_value_sq": df.avg_mana_value ** 2,
        "num_creatures": df.num_creatures,
        "num_creatures_sq": df.num_creatures ** 2,
        "num_lands": df.num_lands,
        "num_lands_sq": df.num_lands ** 2,
    })
    # colour pair is a category, so it becomes 0/1 columns; drop_first leaves one out as the reference
    dummies = pd.get_dummies(df["main_colors"], prefix="main_colors", drop_first=True, dtype=float)
    X = pd.concat([X, dummies], axis=1)
    if columns is not None:
        # make the test table have exactly the training columns, in the same order
        X = X.reindex(columns=columns, fill_value=0.0)
    return X


def error_per_100(test, pred):
    """Accuracy score: on average, how far off is the predicted win rate, in wins per 100 games.

    Smaller is better. Decks with more games count more (weights=games),
    because their real win rate is less noisy.
    """
    return 100 * np.average(np.abs(test.wins / test.games - pred), weights=test.games)


# how close a deck must be to a "peak" value to count as following the advice
PEAK_TOLERANCE = {"avg_mana_value": 0.2, "num_creatures": 1, "num_lands": 0}


def follows_advice(decks, best, train):
    """True for each deck that follows the advice on all three choices.

    - a peak (sweet spot): the deck is within PEAK_TOLERANCE of the best value
    - "lower is better": the deck is in the lowest quarter of training decks on that choice
    - "higher is better": the deck is in the highest quarter of training decks on that choice
    """
    ok = pd.Series(True, index=decks.index)
    for col, b in best.items():
        if b["shape"] == "peak":
            ok &= (decks[col] - b["best"]).abs() <= PEAK_TOLERANCE[col]
        elif b["shape"] == "lower is better":
            ok &= decks[col] <= train[col].quantile(0.25)
        else:
            ok &= decks[col] >= train[col].quantile(0.75)
    return ok


def value_per_100(test, follows):
    """Do test decks that follow the advice win more than test decks that played 17 lands?

    follows: True/False for each test deck (from follows_advice).
    Answer is in wins per 100 games. 'gain' is the extra wins per 100.
    """
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
