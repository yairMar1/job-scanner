"""Filtering engine for job listings based on configurable rules."""

import logging
import re

logger = logging.getLogger(__name__)

# Matches patterns like "5+ years", "3-5 years", "5 yrs" in requirements text
EXPERIENCE_PATTERN = re.compile(r"(\d+)\+?\s*(?:years|yrs)", re.IGNORECASE)


def filter_jobs(jobs: list[dict], filter_config: dict) -> list[dict]:
    """Filter job listings based on experience, field, location, and title rules.

    A job must pass ALL five checks to be included:
    1. Experience: at or below max_experience_years (missing = pass)
    2. Field: in the allowed fields list
    3. Location: at least one location in the allowed list (missing = pass)
    4. Title: no excluded keywords present
    5. Requirements text: no experience mention exceeding max years

    Args:
        jobs: List of job dicts from the scraper (with resolved selection names).
        filter_config: The 'filter' section of config.yaml.

    Returns:
        List of jobs that passed all filters.
    """
    max_exp = filter_config["max_experience_years"]
    allowed_fields = set(filter_config["fields"])
    allowed_locations = set(filter_config["locations"])
    excluded_keywords = [kw.lower() for kw in filter_config["exclude_title_keywords"]]

    passed = []

    for job in jobs:
        # 1. Experience check
        exp = job.get("Min Experience (Y)")
        if exp is not None and exp > max_exp:
            continue

        # 2. Field check
        field = job.get("Field")
        if field not in allowed_fields:
            continue

        # 3. Location check — pass if missing, otherwise at least one must match
        locations = job.get("Location")
        if locations is not None:
            if isinstance(locations, list):
                if not any(loc in allowed_locations for loc in locations):
                    continue
            elif locations not in allowed_locations:
                continue

        # 4. Title exclusion check
        title = job.get("Job Title", "").lower()
        if any(kw in title for kw in excluded_keywords):
            continue

        # 5. Requirements text check — catch jobs where Goozali says <=3Y
        #    but the actual description mentions higher experience requirements
        reqs = job.get("Requirements", "") or ""
        clean_reqs = re.sub(r"<[^>]+>", " ", reqs)  # Strip HTML tags
        exp_mentions = [int(m) for m in EXPERIENCE_PATTERN.findall(clean_reqs)]
        if exp_mentions and max(exp_mentions) > max_exp:
            continue

        passed.append(job)

    logger.info(
        "Filter: %d total -> %d passed (rejected %d)",
        len(jobs), len(passed), len(jobs) - len(passed),
    )
    return passed


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    import yaml
    from goozali_scraper import scrape_goozali_jobs

    with open("config.yaml", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    jobs = scrape_goozali_jobs(config["goozali_url"])
    filtered = filter_jobs(jobs, config["filter"])

    # Show some examples of what passed
    logger.info("Sample filtered jobs:")
    for job in filtered[:10]:
        logger.info(
            "  [%sY] %s @ %s | %s | %s",
            job.get("Min Experience (Y)", "?"),
            job.get("Job Title", "?"),
            job.get("Company", "?"),
            job.get("Field", "?"),
            job.get("Location", "?"),
        )
