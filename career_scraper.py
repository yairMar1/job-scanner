import requests

def fetch_greenhouse_jobs(token: str) -> list[dict]:
    """Fetch all jobs from a Greenhouse job board. Returns raw JSON list."""
    url = f"https://boards-api.greenhouse.io/v1/boards/{token}/jobs"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()["jobs"]

def fetch_lever_jobs(company: str) -> list[dict]:
    """Fetch all jobs from a Lever job board. Returns raw JSON list."""
    url = f"https://api.lever.co/v0/postings/{company}"
    headers = {"Accept": "application/json"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def normalize_job(raw: dict, platform: str, company_name: str, department_mapping: dict) -> dict:
    """Convert a raw API job dict to our standard pipeline format."""
    if platform == "greenhouse":
        return {
            "Job ID": f"gh-{raw['id']}",
            "Job Title": raw["title"],
            "Company": company_name,
            "Location": (raw.get("location") or {}).get("name"),
            "Field": department_mapping.get((raw.get("departments") or [{}])[0].get("name", ""), None),
            "Position Link": raw["absolute_url"],
            "platform": platform,
        }
    elif platform == "lever":
        return {
            "Job ID": f"lv-{raw['id']}",
            "Job Title": raw["text"],
            "Company": company_name,
            "Location": raw.get("categories", {}).get("location", "Remote"),
            "Field": department_mapping.get(raw.get("categories", {}).get("team", ""), None),
            "Position Link": raw["hostedUrl"],
            "platform": platform,
        }
    else:
        raise ValueError(f"Unsupported platform: {platform}")
    

def scrape_career_pages(companies: list[dict], department_mapping: dict) -> list[dict]:
    """Scrape jobs from all configured companies. Returns normalized job list."""
    all_jobs = []
    for company in companies:
        name = company["name"]
        platform = company["platform"]
        try:
            if platform == "greenhouse":
                raw_jobs = fetch_greenhouse_jobs(company["token"])
            elif platform == "lever":
                raw_jobs = fetch_lever_jobs(company["token"])
            else:
                continue  # unknown platform, skip
            for raw in raw_jobs:
                all_jobs.append(normalize_job(raw, platform, name, department_mapping))
        except Exception:
            pass  # one company failing shouldn't break the rest
    return all_jobs
