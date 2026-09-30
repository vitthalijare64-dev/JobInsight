from pathlib import Path
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_PATH = PROJECT_ROOT / "data" / "processed" / "jobs_processed.parquet"
OUTPUT_PATH = PROJECT_ROOT / "data" / "processed" / "jobs_normalized.parquet"


# ============================================================
# COUNTRY NORMALIZATION
# ============================================================

def normalize_country(value):
    if pd.isna(value):
        return "Unknown"

    value = str(value).strip().lower()

    mapping = {
        "usa": "United States",
        "us": "United States",
        "u.s.": "United States",
        "u.s.a.": "United States",
        "united states": "United States",
        "united states of america": "United States",

        "uk": "United Kingdom",
        "u.k.": "United Kingdom",
        "united kingdom": "United Kingdom",
        "great britain": "United Kingdom",
        "gb": "United Kingdom",

        "uae": "United Arab Emirates",
        "u.a.e.": "United Arab Emirates",
        "united arab emirates": "United Arab Emirates",

        "canada": "Canada",
        "australia": "Australia",
        "india": "India",
        "germany": "Germany",
        "france": "France",
        "spain": "Spain",
        "italy": "Italy",
        "singapore": "Singapore",
        "netherlands": "Netherlands",
        "ireland": "Ireland",
        "mexico": "Mexico",
        "brazil": "Brazil",
        "china": "China",
        "philippines": "Philippines",
        "malaysia": "Malaysia",
        "south africa": "South Africa",
        "indonesia": "Indonesia",
        "new zealand": "New Zealand",
        "japan": "Japan",
        "switzerland": "Switzerland",
        "sweden": "Sweden",
        "norway": "Norway",
        "denmark": "Denmark",
        "belgium": "Belgium",
        "portugal": "Portugal",
        "poland": "Poland",
        "austria": "Austria",
        "finland": "Finland",
        "israel": "Israel",
        "saudi arabia": "Saudi Arabia",
        "qatar": "Qatar",
        "hong kong": "Hong Kong",
        "south korea": "South Korea",
        "korea": "South Korea",
    }

    return mapping.get(value, str(value).strip().title())


# ============================================================
# WORK MODEL NORMALIZATION
# ============================================================

def normalize_work_model(value):
    if pd.isna(value):
        return "Unknown"

    value = str(value).strip().lower()

    # Convert all common Unicode dash characters to normal hyphen
    value = (
        value
        .replace("\u2010", "-")
        .replace("\u2011", "-")
        .replace("\u2012", "-")
        .replace("\u2013", "-")
        .replace("\u2014", "-")
        .replace("\u2212", "-")
        .replace("_", "-")
    )

    if value in {
        "remote",
        "fully remote",
        "100% remote",
    }:
        return "Remote"

    if value in {
        "hybrid",
        "hybrid remote",
        "hybrid/remote",
        "remote/hybrid",
    }:
        return "Hybrid"

    if value in {
        "on-site",
        "onsite",
        "on site",
        "office",
        "in office",
    }:
        return "On-site"

    if value in {
        "unknown",
        "nan",
        "none",
        "",
        "??",
    }:
        return "Unknown"

    return "Unknown"


# ============================================================
# EXPERIENCE LEVEL NORMALIZATION
# ============================================================

def normalize_experience(value):
    if pd.isna(value):
        return "Unknown"

    value = str(value).strip().lower()

    # Standard levels
    if value in {
        "intern",
        "internship",
    }:
        return "Intern"

    if value in {
        "entry",
        "entry-level",
        "entry level",
    }:
        return "Entry"

    if value in {
        "junior",
        "jr",
        "jr.",
    }:
        return "Junior"

    if value in {
        "mid",
        "mid-level",
        "mid level",
        "intermediate",
    }:
        return "Mid"

    if value in {
        "senior",
        "sr",
        "sr.",
        "senior associate",
    }:
        return "Senior"

    if value in {
        "lead",
        "team lead",
    }:
        return "Lead"

    if value == "director":
        return "Director"

    if value in {
        "executive",
        "c-suite",
        "c suite",
        "vp",
        "vice president",
        "principal",
    }:
        return "Executive"

    # Numeric experience ranges
    if value in {
        "0-1",
        "1",
        "1-2",
        "1-3",
        "1 year",
        "1-3 years",
    }:
        return "Entry"

    if value in {
        "3",
        "3 years",
        "3-5",
        "5-7",
        "experienced",
    }:
        return "Mid"

    if value in {
        "7-10",
        "8+",
        "10+",
    }:
        return "Senior"

    # Missing / malformed / descriptive text
    if value in {
        "unknown",
        "nan",
        "none",
        "",
    }:
        return "Unknown"

    if "|" in value:
        return "Unknown"

    if value.startswith("["):
        return "Unknown"

    # Anything else is too ambiguous to classify safely.
    return "Unknown"


# ============================================================
# EMPLOYMENT TYPE NORMALIZATION
# ============================================================

def normalize_employment_type(value):
    if pd.isna(value):
        return "Unknown"

    value = str(value).strip().lower()

    value = (
        value
        .replace("_", "-")
        .replace("\u2010", "-")
        .replace("\u2011", "-")
        .replace("\u2012", "-")
        .replace("\u2013", "-")
        .replace("\u2014", "-")
        .replace("\u2212", "-")
    )

    if value in {
        "full-time",
        "full time",
        "fulltime",
        "full-",
        "full",
    }:
        return "Full-time"

    if value in {
        "part-time",
        "part time",
        "parttime",
        "part_",
        "part",
    }:
        return "Part-time"

    if value in {
        "contract",
        "contractor",
        "independent contractor",
    }:
        return "Contract"

    if value in {
        "temporary",
        "temp",
    }:
        return "Temporary"

    if value in {
        "internship",
        "intern",
    }:
        return "Internship"

    if value in {
        "freelance",
        "freelancer",
    }:
        return "Freelance"

    if value == "seasonal":
        return "Seasonal"

    if value == "casual":
        return "Casual"

    if value == "per diem":
        return "Per Diem"

    if value in {
        "apprenticeship",
        "apprentice",
    }:
        return "Apprenticeship"

    if value in {
        "volunteer",
        "volunteering",
    }:
        return "Volunteer"

    if value in {
        "permanent",
    }:
        return "Permanent"

    if value in {
        "hourly",
    }:
        return "Hourly"

    if value in {
        "flex/per diem",
    }:
        return "Per Diem"

    if value in {
        "unknown",
        "nan",
        "none",
        "",
    }:
        return "Unknown"

    # Combined employment types
    if "full-time" in value and "part-time" in value:
        return "Full-time / Part-time"

    if "full-time" in value and "contract" in value:
        return "Full-time / Contract"

    if "part-time" in value and "contract" in value:
        return "Part-time / Contract"

    if "temporary" in value and "part-time" in value:
        return "Temporary / Part-time"

    return "Unknown"


# ============================================================
# EDUCATION NORMALIZATION
# ============================================================

def normalize_education(value):
    if pd.isna(value):
        return "Unknown"

    value = str(value).strip().lower()

    if value in {
        "0",
        "none",
        "none required",
        "not required",
        "no degree required",
    }:
        return "Not specified / Not required"

    # Doctorate first
    if (
        "ph.d" in value
        or "phd" in value
        or "doctorate" in value
        or "doctoral" in value
    ):
        return "Doctorate"

    # Master
    if (
        "master" in value
        or "msc" in value
        or "m.s." in value
        or "mba" in value
        or "msw" in value
    ):
        return "Master"

    # Bachelor
    if (
        "bachelor" in value
        or "bsc" in value
        or "b.s." in value
        or "ba/bs" in value
        or "b.e" in value
        or "b.tech" in value
        or "btech" in value
        or "bac+4" in value
    ):
        return "Bachelor"

    # Associate
    if (
        "associate" in value
        or "2-year" in value
        or "two year" in value
    ):
        return "Associate"

    # High school
    if (
        "high school" in value
        or "secondary" in value
        or "highschool" in value
    ):
        return "High School"

    # Diploma / certificate
    if (
        "diploma" in value
        or "certificate" in value
        or "trade school" in value
        or "technical school" in value
        or "vocational" in value
        or "technical training" in value
    ):
        return "Diploma / Certificate"

    if value in {
        "unknown",
        "nan",
        "none",
        "",
    }:
        return "Unknown"

    return "Other"


# ============================================================
# MAIN PIPELINE
# ============================================================

def main():

    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"Processed dataset not found at: {INPUT_PATH}"
        )

    df = pd.read_parquet(INPUT_PATH)

    print("=" * 70)
    print("JobInsight - Category Normalization")
    print("=" * 70)

    print(f"Rows: {len(df):,}")
    print(f"Original columns: {len(df.columns)}")

    # Preserve original values for auditability
    df["country_original"] = df["country"]
    df["work_model_original"] = df["work_model"]
    df["experience_level_original"] = df["experience_level"]
    df["employment_type_original"] = df["employment_type"]
    df["education_level_original"] = df["education_level"]

    # Normalize
    df["country"] = df["country"].apply(normalize_country)
    df["work_model"] = df["work_model"].apply(normalize_work_model)
    df["experience_level"] = df["experience_level"].apply(
        normalize_experience
    )
    df["employment_type"] = df["employment_type"].apply(
        normalize_employment_type
    )
    df["education_level"] = df["education_level"].apply(
        normalize_education
    )

    # Save
    df.to_parquet(
        OUTPUT_PATH,
        index=False
    )

    print(f"Normalized columns: {len(df.columns)}")
    print(f"Saved: {OUTPUT_PATH}")

    # Display results
    categories = [
        "country",
        "work_model",
        "experience_level",
        "employment_type",
        "education_level",
    ]

    for column in categories:

        print("\n" + "-" * 60)
        print(column.upper())
        print("-" * 60)

        counts = df[column].value_counts()

        print(counts.head(25).to_string())

    print("\n" + "=" * 70)
    print("Category normalization completed successfully.")
    print("=" * 70)


if __name__ == "__main__":
    main()