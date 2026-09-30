from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

SKILL_DEMAND_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "skill_demand.csv"
)

ROLE_SKILL_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "role_skill_demand.csv"
)

COOCCURRENCE_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "skill_cooccurrence.csv"
)

JOB_SKILLS_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "job_skills_normalized.parquet"
)


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Skills Intelligence | JobInsight",
    page_icon="🧠",
    layout="wide",
)


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
    <style>

    .skill-card {
        padding: 20px;
        border: 1px solid #e5e7eb;
        border-radius: 16px;
        background: white;
        margin-bottom: 16px;
    }

    .skill-name {
        font-size: 20px;
        font-weight: 700;
    }

    .skill-value {
        font-size: 28px;
        font-weight: 800;
    }

    .skill-label {
        color: #64748b;
        font-size: 14px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_data():

    skill_demand = pd.read_csv(
        SKILL_DEMAND_PATH
    )

    role_skill = pd.read_csv(
        ROLE_SKILL_PATH
    )

    cooccurrence = pd.read_csv(
        COOCCURRENCE_PATH
    )

    job_skills = pd.read_parquet(
        JOB_SKILLS_PATH
    )

    return (
        skill_demand,
        role_skill,
        cooccurrence,
        job_skills,
    )


skill_demand, role_skill, cooccurrence, job_skills = load_data()


# ============================================================
# NORMALIZE COLUMN NAMES
# ============================================================

skill_demand.columns = [
    str(c).strip()
    for c in skill_demand.columns
]

role_skill.columns = [
    str(c).strip()
    for c in role_skill.columns
]

cooccurrence.columns = [
    str(c).strip()
    for c in cooccurrence.columns
]


# ============================================================
# HELPER
# ============================================================

def find_column(df, candidates):

    for candidate in candidates:

        if candidate in df.columns:
            return candidate

    return None


skill_column = find_column(
    skill_demand,
    [
        "skill",
        "Skill",
        "canonical_skill",
    ],
)

count_column = find_column(
    skill_demand,
    [
        "job_count",
        "count",
        "frequency",
        "demand",
    ],
)


# ============================================================
# HEADER
# ============================================================

st.title("🧠 Skills Intelligence")

st.markdown(
    """
    Understand which skills are demanded across the job market,
    which roles require them, and which skills frequently appear
    together.
    """
)


# ============================================================
# KPI SECTION
# ============================================================

if skill_column:

    total_skills = (
        skill_demand[skill_column]
        .nunique()
    )

else:
    total_skills = len(skill_demand)


if count_column:

    total_skill_detections = (
        pd.to_numeric(
            skill_demand[count_column],
            errors="coerce"
        )
        .fillna(0)
        .sum()
    )

else:
    total_skill_detections = 0


total_relationships = len(cooccurrence)

total_job_skill_records = len(job_skills)


k1, k2, k3, k4 = st.columns(4)

k1.metric(
    "Unique Skills",
    f"{total_skills:,}"
)

k2.metric(
    "Skill Detections",
    f"{total_skill_detections:,.0f}"
)

k3.metric(
    "Skill Relationships",
    f"{total_relationships:,}"
)

k4.metric(
    "Job-Skill Records",
    f"{total_job_skill_records:,}"
)


st.divider()


# ============================================================
# SIDEBAR FILTER
# ============================================================

st.sidebar.header("Skill Filters")


top_n = st.sidebar.slider(
    "Skills to display",
    min_value=5,
    max_value=30,
    value=15,
    step=5,
)


# ============================================================
# MOST DEMANDED SKILLS
# ============================================================

st.subheader("🔥 Most Demanded Skills")

if skill_column and count_column:

    demand_chart = skill_demand.copy()

    demand_chart[count_column] = pd.to_numeric(
        demand_chart[count_column],
        errors="coerce"
    )

    demand_chart = (
        demand_chart
        .dropna(subset=[count_column])
        .sort_values(
            count_column,
            ascending=False
        )
        .head(top_n)
        .sort_values(
            count_column,
            ascending=True
        )
    )

    fig = px.bar(
        demand_chart,
        x=count_column,
        y=skill_column,
        orientation="h",
        labels={
            count_column: "Jobs",
            skill_column: "Skill",
        },
        title=f"Top {top_n} Skills by Job Demand",
    )

    fig.update_layout(
        height=550,
        margin=dict(
            l=20,
            r=20,
            t=60,
            b=20,
        ),
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

else:

    st.warning(
        "Skill demand columns could not be detected."
    )


# ============================================================
# SKILL EXPLORER
# ============================================================

st.divider()

st.subheader("🔎 Explore a Skill")

if skill_column:

    available_skills = sorted(
        skill_demand[skill_column]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    selected_skill = st.selectbox(
        "Select a skill",
        available_skills,
    )

    selected_row = skill_demand[
        skill_demand[skill_column].astype(str)
        == selected_skill
    ]

    if not selected_row.empty and count_column:

        demand_value = pd.to_numeric(
            selected_row.iloc[0][count_column],
            errors="coerce"
        )

        if pd.notna(demand_value):

            st.markdown(
                f"""
                <div class="skill-card">
                    <div class="skill-name">
                        {selected_skill}
                    </div>
                    <div class="skill-label">
                        Detected in approximately
                    </div>
                    <div class="skill-value">
                        {demand_value:,.0f}
                    </div>
                    <div class="skill-label">
                        job records
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )


# ============================================================
# ROLE-SKILL ANALYSIS
# ============================================================

st.divider()

st.subheader("💼 Skill Demand by Role")

if not role_skill.empty:

    role_skill_columns = role_skill.columns.tolist()

    role_column = find_column(
        role_skill,
        [
            "title",
            "role",
            "normalized_title",
            "job_title",
        ],
    )

    role_skill_column = find_column(
        role_skill,
        [
            "skill",
            "Skill",
            "canonical_skill",
        ],
    )

    role_count_column = find_column(
        role_skill,
        [
            "job_count",
            "count",
            "frequency",
            "demand",
        ],
    )

    if (
        role_column
        and role_skill_column
        and role_count_column
    ):

        role_options = sorted(
            role_skill[role_column]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        selected_role = st.selectbox(
            "Select a job role",
            role_options,
        )

        role_data = role_skill[
            role_skill[role_column].astype(str)
            == selected_role
        ].copy()

        role_data[role_count_column] = pd.to_numeric(
            role_data[role_count_column],
            errors="coerce"
        )

        role_data = (
            role_data
            .dropna(subset=[role_count_column])
            .sort_values(
                role_count_column,
                ascending=False
            )
            .head(15)
        )

        fig_role = px.bar(
            role_data.sort_values(
                role_count_column,
                ascending=True
            ),
            x=role_count_column,
            y=role_skill_column,
            orientation="h",
            labels={
                role_count_column: "Jobs",
                role_skill_column: "Skill",
            },
            title=f"Top Skills for {selected_role}",
        )

        fig_role.update_layout(
            height=500,
            margin=dict(
                l=20,
                r=20,
                t=60,
                b=20,
            ),
        )

        st.plotly_chart(
            fig_role,
            use_container_width=True
        )

    else:

        st.info(
            "Role-skill columns could not be detected."
        )


# ============================================================
# SKILL CO-OCCURRENCE
# ============================================================

st.divider()

st.subheader("🔗 Skill Co-occurrence")

st.markdown(
    """
    These relationships show which skills frequently appear
    together within the same job postings.
    """
)

if not cooccurrence.empty:

    skill_a_column = find_column(
        cooccurrence,
        [
            "skill_1",
            "skill_a",
            "skill1",
        ],
    )

    skill_b_column = find_column(
        cooccurrence,
        [
            "skill_2",
            "skill_b",
            "skill2",
        ],
    )

    pair_count_column = find_column(
        cooccurrence,
        [
            "cooccurrence_count",
            "count",
            "frequency",
            "jobs",
        ],
    )

    if (
        skill_a_column
        and skill_b_column
        and pair_count_column
    ):

        pair_data = cooccurrence.copy()

        pair_data[pair_count_column] = pd.to_numeric(
            pair_data[pair_count_column],
            errors="coerce"
        )

        pair_data = (
            pair_data
            .dropna(subset=[pair_count_column])
            .sort_values(
                pair_count_column,
                ascending=False
            )
            .head(20)
        )

        pair_data["Skill Pair"] = (
            pair_data[skill_a_column].astype(str)
            + " + "
            + pair_data[skill_b_column].astype(str)
        )

        fig_pairs = px.bar(
            pair_data.sort_values(
                pair_count_column,
                ascending=True
            ),
            x=pair_count_column,
            y="Skill Pair",
            orientation="h",
            labels={
                pair_count_column: "Jobs"
            },
            title="Most Common Skill Combinations",
        )

        fig_pairs.update_layout(
            height=600,
            margin=dict(
                l=20,
                r=20,
                t=60,
                b=20,
            ),
        )

        st.plotly_chart(
            fig_pairs,
            use_container_width=True
        )

        st.dataframe(
            pair_data[
                [
                    skill_a_column,
                    skill_b_column,
                    pair_count_column,
                ]
            ].reset_index(drop=True),
            use_container_width=True,
            hide_index=True,
        )

    else:

        st.info(
            "Co-occurrence columns could not be detected."
        )


# ============================================================
# METHODOLOGY
# ============================================================

st.divider()

with st.expander("📘 About Skills Intelligence"):

    st.markdown(
        """
        ### Skill Demand

        Skill demand is derived from the normalized skill extraction
        dataset. Each detected skill is counted across job postings.

        ### Role-Skill Demand

        Role-level analysis connects job roles with the skills
        detected in their associated postings.

        ### Skill Co-occurrence

        Co-occurrence measures how frequently two skills appear
        together in the same job posting.

        ### Important Note

        These metrics describe patterns in the available job-posting
        dataset. They should not be interpreted as guarantees of
        hiring demand, salary outcomes, or future market trends.
        """
    )