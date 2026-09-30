from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

SKILL_DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "job_skills_normalized.parquet"
)

OUTPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "skill_gap_reference.csv"
)


def normalize_skill(skill):
    """Normalize a skill name for comparison."""

    if skill is None:
        return ""

    return str(skill).strip().lower()


def load_skill_data():
    df = pd.read_parquet(
        SKILL_DATA_PATH
    )

    df["skills"] = df["skills"].apply(
        lambda skills: (
            list(skills)
            if skills is not None
            else []
        )
    )

    return df


def calculate_skill_demand(df):
    """Calculate how frequently each skill occurs."""

    records = []

    for _, row in df.iterrows():

        skills = row["skills"]

        for skill in skills:

            skill = str(skill).strip()

            if not skill:
                continue

            records.append(
                {
                    "skill": skill,
                    "skill_normalized": normalize_skill(
                        skill
                    ),
                    "title": row["title"],
                    "country": row["country"],
                    "work_model": row["work_model"],
                    "experience_level": row[
                        "experience_level"
                    ],
                }
            )

    relationships = pd.DataFrame(
        records
    )

    if relationships.empty:
        return relationships

    demand = (
        relationships
        .groupby(
            [
                "skill",
                "skill_normalized",
            ],
            as_index=False,
        )
        .agg(
            job_count=(
                "title",
                "count",
            ),
            unique_roles=(
                "title",
                "nunique",
            ),
            unique_countries=(
                "country",
                "nunique",
            ),
        )
        .sort_values(
            "job_count",
            ascending=False,
        )
    )

    return demand


def calculate_skill_gap(
    user_skills,
    required_skills,
):
    """
    Compare a user's skills with skills required
    by a target job or group of jobs.
    """

    user_normalized = {
        normalize_skill(skill)
        for skill in user_skills
    }

    required_normalized = {
        normalize_skill(skill)
        for skill in required_skills
    }

    matched = (
        user_normalized
        & required_normalized
    )

    missing = (
        required_normalized
        - user_normalized
    )

    extra = (
        user_normalized
        - required_normalized
    )

    if required_normalized:
        match_percentage = (
            len(matched)
            / len(required_normalized)
            * 100
        )
    else:
        match_percentage = 0.0

    return {
        "matched_skills": sorted(
            matched
        ),
        "missing_skills": sorted(
            missing
        ),
        "additional_user_skills": sorted(
            extra
        ),
        "match_percentage": round(
            match_percentage,
            2,
        ),
    }


if __name__ == "__main__":

    print("=" * 60)
    print("JobInsight - Skill Gap Engine")
    print("=" * 60)

    df = load_skill_data()

    print(
        f"Job records loaded: {len(df):,}"
    )

    demand = calculate_skill_demand(
        df
    )

    print(
        f"Unique skills detected: "
        f"{len(demand):,}"
    )

    print("\nTop 20 demanded skills:")

    print(
        demand.head(20).to_string(
            index=False
        )
    )

    # Example candidate profile.
    example_user_skills = [
        "Python",
        "SQL",
        "Pandas",
        "Git",
    ]

    # Use the most frequently demanded skills
    # as a market-level reference profile.
    reference_skills = (
        demand.head(10)["skill"]
        .tolist()
    )

    gap = calculate_skill_gap(
        example_user_skills,
        reference_skills,
    )

    print(
        "\nExample candidate skills:"
    )

    print(
        example_user_skills
    )

    print(
        "\nReference market skills:"
    )

    print(
        reference_skills
    )

    print("\nSkill gap result:")

    print(
        f"Matched skills: "
        f"{gap['matched_skills']}"
    )

    print(
        f"Missing skills: "
        f"{gap['missing_skills']}"
    )

    print(
        f"Additional user skills: "
        f"{gap['additional_user_skills']}"
    )

    print(
        f"Match percentage: "
        f"{gap['match_percentage']:.2f}%"
    )

    demand.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    print("\nSaved:")
    print(OUTPUT_PATH)

    print("=" * 60)
    print(
        "Skill gap analysis completed."
    )
    print("=" * 60)