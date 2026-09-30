from pathlib import Path

import pandas as pd

from skill_extractor import extract_skills_from_job


PROJECT_ROOT = Path(__file__).resolve().parents[2]

PROCESSED_DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "jobs_processed.parquet"
)

SKILL_DATASET_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "job_skills.parquet"
)


def build_skill_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extract baseline skills from every job and create
    a job-level skill dataset.
    """

    records = []

    for _, row in df.iterrows():
        skills = extract_skills_from_job(row)

        records.append({
            "title": row["title"],
            "company_name": row["company_name"],
            "country": row["country"],
            "work_model": row["work_model"],
            "experience_level": row["experience_level"],
            "skills": skills,
            "skill_count": len(skills),
        })

    return pd.DataFrame(records)


def save_skill_dataset(df: pd.DataFrame) -> None:
    """Save the extracted skill dataset."""

    SKILL_DATASET_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_parquet(
        SKILL_DATASET_PATH,
        index=False
    )


if __name__ == "__main__":
    print("=" * 60)
    print("JobInsight - Skill Dataset Builder")
    print("=" * 60)

    if not PROCESSED_DATA_PATH.exists():
        raise FileNotFoundError(
            f"Processed dataset not found at: {PROCESSED_DATA_PATH}"
        )

    jobs = pd.read_parquet(PROCESSED_DATA_PATH)

    print(f"Input jobs: {len(jobs):,}")

    skill_dataset = build_skill_dataset(jobs)

    save_skill_dataset(skill_dataset)

    jobs_with_skills = (
        skill_dataset["skill_count"] > 0
    ).sum()

    print(f"Output rows: {len(skill_dataset):,}")
    print(f"Jobs with detected skills: {jobs_with_skills:,}")

    print("\nExample:")
    print(skill_dataset.iloc[0].to_dict())

    print("=" * 60)
    print("Skill dataset created successfully.")
    print(f"Saved to:")
    print(SKILL_DATASET_PATH)
    print("=" * 60)