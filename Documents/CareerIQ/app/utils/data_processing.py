import pandas as pd

def clean_location(loc):
    if pd.isna(loc):
        return None
    loc = loc.lower()
    if "pune" in loc:
        return "Pune"
    if "bangalore" in loc or "bengaluru" in loc:
        return "Bengaluru"
    if "mumbai" in loc:
        return "Mumbai"
    if "hyderabad" in loc:
        return "Hyderabad"
    if "chennai" in loc:
        return "Chennai"
    if "delhi" in loc or "ncr" in loc or "gurgaon" in loc:
        return "Delhi NCR"
    return loc.title()


def map_job_group(title):
    title = str(title).lower()
    if "data scientist" in title:
        return "Data Scientist"
    if "data analyst" in title:
        return "Data Analyst"
    if "machine learning" in title or "ml engineer" in title:
        return "ML Engineer"
    if "ai engineer" in title:
        return "AI Engineer"
    if "data engineer" in title:
        return "Data Engineer"
    if "cloud" in title:
        return "Cloud Engineer"
    if "business analyst" in title:
        return "Business Analyst"
    if "software" in title or "developer" in title:
        return "Software Engineer"
    return "Other Roles"


def preprocess_data(df):
    df["clean_location"] = df["location"].apply(clean_location)
    df["job_group"] = df["job_title"].apply(map_job_group)

    df["experience"] = df["experience"].astype(str).str.strip()
    valid_exp = ["0-1", "1-2", "2-5", "5-10", "10+"]
    df = df[df["experience"].isin(valid_exp)]

    return df