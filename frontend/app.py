from pathlib import Path

import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="JobInsight",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded",
)


# -------------------------
# Paths
# -------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

JOBS_FILE = PROCESSED_DIR / "jobs_normalized.parquet"
SKILLS_FILE = PROCESSED_DIR / "job_skills_normalized.parquet"


# -------------------------
# Data loading
# -------------------------

@st.cache_data
def load_home_metrics():
    jobs = pd.read_parquet(JOBS_FILE)

    jobs_analyzed = len(jobs)

    # Job roles
    role_column = None
    for column in ["normalized_title", "title", "job_title"]:
        if column in jobs.columns:
            role_column = column
            break

    if role_column:
        job_roles = jobs[role_column].dropna().astype(str).str.strip()
        job_roles = job_roles[job_roles != ""].nunique()
    else:
        job_roles = 0

    # Locations
    location_column = None
    for column in [
        "country_normalized",
        "country",
        "location_resolved",
        "city",
    ]:
        if column in jobs.columns:
            location_column = column
            break

    if location_column:
        locations = jobs[location_column].dropna().astype(str).str.strip()
        locations = locations[locations != ""].nunique()
    else:
        locations = 0

    # Unique skills
    skills_identified = 0

    if SKILLS_FILE.exists():
        skills = pd.read_parquet(SKILLS_FILE)

        skill_column = None

        for column in [
            "normalized_skill",
            "skill",
            "skill_name",
            "skills",
        ]:
            if column in skills.columns:
                skill_column = column
                break

        if skill_column:
            skill_values = (
                skills[skill_column]
                .dropna()
                .astype(str)
                .str.strip()
            )

            skill_values = skill_values[skill_values != ""]
            skills_identified = skill_values.nunique()

    return (
        jobs_analyzed,
        skills_identified,
        job_roles,
        locations,
    )


# -------------------------
# Styling
# -------------------------

st.markdown(
    """
    <style>
        .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
            max-width: 1400px;
        }

        .hero {
            padding: 3rem 2rem;
            border-radius: 24px;
            background: linear-gradient(
                135deg,
                #111827 0%,
                #1e293b 50%,
                #312e81 100%
            );
            color: white;
            margin-bottom: 2rem;
        }

        .hero h1 {
            font-size: 3.2rem;
            margin-bottom: 0.5rem;
        }

        .hero p {
            font-size: 1.2rem;
            color: #cbd5e1;
            max-width: 800px;
        }

        .metric-card {
            padding: 1.4rem;
            border-radius: 18px;
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            text-align: center;
        }

        .metric-value {
            font-size: 2rem;
            font-weight: 700;
        }

        .metric-label {
            color: #64748b;
            font-size: 0.95rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# -------------------------
# Sidebar
# -------------------------

with st.sidebar:
    st.markdown("## 💼 JobInsight")
    st.caption("AI-Powered Job Market Intelligence")

    st.divider()

    page = st.radio(
        "Navigation",
        [
            "🏠 Home",
            "📊 Market Intelligence",
            "💼 Job Explorer",
            "🧠 Skills Intelligence",
            "💰 Salary Intelligence",
            "📄 Resume Analyzer",
            "🎯 Job Matcher",
            "🧩 Skill Gap",
            "🚀 Career Recommendations",
        ],
    )

    st.divider()

    st.caption("JobInsight v0.1")
    st.caption("Research & Development Build")


# -------------------------
# Home
# -------------------------

if page == "🏠 Home":

    st.markdown(
        """
        <div class="hero">
            <h1>Understand the Job Market.</h1>
            <h1>Understand Your Skills.</h1>
            <h1>Build Your Career.</h1>
            <p>
                JobInsight combines job-market analytics, NLP, machine learning,
                semantic matching and career intelligence into one platform.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Load real market statistics
    try:
        (
            jobs_analyzed,
            skills_identified,
            job_roles,
            locations,
        ) = load_home_metrics()

        metrics = [
            (f"{jobs_analyzed:,}", "Jobs Analyzed"),
            (f"{skills_identified:,}", "Skills Identified"),
            (f"{job_roles:,}", "Job Roles"),
            (f"{locations:,}", "Locations"),
        ]

    except Exception as e:
        st.warning(f"Unable to load homepage statistics: {e}")

        metrics = [
            ("—", "Jobs Analyzed"),
            ("—", "Skills Identified"),
            ("—", "Job Roles"),
            ("—", "Locations"),
        ]

    col1, col2, col3, col4 = st.columns(4)

    for col, (value, label) in zip(
        [col1, col2, col3, col4],
        metrics,
    ):
        with col:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-value">{value}</div>
                    <div class="metric-label">{label}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("##")

    st.subheader("Explore Job Market Intelligence")

    col1, col2 = st.columns(2)

    with col1:
        if st.button(
            "📊 Explore Market Intelligence",
            use_container_width=True,
        ):
            st.info(
                "Use the Market Intelligence page from the sidebar "
                "to explore job-market statistics."
            )

    with col2:
        if st.button(
            "📄 Analyze Your Resume",
            use_container_width=True,
        ):
            st.info(
                "Use the Resume Analyzer page from the sidebar "
                "to upload and analyze your resume."
            )

    st.markdown("##")

    st.subheader("What JobInsight Provides")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            """
            ### 📈 Market Analytics

            Discover job demand, skill trends, role distributions,
            locations and market patterns.
            """
        )

    with col2:
        st.markdown(
            """
            ### 🧠 AI Career Intelligence

            Extract skills from resumes and job descriptions,
            identify skill gaps and perform semantic matching.
            """
        )

    with col3:
        st.markdown(
            """
            ### 🚀 Career Recommendations

            Connect candidate profiles with jobs, skills,
            salary intelligence and career opportunities.
            """
        )


# -------------------------
# Placeholder pages
# -------------------------

else:

    st.title(page)

    st.info(
        "Use the corresponding page from the Streamlit navigation "
        "to access the full JobInsight module."
    )