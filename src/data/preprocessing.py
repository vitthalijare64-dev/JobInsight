from pathlib import Path

import pandas as pd

from loader import load_raw_jobs


PROJECT_ROOT = Path(__file__).resolve().parents[2]

PROCESSED_DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "jobs_processed.parquet"
)


def clean_text(value):
    """Clean a text value without changing its meaning."""

    if pd.isna(value):
        return None

    value = str(value).strip()

    if not value:
        return None

    return value


def preprocess_jobs(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create a cleaned working copy of the raw job dataset.

    The original dataframe is never modified.
    """

    processed = df.copy()

    # Clean important text fields.
    text_columns = [
        "title",
        "normalized_title",
        "company_name",
        "industry",
        "function",
        "occupational_category",
        "employment_type",
        "work_model",
        "experience_level",
        "education_level",
        "city",
        "country",
        "location_resolved",
        "skills_required",
        "minimum_qualifications",
        "preferred_qualifications",
        "responsibilities",
        "certifications",
        "languages_required",
        "job_description",
    ]

    for column in text_columns:
        if column in processed.columns:
            processed[column] = processed[column].apply(clean_text)

    # Convert date fields to proper datetime values.
    for column in ["date_posted", "closing_date"]:
        if column in processed.columns:
            processed[column] = pd.to_datetime(
                processed[column],
                errors="coerce"
            )

    # Convert salary fields to numeric values.
    for column in ["salary_min", "salary_max", "years_experience_numeric"]:
        if column in processed.columns:
            processed[column] = pd.to_numeric(
                processed[column],
                errors="coerce"
            )

    return processed


def save_processed_jobs(df: pd.DataFrame) -> None:
    """Save the processed dataset."""

    PROCESSED_DATA_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_parquet(
        PROCESSED_DATA_PATH,
        index=False
    )


if __name__ == "__main__":
    print("=" * 60)
    print("JobInsight - Data Preprocessing")
    print("=" * 60)

    jobs = load_raw_jobs()

    print(f"Raw rows: {len(jobs):,}")
    print(f"Raw columns: {len(jobs.columns)}")

    processed_jobs = preprocess_jobs(jobs)

    print(f"Processed rows: {len(processed_jobs):,}")
    print(f"Processed columns: {len(processed_jobs.columns)}")

    save_processed_jobs(processed_jobs)

    print("=" * 60)
    print("Preprocessing completed successfully.")
    print(f"Saved to:")
    print(PROCESSED_DATA_PATH)
    print("=" * 60)