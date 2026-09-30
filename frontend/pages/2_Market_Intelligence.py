from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[2]

JOBS_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "jobs_normalized.parquet"
)

SKILL_DEMAND_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "skill_demand.csv"
)

SALARY_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "salary_normalized.parquet"
)


st.set_page_config(
    page_title="Market Intelligence | JobInsight",
    page_icon="📊",
    layout="wide",
)


# ---------------------------------------------------------
# Styling
# ---------------------------------------------------------

st.markdown(
    """
    <style>
    .hero {
        padding: 1.2rem 0 1rem 0;
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

    .insight-card {
        padding: 1rem;
        border: 1px solid #e5e7eb;
        border-radius: 14px;
        background: #ffffff;
        margin-bottom: 0.8rem;
    }

    .insight-title {
        font-weight: 650;
        font-size: 1rem;
    }

    .insight-text {
        color: #6b7280;
        margin-top: 0.3rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# Load data
# ---------------------------------------------------------

required_files = [
    JOBS_PATH,
    SKILL_DEMAND_PATH,
    SALARY_PATH,
]

for file_path in required_files:
    if not file_path.exists():
        st.error(
            f"Required data file not found: {file_path}"
        )
        st.stop()


jobs = pd.read_parquet(JOBS_PATH)
skill_demand = pd.read_csv(
    SKILL_DEMAND_PATH
)
salary = pd.read_parquet(
    SALARY_PATH
)


# ---------------------------------------------------------
# Header
# ---------------------------------------------------------

st.markdown(
    """
    <div class="hero">
        <div class="hero-title">
            📊 Market Intelligence
        </div>
        <div class="hero-subtitle">
            Explore job-market demand, work models,
            experience levels, geography, skills, and salary signals.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# Sidebar filters
# ---------------------------------------------------------

st.sidebar.header(
    "Market Filters"
)

countries = sorted(
    jobs["country"]
    .dropna()
    .astype(str)
    .unique()
)

experience_levels = sorted(
    jobs["experience_level"]
    .dropna()
    .astype(str)
    .unique()
)

work_models = sorted(
    jobs["work_model"]
    .dropna()
    .astype(str)
    .unique()
)

selected_country = st.sidebar.selectbox(
    "Country",
    ["All"] + countries,
)

selected_experience = st.sidebar.selectbox(
    "Experience level",
    ["All"] + experience_levels,
)

selected_work_model = st.sidebar.selectbox(
    "Work model",
    ["All"] + work_models,
)


filtered_jobs = jobs.copy()

if selected_country != "All":
    filtered_jobs = filtered_jobs[
        filtered_jobs["country"].astype(str)
        == selected_country
    ]

if selected_experience != "All":
    filtered_jobs = filtered_jobs[
        filtered_jobs[
            "experience_level"
        ].astype(str)
        == selected_experience
    ]

if selected_work_model != "All":
    filtered_jobs = filtered_jobs[
        filtered_jobs["work_model"].astype(str)
        == selected_work_model
    ]


# ---------------------------------------------------------
# KPI calculations
# ---------------------------------------------------------

total_jobs = len(filtered_jobs)

salary_available = (
    pd.to_numeric(
        filtered_jobs["salary_min"],
        errors="coerce",
    )
    .notna()
    .sum()
)

salary_coverage = (
    salary_available / total_jobs * 100
    if total_jobs
    else 0
)

remote_jobs = (
    filtered_jobs["work_model"]
    .astype(str)
    .str.contains(
        "remote",
        case=False,
        na=False,
    )
    .sum()
)

remote_percentage = (
    remote_jobs / total_jobs * 100
    if total_jobs
    else 0
)


# ---------------------------------------------------------
# KPI row
# ---------------------------------------------------------

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Jobs",
        f"{total_jobs:,}",
    )

with col2:
    st.metric(
        "Salary Coverage",
        f"{salary_coverage:.1f}%",
    )

with col3:
    st.metric(
        "Remote Jobs",
        f"{remote_percentage:.1f}%",
    )

with col4:
    st.metric(
        "Countries",
        f"{filtered_jobs['country'].nunique():,}",
    )


st.divider()


# ---------------------------------------------------------
# Top skills
# ---------------------------------------------------------

st.subheader(
    "🔥 Most Demanded Skills"
)

top_skills = skill_demand.head(
    15
).copy()

top_skills = top_skills.sort_values(
    "job_count",
    ascending=True,
)

fig_skills = px.bar(
    top_skills,
    x="job_count",
    y="skill",
    orientation="h",
    labels={
        "job_count": "Number of Jobs",
        "skill": "",
    },
)

fig_skills.update_layout(
    height=520,
    margin=dict(
        l=10,
        r=20,
        t=20,
        b=20,
    ),
)

st.plotly_chart(
    fig_skills,
    use_container_width=True,
)


# ---------------------------------------------------------
# Experience + work model
# ---------------------------------------------------------

col1, col2 = st.columns(2)

with col1:

    st.subheader(
        "Experience Level"
    )

    experience_data = (
        filtered_jobs[
            "experience_level"
        ]
        .fillna("Not specified")
        .value_counts()
        .reset_index()
    )

    experience_data.columns = [
        "experience_level",
        "job_count",
    ]

    fig_experience = px.pie(
        experience_data,
        names="experience_level",
        values="job_count",
        hole=0.45,
    )

    fig_experience.update_layout(
        height=400,
        margin=dict(
            l=10,
            r=10,
            t=20,
            b=20,
        ),
    )

    st.plotly_chart(
        fig_experience,
        use_container_width=True,
    )


with col2:

    st.subheader(
        "Work Model"
    )

    work_model_data = (
        filtered_jobs[
            "work_model"
        ]
        .fillna("Not specified")
        .value_counts()
        .reset_index()
    )

    work_model_data.columns = [
        "work_model",
        "job_count",
    ]

    fig_work = px.bar(
        work_model_data,
        x="work_model",
        y="job_count",
        labels={
            "work_model": "",
            "job_count": "Jobs",
        },
    )

    fig_work.update_layout(
        height=400,
        margin=dict(
            l=10,
            r=10,
            t=20,
            b=20,
        ),
    )

    st.plotly_chart(
        fig_work,
        use_container_width=True,
    )


# ---------------------------------------------------------
# Geographic distribution
# ---------------------------------------------------------

st.subheader(
    "🌍 Job Distribution by Country"
)

country_data = (
    filtered_jobs[
        "country"
    ]
    .fillna("Not specified")
    .value_counts()
    .head(15)
    .sort_values()
    .reset_index()
)

country_data.columns = [
    "country",
    "job_count",
]

fig_country = px.bar(
    country_data,
    x="job_count",
    y="country",
    orientation="h",
    labels={
        "job_count": "Jobs",
        "country": "",
    },
)

fig_country.update_layout(
    height=500,
    margin=dict(
        l=10,
        r=20,
        t=20,
        b=20,
    ),
)

st.plotly_chart(
    fig_country,
    use_container_width=True,
)


# ---------------------------------------------------------
# Salary distribution
# ---------------------------------------------------------

st.subheader(
    "💰 Salary Intelligence"
)

salary_values = pd.to_numeric(
    salary[
        "annual_salary_min_usd"
    ],
    errors="coerce",
)

salary_values = salary_values[
    salary_values > 0
]

# Keep visualization robust against extreme values.
salary_values = salary_values[
    salary_values.between(
        salary_values.quantile(0.01),
        salary_values.quantile(0.99),
    )
]

fig_salary = px.histogram(
    x=salary_values,
    nbins=40,
    labels={
        "x": "Annual Minimum Salary (USD)",
        "y": "Jobs",
    },
)

fig_salary.update_layout(
    height=420,
    margin=dict(
        l=10,
        r=20,
        t=20,
        b=20,
    ),
)

st.plotly_chart(
    fig_salary,
    use_container_width=True,
)


# ---------------------------------------------------------
# Market insights
# ---------------------------------------------------------

st.subheader(
    "💡 Market Signals"
)

top_skill = (
    skill_demand
    .sort_values(
        "job_count",
        ascending=False,
    )
    .iloc[0]
)

top_country = (
    filtered_jobs["country"]
    .dropna()
    .astype(str)
    .value_counts()
)

if len(top_country):
    country_name = top_country.index[0]
    country_count = top_country.iloc[0]
else:
    country_name = "Not available"
    country_count = 0

insight_col1, insight_col2 = st.columns(2)

with insight_col1:
    st.markdown(
        f"""
        <div class="insight-card">
            <div class="insight-title">
                Highest-demand detected skill
            </div>
            <div class="insight-text">
                {top_skill['skill']} appears in
                {int(top_skill['job_count']):,} job records
                in the current skill dataset.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with insight_col2:
    st.markdown(
        f"""
        <div class="insight-card">
            <div class="insight-title">
                Largest country segment
            </div>
            <div class="insight-text">
                {country_name} contains
                {country_count:,} jobs under the current filters.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------
# Methodology
# ---------------------------------------------------------

with st.expander(
    "About this dashboard"
):

    st.markdown(
        """
        **Data source**

        JobInsight currently analyzes the processed
        June 2026 job-posting dataset used by the project.

        **Skill analytics**

        Skills are based on the project's controlled
        baseline skill extraction and normalization pipeline.

        **Salary analytics**

        Salary visualization uses normalized annual
        minimum salary values. Extreme values are excluded
        from the visualization using the 1st–99th percentile
        range, while the underlying dataset remains unchanged.

        **Interpretation**

        These charts describe patterns in the available
        dataset. They should not be interpreted as a complete
        representation of the entire global job market.
        """
    )