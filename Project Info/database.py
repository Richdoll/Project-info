"""SQL database (SQLite): one table per source. No external dependency."""
import os
import sqlite3
from datetime import datetime
from pathlib import Path

import pandas as pd

DB_PATH = os.getenv("DB_PATH", "data/collection.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS books (
    url              TEXT PRIMARY KEY,
    title            TEXT,
    price            REAL,
    availability     TEXT,
    stock_quantity   INTEGER,
    products_on_page INTEGER,
    rating           INTEGER,
    reviews_count    INTEGER,
    description      TEXT,
    category         TEXT,
    tax              REAL,
    upc              TEXT,
    scraped_at       TEXT
);
CREATE TABLE IF NOT EXISTS cars (
    url        TEXT PRIMARY KEY,
    brand      TEXT,
    model      TEXT,
    year       INTEGER,
    price      INTEGER,
    mileage    INTEGER,
    gearbox    TEXT,
    region     TEXT,
    fuel       TEXT,
    scraped_at TEXT
);
"""
TABLES = {"books": "data/clean/books_clean.csv", "cars": "data/clean/gaaraas_clean.csv"}


def connect() -> sqlite3.Connection:
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH)


def init_db() -> None:
    with connect() as con:
        con.executescript(SCHEMA)


def save_df(table: str, df: pd.DataFrame) -> int:
    """Insert or update (key = url) the DataFrame rows. Returns the number of rows."""
    if df is None or df.empty:
        return 0
    d = df.copy()
    d["scraped_at"] = datetime.now().isoformat(timespec="seconds")
    d = d.astype(object).where(d.notna(), None)
    cols = list(d.columns)
    sql = (f"INSERT OR REPLACE INTO {table} ({', '.join(cols)}) "
           f"VALUES ({', '.join('?' for _ in cols)})")
    with connect() as con:
        con.executemany(sql, [tuple(None if v is pd.NA else v for v in row) for row in d.itertuples(index=False)])
    return len(d)


def load_table(table: str) -> pd.DataFrame:
    with connect() as con:
        return pd.read_sql(f"SELECT * FROM {table}", con)


def seed_from_csv_if_empty() -> None:
    """On first start (e.g. Streamlit Cloud), fill the database from the CSV files in the repo."""
    for table, csv in TABLES.items():
        if load_table(table).empty and Path(csv).exists():
            save_df(table, pd.read_csv(csv))
