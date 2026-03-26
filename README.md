# Job Scanner

Automated system that scans Israeli tech job listings, filters positions relevant to a junior developer, and sends alerts to Discord.

## About

Built by **Yair Margalit** — B.Sc. Computer Science graduate (Ariel University, 2025) with a Deep Learning Specialization (DeepLearning.AI). This project automates my job search while serving as a portfolio piece demonstrating real-world Python skills.

## How it works

```
Goozali Airtable ──> Scraper ──> Filter ──> State Manager ──> Discord
  (6,400+ jobs)     (fetch &     (keep      (skip already    (send rich
                     parse)     relevant)    sent jobs)       embeds)
```

1. **Scrape** — Fetches job listings from Goozali's Airtable shared view by reverse-engineering the internal API
2. **Filter** — Applies configurable rules: experience (0-3Y), field, location, title keywords
3. **Deduplicate** — Checks against `state.json` to avoid sending the same job twice
4. **Notify** — Sends new relevant jobs to Discord as rich embed messages
5. **Repeat** — GitHub Actions runs the pipeline every 2 hours automatically

## Data sources

| Source | Method | Status |
|--------|--------|--------|
| Goozali Airtable (6,400+ jobs) | Reverse-engineered internal API | Done |
| Greenhouse career pages | Public API | Planned (Step 8) |
| Lever career pages | Public API | Planned (Step 8) |
| Comeet career pages | HTML parsing | Planned (Step 8) |

## Filter rules (configurable in `config.yaml`)

| Rule | Value |
|------|-------|
| Max experience | 3 years |
| Fields | Software Engineering, Frontend, Mobile, Data Science/ML, QA |
| Locations | Tel Aviv area, Sharon region, Central Israel, Remote |
| Title exclusions | senior, lead, staff, principal, manager, director, VP, architect |

Current result: **~500 relevant jobs** out of 6,400+ total.

## Project structure

```
job-scanner/
├── config.yaml              # Settings: URLs, filter rules
├── goozali_scraper.py       # Scrape Goozali's Airtable shared view
├── job_filter.py            # Filter engine: experience, field, location, title
├── discord_notifier.py      # Send rich embeds to Discord webhook (Step 3)
├── state_manager.py         # Deduplication via JSON state file (Step 4)
├── main.py                  # Orchestrator: scrape → filter → deduplicate → notify (Step 5)
├── state.json               # Tracks already-sent jobs (gitignored)
├── requirements.txt         # Python dependencies
├── .github/workflows/
│   └── scan.yml             # GitHub Actions cron job (Step 7)
└── README.md
```

## Roadmap

| Step | Module | Description | Status |
|------|--------|-------------|--------|
| 0 | Setup | Discord webhook, Git, Python, venv | Done |
| 1 | `goozali_scraper.py` | HTTP sessions, regex extraction, Airtable internal API | Done |
| 2 | `job_filter.py` | Keyword matching, experience/field/location filtering | Done |
| 3 | `discord_notifier.py` | Discord webhook API, rich embed messages | **Next** |
| 4 | `state_manager.py` | JSON read/write, deduplication by Job ID | Planned |
| 5 | `main.py` | Wire all modules into a single pipeline | Planned |
| 6 | Local testing | End-to-end run, debug, fix issues | Planned |
| 7 | GitHub Actions | Workflow YAML, cron every 2 hours, secrets, auto-commit state | Planned |
| 8 | `career_scraper.py` | Greenhouse/Lever public APIs, Comeet HTML parsing | Planned |
| 9 | README + blog | Documentation, portfolio write-up | Planned |

## Tech stack

- **Python 3.13** — core language
- **requests** — HTTP client for scraping and API calls
- **pyyaml** — configuration file loading
- **beautifulsoup4** — HTML parsing (Step 8)
- **Discord Webhook API** — job notifications
- **GitHub Actions** — automated scheduling

## Setup

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/job-scanner.git
cd job-scanner

# Create virtual environment
python -m venv venv
source venv/Scripts/activate  # Windows Git Bash
# source venv/bin/activate    # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Create config (not tracked by git)
cp config.yaml.example config.yaml
# Edit config.yaml with your Airtable URL and filter preferences

# Set Discord webhook (when Step 3 is done)
export DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/..."

# Run
python main.py  # (available after Step 5)
```

## Key concepts used

- **HTTP Sessions** — cookie persistence across requests for API authentication
- **Regex** — extracting structured data from JavaScript embedded in HTML
- **Reverse engineering** — understanding Airtable's internal API by inspecting page source
- **Configuration-driven filtering** — YAML-based rules, no hardcoded values
- **Deduplication** — state file tracking to prevent duplicate notifications
- **CI/CD** — GitHub Actions for automated, scheduled execution
