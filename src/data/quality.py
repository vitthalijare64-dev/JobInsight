from pathlib import Path

import pandas as pd

from loader import load_raw_jobs


PROJECT_ROOT = Path(__file__).resolve().parents[2]

REPORT_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "data_quality_report.csv"
)


def generate_quality_report(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate a basic data-quality report for the raw job dataset.
    """

    total_rows = len(df)

    report = pd.DataFrame({
        "metric": [
            "total_rows",
            "total_columns",
            "duplicate_complete_rows",
            "missing_job_descriptions",
            "empty_job_descriptions",
            "jobs_with_salary",
            "jobs_without_salary",
            "salary_coverage_percent",
        ],
        "value": [
            total_rows,
            len(df.columns),
            int(df.duplicated().sum()),
            int(df["job_description"].isna().sum()),
            int(
                df["job_description"]
                .fillna("")
                .astype(str)
                .str.strip()
                .eq("")
                .sum()
            ),
            int(df["salary_min"].notna().sum()),
            int(df["salary_min"].isna().sum()),
            round(df["salary_min"].notna().mean() * 100, 2),
        ],
    })

    return report


if __name__ == "__main__":
    print("=" * 60)
    print("JobInsight - Data Quality Check")
    print("=" * 60)

    jobs = load_raw_jobs()

    report = generate_quality_report(jobs)

    print(report.to_string(index=False))

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    report.to_csv(REPORT_PATH, index=False)

    print("=" * 60)
    print(f"Report saved to:")
    print(REPORT_PATH)
    print("=" * 60)