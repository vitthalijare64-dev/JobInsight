from pathlib import Path

import html
import pandas as pd
import plotly.express as px
import streamlit as st


# ============================================================
# Paths
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RECOMMENDATIONS_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "career_recommendations.csv"
)


# ============================================================
# Page configuration
# ============================================================

st.set_page_config(
    page_title="Career Recommendations | JobInsight",
    page_icon="🎯",
    layout="wide",
)


# ============================================================
# Styling
# ============================================================

st.markdown(
    """
    <style>
    .hero {
        padding: 1.5rem 0 1rem 0;
    }

    .hero-title {
        font-size: 2.4rem;
        font-weight: 700;
        margin-bottom: 0.3rem;
    }

    .hero-subtitle {
        color: #6b7280;
        font-size: 1.05rem;
    }

    .job-card {
        padding: 1.2rem;
        border-radius: 16px;
        border: 1px solid #e5e7eb;
        background: #ffffff;
        margin-bottom: 0.8rem;
    }

    .job-title {
        font-size: 1.25rem;
        font-weight: 650;
        margin-bottom: 0.45rem;
    }

    .company {
        color: #6b7280;
        font-size: 0.95rem;
    }

    .skill-chip {
        display: inline-block;
        padding: 0.3rem 0.6rem;
        margin: 0.15rem;
        border-radius: 999px;
        background: #eef2ff;
        font-size: 0.82rem;
    }

    .missing-chip {
        display: inline-block;
        padding: 0.3rem 0.6rem;
        margin: 0.15rem;
        border-radius: 999px;
        background: #fff7ed;
        font-size: 0.82rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# Helper functions
# ============================================================

def clean_value(value, default="Not specified"):
    """
    Convert missing/NaN/empty values into a clean display value.
    """
    if pd.isna(value):
        return default

    text = str(value).strip()

    if not text or text.lower() in {"nan", "none", "null"}:
        return default

    return text


def clean_skill_list(value):
    """
    Convert a comma-separated skill field into a clean list.
    """
    if pd.isna(value):
        return []

    text = str(value).strip()

    if not text or text.lower() in {"nan", "none", "null"}:
        return []

    skills = []

    for skill in text.split(","):
        skill = skill.strip()

        if skill and skill.lower() not in {
            "nan",
            "none",
            "null",
        }:
            skills.append(skill)

    return skills


def safe_number(value, default=0.0):
    """
    Safely convert a value to float.
    """
    try:
        if pd.isna(value):
            return default

        return float(value)

    except (TypeError, ValueError):
        return default


# ============================================================
# Load recommendation data
# ============================================================

if not RECOMMENDATIONS_PATH.exists():
    st.error(
        "Career recommendation data was not found."
    )
    st.stop()


df = pd.read_csv(RECOMMENDATIONS_PATH)


if df.empty:
    st.warning(
        "No career recommendations are available yet."
    )
    st.stop()


# ============================================================
# Clean important columns
# ============================================================

required_columns = [
    "title",
    "company_name",
    "work_model",
    "experience_level",
    "skill_match_percentage",
    "semantic_similarity",
    "recommendation_score",
    "matched_skills",
    "missing_skills",
]


missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
]


if missing_columns:
    st.error(
        "The recommendation dataset is missing required columns: "
        + ", ".join(missing_columns)
    )
    st.stop()


# Clean display columns without changing recommendation logic.

for column in [
    "title",
    "company_name",
    "work_model",
    "experience_level",
]:
    df[column] = df[column].apply(clean_value)


# Make numeric fields robust.

df["skill_match_percentage"] = pd.to_numeric(
    df["skill_match_percentage"],
    errors="coerce",
).fillna(0.0)

df["semantic_similarity"] = pd.to_numeric(
    df["semantic_similarity"],
    errors="coerce",
).fillna(0.0)

df["recommendation_score"] = pd.to_numeric(
    df["recommendation_score"],
    errors="coerce",
).fillna(0.0)


# ============================================================
# Header
# ============================================================

st.markdown(
    """
    <div class="hero">
        <div class="hero-title">
            🎯 Career Recommendations
        </div>
        <div class="hero-subtitle">
            Explore jobs matched using semantic relevance,
            skill coverage, and market demand.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# Sidebar filters
# ============================================================

st.sidebar.header(
    "Recommendation Filters"
)


companies = sorted(
    [
        value
        for value in df["company_name"].unique()
        if value != "Not specified"
    ]
)


work_models = sorted(
    [
        value
        for value in df["work_model"].unique()
        if value != "Not specified"
    ]
)


selected_company = st.sidebar.selectbox(
    "Company",
    ["All"] + companies,
)


selected_work_model = st.sidebar.selectbox(
    "Work model",
    ["All"] + work_models,
)


min_skill_match = st.sidebar.slider(
    "Minimum skill match (%)",
    min_value=0,
    max_value=100,
    value=0,
    step=5,
)


# ============================================================
# Apply filters
# ============================================================

filtered = df.copy()


if selected_company != "All":
    filtered = filtered[
        filtered["company_name"] == selected_company
    ]


if selected_work_model != "All":
    filtered = filtered[
        filtered["work_model"] == selected_work_model
    ]


filtered = filtered[
    filtered["skill_match_percentage"]
    >= min_skill_match
]


filtered = filtered.sort_values(
    "recommendation_score",
    ascending=False,
)


# ============================================================
# KPI row
# ============================================================

col1, col2, col3, col4 = st.columns(4)


with col1:
    st.metric(
        "Jobs Analyzed",
        len(filtered),
    )


with col2:
    avg_skill = (
        filtered["skill_match_percentage"].mean()
        if not filtered.empty
        else 0
    )

    st.metric(
        "Avg. Skill Match",
        f"{avg_skill:.1f}%",
    )


with col3:
    avg_semantic = (
        filtered["semantic_similarity"].mean()
        if not filtered.empty
        else 0
    )

    st.metric(
        "Avg. Semantic Relevance",
        f"{avg_semantic * 100:.1f}%",
    )


with col4:
    avg_recommendation = (
        filtered["recommendation_score"].mean()
        if not filtered.empty
        else 0
    )

    st.metric(
        "Avg. Recommendation Score",
        f"{avg_recommendation:.1f}",
    )


st.divider()


# ============================================================
# Empty result handling
# ============================================================

if filtered.empty:
    st.info(
        "No recommendations match the selected filters."
    )
    st.stop()


# ============================================================
# Recommendation Overview
# ============================================================

st.subheader(
    "Recommendation Overview"
)


chart_df = filtered.head(10).copy()


chart_df["job_label"] = (
    chart_df["title"]
    + " — "
    + chart_df["company_name"]
)


fig = px.bar(
    chart_df,
    x="recommendation_score",
    y="job_label",
    orientation="h",
    labels={
        "recommendation_score": "Recommendation Score",
        "job_label": "",
    },
)


fig.update_layout(
    height=450,
    margin=dict(
        l=10,
        r=10,
        t=20,
        b=20,
    ),
)


st.plotly_chart(
    fig,
    use_container_width=True,
)


st.divider()


# ============================================================
# Recommended Opportunities
# ============================================================

st.subheader(
    "Recommended Opportunities"
)


for rank, (_, row) in enumerate(
    filtered.head(10).iterrows(),
    start=1,
):

    title = clean_value(
        row["title"],
        "Untitled position",
    )

    company = clean_value(
        row["company_name"],
        "Company not specified",
    )

    work_model = clean_value(
        row["work_model"],
        "Not specified",
    )

    experience = clean_value(
        row["experience_level"],
        "Not specified",
    )

    recommendation_score = safe_number(
        row["recommendation_score"]
    )

    semantic_similarity = safe_number(
        row["semantic_similarity"]
    )

    skill_match = safe_number(
        row["skill_match_percentage"]
    )


    # --------------------------------------------------------
    # Job header
    # --------------------------------------------------------

    st.markdown(
        f"""
        <div class="job-card">
            <div class="job-title">
                {html.escape(title)}
            </div>
            <div class="company">
                {html.escape(company)}
                · {html.escape(work_model)}
                · {html.escape(experience)}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


    # --------------------------------------------------------
    # Metrics
    # --------------------------------------------------------

    col1, col2, col3 = st.columns(3)


    with col1:
        st.metric(
            "Recommendation",
            f"{recommendation_score:.2f}",
        )


    with col2:
        st.metric(
            "Semantic Relevance",
            f"{semantic_similarity * 100:.1f}%",
        )


    with col3:
        st.metric(
            "Skill Match",
            f"{skill_match:.1f}%",
        )


    # --------------------------------------------------------
    # Matched skills
    # --------------------------------------------------------

    st.markdown(
        "**Matched skills**"
    )


    matched = clean_skill_list(
        row["matched_skills"]
    )


    if matched:

        chips = " ".join(
            [
                f'<span class="skill-chip">'
                f'{html.escape(skill)}'
                f'</span>'
                for skill in matched
            ]
        )

        st.markdown(
            chips,
            unsafe_allow_html=True,
        )

    else:

        st.caption(
            "No detected matched skills."
        )


    # --------------------------------------------------------
    # Missing skills
    # --------------------------------------------------------

    st.markdown(
        "**Skills to develop**"
    )


    missing = clean_skill_list(
        row["missing_skills"]
    )


    if missing:

        chips = " ".join(
            [
                f'<span class="missing-chip">'
                f'{html.escape(skill)}'
                f'</span>'
                for skill in missing
            ]
        )

        st.markdown(
            chips,
            unsafe_allow_html=True,
        )

    else:

        st.caption(
            "No missing skills detected."
        )


    st.caption(
        "Recommendation score combines semantic relevance, "
        "existing skill coverage, and market demand."
    )


    st.divider()


# ============================================================
# Methodology
# ============================================================

with st.expander(
    "How are recommendations calculated?"
):

    st.markdown(
        """
        JobInsight uses three transparent components:

        **50% — Semantic relevance**

        Measures how closely the candidate profile
        matches the job using Sentence Transformer
        embeddings.

        **35% — Skill coverage**

        Measures the percentage of detected job skills
        already present in the candidate profile.

        **15% — Market demand**

        Measures the relative demand for skills that
        are missing from the candidate profile.

        The resulting score is an engineering/research
        ranking signal, not a probability of getting a job.
        """
    )