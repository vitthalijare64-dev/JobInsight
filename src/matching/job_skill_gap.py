from pathlib import Path

import pandas as pd

from semantic_matcher import (
    semantic_match,
    build_query_text,
)


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
    / "semantic_skill_gap_results.csv"
)


def normalize_skill(skill):
    if skill is None:
        return ""

    text = str(skill).strip().lower()

    if text in {"", "nan", "none", "null"}:
        return ""

    return text


def calculate_skill_gap(
    user_skills,
    required_skills,
):
    user_normalized = {
        normalize_skill(skill)
        for skill in user_skills
        if normalize_skill(skill)
    }

    required_normalized = {
        normalize_skill(skill)
        for skill in required_skills
        if normalize_skill(skill)
    }

    matched = (
        user_normalized
        & required_normalized
    )

    missing = (
        required_normalized
        - user_normalized
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
        "matched": sorted(matched),
        "missing": sorted(missing),
        "match_percentage": round(
            match_percentage,
            2,
        ),
    }


def main():

    print("=" * 60)
    print("JobInsight - Semantic Job + Skill Gap Engine")
    print("=" * 60)

    # --------------------------------------------------------
    # Load skill dataset
    # --------------------------------------------------------

    print(
        f"\nSkill dataset:"
    )
    print(SKILL_DATA_PATH)

    skills_df = pd.read_parquet(
        SKILL_DATA_PATH
    )

    print(
        f"Skill records: {len(skills_df):,}"
    )

    # --------------------------------------------------------
    # Prepare skills
    # --------------------------------------------------------

    skills_df["skills"] = skills_df[
        "skills"
    ].apply(
        lambda skills: (
            list(skills)
            if skills is not None
            else []
        )
    )

    # --------------------------------------------------------
    # Example candidate profile
    # --------------------------------------------------------

    candidate_title = "Data Scientist"

    candidate_skills = [
        "Python",
        "SQL",
        "Pandas",
        "Git",
        "Machine Learning",
    ]

    candidate_experience = "Mid-level"

    candidate_description = (
        "Looking for data science roles "
        "involving machine learning, "
        "data analysis and predictive modeling."
    )

    query = build_query_text(
        candidate_title,
        " ".join(candidate_skills),
        candidate_experience,
        candidate_description,
    )

    print(
        f"\nCandidate: {candidate_title}"
    )

    print(
        f"Candidate skills: "
        f"{candidate_skills}"
    )

    print("\nFinding relevant jobs...")

    # --------------------------------------------------------
    # Semantic matching
    # --------------------------------------------------------
    # The optimized semantic matcher loads the precomputed
    # job embeddings internally.
    # --------------------------------------------------------

    matched_jobs = semantic_match(
        query,
        top_k=10,
    )

    results = []

    # --------------------------------------------------------
    # Calculate skill gaps
    # --------------------------------------------------------

    for _, job in matched_jobs.iterrows():

        # The semantic matcher preserves the original
        # dataset index in the returned DataFrame.
        job_index = job.name

        if job_index in skills_df.index:

            skill_row = skills_df.loc[
                job_index
            ]

        else:

            # Fallback for datasets whose index was
            # reset during processing.
            skill_row = skills_df.iloc[
                int(job_index)
            ]

        required_skills = skill_row[
            "skills"
        ]

        gap = calculate_skill_gap(
            candidate_skills,
            required_skills,
        )

        results.append(
            {
                "title": job["title"],
                "company_name": job[
                    "company_name"
                ],
                "work_model": job[
                    "work_model"
                ],
                "experience_level": job[
                    "experience_level"
                ],
                "semantic_similarity": round(
                    float(
                        job[
                            "similarity_score"
                        ]
                    ),
                    4,
                ),
                "required_skill_count": len(
                    required_skills
                ),
                "matched_skill_count": len(
                    gap["matched"]
                ),
                "missing_skill_count": len(
                    gap["missing"]
                ),
                "skill_match_percentage": gap[
                    "match_percentage"
                ],
                "matched_skills": ", ".join(
                    gap["matched"]
                ),
                "missing_skills": ", ".join(
                    gap["missing"]
                ),
            }
        )

    # --------------------------------------------------------
    # Create results
    # --------------------------------------------------------

    results_df = pd.DataFrame(
        results
    )

    print(
        "\nSemantic matches with skill gaps:"
    )

    if not results_df.empty:

        display_columns = [
            "title",
            "company_name",
            "semantic_similarity",
            "skill_match_percentage",
            "matched_skills",
            "missing_skills",
        ]

        print(
            results_df[
                display_columns
            ].to_string(index=False)
        )

    else:

        print(
            "No semantic matches were returned."
        )

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    results_df.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    print("\nSaved:")
    print(OUTPUT_PATH)

    print("=" * 60)
    print(
        "Semantic skill-gap analysis completed."
    )
    print("=" * 60)


if __name__ == "__main__":
    main()