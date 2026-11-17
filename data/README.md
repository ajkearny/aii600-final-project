# Data

The files the notebook reads are not committed. When the terms let you republish them, they are assets on the GitHub release tagged `data`. The release is public. When the terms let you download the files but not republish them, do not create that release. Write the command that downloads them from the source, and say what it needs (an account, a key in `.env`, a path).

`OWNER/REPO` is your fork, the form `username/aii600-final-project`. In the clone, once:

```bash
gh repo set-default OWNER/REPO
```

Create the release from the project root, after the files are in this folder:

```bash
gh release create data data/your-file.csv --repo OWNER/REPO --title "Data" --notes "See data/README.md"
```

Add every file the notebook reads. When a file changes:

```bash
gh release upload data data/your-file.csv --repo OWNER/REPO --clobber
```

On another machine:

```bash
gh release download data --dir data --repo OWNER/REPO
```

Record a SHA-256 for each file. Replacing a file with `--clobber` does not show up in git, so update the hash in the same commit:

```bash
shasum -a 256 data/your-file.csv
```

## Raw files

| File | Source | SHA-256 |
|---|---|---|
| `game_data_public.BLB.PremierDraft.csv.gz` | 17lands public datasets, Bloomburrow (BLB) Premier Draft game data | `61fed2a4db5854ca9f247eba9ea4176cf70a25ee253024928963335d32dbf281` |
| `oracle-cards-20261116220156.jsonl.gz` | Scryfall bulk data, "Oracle Cards", file dated 2026-11-16 | `581ee80de9a458111320f4c1067de03091b1bd2106e0e9e6bba6a9e72ef30d34` |

Both files stay in `data/` and are not committed.

## Download

Run from the project root. Neither needs an account or a key.

```bash
curl -fL -o data/game_data_public.BLB.PremierDraft.csv.gz \
  https://17lands-public.s3.amazonaws.com/analysis_data/game_data/game_data_public.BLB.PremierDraft.csv.gz

curl -fL -H "User-Agent: aii600-project/1.0" -o data/oracle-cards-20261116220156.jsonl.gz \
  https://data.scryfall.io/oracle-cards/oracle-cards-20261116220156.jsonl.gz
```

Scryfall replaces its bulk files daily, so the dated link may stop working. Take the current link (`jsonl_download_uri`) from https://api.scryfall.com/bulk-data/oracle-cards. The new file has a different hash, so update the hash here and in `mtg.py` together.

## Build the database

```bash
python mtg.py
```

This checks both SHA-256 values and writes `data/mtg.duckdb` (about 30 seconds). The database is not committed. Rebuild it from the raw files.

| Table | One row per | Columns |
|---|---|---|
| `games` | game | `draft_id`, `draft_time`, `game_time`, `build_index`, `match_number`, `game_number`, `rank`, `opp_rank`, `main_colors`, `splash_colors`, `on_play`, `num_mulligans`, `num_turns`, `won` |
| `cards` | Scryfall Oracle card | `oracle_id`, `name`, `mana_value`, `type_line`, `colors`, `layout` |

The 17lands file has about 1,500 columns, mostly one set per card. `games` keeps only the 14 game columns. The card columns are not loaded yet.

## Unit of observation, sample size, time span

- Unit: one game of Bloomburrow Premier Draft (best-of-1).
- Sample: 931,230 games from 160,150 drafts.
- Time span: games played 2024-07-30 to 2024-09-03.
- `cards` has 39,297 rows but 38,788 distinct names, because some names repeat. This has to be handled when cards are joined to decks.

## Republishing

- Scryfall: its terms say the data may not be repackaged or republished, so the file is not on GitHub and is downloaded with the command above.
- 17lands: licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/), which allows republishing with credit to 17lands, a link to the licence, and a note of any changes. We do not change the raw file. The tables in `mtg.duckdb` are derived from it and are not published.
- Because Scryfall cannot be republished, the project downloads both files from their sources, so there is no `data` release.
