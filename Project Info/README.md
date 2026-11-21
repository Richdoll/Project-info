# Data Collection project - Books to Scrape & Gaaraas

Scraping (Selenium), cleaning (pandas), SQL database (SQLite), Streamlit app, Kobo + Google Forms evaluation forms.

## Structure
- `scrapers/`: `driver.py` (headless Chrome), `books.py`, `gaaraas.py` (Selenium scraping + cleaning)
- `run_scraping.py`: scrapes both sources, writes `data/clean/*.csv` and the database `data/collection.db`
- `database.py`: tables `books` and `cars` (SQLite)
- `app.py`: Streamlit app (scraper, raw data, dashboard, evaluation)
- `webscraper/`: JSON sitemaps to import into the Web Scraper Chrome extension
- `forms/`: `kobo_evaluation_form.xlsx` (XLSForm) and `google_form_script.gs` (Apps Script)

## Steps to do
1. `pip install -r requirements.txt`, then `python run_scraping.py --source both` (creates `data/clean/` and the database).
2. Web Scraper (Chrome): *Create new sitemap > Import sitemap*, paste each JSON from `webscraper/`, run it, export to CSV as
   `data/raw/books_webscraper_raw.csv` and `data/raw/gaaraas_webscraper_raw.csv` (no cleaning).
3. Kobo: kf.kobotoolbox.org > New project > Upload an XLSForm > `forms/kobo_evaluation_form.xlsx` > Deploy > copy the link.
4. Google Forms: script.google.com > paste `forms/google_form_script.gs` > run `createForm` > copy the link.
5. Set `KOBO_URL` and `GFORM_URL` (file `.streamlit/secrets.toml`, template in `.streamlit/secrets.toml.example`).
6. GitHub: push the folder (including `data/clean` and `data/raw`). Deploy on share.streamlit.io (`app.py`) and paste the
   secrets in Settings > Secrets. `packages.txt` installs Chromium on Streamlit Cloud.

## Video outline (10 min)
8 min of code: Selenium driver > Books scraping (list pages, then book pages) > cleaning > Gaaraas scraping (regex on listing text)
> cleaning > SQL database > app.py (4 pages); 2 min demo of the deployed app.
