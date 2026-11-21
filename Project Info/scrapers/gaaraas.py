"""Source 2 - Gaaraas (Dakar car listings). 100% Selenium scraping + pandas cleaning.

Each listing is a link <a href=".../vehicle_listings/..."> whose text looks like:
"<photo count> <year> <brand model> <region> Prix CFA <price> Kilométrage <km> km Engine ... (<fuel>) Transmission ... <gearbox>"
(the labels are French because the website is French). Selenium reads this text and regexes parse it.
"""
import re
import time
import pandas as pd

BASE_URL = "https://www.gaaraas.com/fr/users/dakar-auto?page={}"
CARD_CSS = "a[href*='/vehicle_listings/']"

CARD_RE = re.compile(
    r"(?<!\d)((?:19|20)\d{2})(?!\d)\s*(.+?)\s*Prix\s*CFA\s*([\d ]+?)\s*Kilom[ée]trage\s*([\d ]+?)\s*km", re.I
)
GEARBOX_RE = re.compile(r"Transmission\s*(?:xs\s*)?(Manuelle|Automatique|Manual|Automatic)", re.I)
FUEL_RE = re.compile(r"Engine.*?\((\w+)\)", re.I)
MULTI_WORD_BRANDS = ("Land Rover", "Alfa Romeo", "Aston Martin", "Rolls Royce", "Great Wall")


def parse_card(text: str, url: str = ""):
    """Turn a listing's raw text into a dict (None if the format is unexpected)."""
    text = " ".join(text.split())  # normalise spaces / non-breaking spaces
    m = CARD_RE.search(text)
    if not m:
        return None
    year, title_region, price, km = m.groups()
    gearbox = GEARBOX_RE.search(text)
    fuel = FUEL_RE.search(text)
    return {
        "year_raw": year,
        "title_region_raw": title_region,
        "price_raw": price,
        "km_raw": km,
        "gearbox_raw": gearbox.group(1) if gearbox else "",
        "fuel": fuel.group(1) if fuel else "",
        "url": url,
    }


def scrape_page(driver, page: int, wait: int = 10) -> list[dict]:
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.common.exceptions import TimeoutException

    driver.get(BASE_URL.format(page))
    try:
        WebDriverWait(driver, wait).until(lambda d: d.find_elements(By.CSS_SELECTOR, CARD_CSS))
    except TimeoutException:
        return []
    rows = []
    for card in driver.find_elements(By.CSS_SELECTOR, CARD_CSS):
        # textContent = all the text of the block, even if visually hidden
        href = card.get_attribute("href") or ""
        # try the visible text first (keeps spaces/line breaks), then the raw textContent
        row = parse_card(card.text or "", href) or parse_card(card.get_attribute("textContent") or "", href)
        if row:
            rows.append(row)
    return rows


def scrape_gaaraas(driver, start: int = 1, end: int = 100, progress=None, pause: float = 1.0) -> pd.DataFrame:
    """Scrape pages start..end; stops as soon as a page is empty (end of pagination)."""
    rows, seen = [], set()
    for page in range(start, end + 1):
        page_rows = [r for r in scrape_page(driver, page) if r["url"] not in seen]
        if not page_rows:
            break
        seen.update(r["url"] for r in page_rows)
        rows.extend(page_rows)
        if progress:
            progress(page, len(page_rows), len(page_rows))
        time.sleep(pause)
    return pd.DataFrame(rows)


def _split_brand_model(title_region: str):
    t = title_region.replace("\u2012", "-").replace("\u2013", "-").replace("\u2011", "-")  # Mercedes‒Benz
    words = t.split()
    region = words[-1] if len(words) > 2 else ""
    if region:
        words = words[:-1]
    name = " ".join(words)
    for brand in MULTI_WORD_BRANDS:
        if name.lower().startswith(brand.lower()):
            return brand, name[len(brand):].strip(), region
    return (words[0], " ".join(words[1:]), region) if words else ("", "", region)


GEARBOX_EN = {"manuelle": "Manual", "automatique": "Automatic"}


def clean_gaaraas(raw: pd.DataFrame) -> pd.DataFrame:
    if raw.empty:
        return raw
    d = raw.copy()
    parts = d.pop("title_region_raw").map(_split_brand_model)
    d["brand"] = parts.str[0]
    d["model"] = parts.str[1]
    d["region"] = parts.str[2]
    d["year"] = pd.to_numeric(d.pop("year_raw"), errors="coerce").astype("Int64")
    d["price"] = pd.to_numeric(d.pop("price_raw").str.replace(r"\D", "", regex=True), errors="coerce").astype("Int64")
    d["mileage"] = pd.to_numeric(d.pop("km_raw").str.replace(r"\D", "", regex=True), errors="coerce").astype("Int64")
    d["gearbox"] = d.pop("gearbox_raw").str.lower().map(GEARBOX_EN).fillna("Unknown")
    d["fuel"] = d["fuel"].replace({"Essence": "Petrol", "Gasoil": "Diesel"})
    d = d.drop_duplicates(subset="url").dropna(subset=["year", "price"]).reset_index(drop=True)
    return d[["brand", "model", "year", "price", "mileage", "gearbox", "region", "fuel", "url"]]
