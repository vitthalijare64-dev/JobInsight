from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Market Intelligence | JobInsight",
    page_icon="📊",
    layout="wide",
)


# ============================================================
# PATHS
# ============================================================

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


# ============================================================
# HTML HELPER
# ============================================================

def render_html(content):
    st.html(content)


# ============================================================
# PROFESSIONAL DESIGN
# ============================================================

render_html(
    """
    <style>

    /* ========================================================
       GLOBAL
       ======================================================== */

    .block-container {
        padding-top: 2rem;
        padding-bottom: 4rem;
        max-width: 1450px;
    }


    /* ========================================================
       HERO
       ======================================================== */

    .market-hero {
        position: relative;
        overflow: hidden;

        padding: 2.7rem 2.8rem;
        margin-bottom: 1.8rem;

        border-radius: 26px;

        background:
            radial-gradient(
                circle at 88% 18%,
                rgba(129, 140, 248, 0.35),
                transparent 30%
            ),
            linear-gradient(
                135deg,
                #0f172a 0%,
                #172554 52%,
                #312e81 100%
            );

        color: white;

        box-shadow:
            0 20px 48px rgba(15, 23, 42, 0.16);
    }

    .market-hero::after {
        content: "";

        position: absolute;

        width: 300px;
        height: 300px;

        right: -100px;
        bottom: -170px;

        border-radius: 50%;

        border: 1px solid rgba(255,255,255,0.14);

        box-shadow:
            0 0 0 38px rgba(255,255,255,0.035),
            0 0 0 76px rgba(255,255,255,0.02);
    }

    .market-badge {
        position: relative;
        z-index: 2;

        display: inline-block;

        padding: 0.45rem 0.85rem;

        margin-bottom: 1rem;

        border-radius: 999px;

        background: rgba(255,255,255,0.10);

        border: 1px solid rgba(255,255,255,0.18);

        color: #dbeafe;

        font-size: 0.78rem;

        font-weight: 700;

        letter-spacing: 0.05em;
    }

    .market-title {
        position: relative;
        z-index: 2;

        margin: 0;

        color: white;

        font-size: 2.8rem;

        line-height: 1.05;

        font-weight: 800;

        letter-spacing: -0.045em;
    }

    .market-description {
        position: relative;
        z-index: 2;

        max-width: 900px;

        margin-top: 1rem;

        color: #cbd5e1;

        font-size: 1.02rem;

        line-height: 1.7;
    }


    /* ========================================================
       SECTION HEADERS
       ======================================================== */

    .section-title {
        margin-top: 2rem;
        margin-bottom: 0.3rem;

        color: #0f172a;

        font-size: 1.45rem;

        font-weight: 800;

        letter-spacing: -0.025em;
    }

    .section-subtitle {
        margin-bottom: 1rem;

        color: #64748b;

        font-size: 0.93rem;
    }


    /* ========================================================
       KPI CARDS
       ======================================================== */

    .market-kpi {
        position: relative;

        overflow: hidden;

        min-height: 140px;

        padding: 1.3rem;

        border-radius: 20px;

        background: rgba(255,255,255,0.97);

        border: 1px solid #e2e8f0;

        box-shadow:
            0 9px 26px rgba(15,23,42,0.055);
    }

    .market-kpi::before {
        content: "";

        position: absolute;

        top: 0;
        left: 0;
        right: 0;

        height: 4px;

        background:
            linear-gradient(
                90deg,
                #4f46e5,
                #06b6d4
            );
    }

    .market-kpi-icon {
        font-size: 1.45rem;

        margin-bottom: 0.55rem;
    }

    .market-kpi-value {
        color: #0f172a;

        font-size: 1.85rem;

        font-weight: 800;

        line-height: 1;
    }

    .market-kpi-label {
        margin-top: 0.55rem;

        color: #64748b;

        font-size: 0.86rem;

        font-weight: 600;
    }


    /* ========================================================
       CHART CONTAINER
       ======================================================== */

    .chart-header {
        padding: 0.9rem 1rem 0.2rem;

        margin-bottom: 0.4rem;

        border-radius: 14px 14px 0 0;

        color: #0f172a;

        font-size: 1.05rem;

        font-weight: 750;
    }


    /* ========================================================
       INSIGHT CARDS
       ======================================================== */

    .insight-card {
        min-height: 150px;

        padding: 1.35rem;

        border-radius: 18px;

        background: white;

        border: 1px solid #e2e8f0;

        box-shadow:
            0 8px 24px rgba(15,23,42,0.05);
    }

    .insight-icon {
        font-size: 1.55rem;

        margin-bottom: 0.55rem;
    }

    .insight-title {
        color: #0f172a;

        font-size: 0.98rem;

        font-weight: 750;

        margin-bottom: 0.4rem;
    }

    .insight-text {
        color: #64748b;

        font-size: 0.88rem;

        line-height: 1.6;
    }


    /* ========================================================
       SIDEBAR
       ======================================================== */

    [data-testid="stSidebar"] {
        background:
            linear-gradient(
                180deg,
                #0f172a 0%,
                #111827 55%,
                #172554 100%
            );
    }

    [data-testid="stSidebar"] * {
        color: #e2e8f0;
    }


    /* ========================================================
       LOADING ORB
       ======================================================== */

    .loading-orb {
        width: 38px;
        height: 38px;

        margin: 0 auto 0.7rem;

        border-radius: 50%;

        border: 4px solid #e0e7ff;

        border-top-color: #4f46e5;

        animation:
            market-spin 0.9s linear infinite;
    }

    @keyframes market-spin {
        to {
            transform: rotate(360deg);
        }
    }


    /* ========================================================
       BUTTONS / CONTROLS
       ======================================================== */

    .stButton > button {
        border-radius: 10px;

        font-weight: 650;

        border: 1px solid #cbd5e1;

        transition:
            all 0.18s ease;
    }

    .stButton > button:hover {
        border-color: #818cf8;

        color: #3730a3;

        transform: translateY(-1px);
    }


    /* ========================================================
       EXPANDER
       ======================================================== */

    [data-testid="stExpander"] {
        border-radius: 14px !important;

        border: 1px solid #e2e8f0 !important;

        background: #fafafa !important;
    }

    </style>
    """
)


# ============================================================
# DATA LOADING
# ============================================================

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


@st.cache_data
def load_market_data():

    jobs = pd.read_parquet(
        JOBS_PATH
    )

    skill_demand = pd.read_csv(
        SKILL_DEMAND_PATH
    )

    salary = pd.read_parquet(
        SALARY_PATH
    )

    return (
        jobs,
        skill_demand,
        salary,
    )


with st.spinner(
    "Loading market intelligence..."
):

    jobs, skill_demand, salary = (
        load_market_data()
    )


# ============================================================
# HERO
# ============================================================

render_html(
    """
    <div class="market-hero">

        <div class="market-badge">
            ✦ JOB MARKET ANALYTICS
        </div>

        <div class="market-title">
            Market Intelligence
        </div>

        <div class="market-description">
            Explore job-market demand, work models,
            experience levels, geography, skills and
            salary signals across the JobInsight dataset.
        </div>

    </div>
    """
)


# ============================================================
# SIDEBAR FILTERS
# ============================================================

with st.sidebar:

    st.markdown(
        "## 🎛️ Market Filters"
    )

    st.caption(
        "Adjust the market view using the filters below."
    )

    st.divider()


# ------------------------------------------------------------
# Countries
# ------------------------------------------------------------

countries = sorted(
    jobs["country"]
    .dropna()
    .astype(str)
    .str.strip()
    .loc[
        lambda series:
        series != ""
    ]
    .unique()
)


# ------------------------------------------------------------
# Experience
# ------------------------------------------------------------

experience_levels = sorted(
    jobs["experience_level"]
    .dropna()
    .astype(str)
    .str.strip()
    .loc[
        lambda series:
        series != ""
    ]
    .unique()
)


# ------------------------------------------------------------
# Work model
# ------------------------------------------------------------

work_models = sorted(
    jobs["work_model"]
    .dropna()
    .astype(str)
    .str.strip()
    .loc[
        lambda series:
        series != ""
    ]
    .unique()
)


with st.sidebar:

    selected_country = st.selectbox(
        "🌍 Country",
        ["All"] + countries,
    )

    selected_experience = st.selectbox(
        "🎯 Experience Level",
        ["All"] + experience_levels,
    )

    selected_work_model = st.selectbox(
        "💼 Work Model",
        ["All"] + work_models,
    )


# ============================================================
# FILTER JOBS
# ============================================================

filtered_jobs = jobs.copy()


if selected_country != "All":

    filtered_jobs = filtered_jobs[
        filtered_jobs[
            "country"
        ].astype(str)
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
        filtered_jobs[
            "work_model"
        ].astype(str)
        == selected_work_model
    ]


# ============================================================
# KPI CALCULATIONS
# ============================================================

total_jobs = len(
    filtered_jobs
)


salary_available = (
    pd.to_numeric(
        filtered_jobs[
            "salary_min"
        ],
        errors="coerce",
    )
    .notna()
    .sum()
)


salary_coverage = (
    salary_available
    / total_jobs
    * 100
    if total_jobs
    else 0
)


remote_jobs = (
    filtered_jobs[
        "work_model"
    ]
    .astype(str)
    .str.contains(
        "remote",
        case=False,
        na=False,
    )
    .sum()
)


remote_percentage = (
    remote_jobs
    / total_jobs
    * 100
    if total_jobs
    else 0
)


country_count = (
    filtered_jobs[
        "country"
    ]
    .nunique()
)


# ============================================================
# KPI ROW
# ============================================================

kpi_data = [
    (
        "💼",
        f"{total_jobs:,}",
        "Jobs",
    ),
    (
        "💰",
        f"{salary_coverage:.1f}%",
        "Salary Coverage",
    ),
    (
        "🌐",
        f"{remote_percentage:.1f}%",
        "Remote Jobs",
    ),
    (
        "🌍",
        f"{country_count:,}",
        "Countries",
    ),
]


kpi_columns = st.columns(4)


for column, (
    icon,
    value,
    label,
) in zip(
    kpi_columns,
    kpi_data,
):

    with column:

        render_html(
            f"""
            <div class="market-kpi">

                <div class="market-kpi-icon">
                    {icon}
                </div>

                <div class="market-kpi-value">
                    {value}
                </div>

                <div class="market-kpi-label">
                    {label}
                </div>

            </div>
            """
        )


# ============================================================
# FILTER STATUS
# ============================================================

filter_parts = []

if selected_country != "All":
    filter_parts.append(
        f"Country: {selected_country}"
    )

if selected_experience != "All":
    filter_parts.append(
        f"Experience: {selected_experience}"
    )

if selected_work_model != "All":
    filter_parts.append(
        f"Work model: {selected_work_model}"
    )


if filter_parts:

    filter_text = " • ".join(
        filter_parts
    )

    st.caption(
        f"Active filters: {filter_text}"
    )

else:

    st.caption(
        "Showing the full available market dataset."
    )


st.divider()


# ============================================================
# TOP SKILLS
# ============================================================

render_html(
    """
    <div class="section-title">
        🔥 Most Demanded Skills
    </div>

    <div class="section-subtitle">
        Skills with the highest job-count demand
        in the project's skill-demand dataset.
    </div>
    """
)


top_skills = (
    skill_demand
    .head(15)
    .copy()
)


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

    paper_bgcolor="rgba(0,0,0,0)",

    plot_bgcolor="rgba(0,0,0,0)",

    hovermode="y",

    font=dict(
        color="#334155",
    ),
)


fig_skills.update_xaxes(
    showgrid=True,
    gridcolor="#e2e8f0",
)


fig_skills.update_yaxes(
    showgrid=False,
)


st.plotly_chart(
    fig_skills,
    use_container_width=True,
)


# ============================================================
# EXPERIENCE + WORK MODEL
# ============================================================

col1, col2 = st.columns(2)


# ------------------------------------------------------------
# EXPERIENCE
# ------------------------------------------------------------

with col1:

    render_html(
        """
        <div class="section-title">
            🎯 Experience Level
        </div>

        <div class="section-subtitle">
            Distribution of jobs by experience level.
        </div>
        """
    )


    experience_data = (
        filtered_jobs[
            "experience_level"
        ]
        .fillna(
            "Not specified"
        )
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
        hole=0.50,
    )


    fig_experience.update_layout(
        height=420,

        margin=dict(
            l=10,
            r=10,
            t=20,
            b=20,
        ),

        paper_bgcolor="rgba(0,0,0,0)",

        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.15,
            xanchor="center",
            x=0.5,
        ),
    )


    st.plotly_chart(
        fig_experience,
        use_container_width=True,
    )


# ------------------------------------------------------------
# WORK MODEL
# ------------------------------------------------------------

with col2:

    render_html(
        """
        <div class="section-title">
            💼 Work Model
        </div>

        <div class="section-subtitle">
            Distribution of jobs by work arrangement.
        </div>
        """
    )


    work_model_data = (
        filtered_jobs[
            "work_model"
        ]
        .fillna(
            "Not specified"
        )
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
        height=420,

        margin=dict(
            l=10,
            r=10,
            t=20,
            b=20,
        ),

        paper_bgcolor="rgba(0,0,0,0)",

        plot_bgcolor="rgba(0,0,0,0)",
    )


    fig_work.update_yaxes(
        showgrid=True,
        gridcolor="#e2e8f0",
    )


    st.plotly_chart(
        fig_work,
        use_container_width=True,
    )


# ============================================================
# GEOGRAPHIC DISTRIBUTION
# ============================================================

render_html(
    """
    <div class="section-title">
        🌍 Job Distribution by Country
    </div>

    <div class="section-subtitle">
        The largest country segments under the current filters.
    </div>
    """
)


country_data = (
    filtered_jobs[
        "country"
    ]
    .fillna(
        "Not specified"
    )
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

    paper_bgcolor="rgba(0,0,0,0)",

    plot_bgcolor="rgba(0,0,0,0)",
)


fig_country.update_xaxes(
    showgrid=True,
    gridcolor="#e2e8f0",
)


st.plotly_chart(
    fig_country,
    use_container_width=True,
)


# ============================================================
# SALARY DISTRIBUTION
# ============================================================

render_html(
    """
    <div class="section-title">
        💰 Salary Intelligence
    </div>

    <div class="section-subtitle">
        Distribution of normalized annual minimum salary values.
        Extreme values are excluded from this visualization.
    </div>
    """
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


if len(salary_values) > 0:

    lower_bound = (
        salary_values
        .quantile(0.01)
    )

    upper_bound = (
        salary_values
        .quantile(0.99)
    )

    salary_values = salary_values[
        salary_values.between(
            lower_bound,
            upper_bound,
        )
    ]


if len(salary_values) > 0:

    fig_salary = px.histogram(
        x=salary_values,
        nbins=40,
        labels={
            "x": "Annual Minimum Salary (USD)",
            "y": "Jobs",
        },
    )


    fig_salary.update_layout(
        height=430,

        margin=dict(
            l=10,
            r=20,
            t=20,
            b=20,
        ),

        paper_bgcolor="rgba(0,0,0,0)",

        plot_bgcolor="rgba(0,0,0,0)",
    )


    fig_salary.update_xaxes(
        showgrid=True,
        gridcolor="#e2e8f0",
    )


    fig_salary.update_yaxes(
        showgrid=True,
        gridcolor="#e2e8f0",
    )


    st.plotly_chart(
        fig_salary,
        use_container_width=True,
    )

else:

    render_html(
        """
        <div class="insight-card">

            <div class="insight-icon">
                💰
            </div>

            <div class="insight-title">
                Salary data unavailable
            </div>

            <div class="insight-text">
                There are no valid positive annual salary
                values available for the visualization.
            </div>

        </div>
        """
    )


# ============================================================
# MARKET SIGNALS
# ============================================================

render_html(
    """
    <div class="section-title">
        💡 Market Signals
    </div>

    <div class="section-subtitle">
        Simple descriptive signals derived from the available
        JobInsight datasets.
    </div>
    """
)


# ------------------------------------------------------------
# Top skill
# ------------------------------------------------------------

if (
    not skill_demand.empty
    and "job_count"
    in skill_demand.columns
):

    top_skill = (
        skill_demand
        .sort_values(
            "job_count",
            ascending=False,
        )
        .iloc[0]
    )

    top_skill_name = str(
        top_skill["skill"]
    )

    top_skill_count = int(
        top_skill["job_count"]
    )

else:

    top_skill_name = (
        "Not available"
    )

    top_skill_count = 0


# ------------------------------------------------------------
# Top country
# ------------------------------------------------------------

top_country = (
    filtered_jobs[
        "country"
    ]
    .dropna()
    .astype(str)
    .value_counts()
)


if len(top_country):

    country_name = (
        top_country.index[0]
    )

    country_count = int(
        top_country.iloc[0]
    )

else:

    country_name = (
        "Not available"
    )

    country_count = 0


insight_col1, insight_col2 = (
    st.columns(2)
)


with insight_col1:

    render_html(
        f"""
        <div class="insight-card">

            <div class="insight-icon">
                🧠
            </div>

            <div class="insight-title">
                Highest-demand detected skill
            </div>

            <div class="insight-text">
                {top_skill_name}
                appears in
                <strong>
                    {top_skill_count:,}
                </strong>
                job records in the current
                skill-demand dataset.
            </div>

        </div>
        """
    )


with insight_col2:

    render_html(
        f"""
        <div class="insight-card">

            <div class="insight-icon">
                🌍
            </div>

            <div class="insight-title">
                Largest country segment
            </div>

            <div class="insight-text">
                {country_name}
                contains
                <strong>
                    {country_count:,}
                </strong>
                jobs under the current filters.
            </div>

        </div>
        """
    )


# ============================================================
# METHODOLOGY
# ============================================================

with st.expander(
    "📘 About this dashboard"
):

    st.markdown(
        """
        ### Data source

        JobInsight currently analyzes the processed
        June 2026 job-posting dataset used by the project.

        ### Skill analytics

        Skills are based on the project's controlled
        baseline skill extraction and normalization pipeline.

        ### Salary analytics

        Salary visualization uses normalized annual
        minimum salary values. Extreme values are excluded
        from the visualization using the 1st–99th percentile
        range, while the underlying dataset remains unchanged.

        ### Interpretation

        These charts describe patterns in the available
        dataset. They should not be interpreted as a complete
        representation of the entire global job market.
        """
    )


# ============================================================
# FOOTER
# ============================================================

render_html(
    """
    <div style="
        margin-top: 3.5rem;
        padding-top: 1.5rem;
        border-top: 1px solid #e2e8f0;
        text-align: center;
        color: #94a3b8;
        font-size: 0.82rem;
    ">
        <strong>JobInsight</strong>
        &nbsp;•&nbsp;
        Market Intelligence
        &nbsp;•&nbsp;
        Research & Development Build
    </div>
    """
)