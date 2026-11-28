import hashlib
from pathlib import Path
import duckdb


# data importing with duckDB

# parent that holds the files is data so paths work from anywhere
data = Path(__file__).parent / "data"

# creating the paths to the files we want to use
games_file = data / "game_data_public.BLB.PremierDraft.csv.gz"
scryfall_file = data / "oracle-cards-20261116220156.jsonl.gz"
db_file = data / "mtg.duckdb"


# the SHA-256 each raw file should have, so we can tell if a file changed
expected_sha256 = {
    games_file.name: "61fed2a4db5854ca9f247eba9ea4176cf70a25ee253024928963335d32dbf281",
    scryfall_file.name: "581ee80de9a458111320f4c1067de03091b1bd2106e0e9e6bba6a9e72ef30d34",
}


# work out SHA-256 of one file
def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        # read 1mb at a time so a big file does not sit in memory and clog it
        while True:
            block = f.read(1024 * 1024)
            if not block:
                break
            h.update(block)
    return h.hexdigest()


# stop with an error if a raw file is missing or isnt the file we recorded
def verify_files():
    for name, expected in expected_sha256.items():
        path = data / name
        if not path.exists():
            raise FileNotFoundError(
                f"Missing file: {path} is missing, see data/README.md"
            )
        actual = sha256(path)
        if actual != expected:
            raise ValueError(
                f"File {path} has changed. Expected SHA-256: {expected}, got: {actual}"
            )


# Game table creations


# creating whole database from raw files
def build_database():
    # verify raw files
    verify_files()

    # deleting old database so each build starts clean
    if db_file.exists():
        db_file.unlink()

    # opening a connection to the database file, creating it if it does not exist
    con = duckdb.connect(str(db_file))

    # cap the memory DuckDB can use to 4Gb sothe codespace doesnt kill the process
    con.execute("SET memory_limit TO '4GB'")

    # games table creation with 1 row per game, keeping every column in the CSV
    # 20 game-level columns, plus 5 per-card count columns for each of the 276 cards
    # (opening_, drawn_, tutored_, deck_, sideboard_)
    # card counts are 0-22, so they are stored as UTINYINT (1 byte) instead of
    # BIGINT (8 bytes); this keeps the table about 1.3GB in pandas instead of ~10GB
    card_cols = "'^(opening|drawn|tutored|deck|sideboard)_'"
    con.execute(
        f"""
        CREATE TABLE games AS
        SELECT COLUMNS(lambda c: NOT regexp_matches(c, {card_cols})),
               COLUMNS({card_cols})::UTINYINT
        FROM read_csv('{games_file}', sample_size=20000)
        """
    )

    # cards table: one row per Scryfall card
    # we name the columns we want, because a Scryfall card has dozens of nested fields
    # cmc is renamed mana_value, which is what the project calls it
    # colors comes as a list, so array_to_string joins it into a string like 'BG'
    # newline_delimited because the file has one JSON card per line
    con.execute(f"""
        CREATE TABLE cards AS
        SELECT oracle_id, name, cmc AS mana_value, type_line,
                array_to_string(colors, '') AS colors, layout
        FROM read_json('{scryfall_file}', format='newline_delimited',
                        columns={{oracle_id: 'VARCHAR', name: 'VARCHAR',
                                    cmc: 'DOUBLE', type_line: 'VARCHAR',
                                    colors: 'VARCHAR[]', layout: 'VARCHAR'}})
    """)

    # close database so file is saved and not locked
    con.close()


# open the finished database for reading, for the notebook and analysis code
# read_only means an analysis can never change the data by accident
def connect():
    return duckdb.connect(str(db_file), read_only=True)


# runs only when you type `python mtg.py`, not when another file imports it
if __name__ == "__main__":
    build_database()
