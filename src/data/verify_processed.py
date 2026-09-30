from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

PROCESSED_DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "jobs_processed.parquet"
)


def verify_processed_data(path: Path = PROCESSED_DATA_PATH) -> pd.DataFrame:
    """Load and verify the processed JobInsight dataset."""

    if not path.exists():
        raise FileNotFoundError(
            f"Processed dataset not found at: {path}"
        )

    df = pd.read_parquet(path)

    if df.empty:
        raise ValueError("Processed dataset is empty.")

    return df


if __name__ == "__main__":
    print("=" * 60)
    print("JobInsight - Processed Data Verification")
    print("=" * 60)

    jobs = verify_processed_data()

    print(f"Rows: {len(jobs):,}")
    print(f"Columns: {len(jobs.columns)}")

    print("\nImportant columns:")
    for column in [
        "title",
        "company_name",
        "work_model",
        "experience_level",
        "salary_min",
        "salary_max",
        "date_posted",
        "job_description",
    ]:
        print(f"  {column}: {jobs[column].dtype}")

    print("\nSample job:")
    print(f"Title: {jobs.iloc[0]['title']}")
    print(f"Company: {jobs.iloc[0]['company_name']}")
    print(f"Work model: {jobs.iloc[0]['work_model']}")
    print(f"Experience: {jobs.iloc[0]['experience_level']}")

    print("=" * 60)
    print("Processed dataset verification successful.")
    print("=" * 60)