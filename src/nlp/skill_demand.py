from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

RELATIONSHIP_DATASET_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "job_skill_relationships.parquet"
)


def calculate_skill_demand(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate overall skill demand from the job-skill
    relationship dataset.
    """

    demand = (
        df.groupby("skill")
        .agg(
            job_count=("title", "count"),
            unique_companies=("company_name", "nunique"),
        )
        .reset_index()
    )

    demand = demand.sort_values(
        "job_count",
        ascending=False
    ).reset_index(drop=True)

    return demand


def calculate_role_skill_demand(
    df: pd.DataFrame,
    minimum_jobs: int = 20
) -> pd.DataFrame:
    """
    Calculate skill demand by normalized job title.

    Roles with very few postings are excluded to reduce
    unstable frequency estimates.
    """

    role_counts = (
        df.groupby("title")
        .size()
        .reset_index(name="role_job_count")
    )

    valid_roles = role_counts[
        role_counts["role_job_count"] >= minimum_jobs
    ]["title"]

    filtered = df[df["title"].isin(valid_roles)]

    role_skill_demand = (
        filtered.groupby(["title", "skill"])
        .agg(
            job_count=("skill", "count"),
            unique_companies=("company_name", "nunique"),
        )
        .reset_index()
    )

    role_skill_demand = role_skill_demand.sort_values(
        ["title", "job_count"],
        ascending=[True, False]
    ).reset_index(drop=True)

    return role_skill_demand


if __name__ == "__main__":
    print("=" * 60)
    print("JobInsight - Skill Demand Intelligence")
    print("=" * 60)

    if not RELATIONSHIP_DATASET_PATH.exists():
        raise FileNotFoundError(
            "Job-skill relationship dataset not found at: "
            f"{RELATIONSHIP_DATASET_PATH}"
        )

    relationships = pd.read_parquet(
        RELATIONSHIP_DATASET_PATH
    )

    print(
        f"Input job-skill relationships: "
        f"{len(relationships):,}"
    )

    # ---------------------------------------------------------
    # Overall skill demand
    # ---------------------------------------------------------

    demand = calculate_skill_demand(
        relationships
    )

    print("\nTop 20 skills by job demand:")

    print(
        demand.head(20).to_string(
            index=False
        )
    )

    # ---------------------------------------------------------
    # Role-level skill demand
    # ---------------------------------------------------------

    role_skill_demand = calculate_role_skill_demand(
        relationships
    )

    print(
        "\nRole-skill relationships after "
        "minimum-posting filtering:"
    )

    print(
        f"{len(role_skill_demand):,}"
    )

    print("\nExample role-skill demand:")

    print(
        role_skill_demand.head(20).to_string(
            index=False
        )
    )

    # ---------------------------------------------------------
    # Save analytical datasets
    # ---------------------------------------------------------

    overall_path = (
        PROJECT_ROOT
        / "data"
        / "processed"
        / "skill_demand.csv"
    )

    role_path = (
        PROJECT_ROOT
        / "data"
        / "processed"
        / "role_skill_demand.csv"
    )

    demand.to_csv(
        overall_path,
        index=False
    )

    role_skill_demand.to_csv(
        role_path,
        index=False
    )

    print("\nSaved:")
    print(overall_path)
    print(role_path)

    print("=" * 60)
    print("Skill demand analysis completed successfully.")
    print("=" * 60)