import requests
from bs4 import BeautifulSoup
import json
import datetime
import pandas as pd

# ── STEP 1: SCRAPE REVIEWS ───────────────────────────────────
def scrape_reviews():
    reviews = []
    headers = {"User-Agent": "Mozilla/5.0"}

    print("🔍 Scraping product reviews...")

    for page in range(1, 4):
        url = f"http://books.toscrape.com/catalogue/page-{page}.html"
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        for book in soup.select("article.product_pod"):
            title = book.h3.a["title"]
            price = book.select_one(".price_color").text.strip()
            rating_map = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
            rating = rating_map.get(book.p["class"][1], 0)
            availability = book.select_one(".availability").text.strip()

            # Simulate review text based on rating
            review_templates = {
                5: "Absolutely loved this book! Highly recommend to everyone.",
                4: "Really good read, enjoyed it a lot. Minor issues but overall great.",
                3: "It was okay, nothing special. Average experience overall.",
                2: "Disappointing. Expected much better quality for the price.",
                1: "Terrible. Complete waste of money. Would not recommend."
            }

            reviews.append({
                "title": title,
                "price": price,
                "rating": rating,
                "availability": availability,
                "review_text": review_templates.get(rating, "No review"),
                "date": datetime.date.today().strftime("%Y-%m-%d")
            })

        print(f"✅ Scraped page {page} — {len(reviews)} reviews so far")

    return reviews

# ── STEP 2: BASIC SENTIMENT SCORING ─────────────────────────
def score_sentiment(reviews):
    print("\n📊 Scoring sentiment...")

    for review in reviews:
        rating = review["rating"]
        if rating >= 4:
            review["sentiment"] = "POSITIVE"
            review["sentiment_score"] = rating / 5
        elif rating == 3:
            review["sentiment"] = "NEUTRAL"
            review["sentiment_score"] = 0.5
        else:
            review["sentiment"] = "NEGATIVE"
            review["sentiment_score"] = rating / 5

    # Save to CSV
    df = pd.DataFrame(reviews)
    df.to_csv("reviews.csv", index=False)

    # Summary stats
    positive = len([r for r in reviews if r["sentiment"] == "POSITIVE"])
    neutral = len([r for r in reviews if r["sentiment"] == "NEUTRAL"])
    negative = len([r for r in reviews if r["sentiment"] == "NEGATIVE"])

    stats = {
        "total_reviews": len(reviews),
        "positive": positive,
        "neutral": neutral,
        "negative": negative,
        "positive_pct": round(positive / len(reviews) * 100, 1),
        "negative_pct": round(negative / len(reviews) * 100, 1),
        "avg_rating": round(sum(r["rating"] for r in reviews) / len(reviews), 2),
        "sample_positive": [r for r in reviews if r["sentiment"] == "POSITIVE"][:3],
        "sample_negative": [r for r in reviews if r["sentiment"] == "NEGATIVE"][:3]
    }

    print(f"✅ Positive: {positive} ({stats['positive_pct']}%)")
    print(f"✅ Neutral:  {neutral}")
    print(f"✅ Negative: {negative} ({stats['negative_pct']}%)")
    print(f"💾 Saved reviews.csv")

    return stats

# ── STEP 3: DEEP AI SENTIMENT ANALYSIS ──────────────────────
def analyze_sentiment_with_llm(stats):
    print("\n🤖 Running deep AI sentiment analysis...")

    prompt = f"""
You are a product review analyst. Here is sentiment data from {stats['total_reviews']} product reviews:

SENTIMENT BREAKDOWN:
- Positive reviews: {stats['positive']} ({stats['positive_pct']}%)
- Neutral reviews: {stats['neutral']}
- Negative reviews: {stats['negative']} ({stats['negative_pct']}%)
- Average rating: {stats['avg_rating']}/5

SAMPLE POSITIVE REVIEWS:
{json.dumps(stats['sample_positive'], indent=2)}

SAMPLE NEGATIVE REVIEWS:
{json.dumps(stats['sample_negative'], indent=2)}

Please provide:
1. Overall sentiment verdict (Positive/Neutral/Negative) and confidence level
2. Key themes in positive reviews — what do customers love?
3. Key themes in negative reviews — what are main complaints?
4. Top 3 actionable recommendations for the business
5. Customer satisfaction score out of 100
"""

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "qwen3-vl:4b",
            "prompt": prompt,
            "stream": False
        },
        timeout=None
    )

    analysis = response.json()["response"]

    # Save final report
    today = datetime.date.today().strftime("%Y-%m-%d")
    report = {
        "date": today,
        "sentiment_stats": stats,
        "ai_analysis": analysis,
        "files": ["reviews.csv", f"sentiment_report_{today}.json"]
    }

    with open(f"sentiment_report_{today}.json", "w") as f:
        json.dump(report, f, indent=2)

    print("\n💬 AI SENTIMENT ANALYSIS:")
    print("=" * 50)
    print(analysis)
    print("=" * 50)
    print(f"\n✅ Saved sentiment_report_{today}.json")

    return analysis

# ── RUN ──────────────────────────────────────────────────────
if __name__ == "__main__":
    print("🚀 Starting Review Sentiment Analyzer...\n")
    reviews = scrape_reviews()
    stats = score_sentiment(reviews)
    analyze_sentiment_with_llm(stats)
    print("\n🎉 Sentiment analysis complete!")