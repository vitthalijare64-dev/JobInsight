from pathlib import Path
from collections import Counter

import pandas as pd

from skill_extractor import extract_skills_from_job


PROJECT_ROOT = Path(__file__).resolve().parents[2]

PROCESSED_DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "jobs_processed.parquet"
)


def analyze_skills(df: pd.DataFrame):
    """Run baseline skill extraction across all jobs."""

    skill_counter = Counter()
    jobs_with_skills = 0
    total_detected_skills = 0

    for _, row in df.iterrows():
        skills = extract_skills_from_job(row)

        if skills:
            jobs_with_skills += 1
            total_detected_skills += len(skills)
            skill_counter.update(skills)

    total_jobs = len(df)
    jobs_without_skills = total_jobs - jobs_with_skills

    average_skills = (
        total_detected_skills / jobs_with_skills
        if jobs_with_skills
        else 0
    )

    return (
        skill_counter,
        jobs_with_skills,
        jobs_without_skills,
        average_skills,
    )


if __name__ == "__main__":
    print("=" * 60)
    print("JobInsight - Skill Demand Analysis")
    print("=" * 60)

    if not PROCESSED_DATA_PATH.exists():
        raise FileNotFoundError(
            f"Processed dataset not found at: {PROCESSED_DATA_PATH}"
        )

    jobs = pd.read_parquet(PROCESSED_DATA_PATH)

    (
        skill_counter,
        jobs_with_skills,
        jobs_without_skills,
        average_skills,
    ) = analyze_skills(jobs)

    print(f"Total jobs: {len(jobs):,}")
    print(f"Jobs with detected skills: {jobs_with_skills:,}")
    print(f"Jobs without detected skills: {jobs_without_skills:,}")
    print(f"Average skills per job with skills: {average_skills:.2f}")

    print("\nTop 20 detected skills:")

    for skill, count in skill_counter.most_common(20):
        percentage = (count / len(jobs)) * 100
        print(
            f"{skill:35} "
            f"{count:7,} jobs "
            f"({percentage:6.2f}%)"
        )

    print("=" * 60)
    print("Skill demand analysis completed.")
    print("=" * 60)