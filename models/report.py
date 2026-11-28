# fits every model and prints the results in one go, used by models.ipynb
import pandas as pd

from . import baseline, common, neural_net, sgd_logit, statsmodels_logit, trees


# real win rate per 100 of the test decks at each value of col
def test_rates(test, col, step):
    rounded = ((test[col] / step).round() * step).round(2)
    g = test.groupby(rounded)[["wins", "games"]].sum()
    return 100 * g.wins / g.games


def final_results(train, test):
    # fit every method on the training decks only
    base = baseline.fit(train)
    sml = statsmodels_logit.fit(train)
    tree = trees.fit(train)
    net = neural_net.fit(train)
    sgd = sgd_logit.fit(train)
    best = statsmodels_logit.best_values(sml, train)
    colour = statsmodels_logit.best_colour(sml, train)

    # error of each model on the test decks, wins per 100 games
    errors = pd.Series(
        {
            "baseline": common.error_per_100(test, baseline.predict(base, test)),
            "statsmodels logit": common.error_per_100(
                test, statsmodels_logit.predict(sml, test)
            ),
            "sgd logit": common.error_per_100(test, sgd_logit.predict(sgd, test)),
            "boosted trees": common.error_per_100(test, trees.predict(tree, test)),
            "neural net": common.error_per_100(test, neural_net.predict(net, test)),
        }
    )

    print("train decks:", len(train), " test decks:", len(test))
    print()
    print(sml.params.round(4))

    # model = predicted wins per 100 if every training deck had that value
    # test = what test decks with that value really won
    for col, b in best.items():
        table = pd.DataFrame({"model": b["wins_per_100"]}, index=b["grid"])
        table["test"] = test_rates(test, col, statsmodels_logit.STEPS[col])
        print(f"\n{col}: best {b['best']:g} ({b['shape']})")
        print(table.round(2))
        if not b["bends_down"]:
            print(
                "curve bends up so -b1/(2*b2) is the worst value:",
                round(b["formula_peak"], 2),
            )

    table = pd.DataFrame(colour["ranking"], columns=["pair", "model"]).set_index("pair")
    by_pair = test.groupby("main_colors")[["wins", "games"]].sum()
    table["test"] = 100 * by_pair.wins / by_pair.games
    print("\ncolour pairs")
    print(table.round(2))
    print(
        "best",
        colour["best"],
        "vs runner-up",
        colour["runner_up"],
        "p =",
        round(colour["p_vs_runner_up"], 3),
    )

    print("\ntest error (wins per 100 games, smaller is better)")
    print(errors.round(2))

    # what following the advice is worth on the test decks
    follows = common.follows_advice(test, best, train)
    value = common.value_per_100(test, follows)
    print(
        "\nfollow the advice:",
        round(value["follows_advice"], 1),
        f"({value['n_follow']} decks)",
    )
    print(
        "played 17 lands:  ", round(value["baseline"], 1), f"({value['n_base']} decks)"
    )
    print("gain:", round(value["gain"], 1), "wins per 100 games")

    return {"best": best, "colour": colour, "errors": errors, "value": value}
