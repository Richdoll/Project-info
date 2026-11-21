"""Shows what Chrome sees on Gaaraas. Run: python debug_gaaraas.py  (add --show-browser to watch)"""
import sys
from selenium.webdriver.common.by import By
from scrapers.driver import get_driver
from scrapers.gaaraas import BASE_URL, CARD_CSS, parse_card

d = get_driver(headless="--show-browser" not in sys.argv)
try:
    d.get(BASE_URL.format(2))
    import time; time.sleep(5)
    print("Page title :", d.title)
    print("Page length:", len(d.page_source), "characters")
    cards = d.find_elements(By.CSS_SELECTOR, CARD_CSS)
    print("Cards found:", len(cards))
    for c in cards[:2]:
        print("--- .text ---------->", repr(c.text[:300]))
        print("--- textContent ---->", repr((c.get_attribute("textContent") or "")[:300]))
        print("--- parsed -------->", parse_card(c.text, c.get_attribute("href")) or parse_card(c.get_attribute("textContent") or "", ""))
    if not cards:
        print("First 500 chars of page:", d.page_source[:500])
finally:
    d.quit()
