"""
CareerIQ – Data Loader (Dynamic)
Loads jobs_master.csv with smart caching.
Auto-triggers a scrape if data is stale (>12 hours old).
"""

import pandas as pd
import os
import streamlit as st
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_PATH = os.path.join(BASE_DIR, "Data", "Processed", "jobs_master.csv")
SCRAPE_LOG_PATH = os.path.join(BASE_DIR, "Data", "Processed", "scrape_log.csv")

AUTO_REFRESH_HOURS = 12


@st.cache_data(ttl=3600, show_spinner=False)
def load_data() -> pd.DataFrame:
    """Load jobs master CSV. Cache refreshes every hour or on manual clear."""
    if not os.path.exists(DATA_PATH):
        return pd.DataFrame(columns=[
            "job_title", "job_description", "skills_extracted",
            "location", "experience", "role_category", "source_dataset"
        ])
    return pd.read_csv(DATA_PATH, dtype=str)


def force_reload() -> pd.DataFrame:
    """Clear Streamlit cache and reload fresh data from disk."""
    load_data.clear()
    return load_data()


def get_data_stats() -> dict:
    """Return metadata about the current dataset."""
    stats = {
        "file_exists": os.path.exists(DATA_PATH),
        "total_records": 0,
        "last_modified": None,
        "last_scraped": None,
        "is_stale": True,
        "age_hours": None,
    }

    if stats["file_exists"]:
        mtime = os.path.getmtime(DATA_PATH)
        stats["last_modified"] = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
        try:
            df = pd.read_csv(DATA_PATH, dtype=str)
            stats["total_records"] = len(df)
        except Exception:
            pass

    if os.path.exists(SCRAPE_LOG_PATH):
        try:
            log_df = pd.read_csv(SCRAPE_LOG_PATH)
            if not log_df.empty:
                last = log_df.iloc[-1]
                stats["last_scraped"] = last.get("timestamp", None)
                last_ts = datetime.strptime(str(last["timestamp"]), "%Y-%m-%d %H:%M:%S")
                age_hours = (datetime.now() - last_ts).total_seconds() / 3600
                stats["is_stale"] = age_hours > AUTO_REFRESH_HOURS
                stats["age_hours"] = round(age_hours, 1)
        except Exception:
            pass

    return stats


def should_auto_refresh() -> bool:
    """True if data is stale and auto-refresh should trigger."""
    return get_data_stats().get("is_stale", True)