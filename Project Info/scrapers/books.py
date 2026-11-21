"""Source 1 - Books to Scrape. 100% Selenium scraping (no BeautifulSoup) + pandas cleaning."""
import re
import pandas as pd

LIST_URL = "https://books.toscrape.com/catalogue/page-{}.html"
RATINGS = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}


def get_book_links(driver, page: int) -> list[str]:
    from selenium.webdriver.common.by import By
    driver.get(LIST_URL.format(page))
    anchors = driver.find_elements(By.CSS_SELECTOR, "article.product_pod h3 a")
    return [a.get_attribute("href") for a in anchors]


def scrape_book(driver, url: str, products_on_page: int) -> dict:
    """Visit a book page and return the raw data."""
    from selenium.webdriver.common.by import By
    driver.get(url)
    css = lambda sel: driver.find_element(By.CSS_SELECTOR, sel).text.strip()

    desc = driver.find_elements(By.XPATH, "//div[@id='product_description']/following-sibling::p")
    crumbs = driver.find_elements(By.CSS_SELECTOR, "ul.breadcrumb li a")
    table = {}
    for tr in driver.find_elements(By.CSS_SELECTOR, "table.table-striped tr"):
        table[tr.find_element(By.TAG_NAME, "th").text.strip()] = tr.find_element(By.TAG_NAME, "td").text.strip()

    return {
        "title": css("div.product_main h1"),
        "price_raw": css("div.product_main p.price_color"),
        "availability_raw": css("div.product_main p.availability"),
        "products_on_page": products_on_page,
        "rating_raw": driver.find_element(By.CSS_SELECTOR, "p.star-rating").get_attribute("class"),
        "reviews_raw": table.get("Number of reviews", "0"),
        "description": desc[0].text.strip() if desc else "",
        "category": crumbs[-1].text.strip() if crumbs else "",
        "tax_raw": table.get("Tax", ""),
        "upc": table.get("UPC", ""),
        "url": url,
    }


def scrape_books(driver, start: int = 1, end: int = 50, progress=None) -> pd.DataFrame:
    """Scrape catalogue pages start..end (stops if a page is empty)."""
    rows = []
    for page in range(start, end + 1):
        links = get_book_links(driver, page)
        if not links:
            break
        for i, link in enumerate(links, 1):
            try:
                rows.append(scrape_book(driver, link, products_on_page=len(links)))
            except Exception as exc:  # one broken page must not stop the whole run
                print(f"[books] error on {link}: {exc}")
            if progress:
                progress(page, i, len(links))
    return pd.DataFrame(rows)


def _first_number(text):
    m = re.search(r"\d+(?:\.\d+)?", str(text))
    return float(m.group()) if m else None


def _stock_qty(text) -> int:
    m = re.search(r"\((\d+)\s+available", str(text))
    return int(m.group(1)) if m else 0


def clean_books(raw: pd.DataFrame) -> pd.DataFrame:
    if raw.empty:
        return raw
    d = raw.copy()
    d["price"] = d.pop("price_raw").map(_first_number)          # "£51.77" -> 51.77
    d["tax"] = d.pop("tax_raw").map(_first_number)              # "£0.00"  -> 0.0
    availability = d.pop("availability_raw")
    d["availability"] = availability.str.contains("In stock", case=False).map({True: "In stock", False: "Out of stock"})
    d["stock_quantity"] = availability.map(_stock_qty)
    d["rating"] = d.pop("rating_raw").str.split().str[-1].map(RATINGS)  # "star-rating Three" -> 3
    d["reviews_count"] = d.pop("reviews_raw").map(_first_number).fillna(0).astype(int)
    d["description"] = d["description"].fillna("").str.strip()
    d["title"] = d["title"].str.strip()
    d["category"] = d["category"].str.strip()
    d = d.drop_duplicates(subset="url").reset_index(drop=True)
    return d[["title", "price", "availability", "stock_quantity", "products_on_page", "rating",
              "reviews_count", "description", "category", "tax", "upc", "url"]]
