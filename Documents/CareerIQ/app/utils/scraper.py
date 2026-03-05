"""
CareerIQ – Job Fetcher via JSearch API (RapidAPI)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
JSearch returns real LinkedIn job listings via a licensed API.

Setup (one-time, free):
  1. https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch
  2. Sign up → Subscribe to Basic (200 req/month free)
  3. Copy API key → paste in app/.streamlit/secrets.toml:
       RAPIDAPI_KEY = "your_key_here"
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import requests
import pandas as pd
import os
import time
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_PATH = os.path.join(BASE_DIR, "Data", "Processed", "jobs_master.csv")
SCRAPE_LOG_PATH = os.path.join(BASE_DIR, "Data", "Processed", "scrape_log.csv")

JSEARCH_URL = "https://jsearch.p.rapidapi.com/search"

# ── Queries — no location suffix, no restrictive filters ─────────────────────
# JSearch's free tier works best with simple, broad queries.
# Location filtering done post-fetch by checking job_country/job_city fields.
SCRAPE_QUERIES = [
    {"keyword": "Data Scientist",             "role_category": "Data Science"},
    {"keyword": "Machine Learning Engineer",  "role_category": "ML Engineering"},
    {"keyword": "Data Analyst",               "role_category": "Data Analytics"},
    {"keyword": "AI Engineer",                "role_category": "AI Engineering"},
    {"keyword": "Data Engineer",              "role_category": "Data Engineering"},
]

KNOWN_SKILLS = [
    "python","sql","machine learning","deep learning","tensorflow","pytorch",
    "scikit-learn","pandas","numpy","spark","pyspark","hadoop","kafka",
    "aws","azure","gcp","docker","kubernetes","git","mlflow",
    "tableau","power bi","nlp","computer vision","statistics",
    "r","scala","java","c++","javascript","airflow","dbt",
    "data visualization","big data","neural networks","transformers",
    "llm","langchain","huggingface","mongodb","postgresql","mysql",
    "redis","snowflake","databricks","excel","lstm","xgboost",
    "lightgbm","fastapi","flask","django","streamlit","opencv",
]


def get_api_key() -> str | None:
    try:
        import streamlit as st
        key = st.secrets.get("RAPIDAPI_KEY", "")
        if key and key not in ("your_key_here", ""):
            return key
    except Exception:
        pass
    key = os.environ.get("RAPIDAPI_KEY", "")
    return key if key else None


def extract_skills(text: str) -> str:
    if not text:
        return ""
    t = text.lower()
    return ", ".join(s for s in KNOWN_SKILLS if s in t)


def normalize_experience(months) -> str:
    try:
        yrs = int(months) // 12
    except (TypeError, ValueError):
        return "2-5"
    if yrs == 0:  return "0-1"
    if yrs <= 2:  return "1-2"
    if yrs <= 5:  return "2-5"
    if yrs <= 10: return "5-10"
    return "10+"


def fetch_jsearch_page(keyword: str, role_category: str,
                       api_key: str, page: int = 1) -> tuple[list[dict], str]:
    """
    Fetch one page from JSearch.
    Returns (jobs_list, error_string).
    error_string is empty on success.
    """
    headers = {
        "X-RapidAPI-Key":  api_key,
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com",
    }
    # Minimal params — avoid filters that restrict results on free tier
    params = {
        "query":     keyword,
        "page":      str(page),
        "num_pages": "1",
    }

    try:
        time.sleep(1.5)
        resp = requests.get(JSEARCH_URL, headers=headers, params=params, timeout=20)

        # Surface clear errors
        if resp.status_code == 401:
            return [], "INVALID_KEY: API key rejected. Double-check RAPIDAPI_KEY in secrets.toml."
        if resp.status_code == 403:
            return [], "FORBIDDEN: Subscribe to JSearch on RapidAPI first (free plan available)."
        if resp.status_code == 429:
            return [], "RATE_LIMIT: Too many requests. Wait a minute and retry."
        if resp.status_code != 200:
            return [], f"HTTP_{resp.status_code}: {resp.text[:200]}"

        data = resp.json()

        # JSearch sometimes wraps errors in a 200 response
        if data.get("status") == "ERROR":
            return [], f"API_ERROR: {data.get('message', 'Unknown error from JSearch')}"

        raw_jobs = data.get("data", [])
        logger.info(f"  '{keyword}' p{page}: {len(raw_jobs)} jobs returned")

        jobs = []
        for j in raw_jobs:
            title    = (j.get("job_title") or "").strip()
            if not title:
                continue
            company  = j.get("employer_name") or ""
            city     = j.get("job_city") or ""
            country  = j.get("job_country") or ""
            location = city if city else (country if country else "India")
            desc     = j.get("job_description") or ""
            highlights = j.get("job_highlights") or {}
            qualifications = " ".join(highlights.get("Qualifications", []))
            skills_raw = j.get("job_required_skills") or []
            if isinstance(skills_raw, list):
                skills_raw = ", ".join(skills_raw)

            full_text = f"{title} {desc} {qualifications} {skills_raw}"
            skills = extract_skills(full_text)
            if not skills and skills_raw:
                skills = str(skills_raw)[:300]

            # Experience from structured field
            exp_info = j.get("job_required_experience") or {}
            months = exp_info.get("required_experience_in_months") if isinstance(exp_info, dict) else None
            experience = normalize_experience(months)

            jobs.append({
                "job_title":        title,
                "job_description":  desc[:500],
                "skills_extracted": skills,
                "location":         location,
                "experience":       experience,
                "role_category":    role_category,
                "source_dataset":   "LinkedIn_Live",
                "company":          company,
                "scraped_at":       datetime.now().strftime("%Y-%m-%d"),
            })

        return jobs, ""

    except requests.exceptions.ConnectionError:
        return [], "CONNECTION_ERROR: No internet or JSearch unreachable."
    except requests.exceptions.Timeout:
        return [], "TIMEOUT: JSearch took too long to respond."
    except Exception as e:
        return [], f"UNEXPECTED: {e}"


def scrape_all_jobs(pages_per_query: int = 2) -> tuple[pd.DataFrame, str]:
    """
    Fetch all queries. Returns (DataFrame, last_error_or_empty).
    """
    api_key = get_api_key()
    if not api_key:
        return pd.DataFrame(), (
            "NO_API_KEY: Add RAPIDAPI_KEY to app/.streamlit/secrets.toml\n"
            "Get a free key at: https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch"
        )

    all_jobs = []
    last_error = ""

    for query in SCRAPE_QUERIES:
        kw, cat = query["keyword"], query["role_category"]
        logger.info(f"Fetching: '{kw}'")
        for page in range(1, pages_per_query + 1):
            jobs, err = fetch_jsearch_page(kw, cat, api_key, page)
            if err:
                logger.error(f"  Error: {err}")
                last_error = err
                break   # stop paging this query on error
            all_jobs.extend(jobs)
            if not jobs:
                break   # no point paging further if page 1 was empty

    if not all_jobs:
        if not last_error:
            last_error = "API returned 0 jobs across all queries."
        return pd.DataFrame(), last_error

    return pd.DataFrame(all_jobs), ""


def merge_and_save(df_new: pd.DataFrame) -> tuple[int, int]:
    if os.path.exists(DATA_PATH):
        df_existing = pd.read_csv(DATA_PATH, dtype=str)
    else:
        df_existing = pd.DataFrame()

    if df_new.empty:
        total = len(df_existing)
        _write_log(0, total, "no_new_data")
        return 0, total

    if not df_existing.empty and "scraped_at" not in df_existing.columns:
        df_existing["scraped_at"] = "legacy"

    def key(df):
        return (df["job_title"].str.lower().str.strip() + "|" +
                df["location"].str.lower().str.strip())

    existing_keys = set(key(df_existing).dropna()) if not df_existing.empty else set()
    df_new = df_new.copy()
    df_new["_k"] = key(df_new)
    df_truly_new = df_new[~df_new["_k"].isin(existing_keys)].copy()
    df_truly_new.drop(columns=["_k"], inplace=True, errors="ignore")
    added = len(df_truly_new)

    df_combined = pd.concat([df_existing, df_truly_new], ignore_index=True)
    df_combined.to_csv(DATA_PATH, index=False)
    _write_log(added, len(df_combined), "success" if added > 0 else "no_new_data")
    logger.info(f"+{added} new · total {len(df_combined)}")
    return added, len(df_combined)


def _write_log(added, total, status):
    entry = pd.DataFrame([{
        "timestamp":     datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "new_records":   added,
        "total_records": total,
        "queries":       len(SCRAPE_QUERIES),
        "status":        status,
    }])
    if os.path.exists(SCRAPE_LOG_PATH):
        log_df = pd.concat([pd.read_csv(SCRAPE_LOG_PATH), entry], ignore_index=True)
    else:
        log_df = entry
    log_df.to_csv(SCRAPE_LOG_PATH, index=False)


def run_scrape_pipeline(pages_per_query: int = 2) -> dict:
    start = time.time()
    df_new, error = scrape_all_jobs(pages_per_query)
    added, total = merge_and_save(df_new)
    return {
        "success":         not bool(error),
        "error":           error,
        "new_records":     added,
        "total_records":   total,
        "elapsed_seconds": round(time.time() - start, 1),
        "timestamp":       datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "scraped_raw":     len(df_new),
    }


def get_last_scrape_info() -> dict | None:
    if not os.path.exists(SCRAPE_LOG_PATH):
        return None
    log_df = pd.read_csv(SCRAPE_LOG_PATH)
    return log_df.iloc[-1].to_dict() if not log_df.empty else None


def is_data_stale(max_age_hours: int = 12) -> bool:
    info = get_last_scrape_info()
    if info is None:
        return True
    try:
        last_ts = datetime.strptime(str(info["timestamp"]), "%Y-%m-%d %H:%M:%S")
        return (datetime.now() - last_ts).total_seconds() / 3600 > max_age_hours
    except Exception:
        return True


def test_api_connection() -> dict:
    """
    Quick single-query test. Returns a dict with status and sample data.
    Used by the debug panel in the Data Refresh page.
    """
    api_key = get_api_key()
    if not api_key:
        return {"ok": False, "error": "No API key configured.", "jobs": [], "raw": {}}

    headers = {
        "X-RapidAPI-Key":  api_key,
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com",
    }
    params = {"query": "Data Scientist", "page": "1", "num_pages": "1"}

    try:
        resp = requests.get(JSEARCH_URL, headers=headers, params=params, timeout=15)
        raw = resp.json() if resp.headers.get("content-type","").startswith("application/json") else {}
        jobs = raw.get("data", [])
        return {
            "ok":          resp.status_code == 200 and len(jobs) > 0,
            "status_code": resp.status_code,
            "jobs_count":  len(jobs),
            "error":       raw.get("message", "") if resp.status_code != 200 else "",
            "sample_job":  jobs[0] if jobs else {},
            "raw_status":  raw.get("status", ""),
        }
    except Exception as e:
        return {"ok": False, "error": str(e), "jobs_count": 0, "sample_job": {}}
