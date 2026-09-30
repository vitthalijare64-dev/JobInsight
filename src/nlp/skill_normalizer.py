from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

SKILL_DATASET_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "job_skills.parquet"
)

NORMALIZED_DATASET_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "job_skills_normalized.parquet"
)


# Canonical skill mappings.
# The left side represents common variants.
# The right side is the canonical form used by JobInsight.
SKILL_ALIASES = {
    "python programming": "Python",
    "python developer": "Python",
    "python development": "Python",
    "python scripting": "Python",

    "javascript programming": "JavaScript",
    "js": "JavaScript",

    "typescript programming": "TypeScript",
    "ts": "TypeScript",

    "sql server": "SQL",
    "sql database": "SQL",

    "microsoft excel": "Microsoft Excel",
    "ms excel": "Microsoft Excel",
    "excel": "Microsoft Excel",

    "powerbi": "Power BI",
    "microsoft power bi": "Power BI",

    "amazon web services": "AWS",
    "amazon aws": "AWS",

    "microsoft azure": "Microsoft Azure",
    "azure cloud": "Microsoft Azure",

    "google cloud platform": "Google Cloud",
    "gcp": "Google Cloud",

    "natural language processing": "Natural Language Processing",
    "nlp": "Natural Language Processing",

    "machine learning": "Machine Learning",
    "ml": "Machine Learning",

    "artificial intelligence": "Artificial Intelligence",
    "ai": "Artificial Intelligence",

    "data analytics": "Data Analytics",
    "data analysis": "Data Analysis",

    "project management": "Project Management",
    "pm": "Project Management",

    "rest api": "REST API",
    "rest apis": "REST API",

    "k8s": "Kubernetes",

    "scikit learn": "Scikit-learn",
    "sklearn": "Scikit-learn",

    "pytorch": "PyTorch",

    "tensorflow": "TensorFlow",
}


def normalize_skill(skill: str) -> str:
    """Convert a skill variant into its canonical name."""

    if pd.isna(skill):
        return ""

    skill = str(skill).strip()

    if not skill:
        return ""

    lookup_key = skill.lower()

    return SKILL_ALIASES.get(
        lookup_key,
        skill
    )


def normalize_skill_list(skills) -> list[str]:
    """Normalize and deduplicate a job's skill list."""

    if skills is None:
        return []

    normalized = []

    for skill in skills:
        canonical = normalize_skill(skill)

        if canonical and canonical not in normalized:
            normalized.append(canonical)

    return sorted(normalized)


def normalize_skill_dataset(
    df: pd.DataFrame
) -> pd.DataFrame:
    """Create a normalized copy of the skill dataset."""

    processed = df.copy()

    processed["skills"] = processed["skills"].apply(
        normalize_skill_list
    )

    processed["skill_count"] = processed["skills"].apply(
        len
    )

    return processed


if __name__ == "__main__":
    print("=" * 60)
    print("JobInsight - Skill Normalization")
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

    normalized = normalize_skill_dataset(
        skill_dataset
    )

    normalized.to_parquet(
        NORMALIZED_DATASET_PATH,
        index=False
    )

    print(
        f"Output job records: "
        f"{len(normalized):,}"
    )

    print("\nExample normalized skills:")

    examples = (
        normalized[
            normalized["skill_count"] > 0
        ]
        .head(10)
    )

    for _, row in examples.iterrows():
        print(
            f"{row['title']} → "
            f"{row['skills']}"
        )

    print("\nSaved:")
    print(NORMALIZED_DATASET_PATH)

    print("=" * 60)
    print(
        "Skill normalization completed successfully."
    )
    print("=" * 60)