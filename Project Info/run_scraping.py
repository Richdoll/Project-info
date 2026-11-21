"""Command-line scraping : python run_scraping.py --source both --books-end 50 --cars-end 100"""
import argparse
from pathlib import Path

import database as db
from scrapers.driver import get_driver
from scrapers.books import scrape_books, clean_books
from scrapers.gaaraas import scrape_gaaraas, clean_gaaraas

p = argparse.ArgumentParser()
p.add_argument("--source", choices=["books", "gaaraas", "both"], default="both")
p.add_argument("--books-end", type=int, default=50)
p.add_argument("--cars-end", type=int, default=100)
p.add_argument("--show-browser", action="store_true")
a = p.parse_args()

Path("data/clean").mkdir(parents=True, exist_ok=True)
db.init_db()
driver = get_driver(headless=not a.show_browser)
try:
    if a.source in ("books", "both"):
        raw = scrape_books(driver, 1, a.books_end, progress=lambda pg, i, n: print(f"books p.{pg} {i}/{n}"))
        clean = clean_books(raw)
        clean.to_csv("data/clean/books_clean.csv", index=False)
        print(f"books : {db.save_df('books', clean)} rows")
    if a.source in ("gaaraas", "both"):
        raw = scrape_gaaraas(driver, 1, a.cars_end, progress=lambda pg, i, n: print(f"gaaraas p.{pg}: {i} listings"))
        clean = clean_gaaraas(raw)
        clean.to_csv("data/clean/gaaraas_clean.csv", index=False)
        print(f"gaaraas : {db.save_df('cars', clean)} rows")
finally:
    driver.quit()
