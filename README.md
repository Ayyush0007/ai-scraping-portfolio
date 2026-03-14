# AI Scraping Portfolio — Mindrift Application

4 production-ready AI-powered scraping pipelines combining
web scraping with local LLM analysis using Ollama.

## Projects

### Job Market Analyzer
- Scrapes 50+ real remote jobs from RemoteOK
- LLM analyzes market trends and in-demand skills
- Output: jobs.json, jobs.csv

### News Scraper + AI Summarizer  
- Scrapes BBC Technology and Business headlines
- LLM summarizes top stories and key trends
- Output: news_report.json

### Price Tracker + Deal Finder
- Scrapes 60 products with daily price tracking
- Detects price changes over time
- LLM recommends best deals to buy
- Output: prices.csv, price_report.json

### Review Sentiment Analyzer
- Scrapes 60 product reviews
- Scores sentiment (Positive/Neutral/Negative)
- LLM gives customer satisfaction score + recommendations
- Output: reviews.csv, sentiment_report.json

### Master Pipeline
- Orchestrates all four scraping modules
- Consolidates data from jobs, news, prices, and reviews
- Generates a "Whole Day Summary" using local LLM
- Output: master_summary.json

## Tech Stack
- Python 3.14
- BeautifulSoup, Requests
- Pandas
- Ollama (local LLM — llama3.2)
- JSON + CSV outputs

## How to Run
```bash
python3 -m venv venv
source venv/bin/activate
pip install requests beautifulsoup4 pandas lxml
python3 job_market_analyzer/job_pipeline.py
python3 news_summarizer/news_scraper.py
python3 price_tracker/price_tracker.py
python3 review_sentiment_analyzer/review_analyzer.py
python3 master_pipeline/master_pipeline.py
```

## Skills Demonstrated
- Web scraping static + dynamic sites
- Data cleaning and structured output
- Local LLM integration (Ollama)
- End-to-end AI pipelines
- JSON + CSV data delivery
