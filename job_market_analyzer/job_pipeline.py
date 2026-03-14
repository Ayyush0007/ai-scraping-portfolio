import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import time

# ── STEP 1: SCRAPE REAL REMOTE JOBS ─────────────────────────
def scrape_jobs():
    jobs = []
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
        "Accept": "application/json"
    }
    
    print("🔍 Fetching jobs from RemoteOK...")
    
    # RemoteOK has a free public API — no blocking!
    url = "https://remoteok.com/api"
    response = requests.get(url, headers=headers)
    time.sleep(2)  # Be polite to the server
    
    data = response.json()
    
    # First item is a notice, skip it
    job_list = [item for item in data if item.get("slug")]
    
    print(f"Found {len(job_list)} jobs")
    
    for job in job_list[:50]:  # Take first 50 jobs
        jobs.append({
            "title": job.get("position", "N/A"),
            "company": job.get("company", "N/A"),
            "location": job.get("location", "Remote"),
            "tags": ", ".join(job.get("tags", [])),
            "salary": job.get("salary", "N/A"),
            "date_posted": job.get("date", "N/A"),
            "url": f"https://remoteok.com/remote-jobs/{job.get('slug', '')}"
        })
    
    print(f"✅ Scraped {len(jobs)} jobs successfully")
    return jobs

# ── STEP 2: CLEAN & SAVE DATA ────────────────────────────────
def process_jobs(jobs):
    if not jobs:
        print("❌ No jobs found.")
        return None
    
    # Save raw JSON
    with open("jobs.json", "w") as f:
        json.dump(jobs, f, indent=2)
    print("💾 Saved jobs.json")
    
    # Save CSV
    df = pd.DataFrame(jobs)
    df.to_csv("jobs.csv", index=False)
    print("💾 Saved jobs.csv")
    
    # Build stats
    stats = {
        "total_jobs": len(jobs),
        "unique_companies": df["company"].nunique(),
        "jobs_with_salary": df[df["salary"] != "N/A"].shape[0],
        "top_locations": df["location"].value_counts().head(5).to_dict(),
        "top_titles": df["title"].value_counts().head(5).to_dict(),
        "all_tags": ", ".join(df["tags"].dropna().tolist()),
        "sample_jobs": [{"title": j["title"], "company": j["company"], "tags": j["tags"][:100]} for j in jobs[:5]]
    }
    
    print(f"\n📊 Stats:")
    print(f"   Total jobs: {stats['total_jobs']}")
    print(f"   Unique companies: {stats['unique_companies']}")
    print(f"   Jobs with salary info: {stats['jobs_with_salary']}")
    print(f"   Top locations: {stats['top_locations']}")
    
    return stats

# ── STEP 3: ANALYZE WITH OLLAMA ──────────────────────────────
def analyze_with_llm(stats):
    print("\n🤖 Sending data to local LLM for analysis...")
    
    prompt = f"""
You are a job market analyst. I scraped {stats['total_jobs']} real remote job listings.

Key statistics:
- Unique companies hiring: {stats['unique_companies']}
- Jobs with salary info: {stats['jobs_with_salary']}
- Top locations: {stats['top_locations']}
- Most common job titles: {stats['top_titles']}
- Common skill tags found: {stats['all_tags'][:500]}

Sample job listings:
{json.dumps(stats['sample_jobs'], indent=2)}

Please provide:
1. Top 3 insights about this remote job market
2. Which technical skills are most in demand based on tags
3. Best strategy for a job seeker targeting remote work
4. Salary expectations based on available data
"""

    import os
    ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
    
    try:
        response = requests.post(
            f"{ollama_url}/api/generate",
            json={
                "model": "qwen3-vl:4b",
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.2,
                    "top_p": 0.9,
                    "seed": 42
                }
            },
            timeout=600  # Increased to 10 minutes due to disk/swap pressure
        )
        response.raise_for_status()
        analysis = response.json()["response"]
        
        # Save complete final report
        final_report = {
            "project": "AI-Powered Remote Job Market Analyzer",
            "data_source": "RemoteOK API",
            "statistics": stats,
            "llm_analysis": analysis,
            "output_files": ["jobs.json", "jobs.csv", "final_report.json"]
        }
        
        with open("final_report.json", "w") as f:
            json.dump(final_report, f, indent=2)
        
        print("\n🤖 LLM ANALYSIS:")
        print("=" * 50)
        print(analysis)
        print("=" * 50)
        print("\n✅ Saved: jobs.json, jobs.csv, final_report.json")
        
        return analysis
    except Exception as e:
        print(f"\n❌ LLM Analysis failed: {e}")
        return None

# ── RUN FULL PIPELINE ────────────────────────────────────────
if __name__ == "__main__":
    print("🚀 Starting AI Job Market Analyzer...\n")
    
    jobs = scrape_jobs()
    stats = process_jobs(jobs)
    
    if stats:
        analyze_with_llm(stats)
        print("\n🎉 Pipeline complete! Your output files are ready.")
        print("📁 Files created: jobs.json | jobs.csv | final_report.json")
