# main model (tasks 4d, 4e). Logistic regression for "wins out of games".
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
        family=sm.families.Binomial(),
        freq_weights=d.games,  # decks with more games count more
    ).fit()


def predict(res, df):
    return res.predict(df).to_numpy()


# the three deck choices we give advice on, and the step between values we try for each
STEPS = {"avg_mana_value": 0.1, "num_creatures": 1, "num_lands": 1}


# values of a column that real decks use. round to the step (2.43 -> 2.4) and
# only keep values that at least min_decks training decks have
def data_grid(train, col, step, min_decks=500):
    rounded = ((train[col] / step).round() * step).round(2)
    counts = rounded.value_counts().sort_index()
    return counts[counts >= min_decks].index.to_numpy()


# predicted wins per 100 if every training deck had this value of col,
# with everything else about the deck left alone
def curve(res, train, col, grid):
    wins = []
    for v in grid:
        pred = res.predict(train.assign(**{col: v}))
        wins.append(100 * np.average(pred, weights=train.games))
    return wins


# best value for each deck choice and what the curve looks like
# peak = best value is in the middle, otherwise it is at one of the ends
def best_values(res, train):
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
            # if b2 < 0; if b2 > 0 the curve bends up and this is the worst value instead.
            "formula_peak": -b1 / (2 * b2),
            "bends_down": bool(b2 < 0),
        }
    return out


# vector with a 1 at this colour pair's coefficient, for the t test below
# the reference pair has no coefficient so it stays all zeros
def colour_vector(res, colour):
    v = np.zeros(len(res.params))
    name = f"C(main_colors)[T.{colour}]"
    if name in res.params.index:
        v[res.params.index.get_loc(name)] = 1
    return v


# rank the colour pairs by predicted wins per 100, then test the best pair
# against the runner-up. p < 0.05 means the best one is really better
def best_colour(res, train):
    ranking = []
    for c in sorted(train.main_colors.unique()):
        pred = res.predict(train.assign(main_colors=c))
        ranking.append((c, 100 * np.average(pred, weights=train.games)))
    ranking.sort(key=lambda x: x[1], reverse=True)

    best = ranking[0][0]
    runner_up = ranking[1][0]
    contrast = colour_vector(res, best) - colour_vector(res, runner_up)
    p_value = float(np.squeeze(res.t_test(contrast).pvalue))
    return {"best": best, "runner_up": runner_up, "p_vs_runner_up": p_value, "ranking": ranking}
