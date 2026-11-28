# Decisions

This file is the history of the project. Append an entry when a choice changes the work: the quantity, the data, the split, the model, the loss, or the action. Leave old entries in place. A later entry can reverse an earlier one. If a result depends on a random draw, record the seed under Why. The split entry records the cutoff date, or the seed and the fraction. The pull request that merges the code names this entry.

## YYYY-MM-DD: short title

- Decision. What you chose.
- Why. The evidence.
- Alternative. What you rejected.
- Revisit. What would change the choice.


## 2026-10-25: Autumn Testing Branches

- Decision. What you chose. -Testing the branching workflow.
- Why. The evidence. -We wanted to make sure we understood how to create, change, and push branches before beginning the project.
- Alternative. What you rejected. -Rejected the alternative of not testing it because we both don't want to mess up any of our work.
- Revisit. What would change the choice. -If we were both github pros we probably wouldn't need to test.

## 2026-10-25: Mitch Testing branch
- Decision. What you chose.
    - testing how the git commands work and changing some comments
- Why. The evidence.
    - making sure we both understand what the order of the commands is
- Alternative. What you rejected.
    - no alternatives
- Revisit. What would change the choice.
    - none

## 2026-10-26: Putting in our proposal idea (Mitch)

- Decision. What you chose.
    - We chose to evaluate how the average mana value of a two-colour limited Magic the Gathering deck predicts its game win probability, using 17Lands game data and card attributes from Scryfall and MTGJSON.
- Why. The evidence.
    - Mana value exists for every card in every source we found so it can be computed for every deck. A player controls the average mana value of their deck when building it so it is actionable. keeping the deck selection to two-colour decks keeps the dataset smaller too. 17Lands is also public game-level data from real games so avoid having to simulate.
- Alternative. What you rejected.
    - Using the commander format of the game which has 2.5x the amount of cards and far less real world data to work, which would force us to do simulations. Simulations are a problem because the deck arent piloted by real people making real decisions with past experience.
- Revisit. What would change the choice.
    - Nothing yet


## 2026-11-17: Data source and DuckDB database (Mitch)

- Decision. What you chose.
    - Use 17lands Premier Draft (best-of-1) game data for Bloomburrow (BLB), played 2024-07-30 to 2024-09-03 (931,230 games from 160,150 drafts), with card attributes (mana value, type, colours) from Scryfall's Oracle Cards file dated 2026-11-16. `mtg.py` checks both files by SHA-256 and loads them into one DuckDB file, `data/mtg.duckdb`, with two tables: `games` (one row per game, 14 game columns) and `cards` (one row per Scryfall card). Both raw files are downloaded from their sources and not republished, so there is no `data` release.

- Why. The evidence.
    - The 17lands game file has one row per game with the deck's cards, the player's rank and colours, and whether they won. The draft pick and replay files have no win results, so they can't give us win rates. Premier Draft is best-of-1, so one game stands for one match, and BLB gives a lot of data: 931,230 games from 160,150 drafts. The game file has no card attributes, so we need Scryfall for mana value, type and colours. DuckDB reads the compressed file directly and lets us select only the columns we need. The CSV is about 2.7 GB with about 1,520 columns, and loading it all at once into pandas ran out of memory in the codespace. 17lands publishes the data under CC BY 4.0, so it could be republished with credit. Scryfall's terms do not allow republishing its data, and the project needs both files, so one set of download commands in `data/README.md` covers both.

- Alternative. What you rejected.
    - Traditional Draft (best-of-3), which has far fewer games, and where one game is not one match. The 17lands draft pick and replay files, which have no deck and result rows. Loading the CSV straight into pandas, because of memory. Putting the 17lands file on a GitHub `data` release, because the licence allows it but Scryfall's does not, and the download link works for both.

- Revisit. What would change the choice.
    - If the 17lands download link stops working, we would put the 17lands file on a `data` release (CC BY 4.0 allows it). If the Scryfall link stops working, we would take the current link from its bulk-data API and update the hash. If the date range looks unrepresentative (for example, player skill changing as the season goes on). If DuckDB turns out to be hard to share between us, we would switch to Parquet files.

## 2026-11-17: Keep every column of the 17lands game file (Autumn)

- Decision. What you chose.
    - The `games` table in `data/mtg.duckdb` now keeps all 1,400 columns of the 17lands game file, not only 14. That is 20 game-level columns (adding `expansion`, `event_type`, `opp_num_mulligans`, `opp_colors`, `user_n_games_bucket`, `user_game_win_rate_bucket`) and 1,380 per-card count columns: `opening_hand_`, `drawn_`, `tutored_`, `deck_` and `sideboard_` for each of the 276 BLB cards. This reverses the "14 game columns" part of the entry above.
- Why. The evidence.
    - Leaving out the card columns was a mistake: we need the `deck_` columns to work out each deck's average mana value, which is the whole project question. Card counts range from 0 to 22, so they are stored as `UTINYINT` (1 byte) instead of `BIGINT` (8 bytes). The DuckDB file is 113 MB, and `SELECT * FROM games` loads into pandas in about 4 seconds as a 1.77 GB DataFrame, not about 10 GB with 64-bit integers.
- Alternative. What you rejected.
    - Keeping only the `deck_` columns, because the opening hand and drawn columns may be useful later and are cheap to keep. Leaving the counts as `BIGINT`, because of the memory cost in pandas.
- Revisit. What would change the choice.
    - If a later set has a card count above 255 (the `UTINYINT` maximum). If 1.77 GB is too much for the codespace, we would select only the columns we need in SQL before calling `.df()`.

## 2026-11-17: Including Decks with Standard 40 Cards (Autumn)

- Decision. What you chose.
    - We chose to filter the dataset to only include decks with 40 cards.
- Why. The evidence.
    - Magic the Gathering Standard format includes decks with only 40 cards. If a person in the draft cannot narrow their deck to only 40 before the tournament, they may choose to register more cards, but they must play the game with only 40. This created a discrepency in our data as it did not give us visability into which cards were actually played with vs just registered, so we decided to filter out any decks with more than 40 cards registered.
- Alternative. What you rejected.
    - Keeping decks with more than 40 cards. This would've created null values within our dataset and since it only made up roughly 6% of the data (and still left us with over 100k rows to work with), we chose to ommit instead of work around.
- Revisit. What would change the choice.
    - If we knew what cards were played vs in reserve for each game, we would have been able to use that information to properly calculate the related statistics needed for modeling. 

## 2026-11-18: Split by draft, random 25% held out, seed 0 (Mitch)

- Decision.  What you chose.
    - Hold out a random 25% of drafts as the test set and train on the rest, using `split_by_draft` in `models/common.py` with seed 0. That gives 68,003 drafts (80,264 decks) for training and 22,668 drafts (26,636 decks) for testing. All builds of one draft go on the same side. The test decks are never used to fit the model, to choose the values we try, or to rank colour pairs.

- Why. The evidence.
    - The cleaned table `data/mtg_data_clean.csv` has no draft date, and we work only from that table, so the date split in our plan is not possible. We split by draft, not by deck, because about 13,800 drafts produced two or more decks (builds). If those builds were split across train and test, the model would be tested on decks from drafts it had already seen.

- Alternative. What you rejected.
    - A date split (train on earlier weeks, test on later weeks), which would also test whether the pattern holds as the season goes on. A random split of individual decks, which leaks information between builds of the same draft.
- Revisit. What would change the choice.
    - If dates are added to the table, switch to a date split and record the cutoff. If the test results look very different from the training results, check whether the pattern changes over time.

## 2026-11-18: Model: logistic regression with curves for mana value, creatures and lands (Mitch)

- Decision. What you chose.
    - The main model is a binomial logistic regression (statsmodels GLM, logit link) of each deck's wins out of games on average mana value, average mana value squared, creatures, creatures squared, lands, lands squared, and colour pair (10 pairs). Decks with more games count more (weights = games). The same model is also fitted by stochastic gradient descent written by hand in NumPy (batches of 256, standardised inputs, constant learning rate, seed 0), as in the class slides, as a check on the statsmodels fit. The baseline predicts the average training win rate (about 0.558) for every deck. Player skill is not in the model, because it is not in the cleaned table. One row is one deck build (106,900 decks from 90,671 drafts), so this replaces our earlier "one deck = one draft".

- Why. The evidence.
    - Logistic regression keeps every prediction between 0 and 1 and fits wins out of games directly. The squared terms let each curve bend. Creatures squared was added after we looked at the training win rates by creature count, which rise and then flatten, so it was chosen after seeing the pattern. On the test decks, statsmodels and SGD at learning rate 0.01 both score 17.42 wins per 100 games, which shows the two fits agree. The model beats the baseline only slightly on single decks (17.42 against 17.49), because a deck's win rate over a few games is very noisy. Its value is in the shape of the curves, not in predicting one deck.

- Alternative. What you rejected.
    - No creatures squared term, as in our original plan (a straight line for creatures). The neural network and the random forest and boosting methods from the class slides: they can bend more freely, but give no coefficients we can explain, and we did not run them for Part 1.

- Revisit. What would change the choice.
    - If bootstrap error bars (task 5g) show the curves are not stable. If we can add a measure of card quality, because strong decks may also be cheap and creature-heavy, which this model cannot separate from mana value or creature count.

## 2026-11-18: How we find the best deck: best value inside the data, ties reported as ties (Mitch)

- Decision. What you chose.
    - For average mana value, creatures and lands, we predict the win rate as if every training deck had each value in turn, keeping everything else about the deck as it is, and look only at values that at least 500 training decks use (steps of 0.1, 1 and 1). The best value in that range is the answer. If it is in the middle, it is a sweet spot. If it is at an edge, the advice is "as low as your pool allows" or "as many as your pool allows", with the edge value stated. For colour pair we rank all 10 pairs the same way, and name one only if it beats the runner-up at p < 0.05; otherwise we report the top two as tied. The value of the advice is the test win rate of decks that follow it (within 0.2 mana value and 1 creature of a peak, or in the lowest or highest quarter of decks for an edge) compared with test decks that played 17 lands.

- Why. The evidence. 
    - The formula `-b1 / (2*b2)` only gives a peak if the curve bends down. For creatures it bends up and the formula returns the worst value (12.8). For mana value it returns -1.50, outside any real deck. Mana value and its square move almost together (correlation 0.997), so their p-values one at a time are misleading: together they are strongly significant (p = 2e-11), and the effect is a steady drop in win rate as mana value rises, not a peak. Results on the current split: lands 16 (a real peak, test decks 56.9 against 55.6 for 17 lands), mana value lower is better, creatures more is better, colour pair BG and WG tied (p = 0.24). Decks following the advice won 57.3 per 100 games (1,056 decks) against 55.6 for 17-land decks (19,869 decks).

- Alternative. What you rejected.
    - Report `-b1 / (2*b2)` for every variable, which gives answers outside real decks. Extend the curves past the values real decks use, which would be a guess.

- Revisit. What would change the choice.
    - If the bootstrap error bars (task 5g) show the best value is unstable, especially at the ends of the mana value and creature ranges, where there are few decks. This is observational data, so part of the effect may come from deck quality, not from the mana value or creature count itself.

## 2026-11-18: Loss is 1 - p, scored in wins per 100 games (Mitch)

- Decision. What you chose.
    - The loss is 1 - p, where p is the predicted chance of winning a game. We score in wins per 100 games in two ways. Accuracy is the average gap between each test deck's actual win rate and its predicted win rate, weighted by games played (baseline 17.49, statsmodels 17.42, SGD 17.42 to 17.56 depending on the learning rate). Value is the test win rate of decks that follow the advice minus the test win rate of decks with 17 lands (+1.7 wins per 100 games on this split). The models themselves are fitted by maximum likelihood (log loss for SGD).

- Why. The evidence. 
    - Premier Draft is best-of-1, so one game stands for one match, and 1 - p is the chance of losing it. This replaces the best-of-3 match formula in `PROPOSAL.md`. Wins per 100 games is a unit a player can read, and it is the unit of the decision.

- Alternative. What you rejected.
    - The best-of-3 match formula p^2(3 - 2p), which does not match the data we use. Squared error or log loss as the reported score, which are fine for fitting but not in the units of the decision.
- Revisit. What would change the choice.
    - If the model is used for best-of-3 matches.


## 2026-11-22: Add boosted trees and a neural network as comparisons only (Mitch)

- Decision. What you chose.
    - Added gradient boosted trees (`models/trees.py`) and a small neural network (`models/neural_net.py`) from scikit-learn, scored on the same test decks. Logistic regression stays the main model. Trees: depth 3, learning rate 0.05, 300 rounds, weighted by games. Network: 16 and 8 hidden units, standardised inputs, early stopping, no weights. Seed 0 for both, not tuned.
- Why. The evidence.
    - Test error in wins per 100 games: trees 17.41, logistic regression 17.42, baseline 17.49, network 19.33. The trees gain almost nothing so the squared terms already get the shape. The network is worse partly because `MLPRegressor` can't weight decks by games. Neither gives coefficients, so they can't give the advice.
- Alternative. What you rejected.
    - Using the trees or the network as the main model, or tuning them on the test decks.
- Revisit. What would change the choice.
    - If the trees beat logistic regression by more than about 0.03.

## 2026-11-23: Checks on the method: fake decks, redrawn drafts, data size (Mitch)

- Decision. What you chose.
    - Three checks. Fake decks (`fake_decks`, 20,000 decks, true peak at mana value 2.9 and 17 lands) refit over 30 seeds. Refit on training drafts resampled by draft. Refit on 25%, 50% and 100% of the training drafts, and rerun the best value search with a minimum of 100, 500 and 2,000 decks per value (we keep 500).
- Why. The evidence.
    - The real data has no mana value peak so we needed to know the code can find one. On fake decks it gets mana value 2.89 (true 2.90) and lands 17.07 (true 17), so the missing peak is a finding and not a bug. Across resampled drafts the test error stays at 17.42 (17.40 to 17.45). Four times the data lowers it by only 0.009.
- Alternative. What you rejected.
    - Trusting the real fit without checking. Resampling single decks instead of drafts, since builds from one draft are alike.
- Revisit. What would change the choice.
    - If a change to the model moves the recovered peaks by more than 0.1.

## 2026-11-23: Final advice and framing (Mitch)

- Decision. What you chose.
    - Advice for a two-colour BLB Premier Draft deck: 16 lands, average mana value as low as the pool allows (2.2 is the lowest value with at least 500 decks), as many creatures as the pool allows (19), and BG or WG (tied, p = 0.24). Decks following this won 57.3 per 100 games (1,056 decks) against 55.6 for 17 land decks (19,869 decks), +1.7. There is no middle mana value sweet spot, so our original hypothesis is not supported.
- Why. The evidence.
    - The model is well calibrated and the residuals show no trend against the prediction or time. Bias grows at the edges (+0.7 cheapest, +1.2 most expensive) where there are few decks, but it is within noise. The loss is 1 - p so the best build has the highest predicted p.
- Alternative. What you rejected.
    - Reporting a peak to match the proposal, or naming BG as the best pair at p = 0.24.
- Revisit. What would change the choice.
    - If we can add card quality or skill, refit and check that mana value still matters. Results only cover Bloomburrow, Premier Draft, best-of-1, two-colour decks, 30 July to 3 September 2024.
