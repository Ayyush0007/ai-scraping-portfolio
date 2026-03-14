import requests
from bs4 import BeautifulSoup
import json
import csv
import datetime
import os

# ── STEP 1: SCRAPE PRICES ────────────────────────────────────
def scrape_prices():
    products = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
    }

    # Using Books to Scrape as price source (reliable, no blocking)
    print("🔍 Scraping product prices...")

    for page in range(1, 4):  # 3 pages = 60 products
        url = f"http://books.toscrape.com/catalogue/page-{page}.html"
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        for book in soup.select("article.product_pod"):
            title = book.h3.a["title"]
            price_text = book.select_one(".price_color").text.strip()
            price = float(price_text.replace("£", "").replace("Â", ""))
            availability = book.select_one(".availability").text.strip()
            rating_map = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
            rating = rating_map.get(book.p["class"][1], 0)

            products.append({
                "title": title,
                "price": price,
                "currency": "GBP",
                "availability": availability,
                "rating": rating,
                "date_checked": datetime.date.today().strftime("%Y-%m-%d"),
                "time_checked": datetime.datetime.now().strftime("%H:%M:%S")
            })

        print(f"✅ Scraped page {page} — {len(products)} products so far")

    return products

# ── STEP 2: TRACK PRICE CHANGES ──────────────────────────────
def track_prices(products):
    history_file = "price_history.json"
    today = datetime.date.today().strftime("%Y-%m-%d")

    # Load existing history
    if os.path.exists(history_file):
        with open(history_file, "r") as f:
            history = json.load(f)
        print(f"\n📂 Loaded existing price history")
    else:
        history = {}
        print(f"\n📂 Creating new price history")

    # Track changes
    changes = []
    for product in products:
        title = product["title"]
        current_price = product["price"]

        if title in history:
            old_price = history[title]["price"]
            if current_price != old_price:
                change = current_price - old_price
                pct = round((change / old_price) * 100, 2)
                changes.append({
                    "title": title,
                    "old_price": old_price,
                    "new_price": current_price,
                    "change": round(change, 2),
                    "change_pct": pct,
                    "direction": "📈 UP" if change > 0 else "📉 DOWN"
                })

        # Update history
        history[title] = {
            "price": current_price,
            "last_checked": today,
            "rating": product["rating"]
        }

    # Save updated history
    with open(history_file, "w") as f:
        json.dump(history, f, indent=2)

    # Save current prices CSV
    with open("current_prices.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=products[0].keys())
        writer.writeheader()
        writer.writerows(products)

    print(f"💾 Saved {len(products)} prices to current_prices.csv")
    print(f"💾 Updated price_history.json")

    if changes:
        print(f"\n⚡ {len(changes)} price changes detected!")
        for c in changes:
            print(f"  {c['direction']} {c['title'][:40]}: £{c['old_price']} → £{c['new_price']} ({c['change_pct']}%)")
    else:
        print("\n✅ No price changes detected since last run")

    return products, changes

# ── STEP 3: AI DEAL FINDER ───────────────────────────────────
def find_deals_with_llm(products, changes):
    print("\n🤖 Asking AI to find best deals...")

    # Best value = high rating + low price
    best_value = sorted(
        [p for p in products if p["rating"] >= 4],
        key=lambda x: x["price"]
    )[:10]

    # Most expensive
    most_expensive = sorted(products, key=lambda x: x["price"], reverse=True)[:5]

    # Price drops
    price_drops = [c for c in changes if c["change"] < 0]

    prompt = f"""
You are a smart shopping assistant analyzing product prices.

BEST VALUE PRODUCTS (high rating + low price):
{json.dumps(best_value, indent=2)}

MOST EXPENSIVE PRODUCTS:
{json.dumps(most_expensive, indent=2)}

RECENT PRICE DROPS:
{json.dumps(price_drops if price_drops else "No price drops today", indent=2)}

Please provide:
1. TOP 3 best deals to buy right now and why
2. Which products to AVOID (overpriced for their rating)
3. Any price drop alerts worth acting on
4. Smart shopping strategy based on this data
"""

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "qwen3-vl:4b",
            "prompt": prompt,
            "stream": False
        },
        timeout=300
    )

    analysis = response.json()["response"]

    # Save final report
    today = datetime.date.today().strftime("%Y-%m-%d")
    report = {
        "date": today,
        "total_products": len(products),
        "price_changes": changes,
        "best_value_products": best_value,
        "ai_recommendations": analysis
    }

    with open(f"price_report_{today}.json", "w") as f:
        json.dump(report, f, indent=2)

    print("\n🛍️ AI DEAL FINDER RESULTS:")
    print("=" * 50)
    print(analysis)
    print("=" * 50)
    print(f"\n✅ Saved price_report_{today}.json")

    return analysis

# ── RUN ──────────────────────────────────────────────────────
if __name__ == "__main__":
    print("🚀 Starting Price Tracker...\n")
    products = scrape_prices()
    products, changes = track_prices(products)
    find_deals_with_llm(products, changes)
    print("\n🎉 Price tracking complete!")
    print("💡 Run again tomorrow to track price changes!")