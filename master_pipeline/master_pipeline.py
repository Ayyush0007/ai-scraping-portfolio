import subprocess
import json
import os
import datetime
import requests

def run_script(script_path, cwd):
    print(f"Executing {script_path}...")
    result = subprocess.run(["python3", script_path], cwd=cwd, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"Successfully executed {script_path}")
        return True
    else:
        print(f"Error executing {script_path}: {result.stderr}")
        return False

def main():
    today = datetime.date.today().strftime("%Y-%m-%d")
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    projects = [
        {"name": "Job Market Analyzer", "path": "job_market_analyzer/job_pipeline.py", "dir": "job_market_analyzer", "output": "final_report.json"},
        {"name": "News Summarizer", "path": "news_summarizer/news_scraper.py", "dir": "news_summarizer", "output": f"news_report_{today}.json"},
        {"name": "Price Tracker", "path": "price_tracker/price_tracker.py", "dir": "price_tracker", "output": f"price_report_{today}.json"},
        {"name": "Review Sentiment Analyzer", "path": "review_sentiment_analyzer/review_analyzer.py", "dir": "review_sentiment_analyzer", "output": f"sentiment_report_{today}.json"}
    ]
    
    results_summary = {}
    
    print("Starting Master Pipeline Execution...")
    print("=" * 50)
    
    for project in projects:
        print(f"\n--- Running {project['name']} ---")
        script_abs_path = os.path.join(root_dir, project['path'])
        project_dir = os.path.join(root_dir, project['dir'])
        
        if run_script(script_abs_path, project_dir):
            output_path = os.path.join(project_dir, project['output'])
            if os.path.exists(output_path):
                with open(output_path, "r") as f:
                    results_summary[project['name']] = json.load(f)
            else:
                print(f"Warning: Output file {output_path} not found.")
        else:
            print(f"Failed to run {project['name']}")

    print("\n" + "=" * 50)
    print("Generating Master AI Summary...")
    
    # Prepare data for LLM
    llm_context = {
        "date": today,
        "job_market": results_summary.get("Job Market Analyzer", {}).get("statistics", {}),
        "news_headlines": [a["title"] for a in results_summary.get("News Summarizer", {}).get("articles", [])[:5]],
        "top_deals": results_summary.get("Price Tracker", {}).get("best_value_products", [])[:3],
        "sentiment_stats": results_summary.get("Review Sentiment Analyzer", {}).get("sentiment_stats", {})
    }
    
    prompt = f"""
You are a master data analyst and portfolio reviewer. Today you have collected data from 4 different AI scraping pipelines.

DATE: {today}

DATA COLLECTED:
1. JOB MARKET: {json.dumps(llm_context['job_market'], indent=2)}
2. TOP NEWS: {llm_context['news_headlines']}
3. TOP SHOPPING DEALS: {json.dumps(llm_context['top_deals'], indent=2)}
4. REVIEWS SENTIMENT: {json.dumps(llm_context['sentiment_stats'], indent=2)}

Please provide a "State of the World" master summary:
1. One high-level paragraph summarizing how these different sectors (Jobs, News, Commerce) are interacting today.
2. The most interesting "cross-data" insight (e.g., how news might affect job trends or prices).
3. A final verdict on the performance of these 4 AI pipelines.
4. Recommendations for what to scrape next.
"""

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "qwen3-vl:4b",
                "prompt": prompt,
                "stream": False
            },
            timeout=300
        )
        master_analysis = response.json()["response"]
    except Exception as e:
        master_analysis = f"AI Summary generation failed: {e}"

    master_report = {
        "date": today,
        "collected_data": llm_context,
        "master_ai_analysis": master_analysis
    }
    
    report_file = os.path.join(root_dir, "master_pipeline", "master_summary.json")
    with open(report_file, "w") as f:
        json.dump(master_report, f, indent=2)
        
    print("\nMASTER AI ANALYSIS:")
    print("=" * 100)
    print(master_analysis)
    print("=" * 100)
    print(f"\n✅ Master Pipeline execution complete!")
    print(f"✅ Saved summary to: {report_file}")

if __name__ == "__main__":
    main()
