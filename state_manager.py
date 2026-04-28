"""State manager for tracking already-sent job listings."""

import json
import logging

logger = logging.getLogger(__name__)

STATE_FILE = "state.json"


def load_state(path: str = STATE_FILE) -> set[int | str]:
    """Read state.json and return the set of already-sent Job IDs.
    
    If the file doesn't exist (first run) or is corrupted, return empty set.
    """
    try:
        with open(path, "r") as f:
            return set(json.load(f))
    except (FileNotFoundError, json.JSONDecodeError):
        logger.warning("State file not found or corrupted, starting fresh.")
        return set()


def save_state(sent_ids: set[int | str], path: str = STATE_FILE) -> None:
    """Write the set of sent Job IDs to state.json."""
    with open(path, "w") as f:
        json.dump(list(sent_ids), f, indent=2)


def filter_new_jobs(jobs: list[dict], sent_ids: set[int | str]) -> list[dict]:
    """Return only jobs whose Job ID is NOT in sent_ids."""
    new_jobs = [job for job in jobs if job.get("Job ID") not in sent_ids]
    logger.info("Dedup: %d jobs -> %d new (%d already sent)", len(jobs), len(new_jobs), len(jobs) - len(new_jobs))
    return new_jobs


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Quick test: load, add some IDs, save, reload
    state = load_state()
    logger.info("Loaded %d sent IDs", len(state))

    # Simulate sending 3 jobs
    fake_ids = {99991, 99992, 99993}
    state.update(fake_ids)
    save_state(state)
    logger.info("Saved %d IDs (added 3 fake ones)", len(state))

    # Reload and verify
    state2 = load_state()
    logger.info("Reloaded %d IDs — matches: %s", len(state2), state == state2)
