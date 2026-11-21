"""Selenium driver factory (headless Chrome), works locally and on Streamlit Cloud."""
import os
import shutil
import sys

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")


def _find(paths):
    return next((p for p in paths if os.path.exists(p)), None)


def get_driver(headless: bool = True):
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service

    opts = Options()
    if headless:
        opts.add_argument("--headless=new")
    for arg in ("--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu", "--window-size=1366,900",
                "--disable-blink-features=AutomationControlled", f"--user-agent={UA}"):
        opts.add_argument(arg)
    opts.page_load_strategy = "eager"
    # Images are not loaded: faster scraping
    opts.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})

    binary = _find(["/usr/bin/chromium", "/usr/bin/chromium-browser", "/usr/bin/google-chrome"])
    chromedriver = shutil.which("chromedriver") or _find(["/usr/bin/chromedriver", "/usr/lib/chromium/chromedriver"])

    if sys.platform.startswith("linux"):
        # On Streamlit Cloud, Chromium and its matching driver come from packages.txt.
        # Selenium Manager's downloaded driver does NOT work there, so fail with a clear message instead.
        if not (binary and chromedriver):
            raise RuntimeError(
                "Chromium/chromedriver not found. Make sure packages.txt (with 'chromium' and "
                "'chromium-driver') is at the ROOT of the GitHub repo, then reboot the app."
            )
        opts.binary_location = binary
        service = Service(chromedriver)
    else:  # macOS / Windows: Selenium Manager handles the driver
        service = Service()
    return webdriver.Chrome(service=service, options=opts)
