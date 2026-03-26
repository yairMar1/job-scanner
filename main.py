"""Job Scanner — main orchestrator.

Scrape → Filter → Deduplicate → Notify → Save state.
"""

import logging
import os

import yaml

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None  # Running in CI, env vars set by GitHub Actions

from discord_notifier import notify_jobs
from goozali_scraper import scrape_goozali_jobs
from job_filter import filter_jobs
from state_manager import filter_new_jobs, load_state, save_state

logger = logging.getLogger(__name__)


def main(limit: int | None = None) -> None:
    """Run the full job scanner pipeline.

    Args:
        limit: If set, only send this many jobs (useful for testing).
    """
    if load_dotenv:
        load_dotenv()

    with open("config.yaml", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # Build webhook map: field name -> webhook URL
    webhook_map = {}
    for field_name, env_var in config["discord_webhooks"].items():
        url = os.environ.get(env_var)
        if url:
            webhook_map[field_name] = url
        else:
            logger.warning("Missing env var %s for field '%s'", env_var, field_name)

    if not webhook_map:
        logger.error("No Discord webhooks configured. Set them in .env")
        return

    # 1. Scrape
    logger.info("Step 1: Scraping Goozali...")
    jobs = scrape_goozali_jobs(config["goozali_url"])

    # 2. Filter
    logger.info("Step 2: Filtering jobs...")
    filtered = filter_jobs(jobs, config["filter"])

    # 3. Deduplicate
    logger.info("Step 3: Checking for new jobs...")
    sent_ids = load_state()
    new_jobs = filter_new_jobs(filtered, sent_ids)

    if not new_jobs:
        logger.info("No new jobs to send. Done!")
        return

    # Optional limit for testing (set via --limit flag)
    if limit and len(new_jobs) > limit:
        logger.info("Limiting to %d jobs (out of %d new)", limit, len(new_jobs))
        new_jobs = new_jobs[:limit]

    # 4. Notify
    logger.info("Step 4: Sending %d new jobs to Discord...", len(new_jobs))
    sent_count = notify_jobs(webhook_map, new_jobs)

    # 5. Save state — add the Job IDs of successfully processed jobs
    new_ids = {job["Job ID"] for job in new_jobs if job.get("Job ID") is not None}
    sent_ids.update(new_ids)
    save_state(sent_ids)
    logger.info("Step 5: State saved (%d total sent IDs)", len(sent_ids))

    logger.info("Pipeline complete: %d scraped -> %d filtered -> %d new -> %d sent",
                len(jobs), len(filtered), len(new_jobs), sent_count)


if __name__ == "__main__":
    import argparse

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    parser = argparse.ArgumentParser(description="Job Scanner Pipeline")
    parser.add_argument("--limit", type=int, default=None, help="Max jobs to send (for testing)")
    args = parser.parse_args()

    main(limit=args.limit)
