# report.py
# One place that fits every method and prints the final results:
# the fitted equation, the best value for each deck choice, how wrong each method is,
# what following the advice is worth, and the rule.
from . import baseline, common, sgd_logit, statsmodels_logit

NAMES = {"avg_mana_value": "average mana value", "num_creatures": "creatures", "num_lands": "lands"}


def equation(res):
    """The fitted model written out with its numbers."""
    p = res.params
    return ("logit(P(win)) = "
            f"{p['Intercept']:+.3f} "
            f"{p['avg_mana_value']:+.3f}*mana {p['I(avg_mana_value ** 2)']:+.4f}*mana^2 "
            f"{p['num_creatures']:+.3f}*creatures {p['I(num_creatures ** 2)']:+.4f}*creatures^2 "
            f"{p['num_lands']:+.3f}*lands {p['I(num_lands ** 2)']:+.4f}*lands^2 "
            "+ colour pair effect")


def test_win_rate(test, col, value, step):
    """Real win rate (per 100 games) of test decks whose value of col rounds to value."""
    rounded = ((test[col] / step).round() * step).round(2)
    d = test[rounded == value]
    return (100 * d.wins.sum() / d.games.sum() if len(d) else float("nan")), len(d)


def rule_text(col, b):
    """One line of advice for one deck choice."""
    name, best = NAMES[col], b["best"]
    shown = f"{best:.1f}" if col == "avg_mana_value" else f"{best:.0f}"
    if b["shape"] == "peak":
        return f"{name}: {shown} (a real sweet spot)"
    if b["shape"] == "lower is better":
        return f"{name}: as low as your pool allows (best seen in real decks: {shown})"
    return f"{name}: as many as your pool allows (best seen in real decks: {shown})"


def final_results(train, test):
    # fit every method on the training decks only
    base = baseline.fit(train)
    sml = statsmodels_logit.fit(train)
    sgd = sgd_logit.fit(train)
    best = statsmodels_logit.best_values(sml, train)
    colour = statsmodels_logit.best_colour(sml, train)

    errors = {
        "baseline (average win rate)": common.error_per_100(test, baseline.predict(base, test)),
        "statsmodels logistic regression": common.error_per_100(test, statsmodels_logit.predict(sml, test)),
        "SGD logistic regression": common.error_per_100(test, sgd_logit.predict(sgd, test)),
    }

    print("=" * 72); print("FINAL RESULTS"); print("=" * 72)
    print(f"Training decks: {len(train)}   Test decks: {len(test)}")
    print("\n1. The model\n   " + equation(sml))

    print("\n2. Best value for each deck choice")
    print("   'model' = predicted wins per 100 if every training deck had that value")
    print("   'test'  = real wins per 100 of test decks with that value (unseen by the model)")
    for col, b in best.items():
        step = statsmodels_logit.STEPS[col]
        print(f"\n   {NAMES[col]}: best {b['best']:g}, shape: {b['shape']}")
        print(f"   {'value':>7} {'model':>7} {'test':>7} {'test decks':>11}")
        for v, w in zip(b["grid"], b["wins_per_100"]):
            t, n = test_win_rate(test, col, v, step)
            mark = "  <- best" if v == b["best"] else ""
            print(f"   {v:7g} {w:7.2f} {t:7.2f} {n:11d}{mark}")
        if not b["bends_down"]:
            print(f"   (the curve bends UP, so -b1/(2*b2) = {b['formula_peak']:.2f} is the worst value, not the best)")

    # colour pair: a category, so we rank the pairs instead of looking for a curve
    print(f"\n   colour pair: best {colour['best']}, "
          f"vs runner-up {colour['runner_up']}: p = {colour['p_vs_runner_up']:.3f}")
    print(f"   {'pair':>7} {'model':>7} {'test':>7} {'test decks':>11}")
    for pair, w in colour["ranking"]:
        d = test[test.main_colors == pair]
        t = 100 * d.wins.sum() / d.games.sum() if len(d) else float("nan")
        mark = "  <- best" if pair == colour["best"] else ""
        print(f"   {pair:>7} {w:7.2f} {t:7.2f} {len(d):11d}{mark}")

    print("\n3. How wrong is each method on the test decks? (wins per 100 games, smaller is better)")
    for name, e in errors.items():
        print(f"   {name:40s} {e:6.2f}")

    print("\n4. What the advice is worth (real test decks, wins per 100 games)")
    follows = common.follows_advice(test, best, train)
    value = common.value_per_100(test, follows)
    print(f"   decks that follow the advice: {value['follows_advice']:.1f}  ({value['n_follow']} decks)")
    print(f"   decks that played 17 lands:   {value['baseline']:.1f}  ({value['n_base']} decks)")
    print(f"   gain: {value['gain']:+.1f} wins per 100 games")
    if value["n_follow"] < 200:
        print("   (fewer than 200 decks follow the advice, so this gain is noisy)")

    in_colour = test[test.main_colors == colour["best"]]
    colour_rate = 100 * in_colour.wins.sum() / in_colour.games.sum()
    all_rate = 100 * test.wins.sum() / test.games.sum()
    print(f"   decks in {colour['best']}: {colour_rate:.1f} vs all test decks: {all_rate:.1f} "
          f"({colour_rate - all_rate:+.1f} wins per 100 games, {len(in_colour)} decks)")

    print("\n5. The rule")
    for col, b in best.items():
        print("   " + rule_text(col, b))
    if colour["p_vs_runner_up"] < 0.05:
        print(f"   colour pair: {colour['best']} (clearly the best)")
    else:
        print(f"   colour pair: {colour['best']} or {colour['runner_up']} "
              f"(the top two are too close to separate, p = {colour['p_vs_runner_up']:.2f})")
    print("=" * 72)
    return {"equation": equation(sml), "best": best, "colour": colour,
            "errors": errors, "value": value}
