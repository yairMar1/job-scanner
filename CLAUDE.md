# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Run the full pipeline locally (requires .env + config.yaml)
py main.py

# Run with limited output for testing
py main.py --limit 5

# Run individual modules standalone (each has __main__ block)
py goozali_scraper.py    # Scrape only, prints job count
py job_filter.py         # Scrape + filter, prints sample jobs
py discord_notifier.py   # Scrape + filter + send 3 test jobs to Discord
```

No test framework is configured. No linter or formatter is set up.

## Architecture

Pipeline: **Scrape → Filter → Deduplicate → Notify → Save State**

Five modules, each handling one concern:

- **`goozali_scraper.py`** — Reverse-engineers Airtable's internal API by fetching the shared view HTML, extracting API URL + headers via regex, calling `readSharedViewData`, and parsing column IDs to human-readable names. Requires an HTTP Session for cookie persistence.
- **`job_filter.py`** — Applies 5 sequential checks: max experience, allowed fields, allowed locations, excluded title keywords, and requirements text experience regex. A job must pass all 5 to be included.
- **`state_manager.py`** — Tracks sent Job IDs as a `set[int | str]` persisted in `state.json` (Goozali IDs are ints, career-scraped IDs are prefixed strings like `gh-12345`). Used for deduplication between runs.
- **`discord_notifier.py`** — Builds Discord embeds and routes each job to a field-specific webhook. Handles 429 rate limiting with retry.
- **`main.py`** — Orchestrator. Wires all modules, loads config, builds webhook map from env vars.

## Configuration

- **`config.yaml`** (gitignored) — Filter rules, Goozali URL, webhook env var mappings. Copy from `config.yaml.example`.
- **`.env`** (gitignored) — Discord webhook URLs. Loaded via `python-dotenv` locally; in CI, set as GitHub Actions secrets.
- **`state.json`** (tracked) — Auto-committed by GitHub Actions to persist dedup state.

## Key Conventions

- Job data flows as `list[dict[str, str]]` throughout the pipeline. All modules produce/consume the same dict format with keys like `Company`, `Job Title`, `Location`, `Field`, `Min Experience (Y)`, `Position Link`, `Job ID`.
- The `discord_webhooks` config maps field names (e.g., "Software Engineering") to env var names (e.g., "DISCORD_WEBHOOK_SOFTWARE_ENGINEERING"), not directly to URLs.
- `dotenv` import is wrapped in `try/except ImportError` so the code works in CI without the package.
- Each module has a `if __name__ == "__main__"` block for standalone testing.

## CI/CD

GitHub Actions workflow (`.github/workflows/scan.yml`) runs Sun–Thu at 9/12/15/18 Israel time. It creates `config.yaml` from the `CONFIG_YAML` secret at runtime, runs the pipeline, then auto-commits `state.json`.
