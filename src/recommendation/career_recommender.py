from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

SKILL_GAP_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "semantic_skill_gap_results.csv"
)

SKILL_DEMAND_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "skill_demand.csv"
)

OUTPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "career_recommendations.csv"
)


def normalize_skill(skill):
    if skill is None:
        return ""

    return str(skill).strip().lower()


def calculate_market_demand(
    missing_skills,
    demand_lookup,
):
    """
    Calculate a normalized market-demand score
    for the skills missing from a candidate profile.
    """

    if not missing_skills:
        return 0.0

    scores = []

    for skill in missing_skills:

        skill = normalize_skill(skill)

        if skill in demand_lookup:
            scores.append(
                demand_lookup[skill]
            )

    if not scores:
        return 0.0

    return sum(scores) / len(scores)


def build_recommendations(
    skill_gap_df,
    demand_df,
):
    demand_df = demand_df.copy()

    demand_df["skill_normalized"] = (
        demand_df["skill"]
        .apply(normalize_skill)
    )

    max_demand = demand_df[
        "job_count"
    ].max()

    if max_demand > 0:
        demand_df["demand_score"] = (
            demand_df["job_count"]
            / max_demand
            * 100
        )
    else:
        demand_df["demand_score"] = 0.0

    demand_lookup = dict(
        zip(
            demand_df[
                "skill_normalized"
            ],
            demand_df[
                "demand_score"
            ],
        )
    )

    recommendations = []

    for _, row in skill_gap_df.iterrows():

        missing_skills = [
            skill.strip()
            for skill in str(
                row["missing_skills"]
            ).split(",")
            if skill.strip()
        ]

        market_demand = (
            calculate_market_demand(
                missing_skills,
                demand_lookup,
            )
        )

        semantic_score = (
            float(
                row[
                    "semantic_similarity"
                ]
            )
            * 100
        )

        skill_match = float(
            row[
                "skill_match_percentage"
            ]
        )

        # Transparent weighted recommendation score.
        recommendation_score = (
            0.50 * semantic_score
            + 0.35 * skill_match
            + 0.15 * market_demand
        )

        recommendations.append(
            {
                "title": row["title"],
                "company_name": row[
                    "company_name"
                ],
                "work_model": row[
                    "work_model"
                ],
                "experience_level": row[
                    "experience_level"
                ],
                "semantic_similarity": round(
                    float(
                        row[
                            "semantic_similarity"
                        ]
                    ),
                    4,
                ),
                "skill_match_percentage": round(
                    skill_match,
                    2,
                ),
                "market_demand_score": round(
                    market_demand,
                    2,
                ),
                "recommendation_score": round(
                    recommendation_score,
                    2,
                ),
                "matched_skills": row[
                    "matched_skills"
                ],
                "missing_skills": row[
                    "missing_skills"
                ],
            }
        )

    recommendations_df = pd.DataFrame(
        recommendations
    )

    return recommendations_df.sort_values(
        "recommendation_score",
        ascending=False,
    ).reset_index(drop=True)


def main():

    print("=" * 60)
    print("JobInsight - Career Recommendation Engine")
    print("=" * 60)

    skill_gap_df = pd.read_csv(
        SKILL_GAP_PATH
    )

    demand_df = pd.read_csv(
        SKILL_DEMAND_PATH
    )

    print(
        f"Job candidates analyzed: "
        f"{len(skill_gap_df):,}"
    )

    print(
        f"Market skills available: "
        f"{len(demand_df):,}"
    )

    recommendations = build_recommendations(
        skill_gap_df,
        demand_df,
    )

    print(
        "\nCareer recommendations:"
    )

    display_columns = [
        "title",
        "company_name",
        "semantic_similarity",
        "skill_match_percentage",
        "market_demand_score",
        "recommendation_score",
        "missing_skills",
    ]

    print(
        recommendations[
            display_columns
        ].to_string(index=False)
    )

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    recommendations.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    print("\nSaved:")
    print(OUTPUT_PATH)

    print("=" * 60)
    print(
        "Career recommendation analysis completed."
    )
    print("=" * 60)


if __name__ == "__main__":
    main()