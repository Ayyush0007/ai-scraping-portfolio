import requests
from bs4 import BeautifulSoup
import json
import datetime

# ── STEP 1: SCRAPE NEWS ─────────────────────────────────────
def scrape_news():
    news = []
    headers = {"User-Agent": "Mozilla/5.0"}

    sources = [
        {
            "name": "BBC Technology",
            "url": "https://feeds.bbci.co.uk/news/technology/rss.xml"
        },
        {
            "name": "BBC Business",
            "url": "https://feeds.bbci.co.uk/news/business/rss.xml"
        }
    ]

    for source in sources:
        print(f"🔍 Scraping {source['name']}...")
        response = requests.get(source["url"], headers=headers)
        soup = BeautifulSoup(response.content, "xml")

        items = soup.find_all("item")[:10]  # Top 10 from each source

        for item in items:
            news.append({
                "source": source["name"],
                "title": item.title.text.strip(),
                "description": item.description.text.strip() if item.description else "N/A",
                "link": item.link.text.strip() if item.link else "N/A",
                "published": item.pubDate.text.strip() if item.pubDate else "N/A"
            })

        print(f"✅ Got {len(items)} articles from {source['name']}")

    return news

# ── STEP 2: SAVE DATA ────────────────────────────────────────
def save_news(news):
    today = datetime.date.today().strftime("%Y-%m-%d")

    with open(f"news_{today}.json", "w") as f:
        json.dump(news, f, indent=2)

    print(f"\n💾 Saved {len(news)} articles to news_{today}.json")
    return news

# ── STEP 3: ANALYZE WITH OLLAMA ──────────────────────────────
def analyze_with_llm(news):
    print("\n🤖 Sending to local LLM for analysis...")

    # Prepare headlines for LLM
    headlines = "\n".join([
        f"- [{item['source']}] {item['title']}: {item['description'][:100]}"
        for item in news
    ])

    prompt = f"""
You are a professional news analyst. Here are today's top news headlines:

{headlines}

Please provide:
1. TOP 3 most important stories and why they matter
2. Key trends you notice across these headlines
3. One sentence summary of today's news landscape
4. Any potential impact on the tech/business world
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

    response_data = response.json()
    if "response" in response_data:
        analysis = response_data["response"]
    else:
        print(f"\n❌ Error from Ollama: {response_data.get('error', response_data)}")
        print("💡 Hint: If the error says model not found, try running: ollama pull llama3.2")
        return "Analysis failed due to LLM error."

    # Save final report
    today = datetime.date.today().strftime("%Y-%m-%d")
    report = {
        "date": today,
        "total_articles": len(news),
        "sources": list(set(item["source"] for item in news)),
        "articles": news,
        "ai_analysis": analysis
    }

    with open(f"news_report_{today}.json", "w") as f:
        json.dump(report, f, indent=2)

    print("\n📰 AI NEWS ANALYSIS:")
    print("=" * 50)
    print(analysis)
    print("=" * 50)
    print(f"\n✅ Full report saved to news_report_{today}.json")

    return analysis

# ── RUN ──────────────────────────────────────────────────────
if __name__ == "__main__":
    print("🚀 Starting News Scraper Pipeline...\n")
    news = scrape_news()
    save_news(news)
    analyze_with_llm(news)
    print("\n🎉 Done! Your daily news report is ready.")