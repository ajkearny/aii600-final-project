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
