from pathlib import Path
import html
import math

import pandas as pd
import streamlit as st


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

SALARY_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "salary_normalized.parquet"
)

SKILLS_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "job_skills_normalized.parquet"
)


# ============================================================
# PAGE
# ============================================================

st.set_page_config(
    page_title="Job Explorer | JobInsight",
    page_icon="🔎",
    layout="wide",
)


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
    <style>

    .stApp {
        background:
            radial-gradient(
                circle at 8% 0%,
                rgba(99,102,241,.10),
                transparent 27%
            ),
            radial-gradient(
                circle at 92% 8%,
                rgba(14,165,233,.08),
                transparent 25%
            ),
            #f6f8fc;
    }

    [data-testid="stHeader"] {
        background:transparent;
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
        color:#f8fafc;
    }

    .block-container {
        padding-top:2rem;
        padding-bottom:3rem;
        max-width:1450px;
    }

    .hero {
        position:relative;
        overflow:hidden;
        padding:36px 40px;
        border-radius:26px;
        margin-bottom:25px;
        color:white;

        background:
            radial-gradient(
                circle at 85% 20%,
                rgba(129,140,248,.40),
                transparent 25%
            ),
            radial-gradient(
                circle at 15% 90%,
                rgba(56,189,248,.18),
                transparent 28%
            ),
            linear-gradient(
                135deg,
                #111827,
                #1e1b4b 55%,
                #3730a3
            );

        box-shadow:
            0 20px 50px rgba(15,23,42,.16);
    }

    .orb-one {
        position:absolute;
        width:170px;
        height:170px;
        border-radius:50%;
        right:60px;
        top:-80px;
        background:rgba(129,140,248,.16);
        border:1px solid rgba(255,255,255,.08);
    }

    .orb-two {
        position:absolute;
        width:90px;
        height:90px;
        border-radius:50%;
        right:220px;
        bottom:-45px;
        background:rgba(56,189,248,.14);
    }

    .hero-kicker {
        font-size:13px;
        letter-spacing:.14em;
        text-transform:uppercase;
        font-weight:700;
        color:#a5b4fc;
        margin-bottom:8px;
    }

    .hero-title {
        font-size:38px;
        line-height:1.12;
        font-weight:800;
        margin:0;
        position:relative;
        z-index:2;
    }

    .hero-subtitle {
        margin-top:12px;
        max-width:900px;
        font-size:16px;
        line-height:1.7;
        color:#dbeafe;
        position:relative;
        z-index:2;
    }

    .kpi-card {
        background:rgba(255,255,255,.96);
        border:1px solid #e2e8f0;
        border-radius:20px;
        padding:20px;
        min-height:110px;
        box-shadow:0 8px 24px rgba(15,23,42,.05);
    }

    .kpi-icon {
        float:right;
        font-size:22px;
    }

    .kpi-label {
        font-size:11px;
        text-transform:uppercase;
        letter-spacing:.08em;
        color:#64748b;
        font-weight:700;
    }

    .kpi-value {
        margin-top:8px;
        font-size:26px;
        font-weight:800;
        color:#111827;
    }

    .section-title {
        font-size:22px;
        font-weight:800;
        color:#111827;
        margin:28px 0 8px;
    }

    .section-subtitle {
        color:#64748b;
        font-size:14px;
        margin-bottom:16px;
        line-height:1.6;
    }

    .job-card {
        background:rgba(255,255,255,.98);
        border:1px solid #e2e8f0;
        border-radius:23px;
        padding:25px;
        margin:15px 0;
        box-shadow:0 10px 28px rgba(15,23,42,.055);
    }

    .job-title {
        font-size:22px;
        line-height:1.3;
        font-weight:800;
        color:#111827;
    }

    .company {
        color:#64748b;
        font-size:14px;
        margin-top:5px;
        font-weight:600;
    }

    .meta-row {
        display:flex;
        flex-wrap:wrap;
        gap:8px;
        margin-top:16px;
    }

    .meta-chip {
        display:inline-block;
        padding:7px 11px;
        border-radius:10px;
        background:#f8fafc;
        border:1px solid #e2e8f0;
        color:#475569;
        font-size:12px;
        font-weight:600;
    }

    .salary {
        margin-top:17px;
        font-size:17px;
        font-weight:800;
        color:#047857;
    }

    .skill-wrap {
        display:flex;
        flex-wrap:wrap;
        gap:7px;
        margin-top:9px;
    }

    .skill-chip {
        display:inline-block;
        padding:6px 11px;
        border-radius:999px;
        background:#eef2ff;
        border:1px solid #c7d2fe;
        color:#4338ca;
        font-size:11px;
        font-weight:650;
    }

    .description {
        margin-top:17px;
        color:#475569;
        line-height:1.65;
        font-size:13px;
    }

    .result-box {
        background:white;
        border:1px solid #e2e8f0;
        border-radius:16px;
        padding:13px 17px;
        color:#64748b;
        font-size:13px;
        margin:12px 0;
    }

    .footer {
        margin-top:45px;
        padding:25px;
        text-align:center;
        color:#64748b;
        font-size:12px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# HELPERS
# ============================================================

def render_html(content):
    st.html(content)


def clean_text(value, default="Not specified"):

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


def clean_list(value):

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

    try:

        if pd.isna(value):
            return []

    except Exception:
        pass

    text = str(value).strip()

    if not text or text.lower() in {
        "nan",
        "none",
        "null",
        "[]",
    }:
        return []

    text = (
        text.replace("[", "")
        .replace("]", "")
        .replace("'", "")
        .replace('"', "")
    )

    return [
        item.strip()
        for item in text.split(",")
        if item.strip()
    ]


def format_salary(row):

    minimum = row.get(
        "annual_salary_min_usd"
    )

    maximum = row.get(
        "annual_salary_max_usd"
    )

    try:
        minimum = float(minimum)
    except Exception:
        minimum = None

    try:
        maximum = float(maximum)
    except Exception:
        maximum = None

    if (
        minimum is not None
        and minimum > 0
        and maximum is not None
        and maximum > 0
    ):

        return (
            f"${minimum:,.0f}"
            f" – "
            f"${maximum:,.0f}"
            f" / year"
        )

    if minimum is not None and minimum > 0:

        return (
            f"${minimum:,.0f}+ / year"
        )

    if maximum is not None and maximum > 0:

        return (
            f"Up to ${maximum:,.0f} / year"
        )

    return "Salary not specified"


def format_date(value):

    if value is None:
        return "Date not available"

    try:

        if pd.isna(value):
            return "Date not available"

        return pd.to_datetime(
            value
        ).strftime("%b %d, %Y")

    except Exception:

        return "Date not available"


def truncate_text(
    value,
    length=360,
):

    text = clean_text(
        value,
        "",
    )

    if len(text) <= length:
        return text

    return (
        text[:length]
        .rsplit(" ", 1)[0]
        + "..."
    )


# ============================================================
# DATA
# ============================================================

@st.cache_data
def load_jobs():

    jobs = pd.read_parquet(
        JOBS_PATH
    )

    if "date_posted" in jobs.columns:

        jobs["date_posted"] = pd.to_datetime(
            jobs["date_posted"],
            errors="coerce",
        )

    if SALARY_PATH.exists():

        salary = pd.read_parquet(
            SALARY_PATH
        )

        if len(salary) == len(jobs):

            for column in [
                "annual_salary_min_usd",
                "annual_salary_max_usd",
            ]:

                if column in salary.columns:

                    jobs[column] = pd.to_numeric(
                        salary[column],
                        errors="coerce",
                    ).values

    if SKILLS_PATH.exists():

        skill_df = pd.read_parquet(
            SKILLS_PATH
        )

        if "normalized_skills" not in jobs.columns:

            if (
                "job_index"
                in skill_df.columns
            ):

                mapping = {}

                for _, row in skill_df.iterrows():

                    index = row[
                        "job_index"
                    ]

                    values = clean_list(
                        row.get(
                            "skills",
                            row.get(
                                "normalized_skills",
                                [],
                            ),
                        )
                    )

                    mapping.setdefault(
                        str(index),
                        [],
                    ).extend(values)

                jobs[
                    "normalized_skills"
                ] = [
                    list(
                        dict.fromkeys(
                            mapping.get(
                                str(index),
                                [],
                            )
                        )
                    )
                    for index in jobs.index
                ]

            elif (
                len(skill_df)
                == len(jobs)
            ):

                source_column = (
                    "normalized_skills"
                    if "normalized_skills"
                    in skill_df.columns
                    else "skills"
                    if "skills"
                    in skill_df.columns
                    else None
                )

                if source_column:

                    jobs[
                        "normalized_skills"
                    ] = skill_df[
                        source_column
                    ].apply(clean_list).values

    return jobs


try:

    jobs = load_jobs()

except Exception as exc:

    st.error(
        f"Could not load job data: {exc}"
    )

    st.stop()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.html(
        """
        <div style="
            padding:10px 4px 24px;
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
                🔎
            </div>

            <div style="
                margin-top:12px;
                font-size:18px;
                font-weight:800;
            ">
                Job Explorer
            </div>

            <div style="
                margin-top:5px;
                font-size:12px;
                opacity:.70;
            ">
                Explore the global job market
            </div>

        </div>
        """
    )

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

    st.html(
        """
        <div style="
            margin-top:25px;
            padding:15px;
            border-radius:16px;
            background:rgba(255,255,255,.07);
            border:1px solid rgba(255,255,255,.08);
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
                Explorer Workflow
            </div>

            <div>🔎 Search jobs</div>
            <div>↓</div>
            <div>🎛️ Apply filters</div>
            <div>↓</div>
            <div>💼 Explore opportunities</div>
            <div>↓</div>
            <div>🧠 Inspect skills</div>

        </div>
        """
    )


# ============================================================
# HERO
# ============================================================

render_html(
    """
    <div class="hero">

        <div class="orb-one"></div>
        <div class="orb-two"></div>

        <div class="hero-kicker">
            JOBINSIGHT · JOB MARKET EXPLORER
        </div>

        <div class="hero-title">
            Explore opportunities across the job market.
        </div>

        <div class="hero-subtitle">
            Search normalized job postings by title, company,
            skills, location, experience, work model, salary
            and employment type.
        </div>

    </div>
    """
)


# ============================================================
# KPI
# ============================================================

total_jobs = len(jobs)

salary_count = (
    jobs[
        "annual_salary_min_usd"
    ].notna().sum()
    if "annual_salary_min_usd"
    in jobs.columns
    else 0
)

remote_count = (
    (
        jobs["work_model"]
        == "Remote"
    ).sum()
    if "work_model"
    in jobs.columns
    else 0
)

company_count = (
    jobs[
        "company_name"
    ].nunique()
    if "company_name"
    in jobs.columns
    else 0
)


k1, k2, k3, k4 = st.columns(4)


with k1:

    render_html(
        f"""
        <div class="kpi-card">
            <div class="kpi-icon">💼</div>
            <div class="kpi-label">Jobs Available</div>
            <div class="kpi-value">
                {total_jobs:,}
            </div>
        </div>
        """
    )


with k2:

    render_html(
        f"""
        <div class="kpi-card">
            <div class="kpi-icon">💰</div>
            <div class="kpi-label">Salary Records</div>
            <div class="kpi-value">
                {salary_count:,}
            </div>
        </div>
        """
    )


with k3:

    render_html(
        f"""
        <div class="kpi-card">
            <div class="kpi-icon">🌐</div>
            <div class="kpi-label">Remote Jobs</div>
            <div class="kpi-value">
                {remote_count:,}
            </div>
        </div>
        """
    )


with k4:

    render_html(
        f"""
        <div class="kpi-card">
            <div class="kpi-icon">🏢</div>
            <div class="kpi-label">Companies</div>
            <div class="kpi-value">
                {company_count:,}
            </div>
        </div>
        """
    )


# ============================================================
# SEARCH
# ============================================================

render_html(
    """
    <div class="section-title">
        🔎 Search & Filter Jobs
    </div>

    <div class="section-subtitle">
        Combine keyword search with structured market filters.
    </div>
    """
)


search_query = st.text_input(
    "Search jobs",
    placeholder=(
        "Try: Data Scientist, Python, AWS, "
        "Project Manager..."
    ),
)


col1, col2, col3, col4 = st.columns(4)


with col1:

    countries = ["All"]

    if "country" in jobs.columns:

        countries += sorted(
            jobs["country"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

    selected_country = st.selectbox(
        "Country",
        countries,
    )


with col2:

    experiences = ["All"]

    if "experience_level" in jobs.columns:

        experiences += sorted(
            jobs[
                "experience_level"
            ]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

    selected_experience = st.selectbox(
        "Experience Level",
        experiences,
    )


with col3:

    work_models = ["All"]

    if "work_model" in jobs.columns:

        work_models += sorted(
            jobs[
                "work_model"
            ]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

    selected_work_model = st.selectbox(
        "Work Model",
        work_models,
    )


with col4:

    employment_types = ["All"]

    if "employment_type" in jobs.columns:

        employment_types += sorted(
            jobs[
                "employment_type"
            ]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

    selected_employment = st.selectbox(
        "Employment Type",
        employment_types,
    )


col5, col6 = st.columns(2)


with col5:

    min_salary_filter = st.number_input(
        "Minimum annual salary ($)",
        min_value=0,
        value=0,
        step=5000,
    )


with col6:

    page_size = st.selectbox(
        "Jobs per page",
        [5, 10, 20, 30],
        index=1,
    )


# ============================================================
# FILTER
# ============================================================

filtered = jobs.copy()


if search_query.strip():

    query = search_query.strip().lower()

    searchable_columns = [
        "title",
        "normalized_title",
        "company_name",
        "job_description",
        "responsibilities",
        "minimum_qualifications",
        "preferred_qualifications",
        "industry",
        "function",
        "normalized_skills",
    ]

    mask = pd.Series(
        False,
        index=filtered.index,
    )

    for column in searchable_columns:

        if column not in filtered.columns:
            continue

        mask |= (
            filtered[column]
            .fillna("")
            .astype(str)
            .str.lower()
            .str.contains(
                query,
                regex=False,
            )
        )

    filtered = filtered[mask]


if selected_country != "All":

    filtered = filtered[
        filtered["country"].astype(str)
        == selected_country
    ]


if selected_experience != "All":

    filtered = filtered[
        filtered[
            "experience_level"
        ].astype(str)
        == selected_experience
    ]


if selected_work_model != "All":

    filtered = filtered[
        filtered[
            "work_model"
        ].astype(str)
        == selected_work_model
    ]


if selected_employment != "All":

    filtered = filtered[
        filtered[
            "employment_type"
        ].astype(str)
        == selected_employment
    ]


if min_salary_filter > 0:

    if "annual_salary_min_usd" in filtered.columns:

        filtered = filtered[
            pd.to_numeric(
                filtered[
                    "annual_salary_min_usd"
                ],
                errors="coerce",
            )
            >= min_salary_filter
        ]


# ============================================================
# RESULTS
# ============================================================

result_count = len(filtered)

render_html(
    f"""
    <div class="result-box">
        <b>{result_count:,}</b>
        jobs found with the current filters.
    </div>
    """
)


if result_count == 0:

    st.info(
        "No jobs match the selected filters. "
        "Try removing one or more filters."
    )

    st.stop()


# ============================================================
# PAGINATION
# ============================================================

total_pages = max(
    1,
    math.ceil(
        result_count / page_size
    ),
)


current_page = st.number_input(
    "Page",
    min_value=1,
    max_value=total_pages,
    value=1,
    step=1,
)


start = (
    current_page - 1
) * page_size

end = start + page_size

page_jobs = filtered.iloc[
    start:end
]


st.caption(
    f"Showing {start + 1:,}–"
    f"{min(end, result_count):,} "
    f"of {result_count:,} matching jobs"
)


# ============================================================
# JOB CARDS
# ============================================================

for _, row in page_jobs.iterrows():

    title = clean_text(
        row.get(
            "title"
        ),
        "Untitled Position",
    )

    company = clean_text(
        row.get(
            "company_name"
        ),
        "Company not specified",
    )

    country = clean_text(
        row.get(
            "country"
        ),
        "Unknown",
    )

    work_model = clean_text(
        row.get(
            "work_model"
        ),
        "Unknown",
    )

    experience = clean_text(
        row.get(
            "experience_level"
        ),
        "Unknown",
    )

    employment = clean_text(
        row.get(
            "employment_type"
        ),
        "Unknown",
    )

    salary = format_salary(
        row
    )

    date_posted = format_date(
        row.get(
            "date_posted"
        )
    )

    description = truncate_text(
        row.get(
            "job_description",
            "",
        )
    )

    skills = clean_list(
        row.get(
            "normalized_skills",
            [],
        )
    )

    chips = ""

    for skill in skills[:12]:

        chips += (
            '<span class="skill-chip">'
            f'{html.escape(skill)}'
            '</span>'
        )

    if not chips:

        chips = (
            '<span style="'
            'color:#94a3b8;'
            'font-size:12px;'
            '">'
            'No detected skills'
            '</span>'
        )


    render_html(
        f"""
        <div class="job-card">

            <div class="job-title">
                {html.escape(title)}
            </div>

            <div class="company">
                🏢 {html.escape(company)}
            </div>

            <div class="meta-row">

                <span class="meta-chip">
                    🌍 {html.escape(country)}
                </span>

                <span class="meta-chip">
                    💼 {html.escape(work_model)}
                </span>

                <span class="meta-chip">
                    🎯 {html.escape(experience)}
                </span>

                <span class="meta-chip">
                    📋 {html.escape(employment)}
                </span>

                <span class="meta-chip">
                    📅 {html.escape(date_posted)}
                </span>

            </div>

            <div class="salary">
                💰 {html.escape(salary)}
            </div>

            <div style="
                margin-top:16px;
                font-size:11px;
                text-transform:uppercase;
                letter-spacing:.07em;
                color:#64748b;
                font-weight:800;
            ">
                Skills
            </div>

            <div class="skill-wrap">
                {chips}
            </div>

            <div class="description">
                {html.escape(description)}
            </div>

        </div>
        """
    )


    with st.expander(
        "View full job details"
    ):

        detail_col1, detail_col2 = (
            st.columns(2)
        )

        with detail_col1:

            st.markdown(
                "### Job Information"
            )

            st.write(
                f"**Title:** {title}"
            )

            st.write(
                f"**Company:** {company}"
            )

            st.write(
                f"**Industry:** "
                f"{clean_text(row.get('industry'))}"
            )

            st.write(
                f"**Function:** "
                f"{clean_text(row.get('function'))}"
            )

            st.write(
                f"**Location:** "
                f"{clean_text(row.get('location_resolved'), country)}"
            )


        with detail_col2:

            st.markdown(
                "### Requirements"
            )

            st.write(
                f"**Experience:** {experience}"
            )

            st.write(
                f"**Education:** "
                f"{clean_text(row.get('education_level'))}"
            )

            st.write(
                f"**Work Model:** {work_model}"
            )

            st.write(
                f"**Employment:** {employment}"
            )

            st.write(
                f"**Salary:** {salary}"
            )


        qualifications = clean_text(
            row.get(
                "minimum_qualifications",
                "",
            ),
            "",
        )

        preferred = clean_text(
            row.get(
                "preferred_qualifications",
                "",
            ),
            "",
        )

        responsibilities = clean_text(
            row.get(
                "responsibilities",
                "",
            ),
            "",
        )

        full_description = clean_text(
            row.get(
                "job_description",
                "",
            ),
            "",
        )


        if qualifications:

            st.markdown(
                "### Minimum Qualifications"
            )

            st.write(
                qualifications
            )


        if preferred:

            st.markdown(
                "### Preferred Qualifications"
            )

            st.write(
                preferred
            )


        if responsibilities:

            st.markdown(
                "### Responsibilities"
            )

            st.write(
                responsibilities
            )


        if full_description:

            st.markdown(
                "### Full Job Description"
            )

            st.write(
                full_description
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

        Search · Filter · Explore · Compare

    </div>
    """
)