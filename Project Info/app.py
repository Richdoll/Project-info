from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

import database as db

st.set_page_config(page_title="Data Collection - Books & Cars", page_icon="📊", layout="wide")

try:  # optional secrets (evaluation form links)
    SECRETS = dict(st.secrets)
except Exception:
    SECRETS = {}
KOBO_URL = SECRETS.get("KOBO_URL", "https://ee.kobotoolbox.org/REPLACE_WITH_YOUR_LINK")
GFORM_URL = SECRETS.get("GFORM_URL", "https://forms.gle/REPLACE_WITH_YOUR_LINK")

db.init_db()
db.seed_from_csv_if_empty()

RAW_FILES = {
    "Books to Scrape": "data/raw/books_webscraper_raw.csv",
    "Gaaraas (Dakar cars)": "data/raw/gaaraas_webscraper_raw.csv",
}


# ---------------------------------------------------------------- Scraper
def page_scraper():
    st.header("🕷️ Scrape data (Selenium)")
    source = st.radio("Source", ["Books to Scrape", "Gaaraas (Dakar cars)"], horizontal=True)
    is_books = source == "Books to Scrape"
    max_page = 50 if is_books else 100
    c1, c2 = st.columns(2)
    start = c1.number_input("First page", 1, max_page, 1)
    end = c2.number_input("Last page", 1, max_page, 2 if is_books else 3)
    if is_books:
        st.info("Each page holds 20 books and every book page is visited: expect ~30 s per page.")
    if end < start:
        st.error("The last page must be greater than or equal to the first page.")
        return

    if st.button("Start scraping", type="primary"):
        from scrapers.driver import get_driver
        from scrapers.books import scrape_books, clean_books
        from scrapers.gaaraas import scrape_gaaraas, clean_gaaraas

        bar, info = st.progress(0.0), st.empty()
        total = int(end - start + 1)

        def progress(page, i, n):
            bar.progress(min(((page - start) + i / max(n, 1)) / total, 1.0))
            info.text(f"Page {page} - item {i}/{n}")

        driver = None
        try:
            with st.spinner("Starting headless Chrome..."):
                driver = get_driver()
            if is_books:
                clean = clean_books(scrape_books(driver, int(start), int(end), progress))
            else:
                clean = clean_gaaraas(scrape_gaaraas(driver, int(start), int(end), progress))
            st.session_state["scraped"] = (source, clean)
        except Exception as exc:
            st.error(f"Error while scraping: {exc}")
        finally:
            if driver:
                driver.quit()
        bar.progress(1.0)

    if "scraped" in st.session_state:
        src, df = st.session_state["scraped"]
        st.success(f"{len(df)} cleaned rows - {src}")
        st.dataframe(df)
        c1, c2 = st.columns(2)
        if c1.button("💾 Save to SQL database"):
            n = db.save_df("books" if src == "Books to Scrape" else "cars", df)
            st.success(f"{n} rows saved.")
        c2.download_button("⬇️ Download as CSV", df.to_csv(index=False).encode("utf-8"),
                           file_name="scraping_result.csv", mime="text/csv")


# ------------------------------------------------- Raw data from Web Scraper
def page_raw():
    st.header("📥 Raw data (Web Scraper, not cleaned)")
    for name, path in RAW_FILES.items():
        st.subheader(name)
        if Path(path).exists():
            df = pd.read_csv(path)
            st.caption(f"{len(df)} rows x {df.shape[1]} columns")
            st.dataframe(df.head(50))
            st.download_button(f"⬇️ Download {Path(path).name}", Path(path).read_bytes(),
                               file_name=Path(path).name, mime="text/csv", key=path)
        else:
            st.warning(f"File not found: {path}")


# ---------------------------------------------------------------- Dashboard
def dashboard_books():
    df = db.load_table("books")
    if df.empty:
        st.info("No Books data in the database yet. Run a scrape first.")
        return
    with st.expander("Filters", expanded=False):
        cats = st.multiselect("Categories", sorted(df["category"].dropna().unique()))
        lo, hi = float(df["price"].min()), float(df["price"].max())
        price = st.slider("Price (£)", lo, hi, (lo, hi)) if lo < hi else (lo, hi)
    if cats:
        df = df[df["category"].isin(cats)]
    df = df[df["price"].between(*price)]

    k = st.columns(4)
    k[0].metric("Books", len(df))
    k[1].metric("Average price", f"£{df['price'].mean():.2f}" if len(df) else "-")
    k[2].metric("In stock", f"{(df['availability'] == 'In stock').mean() * 100:.0f} %" if len(df) else "-")
    k[3].metric("Average rating", f"{df['rating'].mean():.2f} / 5" if len(df) else "-")

    a, b = st.columns(2)
    a.plotly_chart(px.histogram(df, x="price", nbins=30, title="Price distribution (£)"))
    ratings = df["rating"].value_counts().sort_index().reset_index()
    ratings.columns = ["rating", "books"]
    b.plotly_chart(px.bar(ratings, x="rating", y="books", title="Rating distribution"))
    cat = (df.groupby("category")["price"].agg(["mean", "count"]).reset_index()
             .sort_values("count", ascending=False).head(15))
    c, d = st.columns(2)
    c.plotly_chart(px.bar(cat, x="category", y="count", title="Top 15 categories (number of books)"))
    d.plotly_chart(px.bar(cat, x="category", y="mean", title="Average price by category (£)"))
    st.dataframe(df.drop(columns=["description"], errors="ignore"))


def dashboard_cars():
    df = db.load_table("cars")
    if df.empty:
        st.info("No listings in the database yet. Run a scrape first.")
        return
    with st.expander("Filters", expanded=False):
        brands = st.multiselect("Brands", sorted(df["brand"].dropna().unique()))
        y0, y1 = int(df["year"].min()), int(df["year"].max())
        years = st.slider("Year", y0, y1, (y0, y1)) if y0 < y1 else (y0, y1)
    if brands:
        df = df[df["brand"].isin(brands)]
    df = df[df["year"].between(*years)]

    k = st.columns(4)
    k[0].metric("Listings", len(df))
    k[1].metric("Average price", f"{df['price'].mean():,.0f} FCFA".replace(",", " ") if len(df) else "-")
    k[2].metric("Average mileage", f"{df['mileage'].mean():,.0f} km".replace(",", " ") if len(df) else "-")
    k[3].metric("Average year", f"{df['year'].mean():.0f}" if len(df) else "-")

    a, b = st.columns(2)
    a.plotly_chart(px.histogram(df, x="price", nbins=30, title="Price distribution (FCFA)"))
    top = df["brand"].value_counts().head(15).reset_index()
    top.columns = ["brand", "listings"]
    b.plotly_chart(px.bar(top, x="brand", y="listings", title="Top 15 brands"))
    c, d = st.columns(2)
    c.plotly_chart(px.scatter(df, x="year", y="price", color="gearbox", hover_data=["brand", "model"],
                              title="Price by year"))
    d.plotly_chart(px.box(df, x="gearbox", y="price", title="Price by gearbox type"))
    e, f = st.columns(2)
    e.plotly_chart(px.scatter(df, x="mileage", y="price", color="fuel", title="Price by mileage"))
    pm = df.groupby("brand")["price"].mean().sort_values(ascending=False).head(15).reset_index()
    f.plotly_chart(px.bar(pm, x="brand", y="price", title="Average price by brand (top 15)"))
    st.dataframe(df)


def page_dashboard():
    st.header("📊 Dashboard (cleaned data, Selenium scraping)")
    t1, t2 = st.tabs(["📚 Books to Scrape", "🚗 Gaaraas"])
    with t1:
        dashboard_books()
    with t2:
        dashboard_cars()


# --------------------------------------------------------------- Evaluation
def page_forms():
    st.header("📝 Evaluate the application")
    st.write("Please fill in one of the two evaluation forms:")
    c1, c2 = st.columns(2)
    c1.link_button("Kobo form", KOBO_URL)
    c2.link_button("Google Forms form", GFORM_URL)
    if "REPLACE" in KOBO_URL or "REPLACE" in GFORM_URL:
        st.warning("Set KOBO_URL and GFORM_URL in `.streamlit/secrets.toml`.")


PAGES = {
    "🕷️ Scraper": page_scraper,
    "📥 Raw data": page_raw,
    "📊 Dashboard": page_dashboard,
    "📝 Evaluation": page_forms,
}
choice = st.sidebar.radio("Navigation", list(PAGES))
PAGES[choice]()
