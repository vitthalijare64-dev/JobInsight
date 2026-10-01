from pathlib import Path

import pandas as pd
import streamlit as st


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="JobInsight | AI Job Market Intelligence",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

JOBS_FILE = PROCESSED_DIR / "jobs_normalized.parquet"
SKILLS_FILE = PROCESSED_DIR / "job_skills_normalized.parquet"


# ============================================================
# HTML RENDERER
# ============================================================

def render_html(html):
    """
    Render custom HTML directly using Streamlit's HTML renderer.
    This prevents HTML from being displayed as Markdown/code.
    """
    st.html(html)


# ============================================================
# GLOBAL DESIGN
# ============================================================

render_html(
    """
    <style>

    /* ========================================================
   PAGE NAVIGATION BUTTONS
   ======================================================== */

[data-testid="stPageLink"] {
    margin-top: 0.6rem;
}

[data-testid="stPageLink"] a {
    border-radius: 12px !important;
    border: 1px solid #c7d2fe !important;
    background: #eef2ff !important;
    color: #3730a3 !important;
    font-weight: 650 !important;
    text-decoration: none !important;
    padding: 0.65rem 1rem !important;
    transition: all 0.2s ease !important;
}

[data-testid="stPageLink"] a:hover {
    background: #e0e7ff !important;
    border-color: #818cf8 !important;
    transform: translateY(-1px);
}

    /* ========================================================
       GLOBAL
       ======================================================== */

    .stApp {
        background:
            radial-gradient(
                circle at 10% 0%,
                rgba(99, 102, 241, 0.08),
                transparent 28%
            ),
            radial-gradient(
                circle at 90% 10%,
                rgba(14, 165, 233, 0.07),
                transparent 25%
            ),
            #f8fafc;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 4rem;
        max-width: 1450px;
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
       HERO
       ======================================================== */

    .ji-hero {
        position: relative;
        overflow: hidden;

        padding: 3.2rem 3rem;

        margin-bottom: 2rem;

        border-radius: 28px;

        background:
            radial-gradient(
                circle at 88% 20%,
                rgba(129, 140, 248, 0.30),
                transparent 32%
            ),
            linear-gradient(
                135deg,
                #0f172a 0%,
                #172554 50%,
                #312e81 100%
            );

        box-shadow:
            0 20px 50px rgba(15, 23, 42, 0.16);
    }

    .ji-hero-circle-1 {
        position: absolute;

        width: 250px;
        height: 250px;

        right: -80px;
        bottom: -130px;

        border-radius: 50%;

        border: 1px solid rgba(255,255,255,0.12);
    }

    .ji-hero-circle-2 {
        position: absolute;

        width: 320px;
        height: 320px;

        right: -115px;
        bottom: -165px;

        border-radius: 50%;

        border: 1px solid rgba(255,255,255,0.06);
    }

    .ji-badge {
        display: inline-block;

        padding: 0.45rem 0.85rem;

        margin-bottom: 1rem;

        border-radius: 999px;

        background: rgba(255,255,255,0.10);

        border: 1px solid rgba(255,255,255,0.16);

        color: #c7d2fe;

        font-size: 0.78rem;

        font-weight: 700;

        letter-spacing: 0.05em;
    }

    .ji-hero-title {
        margin: 0;

        color: white;

        font-size: 3.7rem;

        line-height: 1.05;

        font-weight: 800;

        letter-spacing: -0.045em;
    }

    .ji-hero-gradient {
        background:
            linear-gradient(
                90deg,
                #ffffff,
                #c7d2fe,
                #bae6fd
            );

        -webkit-background-clip: text;

        -webkit-text-fill-color: transparent;
    }

    .ji-hero-description {
        max-width: 820px;

        margin-top: 1.25rem;

        color: #cbd5e1;

        font-size: 1.05rem;

        line-height: 1.7;
    }


    /* ========================================================
       SECTION TITLES
       ======================================================== */

    .ji-section-title {
        margin-top: 2.5rem;

        margin-bottom: 0.35rem;

        color: #0f172a;

        font-size: 1.65rem;

        font-weight: 800;

        letter-spacing: -0.025em;
    }

    .ji-section-subtitle {
        margin-bottom: 1.2rem;

        color: #64748b;

        font-size: 0.98rem;
    }


    /* ========================================================
       KPI CARDS
       ======================================================== */

    .ji-metric {
        position: relative;

        overflow: hidden;

        min-height: 145px;

        padding: 1.35rem;

        border-radius: 20px;

        background: rgba(255,255,255,0.96);

        border: 1px solid #e2e8f0;

        box-shadow:
            0 8px 25px rgba(15,23,42,0.055);
    }

    .ji-metric::before {
        content: "";

        position: absolute;

        left: 0;
        top: 0;

        width: 100%;

        height: 4px;

        background:
            linear-gradient(
                90deg,
                #4f46e5,
                #0ea5e9
            );
    }

    .ji-metric-icon {
        font-size: 1.35rem;

        margin-bottom: 0.55rem;
    }

    .ji-metric-value {
        color: #0f172a;

        font-size: 2rem;

        font-weight: 800;

        letter-spacing: -0.03em;
    }

    .ji-metric-label {
        margin-top: 0.25rem;

        color: #64748b;

        font-size: 0.88rem;

        font-weight: 600;
    }


    /* ========================================================
       NAVIGATION CARDS
       ======================================================== */

    .ji-nav-card {
        min-height: 170px;

        padding: 1.5rem;

        border-radius: 22px;

        background: rgba(255,255,255,0.96);

        border: 1px solid #e2e8f0;

        box-shadow:
            0 8px 24px rgba(15,23,42,0.055);
    }

    .ji-nav-icon {
        display: flex;

        align-items: center;

        justify-content: center;

        width: 48px;

        height: 48px;

        margin-bottom: 1rem;

        border-radius: 14px;

        background:
            linear-gradient(
                135deg,
                #eef2ff,
                #e0f2fe
            );

        font-size: 1.35rem;
    }

    .ji-nav-title {
        margin: 0 0 0.4rem 0;

        color: #0f172a;

        font-size: 1.08rem;

        font-weight: 750;
    }

    .ji-nav-description {
        margin: 0;

        color: #64748b;

        font-size: 0.88rem;

        line-height: 1.55;
    }


    /* ========================================================
       FEATURE CARDS
       ======================================================== */

    .ji-feature {
        min-height: 210px;

        padding: 1.6rem;

        border-radius: 22px;

        background: white;

        border: 1px solid #e2e8f0;

        box-shadow:
            0 8px 25px rgba(15,23,42,0.045);
    }

    .ji-feature-icon {
        font-size: 1.8rem;

        margin-bottom: 0.75rem;
    }

    .ji-feature-title {
        color: #0f172a;

        font-size: 1.08rem;

        font-weight: 750;

        margin-bottom: 0.6rem;
    }

    .ji-feature-text {
        color: #64748b;

        font-size: 0.92rem;

        line-height: 1.65;
    }


    /* ========================================================
       LOADING ORB
       ======================================================== */

    .ji-loading {
        display: flex;

        align-items: center;

        justify-content: center;

        gap: 10px;

        padding: 0.8rem;

        color: #64748b;

        font-size: 0.85rem;
    }

    .ji-loading-orb {
        width: 11px;

        height: 11px;

        border-radius: 50%;

        background: #6366f1;

        box-shadow:
            0 0 0 0 rgba(99,102,241,0.45);

        animation:
            ji-pulse 1.4s infinite;
    }

    @keyframes ji-pulse {

        0% {
            transform: scale(0.75);

            box-shadow:
                0 0 0 0 rgba(99,102,241,0.45);
        }

        70% {
            transform: scale(1);

            box-shadow:
                0 0 0 10px rgba(99,102,241,0);
        }

        100% {
            transform: scale(0.75);

            box-shadow:
                0 0 0 0 rgba(99,102,241,0);
        }

    }


    /* ========================================================
       FOOTER
       ======================================================== */

    .ji-footer {
        margin-top: 4rem;

        padding-top: 1.5rem;

        border-top: 1px solid #e2e8f0;

        text-align: center;

        color: #94a3b8;

        font-size: 0.82rem;
    }

    </style>
    """
)


# ============================================================
# DATA LOADING
# ============================================================

@st.cache_data
def load_home_metrics():

    jobs = pd.read_parquet(JOBS_FILE)

    jobs_analyzed = len(jobs)

    # --------------------------------------------------------
    # Job roles
    # --------------------------------------------------------

    role_column = None

    for column in [
        "normalized_title",
        "title",
        "job_title",
    ]:
        if column in jobs.columns:
            role_column = column
            break

    if role_column:

        roles = (
            jobs[role_column]
            .dropna()
            .astype(str)
            .str.strip()
        )

        roles = roles[roles != ""]

        job_roles = roles.nunique()

    else:

        job_roles = 0


    # --------------------------------------------------------
    # Locations
    # --------------------------------------------------------

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

        location_values = (
            jobs[location_column]
            .dropna()
            .astype(str)
            .str.strip()
        )

        location_values = location_values[
            location_values != ""
        ]

        locations = location_values.nunique()

    else:

        locations = 0


    # --------------------------------------------------------
    # Skills
    # --------------------------------------------------------

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

            skill_values = skill_values[
                skill_values != ""
            ]

            skills_identified = skill_values.nunique()


    return (
        jobs_analyzed,
        skills_identified,
        job_roles,
        locations,
    )


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    render_html(
        """
        <div style="
            padding: 0.5rem 0 1rem 0;
        ">

            <div style="
                font-size: 1.5rem;
                font-weight: 800;
            ">
                💼 JobInsight
            </div>

            <div style="
                color: #94a3b8;
                font-size: 0.78rem;
                margin-top: 0.3rem;
            ">
                AI-Powered Job Market Intelligence
            </div>

        </div>
        """
    )

    st.divider()

    st.caption("Navigation")

    st.page_link(
        "app.py",
        label="🏠 Home",
    )

    st.page_link(
        "pages/1_Job_Explorer.py",
        label="💼 Job Explorer",
    )

    st.page_link(
        "pages/2_Market_Intelligence.py",
        label="📊 Market Intelligence",
    )

    st.page_link(
        "pages/3_Skills_Intelligence.py",
        label="🧠 Skills Intelligence",
    )

    st.page_link(
        "pages/4_Salary_Intelligence.py",
        label="💰 Salary Intelligence",
    )

    st.page_link(
        "pages/5_Resume_Analyzer.py",
        label="📄 Resume Analyzer",
    )

    st.page_link(
        "pages/6_Job_Matcher.py",
        label="🎯 Job Matcher",
    )

    st.page_link(
        "pages/7_Skill_Gap.py",
        label="🧩 Skill Gap",
    )

    st.page_link(
        "pages/8_Career_Recommendations.py",
        label="🚀 Career Recommendations",
    )

    st.page_link(
        "pages/9_Profile.py",
        label="👤 Profile",
    )

    st.divider()

    st.caption("JobInsight v0.1")
    st.caption("Research & Development Build")


# ============================================================
# HERO
# ============================================================

render_html(
    """
    <div class="ji-hero">

        <div class="ji-hero-circle-1"></div>
        <div class="ji-hero-circle-2"></div>

        <div class="ji-badge">
            ✦ AI-POWERED CAREER INTELLIGENCE PLATFORM
        </div>

        <div class="ji-hero-title">
            Understand the Job Market.
            <br>

            <span class="ji-hero-gradient">
                Build Your Career.
            </span>
        </div>

        <div class="ji-hero-description">
            JobInsight combines job-market analytics, NLP,
            machine learning, semantic matching and career
            intelligence into one unified platform.
        </div>

    </div>
    """
)


# ============================================================
# LOADING + METRICS
# ============================================================

with st.spinner("Loading job market intelligence..."):

    try:

        (
            jobs_analyzed,
            skills_identified,
            job_roles,
            locations,
        ) = load_home_metrics()

        metrics = [
            (
                "💼",
                f"{jobs_analyzed:,}",
                "Jobs Analyzed",
            ),
            (
                "🧠",
                f"{skills_identified:,}",
                "Skills Identified",
            ),
            (
                "🎯",
                f"{job_roles:,}",
                "Job Roles",
            ),
            (
                "🌍",
                f"{locations:,}",
                "Locations",
            ),
        ]

    except Exception as e:

        st.warning(
            f"Unable to load homepage statistics: {e}"
        )

        metrics = [
            ("💼", "—", "Jobs Analyzed"),
            ("🧠", "—", "Skills Identified"),
            ("🎯", "—", "Job Roles"),
            ("🌍", "—", "Locations"),
        ]


metric_columns = st.columns(4)


for col, (
    icon,
    value,
    label,
) in zip(
    metric_columns,
    metrics,
):

    with col:

        render_html(
            f"""
            <div class="ji-metric">

                <div class="ji-metric-icon">
                    {icon}
                </div>

                <div class="ji-metric-value">
                    {value}
                </div>

                <div class="ji-metric-label">
                    {label}
                </div>

            </div>
            """
        )


# ============================================================
# EXPLORE SECTION
# ============================================================

render_html(
    """
    <div class="ji-section-title">
        Explore JobInsight
    </div>

    <div class="ji-section-subtitle">
        Explore the job market, analyze your profile,
        and discover career opportunities.
    </div>
    """
)


# ============================================================
# NAVIGATION DATA
# ============================================================

navigation = [

    (
        "📊",
        "Market Intelligence",
        "Explore job demand, market trends and role distributions.",
        "Open Market Intelligence",
        "pages/2_Market_Intelligence.py",
    ),

    (
        "💼",
        "Job Explorer",
        "Search and explore opportunities across the job market.",
        "Explore Jobs",
        "pages/1_Job_Explorer.py",
    ),

    (
        "🧠",
        "Skills Intelligence",
        "Discover high-demand skills and skill relationships.",
        "Explore Skills",
        "pages/3_Skills_Intelligence.py",
    ),

    (
        "💰",
        "Salary Intelligence",
        "Analyze salary distributions and compensation patterns.",
        "Explore Salaries",
        "pages/4_Salary_Intelligence.py",
    ),

    (
        "📄",
        "Resume Analyzer",
        "Upload your resume and extract your professional profile.",
        "Analyze Resume",
        "pages/5_Resume_Analyzer.py",
    ),

    (
        "🎯",
        "Job Matcher",
        "Match your profile with relevant job opportunities.",
        "Find Matching Jobs",
        "pages/6_Job_Matcher.py",
    ),

    (
        "🧩",
        "Skill Gap",
        "Identify skills you already have and skills to develop.",
        "Analyze Skill Gap",
        "pages/7_Skill_Gap.py",
    ),

    (
        "🚀",
        "Career Recommendations",
        "Discover opportunities based on your skills and profile.",
        "View Recommendations",
        "pages/8_Career_Recommendations.py",
    ),

]


# ============================================================
# NAVIGATION CARDS
# ============================================================

for row_start in range(
    0,
    len(navigation),
    2,
):

    row = navigation[
        row_start:row_start + 2
    ]

    columns = st.columns(2)

    for col, item in zip(
        columns,
        row,
    ):

        (
            icon,
            title,
            description,
            button_label,
            page_path,
        ) = item

        with col:

            render_html(
                f"""
                <div class="ji-nav-card">

                    <div class="ji-nav-icon">
                        {icon}
                    </div>

                    <div class="ji-nav-title">
                        {title}
                    </div>

                    <div class="ji-nav-description">
                        {description}
                    </div>

                </div>
                """
            )

            st.page_link(
                page_path,
                label=f"🚀  {button_label}",
                use_container_width=True,
            )


# ============================================================
# FEATURE SECTION
# ============================================================

render_html(
    """
    <div class="ji-section-title">
        What JobInsight Provides
    </div>

    <div class="ji-section-subtitle">
        An integrated workflow connecting market intelligence
        with personalized career analysis.
    </div>
    """
)


feature_columns = st.columns(3)


features = [

    (
        "📈",
        "Market Analytics",
        "Discover job demand, skill trends, role distributions, locations and market patterns.",
    ),

    (
        "🧠",
        "AI Career Intelligence",
        "Extract skills from resumes and job descriptions, identify skill gaps and perform semantic matching.",
    ),

    (
        "🚀",
        "Career Recommendations",
        "Connect candidate profiles with jobs, skills, salary intelligence and career opportunities.",
    ),

]


for col, (
    icon,
    title,
    description,
) in zip(
    feature_columns,
    features,
):

    with col:

        render_html(
            f"""
            <div class="ji-feature">

                <div class="ji-feature-icon">
                    {icon}
                </div>

                <div class="ji-feature-title">
                    {title}
                </div>

                <div class="ji-feature-text">
                    {description}
                </div>

            </div>
            """
        )


# ============================================================
# FOOTER
# ============================================================

render_html(
    """
    <div class="ji-footer">

        <strong>JobInsight</strong>
        &nbsp;•&nbsp;
        AI-Powered Job Market Analytics
        &nbsp;•&nbsp;
        Research & Development Build

    </div>
    """
)