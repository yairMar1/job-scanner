# Job Scanner

An automated job scanner for Israeli tech jobs. Scrapes listings from Goozali and 26+ company career pages, filters by field / seniority / location, and posts new openings to Discord — multiple times a day.

Built by **Yair Margalit** — B.Sc. Computer Science graduate (Ariel University, 2025).

## How it works

```
Goozali Airtable  ──┐
                    ├──► Filter ──► Deduplicate ──► Discord (per field)
Company ATS APIs  ──┘
```

1. **Scrape** — Pulls jobs from Goozali's Airtable shared view (reverse-engineered internal API) and from direct Greenhouse / Lever / Comeet company boards
2. **Filter** — Applies configurable rules: max experience, field, location, title keywords, requirements text
3. **Deduplicate** — Skips jobs already sent, using `state.json` as persistent memory
4. **Notify** — Sends each new job to the matching Discord channel as a rich embed
5. **Repeat** — GitHub Actions runs the pipeline Sun–Thu, 4×/day automatically

## Filter rules (configurable in `config.yaml`)

| Rule | Default |
|------|---------|
| Max experience | 3 years |
| Fields | Software Engineering, Frontend, Mobile, Data Science/ML |
| Locations | Tel Aviv area, Sharon region, Central Israel, Remote |
| Title exclusions | senior, lead, staff, principal, manager, director, VP, architect |

## Project structure

```
job-scanner/
├── main.py                  # Orchestrator: scrape → filter → deduplicate → notify
├── goozali_scraper.py       # Scrapes Goozali's Airtable shared view
├── career_scraper.py        # Scrapes company ATS APIs (Greenhouse, Lever, Comeet)
├── job_filter.py            # Filter engine
├── state_manager.py         # Deduplication via JSON state file
├── discord_notifier.py      # Sends rich embeds to Discord webhooks
├── company_finder.py        # Discovery tool: finds new companies on Greenhouse/Lever
├── config.yaml.example      # Config template (copy to config.yaml)
├── requirements.txt
├── state.json               # Tracks sent jobs (auto-committed by CI)
└── .github/workflows/
    └── scan.yml             # GitHub Actions cron job
```

## Setup

### 1. Clone and install

```bash
git clone https://github.com/yairMar1/job-scanner.git
cd job-scanner
pip install -r requirements.txt
```

### 2. Configure

```bash
cp config.yaml.example config.yaml
```

Edit `config.yaml`:
- Set `goozali_url` to your Goozali shared view URL
- Adjust `filter` rules to your preferences
- Add companies under `companies` (Greenhouse / Lever / Comeet format shown in example)
- Add department name → field mappings under `department_mapping`

### 3. Set up Discord webhooks

Create a `.env` file:

```env
DISCORD_WEBHOOK_SOFTWARE_ENGINEERING=https://discord.com/api/webhooks/...
DISCORD_WEBHOOK_FRONTEND=https://discord.com/api/webhooks/...
DISCORD_WEBHOOK_MOBILE=https://discord.com/api/webhooks/...
DISCORD_WEBHOOK_DATA_SCIENCE_ML=https://discord.com/api/webhooks/...
```

Each key must match the values in `config.yaml` under `discord_webhooks`.

### 4. Run

```bash
# Full pipeline
py main.py

# Limit output for testing (sends at most N jobs)
py main.py --limit 5

# Run individual modules for debugging
py goozali_scraper.py     # Scrape only, print job count
py job_filter.py          # Scrape + filter, print sample jobs
py discord_notifier.py    # Scrape + filter + send 3 test jobs
```

## GitHub Actions (automated scheduling)

The workflow runs Sun–Thu at 9/12/15/18 Israel time. Add these secrets under `Settings → Secrets → Actions`:

| Secret | Value |
|--------|-------|
| `CONFIG_YAML` | Full contents of your `config.yaml` |
| `DISCORD_WEBHOOK_SOFTWARE_ENGINEERING` | Discord webhook URL |
| `DISCORD_WEBHOOK_FRONTEND` | Discord webhook URL |
| `DISCORD_WEBHOOK_MOBILE` | Discord webhook URL |
| `DISCORD_WEBHOOK_DATA_SCIENCE_ML` | Discord webhook URL |

The workflow auto-commits `state.json` after each run to persist deduplication state across runs.

## Discovering new companies

Use `company_finder.py` to find Israeli companies with public Greenhouse or Lever job boards:

```bash
# Auto-discover from company names in your Goozali feed
py company_finder.py --from-goozali

# Or probe specific companies by name
py company_finder.py --companies "Check Point" "Amdocs" "Wix"
```

The script prints config.yaml-ready YAML for every match, skipping companies you already track.

## Tech stack

- **Python 3.13** — core language
- **requests** — HTTP client for all scraping and API calls
- **pyyaml** — configuration loading
- **python-dotenv** — local `.env` file support
- **Discord Webhook API** — job notifications
- **GitHub Actions** — automated scheduling and state persistence

## Key concepts

- **HTTP Sessions** — cookie persistence across requests (needed for Airtable API auth)
- **Regex extraction** — pulling structured data from embedded JavaScript
- **Reverse engineering** — reading Airtable's and Comeet's internal APIs from page source
- **Configuration-driven design** — all filter rules and company lists in YAML, no hardcoded values
- **Deduplication** — JSON state file prevents re-sending the same job on repeated runs
- **CI/CD** — GitHub Actions for scheduled, automated execution

## Credits

Job listings sourced in part from **Goozali** — a community-maintained job board shared by the Israeli tech community.
