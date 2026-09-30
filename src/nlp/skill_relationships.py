from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

SKILL_DATASET_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "job_skills.parquet"
)

RELATIONSHIP_DATASET_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "job_skill_relationships.parquet"
)


def build_skill_relationships(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert job-level skill lists into one row per
    job-skill relationship.
    """

    records = []

    for _, row in df.iterrows():

        skills = row["skills"]

        if skills is None:
            continue

        for skill in skills:
            records.append({
                "title": row["title"],
                "company_name": row["company_name"],
                "country": row["country"],
                "work_model": row["work_model"],
                "experience_level": row["experience_level"],
                "skill": skill,
            })

    return pd.DataFrame(records)


def save_relationships(df: pd.DataFrame) -> None:
    """Save the job-skill relationship dataset."""

    RELATIONSHIP_DATASET_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_parquet(
        RELATIONSHIP_DATASET_PATH,
        index=False
    )


if __name__ == "__main__":
    print("=" * 60)
    print("JobInsight - Job-Skill Relationship Builder")
    print("=" * 60)

    if not SKILL_DATASET_PATH.exists():
        raise FileNotFoundError(
            f"Skill dataset not found at: {SKILL_DATASET_PATH}"
        )

    skill_dataset = pd.read_parquet(SKILL_DATASET_PATH)

    print(f"Input job records: {len(skill_dataset):,}")

    relationships = build_skill_relationships(skill_dataset)

    save_relationships(relationships)

    print(f"Job-skill relationships: {len(relationships):,}")

    print("\nExample relationships:")
    print(relationships.head(10).to_string(index=False))

    print("=" * 60)
    print("Job-skill relationship dataset created successfully.")
    print(f"Saved to:")
    print(RELATIONSHIP_DATASET_PATH)
    print("=" * 60)