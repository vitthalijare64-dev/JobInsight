from pathlib import Path
from itertools import combinations
from collections import Counter

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

SKILL_DATASET_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "job_skills.parquet"
)

COOCCURRENCE_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "skill_cooccurrence.csv"
)


def calculate_cooccurrence(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate how frequently pairs of skills occur
    together within the same job posting.
    """

    pair_counter = Counter()

    for skills in df["skills"]:

        if skills is None:
            continue

        # Remove duplicates within a job.
        unique_skills = sorted(set(skills))

        # A job needs at least two skills to form a pair.
        if len(unique_skills) < 2:
            continue

        for skill_a, skill_b in combinations(
            unique_skills,
            2
        ):
            pair_counter[(skill_a, skill_b)] += 1

    records = []

    for (skill_a, skill_b), count in pair_counter.items():
        records.append({
            "skill_a": skill_a,
            "skill_b": skill_b,
            "job_count": count,
        })

    result = pd.DataFrame(records)

    if result.empty:
        return result

    result = result.sort_values(
        "job_count",
        ascending=False
    ).reset_index(drop=True)

    return result


if __name__ == "__main__":
    print("=" * 60)
    print("JobInsight - Skill Co-occurrence Analysis")
    print("=" * 60)

    if not SKILL_DATASET_PATH.exists():
        raise FileNotFoundError(
            f"Skill dataset not found at: "
            f"{SKILL_DATASET_PATH}"
        )

    skill_dataset = pd.read_parquet(
        SKILL_DATASET_PATH
    )

    print(
        f"Input job records: "
        f"{len(skill_dataset):,}"
    )

    cooccurrence = calculate_cooccurrence(
        skill_dataset
    )

    print(
        f"Unique skill pairs: "
        f"{len(cooccurrence):,}"
    )

    print("\nTop 20 skill combinations:")

    if not cooccurrence.empty:
        print(
            cooccurrence.head(20).to_string(
                index=False
            )
        )

    cooccurrence.to_csv(
        COOCCURRENCE_PATH,
        index=False
    )

    print("\nSaved:")
    print(COOCCURRENCE_PATH)

    print("=" * 60)
    print(
        "Skill co-occurrence analysis "
        "completed successfully."
    )
    print("=" * 60)