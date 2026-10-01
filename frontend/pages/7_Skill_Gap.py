from pathlib import Path
import html
import sys

import pandas as pd
import plotly.express as px
import streamlit as st


# ============================================================
# PATH SETUP
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

JOBS_PATH = PROCESSED_DIR / "jobs_normalized.parquet"

if not JOBS_PATH.exists():
    JOBS_PATH = PROCESSED_DIR / "jobs_processed.parquet"

SKILLS_PATH = (
    PROCESSED_DIR
    / "job_skills_normalized.parquet"
)

SKILL_DEMAND_PATH = (
    PROCESSED_DIR
    / "skill_demand.csv"
)


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Skill Gap | JobInsight",
    page_icon="🧩",
    layout="wide",
)


# ============================================================
# GLOBAL CSS
# ============================================================

st.markdown(
    """
    <style>

    .stApp {
        background:
            radial-gradient(
                circle at 8% 0%,
                rgba(99,102,241,0.10),
                transparent 27%
            ),
            radial-gradient(
                circle at 92% 8%,
                rgba(14,165,233,0.08),
                transparent 25%
            ),
            #f6f8fc;
    }

    [data-testid="stHeader"] {
        background: transparent;
    }

    [data-testid="stSidebar"] {
        background:
            linear-gradient(
                180deg,
                #111827 0%,
                #172554 55%,
                #1e1b4b 100%
            );
    }

    [data-testid="stSidebar"] * {
        color: #f8fafc;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1450px;
    }

    /* ========================================================
       HERO
       ======================================================== */

    .hero {
        position: relative;
        overflow: hidden;
        padding: 34px 38px;
        border-radius: 26px;
        margin-bottom: 24px;
        color: white;

        background:
            radial-gradient(
                circle at 85% 20%,
                rgba(129,140,248,0.40),
                transparent 25%
            ),
            radial-gradient(
                circle at 15% 90%,
                rgba(56,189,248,0.18),
                transparent 28%
            ),
            linear-gradient(
                135deg,
                #111827 0%,
                #1e1b4b 52%,
                #312e81 100%
            );

        box-shadow:
            0 20px 50px rgba(15,23,42,0.16);
    }

    .hero-orb-one {
        position: absolute;
        width: 170px;
        height: 170px;
        border-radius: 50%;
        right: 65px;
        top: -80px;
        background: rgba(129,140,248,0.16);
        border: 1px solid rgba(255,255,255,0.08);
    }

    .hero-orb-two {
        position: absolute;
        width: 90px;
        height: 90px;
        border-radius: 50%;
        right: 225px;
        bottom: -42px;
        background: rgba(56,189,248,0.14);
    }

    .hero-kicker {
        font-size: 13px;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        font-weight: 700;
        color: #a5b4fc;
        margin-bottom: 8px;
    }

    .hero-title {
        font-size: 38px;
        line-height: 1.12;
        font-weight: 800;
        margin: 0;
        position: relative;
        z-index: 2;
    }

    .hero-subtitle {
        margin-top: 12px;
        max-width: 850px;
        font-size: 16px;
        line-height: 1.7;
        color: #dbeafe;
        position: relative;
        z-index: 2;
    }


    /* ========================================================
       SECTION
       ======================================================== */

    .section-title {
        font-size: 22px;
        font-weight: 800;
        color: #111827;
        margin: 28px 0 8px 0;
    }

    .section-subtitle {
        color: #64748b;
        font-size: 14px;
        margin-bottom: 16px;
        line-height: 1.6;
    }


    /* ========================================================
       KPI
       ======================================================== */

    .kpi-card {
        background: rgba(255,255,255,0.96);
        border: 1px solid #e2e8f0;
        border-radius: 20px;
        padding: 20px;
        min-height: 112px;

        box-shadow:
            0 8px 24px rgba(15,23,42,0.05);
    }

    .kpi-icon {
        float: right;
        font-size: 22px;
    }

    .kpi-label {
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #64748b;
        font-weight: 700;
    }

    .kpi-value {
        margin-top: 8px;
        font-size: 25px;
        font-weight: 800;
        color: #111827;
    }


    /* ========================================================
       PROFILE CARD
       ======================================================== */

    .profile-card {
        background:
            linear-gradient(
                135deg,
                #ffffff,
                #f8faff
            );

        border: 1px solid #dbeafe;
        border-radius: 22px;
        padding: 25px;

        box-shadow:
            0 10px 30px rgba(37,99,235,0.06);
    }

    .profile-name {
        font-size: 25px;
        font-weight: 800;
        color: #111827;
    }

    .profile-meta {
        margin-top: 7px;
        color: #64748b;
        font-size: 14px;
    }


    /* ========================================================
       CONTENT CARDS
       ======================================================== */

    .content-card {
        background: rgba(255,255,255,0.97);
        border: 1px solid #e2e8f0;
        border-radius: 20px;
        padding: 22px;

        box-shadow:
            0 8px 24px rgba(15,23,42,0.045);
    }

    .card-heading {
        font-size: 16px;
        font-weight: 800;
        color: #111827;
        margin-bottom: 14px;
    }


    /* ========================================================
       SKILLS
       ======================================================== */

    .skill-wrap {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
    }

    .skill-chip {
        display: inline-block;
        padding: 7px 12px;
        border-radius: 999px;
        background: #eef2ff;
        border: 1px solid #c7d2fe;
        color: #4338ca;
        font-size: 12px;
        font-weight: 650;
    }

    .matched-chip {
        display: inline-block;
        padding: 7px 12px;
        border-radius: 999px;
        background: #ecfdf5;
        border: 1px solid #a7f3d0;
        color: #047857;
        font-size: 12px;
        font-weight: 650;
    }

    .missing-chip {
        display: inline-block;
        padding: 7px 12px;
        border-radius: 999px;
        background: #fff7ed;
        border: 1px solid #fed7aa;
        color: #c2410c;
        font-size: 12px;
        font-weight: 650;
    }


    /* ========================================================
       JOB CARD
       ======================================================== */

    .job-card {
        background: rgba(255,255,255,0.97);
        border: 1px solid #e2e8f0;
        border-radius: 22px;
        padding: 24px;

        box-shadow:
            0 8px 26px rgba(15,23,42,0.05);
    }

    .job-title {
        font-size: 21px;
        font-weight: 800;
        color: #111827;
    }

    .job-company {
        margin-top: 5px;
        color: #64748b;
        font-size: 14px;
        font-weight: 600;
    }

    .job-chip {
        display: inline-block;
        margin: 15px 7px 0 0;
        padding: 7px 11px;
        border-radius: 10px;
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        color: #475569;
        font-size: 12px;
        font-weight: 600;
    }


    /* ========================================================
       COVERAGE
       ======================================================== */

    .coverage-number {
        font-size: 42px;
        font-weight: 850;
        color: #4338ca;
        line-height: 1;
    }

    .coverage-label {
        margin-top: 7px;
        color: #64748b;
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: .07em;
        font-weight: 700;
    }

    .progress-track {
        height: 9px;
        border-radius: 999px;
        background: #e2e8f0;
        overflow: hidden;
        margin-top: 15px;
    }

    .progress-fill {
        height: 100%;
        border-radius: 999px;
        background:
            linear-gradient(
                90deg,
                #6366f1,
                #38bdf8
            );
    }


    /* ========================================================
       PRIORITY
       ======================================================== */

    .priority-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 18px;
        padding: 18px;

        box-shadow:
            0 7px 20px rgba(15,23,42,0.04);
    }

    .priority-name {
        font-weight: 800;
        color: #111827;
        font-size: 15px;
    }

    .priority-demand {
        margin-top: 6px;
        color: #64748b;
        font-size: 12px;
    }


    /* ========================================================
       FOOTER
       ======================================================== */

    .footer {
        margin-top: 45px;
        padding: 25px;
        text-align: center;
        color: #64748b;
        font-size: 12px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# HELPERS
# ============================================================

def render_html(content):
    """
    Always use Streamlit's native HTML renderer.
    This prevents raw HTML from appearing in the UI.
    """
    st.html(content)


def safe_text(
    value,
    default="Unknown",
):

    if value is None:
        return default

    try:
        if pd.isna(value):
            return default
    except Exception:
        pass

    text = str(value).strip()

    if not text:
        return default

    if text.lower() in {
        "nan",
        "none",
        "null",
    }:
        return default

    return text


def safe_list(value):

    if value is None:
        return []

    if isinstance(
        value,
        (list, tuple, set),
    ):
        return [
            str(x).strip()
            for x in value
            if str(x).strip()
        ]

    if hasattr(value, "tolist"):

        try:

            converted = value.tolist()

            if isinstance(
                converted,
                list,
            ):

                return [
                    str(x).strip()
                    for x in converted
                    if str(x).strip()
                ]

        except Exception:
            pass

    text = str(value).strip()

    if not text:
        return []

    if "," in text:

        return [
            x.strip()
            for x in text.split(",")
            if x.strip()
        ]

    return [text]


def normalize_skill(skill):

    return (
        str(skill)
        .strip()
        .lower()
        .replace("-", " ")
        .replace("_", " ")
    )


def unique_clean_skills(skills):

    result = []
    seen = set()

    for skill in safe_list(skills):

        normalized = normalize_skill(
            skill
        )

        if (
            normalized
            and normalized not in seen
        ):

            seen.add(normalized)
            result.append(skill)

    return result


def skill_chips_html(
    skills,
    chip_type="normal",
):

    skills = unique_clean_skills(
        skills
    )

    if not skills:

        return (
            '<span style="'
            'color:#94a3b8;'
            'font-size:13px;'
            '">None detected.</span>'
        )

    if chip_type == "matched":
        css_class = "matched-chip"

    elif chip_type == "missing":
        css_class = "missing-chip"

    else:
        css_class = "skill-chip"

    output = ""

    for skill in skills[:30]:

        output += (
            f'<span class="{css_class}">'
            f'{html.escape(str(skill))}'
            f'</span>'
        )

    if len(skills) > 30:

        output += (
            f'<span class="{css_class}">'
            f'+{len(skills) - 30} more'
            f'</span>'
        )

    return output


def get_candidate_profile():

    keys = [
        "candidate_profile",
        "resume_analysis",
        "resume_profile",
        "parsed_resume",
    ]

    for key in keys:

        value = st.session_state.get(
            key
        )

        if isinstance(
            value,
            dict,
        ):
            return value

    return None


def extract_candidate(
    profile
):

    if not profile:

        return {
            "name": "Demo Candidate",
            "experience": "4+ years",
            "skills": [
                "Python",
                "SQL",
                "Pandas",
                "NumPy",
                "Machine Learning",
                "Data Science",
                "Statistics",
            ],
        }

    name = safe_text(
        profile.get(
            "name",
            "Candidate",
        ),
        "Candidate",
    )

    experience = safe_text(
        profile.get(
            "experience",
            "Not specified",
        ),
        "Not specified",
    )

    skills = unique_clean_skills(
        profile.get(
            "skills",
            [],
        )
    )

    return {
        "name": name,
        "experience": experience,
        "skills": skills,
    }


# ============================================================
# DATA LOADERS
# ============================================================

@st.cache_data
def load_jobs():

    if not JOBS_PATH.exists():
        return pd.DataFrame()

    try:
        return pd.read_parquet(
            JOBS_PATH
        )
    except Exception:
        return pd.DataFrame()


@st.cache_data
def load_skill_data():

    if not SKILLS_PATH.exists():
        return pd.DataFrame()

    try:
        return pd.read_parquet(
            SKILLS_PATH
        )
    except Exception:
        return pd.DataFrame()


@st.cache_data
def load_skill_demand():

    if not SKILL_DEMAND_PATH.exists():
        return pd.DataFrame()

    try:
        return pd.read_csv(
            SKILL_DEMAND_PATH
        )
    except Exception:
        return pd.DataFrame()


# ============================================================
# JOB SKILL EXTRACTION
# ============================================================

def get_job_skills(
    job_id,
    skill_df,
):

    if skill_df.empty:
        return []

    possible_id_columns = [
        "job_index",
        "job_id",
        "index",
        "id",
    ]

    possible_skill_columns = [
        "skill",
        "Skill",
        "skill_name",
        "normalized_skill",
    ]

    id_column = None
    skill_column = None

    for column in possible_id_columns:

        if column in skill_df.columns:
            id_column = column
            break

    for column in possible_skill_columns:

        if column in skill_df.columns:
            skill_column = column
            break

    if skill_column is None:
        return []

    if id_column is None:

        return []

    try:

        matches = skill_df[
            skill_df[id_column]
            == job_id
        ]

    except Exception:

        return []

    if matches.empty:
        return []

    return unique_clean_skills(
        matches[skill_column]
        .dropna()
        .tolist()
    )


# ============================================================
# MARKET DEMAND
# ============================================================

def get_market_demand(
    skill_demand
):

    if skill_demand.empty:
        return {}

    skill_column = None

    for column in [
        "skill",
        "Skill",
        "skills",
        "skill_name",
    ]:

        if column in skill_demand.columns:
            skill_column = column
            break

    if skill_column is None:
        return {}

    demand_column = None

    for column in [
        "job_count",
        "count",
        "demand",
        "frequency",
        "job_demand",
    ]:

        if column in skill_demand.columns:
            demand_column = column
            break

    if demand_column is None:

        numeric_columns = (
            skill_demand
            .select_dtypes(
                include="number"
            )
            .columns
            .tolist()
        )

        if numeric_columns:
            demand_column = numeric_columns[0]

    if demand_column is None:
        return {}

    demand = {}

    for _, row in skill_demand.iterrows():

        skill = safe_text(
            row.get(
                skill_column
            ),
            "",
        )

        if not skill:
            continue

        try:

            value = float(
                row.get(
                    demand_column,
                    0,
                )
            )

        except Exception:

            value = 0

        demand[
            normalize_skill(skill)
        ] = value

    return demand


# ============================================================
# GAP CALCULATION
# ============================================================

def calculate_gap(
    candidate_skills,
    required_skills,
):

    candidate_map = {
        normalize_skill(skill)
        for skill in candidate_skills
    }

    required = unique_clean_skills(
        required_skills
    )

    matched = []
    missing = []

    for skill in required:

        normalized = normalize_skill(
            skill
        )

        if normalized in candidate_map:

            matched.append(skill)

        else:

            missing.append(skill)

    total = len(required)

    if total == 0:

        coverage = 0.0

    else:

        coverage = (
            len(matched)
            / total
            * 100
        )

    return (
        matched,
        missing,
        coverage,
    )


# ============================================================
# HEADER / HERO
# ============================================================

render_html(
    """
    <div class="hero">

        <div class="hero-orb-one"></div>
        <div class="hero-orb-two"></div>

        <div class="hero-kicker">
            JOBINSIGHT · CAREER INTELLIGENCE
        </div>

        <div class="hero-title">
            Understand the skills you need to move forward.
        </div>

        <div class="hero-subtitle">
            Compare your current capabilities with target-job
            requirements and broader market demand. Identify
            what you already have and what you can develop next.
        </div>

    </div>
    """
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    # --------------------------------------------------------
    # SIDEBAR BRANDING
    # --------------------------------------------------------

    st.html(
        """
        <div style="
            padding:10px 4px 24px 4px;
            text-align:center;
        ">

            <div style="
                width:64px;
                height:64px;
                border-radius:20px;
                margin:auto;
                display:flex;
                align-items:center;
                justify-content:center;
                background:
                    linear-gradient(
                        135deg,
                        #6366f1,
                        #38bdf8
                    );
                font-size:30px;
                box-shadow:
                    0 12px 30px
                    rgba(99,102,241,.35);
            ">
                🧩
            </div>

            <div style="
                margin-top:12px;
                font-size:18px;
                font-weight:800;
            ">
                Skill Gap
            </div>

            <div style="
                margin-top:5px;
                font-size:12px;
                opacity:.70;
            ">
                Career skill intelligence
            </div>

        </div>
        """
    )

    # --------------------------------------------------------
    # NAVIGATION
    # --------------------------------------------------------

    st.page_link(
        "app.py",
        label="Home",
        icon="🏠",
    )

    st.page_link(
        "pages/1_Job_Explorer.py",
        label="Job Explorer",
        icon="🔎",
    )

    st.page_link(
        "pages/2_Market_Intelligence.py",
        label="Market Intelligence",
        icon="📊",
    )

    st.page_link(
        "pages/3_Skills_Intelligence.py",
        label="Skills Intelligence",
        icon="🧠",
    )

    st.page_link(
        "pages/4_Salary_Intelligence.py",
        label="Salary Intelligence",
        icon="💰",
    )

    st.page_link(
        "pages/5_Resume_Analyzer.py",
        label="Resume Analyzer",
        icon="📄",
    )

    st.page_link(
        "pages/6_Job_Matcher.py",
        label="Job Matcher",
        icon="🎯",
    )

    st.page_link(
        "pages/7_Skill_Gap.py",
        label="Skill Gap",
        icon="🧩",
    )

    st.page_link(
        "pages/8_Career_Recommendations.py",
        label="Career Recommendations",
        icon="🚀",
    )

    st.page_link(
        "pages/9_Profile.py",
        label="Profile",
        icon="👤",
    )

    # --------------------------------------------------------
    # SIDEBAR PIPELINE
    # --------------------------------------------------------

    st.html(
        """
        <div style="
            margin-top:25px;
            padding:15px;
            border-radius:16px;
            background:
                rgba(255,255,255,.07);
            border:
                1px solid
                rgba(255,255,255,.08);
            font-size:11px;
            line-height:1.7;
            color:#cbd5e1;
        ">

            <div style="
                font-size:12px;
                font-weight:800;
                color:#ffffff;
                margin-bottom:10px;
            ">
                Skill Gap Pipeline
            </div>

            <div>
                👤 Candidate Skills
            </div>

            <div>
                ↓
            </div>

            <div>
                🎯 Target Job
            </div>

            <div>
                ↓
            </div>

            <div>
                🧩 Required Skills
            </div>

            <div>
                ↓
            </div>

            <div>
                📊 Skill Coverage
            </div>

            <div>
                ↓
            </div>

            <div>
                🚀 Development Priorities
            </div>

        </div>
        """
    )


# ============================================================
# CANDIDATE
# ============================================================

profile = get_candidate_profile()

candidate = extract_candidate(
    profile
)

candidate_skills = candidate[
    "skills"
]


# ============================================================
# CANDIDATE PROFILE CARD
# ============================================================

render_html(
    f"""
    <div class="section-title">
        👤 Candidate Profile
    </div>

    <div class="section-subtitle">
        Your current resume profile is used as the
        baseline for skill-gap analysis.
    </div>

    <div class="profile-card">

        <div class="profile-name">
            {html.escape(
                candidate["name"]
            )}
        </div>

        <div class="profile-meta">
            Experience:
            <b>
                {html.escape(
                    candidate["experience"]
                )}
            </b>

            &nbsp; • &nbsp;

            <b>
                {len(candidate_skills)}
            </b>
            detected skills
        </div>

        <div style="
            margin-top:18px;
            font-size:11px;
            text-transform:uppercase;
            letter-spacing:.07em;
            font-weight:800;
            color:#475569;
            margin-bottom:10px;
        ">
            Your Current Skills
        </div>

        <div class="skill-wrap">
            {skill_chips_html(
                candidate_skills
            )}
        </div>

    </div>
    """
)


# ============================================================
# LOAD DATA
# ============================================================

jobs = load_jobs()

skill_df = load_skill_data()

skill_demand_df = load_skill_demand()

market_demand = get_market_demand(
    skill_demand_df
)


# ============================================================
# KPI ROW
# ============================================================

col1, col2, col3, col4 = (
    st.columns(4)
)


with col1:

    render_html(
        f"""
        <div class="kpi-card">

            <div class="kpi-icon">
                🧠
            </div>

            <div class="kpi-label">
                Your Skills
            </div>

            <div class="kpi-value">
                {len(candidate_skills)}
            </div>

        </div>
        """
    )


with col2:

    render_html(
        f"""
        <div class="kpi-card">

            <div class="kpi-icon">
                💼
            </div>

            <div class="kpi-label">
                Jobs Available
            </div>

            <div class="kpi-value">
                {len(jobs):,}
            </div>

        </div>
        """
    )


with col3:

    render_html(
        f"""
        <div class="kpi-card">

            <div class="kpi-icon">
                🧩
            </div>

            <div class="kpi-label">
                Skill Records
            </div>

            <div class="kpi-value">
                {len(skill_df):,}
            </div>

        </div>
        """
    )


with col4:

    render_html(
        f"""
        <div class="kpi-card">

            <div class="kpi-icon">
                📈
            </div>

            <div class="kpi-label">
                Market Skills
            </div>

            <div class="kpi-value">
                {len(market_demand):,}
            </div>

        </div>
        """
    )


# ============================================================
# TARGET JOB
# ============================================================

render_html(
    """
    <div class="section-title">
        🎯 Target Job
    </div>

    <div class="section-subtitle">
        Select a job to compare its required skills
        with your current candidate profile.
    </div>
    """
)


# ------------------------------------------------------------
# JOB SOURCE
# ------------------------------------------------------------

job_source = None

matches = st.session_state.get(
    "job_matcher_results",
    pd.DataFrame(),
)


if (
    isinstance(
        matches,
        pd.DataFrame,
    )
    and not matches.empty
):

    job_source = matches.copy()

elif not jobs.empty:

    job_source = jobs.copy()


if job_source is None or job_source.empty:

    st.warning(
        "No job data is available for skill-gap analysis."
    )

    st.stop()


# ------------------------------------------------------------
# COLUMN HELPERS
# ------------------------------------------------------------

def first_existing_column(
    dataframe,
    columns,
):

    for column in columns:

        if column in dataframe.columns:
            return column

    return None


title_column = first_existing_column(
    job_source,
    [
        "title",
        "job_title",
        "normalized_title",
    ],
)


company_column = first_existing_column(
    job_source,
    [
        "company_name",
        "company",
    ],
)


work_model_column = first_existing_column(
    job_source,
    [
        "work_model",
    ],
)


experience_column = first_existing_column(
    job_source,
    [
        "experience_level",
    ],
)


if title_column is None:

    job_source["__display_title"] = (
        "Job Opportunity"
    )

    title_column = "__display_title"


if company_column is None:

    job_source["__display_company"] = (
        "Company not specified"
    )

    company_column = "__display_company"


# ------------------------------------------------------------
# JOB OPTIONS
# ------------------------------------------------------------

job_options = []

job_records = []


for position, (
    index,
    row,
) in enumerate(
    job_source.head(1000).iterrows()
):

    title = safe_text(
        row.get(
            title_column
        ),
        "Untitled Job",
    )

    company = safe_text(
        row.get(
            company_column
        ),
        "Unknown Company",
    )

    job_options.append(
        f"{position + 1}. "
        f"{title} — "
        f"{company}"
    )

    job_records.append(
        (
            index,
            row,
        )
    )


selected_label = st.selectbox(
    "Choose a target job",
    job_options,
)


selected_position = (
    job_options.index(
        selected_label
    )
)


selected_index, selected_job = (
    job_records[
        selected_position
    ]
)


# ============================================================
# SELECTED JOB INFORMATION
# ============================================================

selected_title = safe_text(
    selected_job.get(
        title_column
    ),
    "Untitled Job",
)

selected_company = safe_text(
    selected_job.get(
        company_column
    ),
    "Unknown Company",
)

selected_work_model = (
    safe_text(
        selected_job.get(
            work_model_column
        )
    )
    if work_model_column
    else "Not specified"
)

selected_experience = (
    safe_text(
        selected_job.get(
            experience_column
        )
    )
    if experience_column
    else "Not specified"
)


render_html(
    f"""
    <div class="job-card">

        <div class="job-title">
            {html.escape(
                selected_title
            )}
        </div>

        <div class="job-company">
            🏢 {html.escape(
                selected_company
            )}
        </div>

        <span class="job-chip">
            💼 {html.escape(
                selected_work_model
            )}
        </span>

        <span class="job-chip">
            🎯 {html.escape(
                selected_experience
            )}
        </span>

    </div>
    """
)


# ============================================================
# REQUIRED JOB SKILLS
# ============================================================

required_skills = get_job_skills(
    selected_index,
    skill_df,
)


# ------------------------------------------------------------
# FALLBACK: TRY INDEX POSITION
# ------------------------------------------------------------

if not required_skills:

    try:

        required_skills = get_job_skills(
            selected_position,
            skill_df,
        )

    except Exception:
        pass


# ------------------------------------------------------------
# FALLBACK: TRY JOB ID
# ------------------------------------------------------------

if not required_skills:

    for id_column in [
        "job_id",
        "id",
        "job_index",
    ]:

        if (
            id_column
            in selected_job.index
        ):

            try:

                required_skills = (
                    get_job_skills(
                        selected_job[
                            id_column
                        ],
                        skill_df,
                    )
                )

            except Exception:
                pass

            if required_skills:
                break


# ============================================================
# JOB GAP
# ============================================================

matched_skills, missing_skills, coverage = (
    calculate_gap(
        candidate_skills,
        required_skills,
    )
)


# ============================================================
# JOB-SPECIFIC GAP HEADER
# ============================================================

render_html(
    """
    <div class="section-title">
        🧩 Job-Specific Skill Gap
    </div>

    <div class="section-subtitle">
        Compare your detected skills with the skills
        identified for the selected opportunity.
    </div>
    """
)


# ============================================================
# COVERAGE CARDS
# ============================================================

gap_col1, gap_col2, gap_col3 = (
    st.columns(3)
)


with gap_col1:

    render_html(
        f"""
        <div class="kpi-card">

            <div class="kpi-icon">
                📋
            </div>

            <div class="kpi-label">
                Required Skills
            </div>

            <div class="kpi-value">
                {len(required_skills)}
            </div>

        </div>
        """
    )


with gap_col2:

    render_html(
        f"""
        <div class="kpi-card">

            <div class="kpi-icon">
                ✅
            </div>

            <div class="kpi-label">
                Matched Skills
            </div>

            <div class="kpi-value">
                {len(matched_skills)}
            </div>

        </div>
        """
    )


with gap_col3:

    render_html(
        f"""
        <div class="kpi-card">

            <div class="kpi-icon">
                📌
            </div>

            <div class="kpi-label">
                Skills to Develop
            </div>

            <div class="kpi-value">
                {len(missing_skills)}
            </div>

        </div>
        """
    )


# ============================================================
# COVERAGE PANEL
# ============================================================

render_html(
    f"""
    <div class="content-card"
         style="margin-top:18px;">

        <div style="
            display:flex;
            align-items:center;
            justify-content:space-between;
            gap:20px;
        ">

            <div>

                <div class="coverage-number">
                    {coverage:.1f}%
                </div>

                <div class="coverage-label">
                    Skill Coverage
                </div>

            </div>

            <div style="
                flex:1;
                max-width:700px;
            ">

                <div class="progress-track">

                    <div
                        class="progress-fill"
                        style="
                            width:{
                                max(
                                    0,
                                    min(
                                        100,
                                        coverage
                                    )
                                )
                            }%;
                        "
                    ></div>

                </div>

                <div style="
                    margin-top:10px;
                    color:#64748b;
                    font-size:12px;
                ">
                    {len(matched_skills)}
                    matched out of
                    {len(required_skills)}
                    detected job skills.
                </div>

            </div>

        </div>

    </div>
    """
)


# ============================================================
# MATCHED / MISSING SKILLS
# ============================================================

matched_col, missing_col = (
    st.columns(2)
)


with matched_col:

    render_html(
        f"""
        <div class="content-card"
             style="margin-top:18px;">

            <div class="card-heading">
                ✅ Skills You Already Have
            </div>

            <div class="skill-wrap">
                {skill_chips_html(
                    matched_skills,
                    "matched",
                )}
            </div>

        </div>
        """
    )


with missing_col:

    render_html(
        f"""
        <div class="content-card"
             style="margin-top:18px;">

            <div class="card-heading">
                📌 Skills to Develop
            </div>

            <div class="skill-wrap">
                {skill_chips_html(
                    missing_skills,
                    "missing",
                )}
            </div>

        </div>
        """
    )


# ============================================================
# MARKET LEVEL ANALYSIS
# ============================================================

render_html(
    """
    <div class="section-title">
        🌐 Market-Level Skill Gap
    </div>

    <div class="section-subtitle">
        Compare your current skills with the skills most
        frequently detected across the broader job market.
    </div>
    """
)


# ------------------------------------------------------------
# TOP MARKET SKILLS
# ------------------------------------------------------------

market_rows = []

for skill, demand in (
    market_demand.items()
):

    market_rows.append(
        {
            "skill": skill,
            "demand": demand,
        }
    )


market_df = pd.DataFrame(
    market_rows
)


if not market_df.empty:

    market_df = (
        market_df
        .sort_values(
            "demand",
            ascending=False,
        )
        .reset_index(
            drop=True
        )
    )


# ------------------------------------------------------------
# MARKET GAP
# ------------------------------------------------------------

candidate_normalized = {
    normalize_skill(skill)
    for skill in candidate_skills
}


market_top_skills = (
    market_df
    .head(20)
    .copy()
    if not market_df.empty
    else pd.DataFrame()
)


market_covered = []
market_missing = []


if not market_top_skills.empty:

    for skill in market_top_skills[
        "skill"
    ]:

        if (
            normalize_skill(skill)
            in candidate_normalized
        ):

            market_covered.append(
                skill
            )

        else:

            market_missing.append(
                skill
            )


# ============================================================
# MARKET KPI
# ============================================================

market_col1, market_col2, market_col3 = (
    st.columns(3)
)


with market_col1:

    render_html(
        f"""
        <div class="kpi-card">

            <div class="kpi-icon">
                🌐
            </div>

            <div class="kpi-label">
                Market Skills Reviewed
            </div>

            <div class="kpi-value">
                {len(market_top_skills)}
            </div>

        </div>
        """
    )


with market_col2:

    render_html(
        f"""
        <div class="kpi-card">

            <div class="kpi-icon">
                ✅
            </div>

            <div class="kpi-label">
                Market Skills Covered
            </div>

            <div class="kpi-value">
                {len(market_covered)}
            </div>

        </div>
        """
    )


with market_col3:

    render_html(
        f"""
        <div class="kpi-card">

            <div class="kpi-icon">
                📌
            </div>

            <div class="kpi-label">
                Market Skills Missing
            </div>

            <div class="kpi-value">
                {len(market_missing)}
            </div>

        </div>
        """
    )


# ============================================================
# MARKET SKILLS
# ============================================================

market_skill_col1, market_skill_col2 = (
    st.columns(2)
)


with market_skill_col1:

    render_html(
        f"""
        <div class="content-card"
             style="margin-top:18px;">

            <div class="card-heading">
                ✅ Covered Market Skills
            </div>

            <div class="skill-wrap">
                {skill_chips_html(
                    market_covered,
                    "matched",
                )}
            </div>

        </div>
        """
    )


with market_skill_col2:

    render_html(
        f"""
        <div class="content-card"
             style="margin-top:18px;">

            <div class="card-heading">
                📌 Missing Market Skills
            </div>

            <div class="skill-wrap">
                {skill_chips_html(
                    market_missing,
                    "missing",
                )}
            </div>

        </div>
        """
    )


# ============================================================
# MARKET DEMAND VISUALIZATION
# ============================================================

if not market_top_skills.empty:

    render_html(
        """
        <div class="section-title">
            📊 Market Skill Demand
        </div>

        <div class="section-subtitle">
            Demand counts show how frequently each skill
            appears in the processed job-skill dataset.
        </div>
        """
    )

    chart_data = (
        market_top_skills
        .head(15)
        .sort_values(
            "demand",
            ascending=True,
        )
    )

    fig = px.bar(
        chart_data,
        x="demand",
        y="skill",
        orientation="h",
        labels={
            "demand": "Job Count",
            "skill": "",
        },
        text="demand",
    )

    fig.update_traces(
        texttemplate="%{text:,}",
        textposition="outside",
    )

    fig.update_layout(
        height=max(
            450,
            len(chart_data) * 38,
        ),
        margin=dict(
            l=10,
            r=80,
            t=20,
            b=20,
        ),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )


# ============================================================
# PRIORITY DEVELOPMENT SKILLS
# ============================================================

render_html(
    """
    <div class="section-title">
        🚀 Priority Skills to Develop
    </div>

    <div class="section-subtitle">
        Missing skills are shown with their market-demand
        signal to help identify development priorities.
    </div>
    """
)


priority_rows = []

for skill in missing_skills:

    normalized = normalize_skill(
        skill
    )

    demand = market_demand.get(
        normalized,
        0,
    )

    priority_rows.append(
        {
            "skill": skill,
            "demand": demand,
        }
    )


priority_df = pd.DataFrame(
    priority_rows
)


if not priority_df.empty:

    priority_df = (
        priority_df
        .sort_values(
            "demand",
            ascending=False,
        )
        .head(12)
    )


if priority_df.empty:

    render_html(
        """
        <div class="content-card">

            <div style="
                color:#047857;
                font-weight:700;
                font-size:14px;
            ">
                🎉 No priority skill gaps detected
            </div>

            <div style="
                margin-top:7px;
                color:#64748b;
                font-size:13px;
            ">
                Your current skills cover the detected
                requirements for this target job.
            </div>

        </div>
        """
    )

else:

    priority_columns = st.columns(
        min(
            3,
            len(priority_df),
        )
    )

    for index, (_, row) in enumerate(
        priority_df.iterrows()
    ):

        skill = safe_text(
            row["skill"]
        )

        demand = row["demand"]

        with priority_columns[
            index % len(priority_columns)
        ]:

            render_html(
                f"""
                <div class="priority-card">

                    <div class="priority-name">
                        📌 {html.escape(skill)}
                    </div>

                    <div class="priority-demand">
                        Market demand:
                        <b>
                            {demand:,.0f}
                        </b>
                        job records
                    </div>

                </div>
                """
            )


# ============================================================
# DEVELOPMENT PATH
# ============================================================

render_html(
    """
    <div class="section-title">
        🛣️ Suggested Development Path
    </div>

    <div class="section-subtitle">
        A simple progression based on the detected skill gaps.
    </div>
    """
)


path_col1, path_col2, path_col3 = (
    st.columns(3)
)


with path_col1:

    render_html(
        """
        <div class="content-card">

            <div class="card-heading">
                01 · Strengthen Existing Skills
            </div>

            <div style="
                color:#64748b;
                font-size:13px;
                line-height:1.7;
            ">
                Continue improving the skills already
                present in your profile and use them
                in projects or practical work.
            </div>

        </div>
        """
    )


with path_col2:

    render_html(
        """
        <div class="content-card">

            <div class="card-heading">
                02 · Close Priority Gaps
            </div>

            <div style="
                color:#64748b;
                font-size:13px;
                line-height:1.7;
            ">
                Focus first on missing skills that are
                both relevant to your selected job and
                visible in broader market demand.
            </div>

        </div>
        """
    )


with path_col3:

    render_html(
        """
        <div class="content-card">

            <div class="card-heading">
                03 · Recheck Your Alignment
            </div>

            <div style="
                color:#64748b;
                font-size:13px;
                line-height:1.7;
            ">
                Re-run Job Matcher and Career
                Recommendations after updating
                your profile with newly acquired skills.
            </div>

        </div>
        """
    )


# ============================================================
# METHODOLOGY
# ============================================================

with st.expander(
    "🧠 How Skill Gap Analysis Works"
):

    st.markdown(
        """
        ### Candidate Skills

        Candidate skills are taken from the profile generated
        by the Resume Analyzer.

        ### Job-Specific Gap

        The selected job's detected skills are compared with
        the candidate's normalized skills.

        **Skill coverage**

        ```text
        matched required skills
        ----------------------- × 100
        total required skills
        ```

        ### Market-Level Gap

        The platform also compares candidate skills with
        frequently detected skills in the processed job market.

        ### Priority Skills

        Missing skills are associated with their observed
        market-demand counts where available.

        This analysis is a decision-support signal. It does
        not guarantee employment outcomes.
        """
    )


# ============================================================
# DATA SOURCES
# ============================================================

with st.expander(
    "ℹ️ Data Sources & Processing"
):

    st.write(
        f"**Jobs:** {JOBS_PATH}"
    )

    st.write(
        f"**Job skills:** {SKILLS_PATH}"
    )

    st.write(
        f"**Skill demand:** {SKILL_DEMAND_PATH}"
    )

    st.write(
        f"**Candidate skills:** "
        f"{len(candidate_skills)}"
    )

    st.write(
        f"**Target job skills:** "
        f"{len(required_skills)}"
    )

    st.write(
        f"**Target job coverage:** "
        f"{coverage:.1f}%"
    )


# ============================================================
# FOOTER
# ============================================================

render_html(
    """
    <div class="footer">

        <b>JobInsight</b> · AI-Powered Job Market
        Analytics & Career Recommendation Platform

        <br>

        Candidate skills · Job requirements ·
        Market demand · Development priorities

    </div>
    """
)