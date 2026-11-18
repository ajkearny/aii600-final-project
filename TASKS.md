# Tasks

Our working list. `CHECKLIST.md` is what gets graded. This file breaks that work into jobs we can hand out.

**How to use it**

- Assign a task by putting a name after `Owner:`.
- Each task is about one branch and one PR. Tick the box in the PR that does the work.
- Only one of us edits `analysis.ipynb` at a time. Shared code goes in `mtg.py`, and the notebook calls it.
- A choice about the data, split, model, loss, or action gets a `decisions.md` entry, and the PR names that entry.

## Choices already made

These still need their `decisions.md` entries. Those entries are tasks below.

- **Data:** 17lands **Premier Draft** game data (best-of-1) for **Bloomburrow (BLB)**. One game stands for one match.
- **Card info:** Scryfall only.
- **Loss:** `1 − p`, where `p` is the predicted chance of winning a game. Value is measured in **extra games won per 100**.
- **One deck = one draft.**
- **Model:** logistic regression on mana value (with a curve), creatures, lands (with a curve), colour pair, and player skill.
- **Split:** by date. Train on the earlier weeks, test on the later weeks.

---

# Part 1: Preliminary results (due Wed 18 Nov, 7:00 pm ET)

## Setup

- [ x] **Fork settings.** Turn Issues on. Add your collaborator and `VadimSokolov` as Write collaborators. Owner:
- [x ] **Point `gh` at our fork.** In each clone, run `gh repo set-default OWNER/REPO`, so pull requests go to our fork, not the course starter. Owner:
- [x] **README names.** Add both names and GitHub usernames under "Who". Owner:
- [ x] **README AI note.** Add one line on which AI tools we used and for what. Owner:
- [x ] **Python version.** Put the real version in `.python-version`, and list the exact package versions the notebook uses in `requirements.txt`. Owner:

## Step 1: Get the data

- [x ] **1a. Lock in the choices.** In `PROPOSAL.md`, fill in Premier Draft, BLB, the dates, and the game and deck counts, and change the loss to `1 − p`. Add a `decisions.md` entry explaining why: more data, and one game stands for one match. Owner:
- [ x] **1b. Check the licences** for 17lands and Scryfall. This decides whether we may re-upload the files to GitHub, or must give a download command instead. Fill in *Republishing* in `PROPOSAL.md`. Owner:
- [ x] **1c. Download the BLB Premier Draft game file** from 17lands (first check it's still listed). It's one row per game, with the deck's cards and whether the game was won. Owner:
- [ x] **1d. Download the Scryfall card data:** mana value, type, and colours for each card. Owner:
- [ x] **1e. Write `data/README.md`:** where each file came from, its name, the download command, and its SHA-256. The SHA-256 is a fingerprint that proves the file hasn't changed. Owner:
- [x ] **1f. Make the GitHub `data` release** if the licences allow it. It must exist by 18 Nov. Owner:
- [ x] **1g. Loading code in `mtg.py`.** It reads the files and checks their fingerprints. Owner:

## Step 2: Clean it

- [ ] **2a. Keep only two-colour decks with no splash.** Owner:
- [ ] **2b. Match card names to Scryfall.** Print any names that don't match, such as double-faced cards, so nothing is silently dropped. Owner:
- [ ] **2c. Work out each deck's numbers:** `m` (average mana value of nonland cards), `c` (creatures), and `L` (lands). Owner:
- [ ] **2d. Group games by draft** into games won and games played. Keep each deck's colour pair and the player's skill bucket. Owner:
- [ ] **2e. Put the cleaning code in `mtg.py`** as functions the notebook calls. Owner:
- [ ] **2f. `decisions.md` entries** for "one deck = one draft" and "include player skill". Owner:

## Step 3: Look at it (before any model)

- [ ] **3a. Main chart:** deck win rate vs. average mana value. Group the decks into mana value bins, plot each bin's average with error bars, and save it to `fig/`. Owner:
- [ ] **3b. Extra charts:** win rate vs. lands, vs. creatures, by colour pair, and by skill bucket. Save them to `fig/`. Owner:
- [ ] **3c. Summary table:** total games, decks, and date range, plus the average, spread, min, and max of `m`, `c`, `L`, and win rate. Owner:
- [ ] **3d. Same table split by colour pair** (10 rows, one per BLB tribe). Owner:
- [ ] **3e. A 2 to 3 sentence note** under the chart on what we see, written before fitting anything. Owner:

## Step 4: Build the model

- [ ] **4a. Split by date.** Pick the cutoff date. Earlier games are for training, later games for testing. Add a `decisions.md` split entry with the date. Owner:
- [ ] **4b. Baseline:** the player plays 17 lands, and we predict the average win rate for every deck. Owner:
- [ ] **4c. Fix the formula in `PROPOSAL.md`.** Change `log(P(win))` to logistic regression, `log(p / (1−p))`, so predictions stay between 0 and 1. Owner:
- [ ] **4d. Fit the model** on the training data: `m`, `m²`, `c`, `L`, `L²`, colour pair, and skill. Each deck counts as "X wins out of Y games". Use `statsmodels`. Owner:
- [ ] **4e. Find the sweet spot:** `m_best = −b1 / (2·b2)`, and the best land count. Check that the curve bends down (`b2` negative). Owner:
- [ ] **4f. `decisions.md` model entry.** Owner:

## Step 5: Test it

- [ ] **5a. Predict every test deck** with both the baseline and the model. Owner:
- [ ] **5b. Accuracy score:** how far off each method is, on average, in wins per 100 games. Owner:
- [ ] **5c. Value score:** the actual test win rate of decks within 0.2 mana value of the sweet spot (with the best land count) vs. decks that followed the baseline, in wins per 100. Owner:
- [ ] **5d. `decisions.md` loss entry:** the loss is `1 − p`, and it's scored in wins per 100. Owner:

## Submit

- [ ] **Run the notebook from top to bottom**, save the charts in `fig/`, and commit it with its outputs. Owner:
- [ ] **Merge everything to `main` through PRs** (the other person merges), and push **before 7:00 pm ET on 18 Nov**. Owner:

---

# Part 2: Final presentation (due Wed 9 Dec, 7:00 pm ET; talk that night)

## Step 4 (cont.): Explain the model

- [ ] **4g. Write the model as equations** in the notebook, with each number explained in words. For example: "`b3` = how much one extra creature changes the odds of winning". Owner:
- [ ] **4h. List the assumptions**, and name the one we trust least. Owner:
- [ ] **4i. Simulation check.** Make fake data with a sweet spot we choose, fit the model, and show that it finds the right answer. Compare the fake data to the real data. Owner:

## Step 5 (cont.): Check the errors

- [ ] **5e. Calibration chart.** When the model says 55%, do those decks win about 55%? Group the test decks by predicted chance and compare. Owner:
- [ ] **5f. Error patterns.** Plot each miss (actual − predicted) against the prediction and against the date. Say whether it looks like random noise or a pattern (bias). Owner:
- [ ] **5g. Error bars** on predictions and on the sweet spot, using bootstrapping (refit on reshuffled copies of the data many times). Owner:
- [ ] **5h. Show where the model gets shaky.** Error bars widen for very cheap or very expensive decks. Owner:
- [ ] **5i. Where the model wins and where it ties** with the baseline, by colour pair or mana value range. Owner:
- [ ] **5j. Test the claim that "too expensive hurts more than too cheap".** Report the result either way. Owner:

## Step 6: Decide and present

- [ ] **6a. Write the rule:** build toward `m_best`, `L_best`, and `c_best`. If there are two possible builds, play the one with the higher predicted win chance. Explain why the loss `1 − p` picks this rule. Owner:
- [ ] **6b. How the advice changes:** a table of the sweet spot per colour pair and per skill level. Owner:
- [ ] **6c. What being less wrong is worth.** Refit on half the training data, see how much worse it scores, and extend that to estimate what more data would add, in wins per 100. Owner:
- [ ] **6d. Layer diagram** `fig/layers.png`: data → model → prediction → decision. Owner:
- [ ] **6e. The question at the top of the notebook:** one sentence, plus what we measure, in what units, and over what dates. Owner:
- [ ] **6f. Write `presentation.qmd`:** a title slide plus 4 slides: the action, the reason (the test score must match the notebook), the risk as a number, and the value of being less wrong. Owner:
- [ ] **6g. Plain-language effects.** For example: "+0.5 average mana value → −X wins per 100 games". Owner:
- [ ] **6h. Limits:** where not to trust the model (other sets, best-of-3, extreme decks), what we assumed, and what we'd do with more time. Owner:
- [ ] **6i. Render `presentation.html` once**, in the final commit (`quarto render presentation.qmd`). Owner:
- [ ] **6j. Pick the speaker** and do a timed 3-minute rehearsal. Both of us must be able to explain the whole repo. Owner:

## Step 7: Final repo check

- [ ] **7a. Check that `decisions.md` tells the story** from the proposal to the advice on the first slide. Owner:
- [ ] **7b. Check that every PR named a `decisions.md` entry.** Owner:
- [ ] **7c. Check that no data files, secrets, or model files are in git.** Owner:
- [ ] **7d. Run the notebook from top to bottom** and commit it with its outputs. Owner:
- [ ] **7e. Tick `CHECKLIST.md`**, with one sentence for any line we can't tick. Owner:
- [ ] **7f. Merge everything to `main`** and push **before 7:00 pm ET on 9 Dec**. Owner:
