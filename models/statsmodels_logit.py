# statsmodels_logit.py: main model (tasks 4d, 4e). Logistic regression for "wins out of games".
import numpy as np
import statsmodels.api as sm
import statsmodels.formula.api as smf

# rate = wins/games. I(x**2) is x squared. C(...) marks a category.
FORMULA = (
    "rate ~ avg_mana_value + I(avg_mana_value**2) + num_creatures + I(num_creatures**2)"
    " + num_lands + I(num_lands**2) + C(main_colors)"
)


def fit(train):
    d = train.assign(rate=train.wins / train.games)
    return smf.glm(
        FORMULA,
        data=d,
        family=sm.families.Binomial(),  # binomial = "wins out of games"
        freq_weights=d.games,  # decks with more games count more
    ).fit()


def predict(res, df):
    return res.predict(df).to_numpy()  # win probability per deck, between 0 and 1


# the three deck choices we give advice on, and the step between values we try for each
STEPS = {"avg_mana_value": 0.1, "num_creatures": 1, "num_lands": 1}


def data_grid(train, col, step, min_decks=500):
    """The values of one column that real decks actually use.

    Round each deck's value to the step (e.g. 2.43 -> 2.4) and keep the values that at least
    min_decks training decks have. Advice outside these values would be a guess.
    """
    rounded = ((train[col] / step).round() * step).round(2)
    counts = rounded.value_counts().sort_index()
    return counts[counts >= min_decks].index.to_numpy()


def curve(res, train, col, grid):
    """Predicted wins per 100 games if every training deck had this value of col.

    Everything else about each deck stays as it really is, so this shows the effect of col alone.
    """
    return [100 * np.average(res.predict(train.assign(**{col: v})), weights=train.games)
            for v in grid]


def best_values(res, train):
    """For each deck choice: the value with the highest predicted win rate inside the data,
    and the shape of the curve.

    shape is "peak" if the best value is in the middle (a real sweet spot),
    "lower is better" if it is the smallest value real decks use,
    "higher is better" if it is the largest.
    """
    p = res.params
    out = {}
    for col, step in STEPS.items():
        grid = data_grid(train, col, step)
        wins = curve(res, train, col, grid)
        i = int(np.argmax(wins))
        if 0 < i < len(grid) - 1:
            shape = "peak"
        elif i == 0:
            shape = "lower is better"
        else:
            shape = "higher is better"
        b1, b2 = p[col], p[f"I({col} ** 2)"]
        out[col] = {
            "best": grid[i],
            "shape": shape,
            "grid": grid,
            "wins_per_100": wins,
            # the textbook formula for the top of a curve b1*x + b2*x^2. It is only a peak
            # if b2 < 0; if b2 > 0 the curve bends up and this is the WORST value instead.
            "formula_peak": -b1 / (2 * b2),
            "bends_down": bool(b2 < 0),
        }
    return out


def colour_vector(res, colour):
    """Picks out one colour pair's coefficient. The reference pair (the first alphabetically)
    has no coefficient of its own: its effect is 0, so its vector is all zeros."""
    v = np.zeros(len(res.params))
    name = f"C(main_colors)[T.{colour}]"
    if name in res.params.index:
        v[res.params.index.get_loc(name)] = 1
    return v


def best_colour(res, train):
    """Rank the colour pairs by predicted wins per 100 if every training deck were that pair.

    Also tests whether the best pair is really better than the runner-up:
    p < 0.05 means a clear winner; otherwise the top two are a tie.
    """
    colours = sorted(train.main_colors.unique())
    wins = [100 * np.average(res.predict(train.assign(main_colors=c)), weights=train.games)
            for c in colours]
    ranking = sorted(zip(colours, wins), key=lambda cw: cw[1], reverse=True)
    best, runner_up = ranking[0][0], ranking[1][0]
    contrast = colour_vector(res, best) - colour_vector(res, runner_up)
    p_value = float(np.squeeze(res.t_test(contrast).pvalue))
    return {"best": best, "runner_up": runner_up, "p_vs_runner_up": p_value, "ranking": ranking}
