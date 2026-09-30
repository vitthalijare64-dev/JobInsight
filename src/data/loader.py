from pathlib import Path

import pandas as pd


# Project root:
# C:\JobInsight
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Raw dataset location
RAW_DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "nextgig_jobs_2026-06.parquet"
)


def load_raw_jobs(path: Path = RAW_DATA_PATH) -> pd.DataFrame:
    """
    Load the raw JobInsight job-posting dataset.

    The raw source file is never modified by this function.
    """

    if not path.exists():
        raise FileNotFoundError(
            f"Job dataset not found at: {path}"
        )

    df = pd.read_parquet(path)

    if df.empty:
        raise ValueError("The job dataset is empty.")

    return df


if __name__ == "__main__":
    jobs = load_raw_jobs()

    print("=" * 60)
    print("JobInsight - Raw Data Loader")
    print("=" * 60)
    print(f"Dataset: {RAW_DATA_PATH}")
    print(f"Rows: {len(jobs):,}")
    print(f"Columns: {len(jobs.columns)}")
    print("=" * 60)