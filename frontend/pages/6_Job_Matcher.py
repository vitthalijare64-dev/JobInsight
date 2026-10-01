from pathlib import Path
import sys
import html

import pandas as pd
import streamlit as st
import plotly.express as px


# ============================================================
# PATH SETUP
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="JobInsight - Job Matcher",
    page_icon="🎯",
    layout="wide",
)


# ============================================================
# FILE PATHS
# ============================================================

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

JOBS_PATH = PROCESSED_DIR / "jobs_normalized.parquet"

if not JOBS_PATH.exists():
    JOBS_PATH = PROCESSED_DIR / "jobs_processed.parquet"

SKILLS_PATH = PROCESSED_DIR / "job_skills_normalized.parquet"

EMBEDDINGS_PATH = (
    PROJECT_ROOT
    / "models"
    / "matching"
    / "job_embeddings.parquet"
)


# ============================================================
# GLOBAL CSS
# ============================================================

st.markdown(
    """
    <style>

    /* Main background */
    .stApp {
        background:
            radial-gradient(circle at 10% 0%, rgba(99,102,241,0.10), transparent 28%),
            radial-gradient(circle at 90% 10%, rgba(14,165,233,0.08), transparent 25%),
            #f6f8fc;
    }

    [data-testid="stHeader"] {
        background: transparent;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background:
            linear-gradient(180deg, #111827 0%, #172554 55%, #1e1b4b 100%);
    }

    [data-testid="stSidebar"] * {
        color: #f8fafc;
    }

    /* Remove excessive top spacing */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1450px;
    }

    /* Hero */
    .hero {
        position: relative;
        overflow: hidden;
        padding: 34px 38px;
        border-radius: 26px;
        margin-bottom: 24px;
        color: white;
        background:
            radial-gradient(circle at 85% 20%, rgba(129,140,248,0.40), transparent 25%),
            radial-gradient(circle at 15% 90%, rgba(56,189,248,0.18), transparent 28%),
            linear-gradient(135deg, #111827 0%, #1e1b4b 52%, #312e81 100%);
        box-shadow: 0 20px 50px rgba(15,23,42,0.16);
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
        max-width: 760px;
        font-size: 16px;
        line-height: 1.7;
        color: #dbeafe;
        position: relative;
        z-index: 2;
    }

    /* Section heading */
    .section-title {
        font-size: 22px;
        font-weight: 800;
        color: #111827;
        margin: 28px 0 12px 0;
    }

    .section-subtitle {
        color: #64748b;
        font-size: 14px;
        margin-bottom: 16px;
    }

    /* KPI cards */
    .kpi-card {
        background: rgba(255,255,255,0.94);
        border: 1px solid #e2e8f0;
        border-radius: 20px;
        padding: 20px;
        min-height: 112px;
        box-shadow: 0 8px 24px rgba(15,23,42,0.05);
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

    .kpi-icon {
        float: right;
        font-size: 22px;
    }

    /* Candidate card */
    .candidate-card {
        background:
            linear-gradient(135deg, rgba(255,255,255,0.98), rgba(238,242,255,0.92));
        border: 1px solid #dbeafe;
        border-radius: 22px;
        padding: 24px;
        box-shadow: 0 10px 28px rgba(30,64,175,0.06);
    }

    .candidate-name {
        font-size: 24px;
        font-weight: 800;
        color: #111827;
    }

    .candidate-meta {
        color: #64748b;
        margin-top: 4px;
        font-size: 14px;
    }

    /* Skill pills */
    .skill-wrap {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 12px;
    }

    .skill-pill {
        display: inline-block;
        padding: 7px 12px;
        border-radius: 999px;
        background: #eef2ff;
        border: 1px solid #c7d2fe;
        color: #3730a3;
        font-size: 12px;
        font-weight: 650;
    }

    .skill-pill.green {
        background: #ecfdf5;
        border-color: #a7f3d0;
        color: #047857;
    }

    .skill-pill.orange {
        background: #fff7ed;
        border-color: #fed7aa;
        color: #c2410c;
    }

    /* Match cards */
    .job-card {
        background: rgba(255,255,255,0.97);
        border: 1px solid #e2e8f0;
        border-radius: 24px;
        padding: 25px;
        margin: 15px 0;
        box-shadow: 0 10px 28px rgba(15,23,42,0.055);
        transition: 0.2s ease;
    }

    .job-card:hover {
        border-color: #c7d2fe;
        box-shadow: 0 16px 35px rgba(79,70,229,0.10);
        transform: translateY(-1px);
    }

    .rank-badge {
        display: inline-block;
        padding: 5px 10px;
        border-radius: 999px;
        background: #eef2ff;
        color: #4338ca;
        font-size: 11px;
        font-weight: 800;
        letter-spacing: 0.04em;
    }

    .job-title {
        font-size: 21px;
        line-height: 1.3;
        font-weight: 800;
        color: #111827;
        margin-top: 10px;
    }

    .company-name {
        font-size: 14px;
        color: #475569;
        margin-top: 5px;
        font-weight: 600;
    }

    .match-score {
        font-size: 30px;
        line-height: 1;
        font-weight: 850;
        color: #4338ca;
        text-align: right;
    }

    .match-label {
        font-size: 11px;
        color: #64748b;
        text-align: right;
        margin-top: 5px;
        text-transform: uppercase;
        letter-spacing: 0.07em;
        font-weight: 700;
    }

    .meta-row {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin: 17px 0;
    }

    .meta-chip {
        display: inline-block;
        padding: 7px 11px;
        border-radius: 10px;
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        color: #475569;
        font-size: 12px;
        font-weight: 600;
    }

    .salary {
        color: #047857;
        font-size: 14px;
        font-weight: 800;
        margin: 12px 0;
    }

    .description {
        color: #64748b;
        font-size: 13px;
        line-height: 1.7;
        margin-top: 14px;
    }

    .score-box {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 15px;
        padding: 12px 15px;
        margin-top: 14px;
    }

    .score-row {
        display: flex;
        justify-content: space-between;
        font-size: 12px;
        color: #475569;
        margin-bottom: 7px;
    }

    .score-row strong {
        color: #111827;
    }

    /* Footer */
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
    st.html(content)


def safe_text(value, default="Unknown"):
    if value is None:
        return default

    try:
        if pd.isna(value):
            return default
    except Exception:
        pass

    text = str(value).strip()

    if not text or text.lower() in {"nan", "none", "null"}:
        return default

    return text


def safe_list(value):
    if value is None:
        return []

    if isinstance(value, (list, tuple, set)):
        return [
            str(x).strip()
            for x in value
            if str(x).strip()
        ]

    if hasattr(value, "tolist"):
        try:
            converted = value.tolist()

            if isinstance(converted, list):
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


def get_candidate_profile():
    possible_keys = [
        "resume_analysis",
        "candidate_profile",
        "resume_profile",
        "parsed_resume",
    ]

    for key in possible_keys:
        value = st.session_state.get(key)

        if isinstance(value, dict):
            return value

    return None


def extract_candidate_data(profile):

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
            "resume_text": "",
        }

    name = (
        profile.get("name")
        or profile.get("candidate_name")
        or profile.get("full_name")
        or "Candidate"
    )

    experience = (
        profile.get("experience")
        or profile.get("experience_level")
        or profile.get("years_experience")
        or "Not detected"
    )

    skills = (
        profile.get("skills")
        or profile.get("detected_skills")
        or profile.get("technical_skills")
        or []
    )

    resume_text = (
        profile.get("text")
        or profile.get("resume_text")
        or profile.get("extracted_text")
        or ""
    )

    return {
        "name": safe_text(name, "Candidate"),
        "experience": safe_text(experience, "Not detected"),
        "skills": safe_list(skills),
        "resume_text": safe_text(resume_text, ""),
    }


@st.cache_data(show_spinner=False)
def load_jobs():

    if not JOBS_PATH.exists():
        return pd.DataFrame()

    try:
        return pd.read_parquet(JOBS_PATH)
    except Exception:
        return pd.DataFrame()


@st.cache_data(show_spinner=False)
def load_skill_data():

    if not SKILLS_PATH.exists():
        return pd.DataFrame()

    try:
        return pd.read_parquet(SKILLS_PATH)
    except Exception:
        return pd.DataFrame()


def get_job_skills(skill_df, job_index):

    if skill_df.empty:
        return []

    if "job_index" in skill_df.columns:

        rows = skill_df[
            skill_df["job_index"].astype(str)
            == str(job_index)
        ]

        if not rows.empty:

            for column in [
                "skills",
                "normalized_skills",
            ]:

                if column in rows.columns:

                    values = []

                    for value in rows[column]:
                        values.extend(
                            safe_list(value)
                        )

                    return list(
                        dict.fromkeys(values)
                    )

    if "skills" in skill_df.columns:

        try:
            row = skill_df.loc[job_index]

            if isinstance(row, pd.Series):
                return safe_list(
                    row.get("skills")
                )

        except Exception:
            pass

    return []


def calculate_skill_match(
    candidate_skills,
    job_skills,
):

    candidate_set = {
        normalize_skill(skill)
        for skill in candidate_skills
        if normalize_skill(skill)
    }

    job_set = {
        normalize_skill(skill)
        for skill in job_skills
        if normalize_skill(skill)
    }

    if not job_set:
        return 0.0, [], []

    matched = sorted(
        candidate_set.intersection(job_set)
    )

    missing = sorted(
        job_set.difference(candidate_set)
    )

    score = (
        len(matched)
        / len(job_set)
    ) * 100

    return score, matched, missing


def text_similarity_score(
    candidate_text,
    job_row,
):

    if not candidate_text:
        return 0.0

    candidate_words = {
        word.lower()
        for word in candidate_text.split()
        if len(word) > 2
    }

    if not candidate_words:
        return 0.0

    fields = [
        "title",
        "normalized_title",
        "job_description",
        "responsibilities",
        "minimum_qualifications",
        "preferred_qualifications",
    ]

    job_text_parts = []

    for field in fields:

        if field in job_row.index:

            value = safe_text(
                job_row[field],
                "",
            )

            if value:
                job_text_parts.append(value)

    job_words = {
        word.lower()
        for word in " ".join(
            job_text_parts
        ).split()
        if len(word) > 2
    }

    if not job_words:
        return 0.0

    overlap = len(
        candidate_words.intersection(
            job_words
        )
    )

    return min(
        100.0,
        (
            overlap
            / max(len(candidate_words), 1)
        ) * 100,
    )


def calculate_matches(
    jobs,
    skill_df,
    candidate,
):

    if jobs.empty:
        return pd.DataFrame()

    candidate_skills = candidate["skills"]

    candidate_text = (
        " ".join(candidate_skills)
        + " "
        + candidate["experience"]
        + " "
        + candidate["resume_text"]
    )

    semantic_results = None

    try:

        from src.matching.semantic_matcher import (
            semantic_match,
        )

        query_text = candidate_text.strip()

        if query_text:

            semantic_results = semantic_match(
                query_text,
                top_k=min(100, len(jobs)),
            )

    except Exception:
        semantic_results = None

    results = []

    if (
        isinstance(
            semantic_results,
            pd.DataFrame,
        )
        and not semantic_results.empty
    ):

        for index, row in semantic_results.iterrows():

            job_index = index

            title = safe_text(
                row.get("title"),
                "Untitled Job",
            )

            company = safe_text(
                row.get("company_name"),
                "Unknown Company",
            )

            job_skills = get_job_skills(
                skill_df,
                job_index,
            )

            skill_score, matched, missing = (
                calculate_skill_match(
                    candidate_skills,
                    job_skills,
                )
            )

            try:
                semantic_score = (
                    float(
                        row.get(
                            "similarity_score",
                            0,
                        )
                    )
                    * 100
                )
            except Exception:
                semantic_score = 0.0

            if job_skills:

                final_score = (
                    semantic_score * 0.65
                    + skill_score * 0.35
                )

            else:
                final_score = semantic_score

            results.append(
                {
                    "job_index": job_index,
                    "title": title,
                    "company": company,
                    "country": safe_text(
                        row.get("country")
                    ),
                    "work_model": safe_text(
                        row.get("work_model")
                    ),
                    "experience_level": safe_text(
                        row.get(
                            "experience_level"
                        )
                    ),
                    "employment_type": safe_text(
                        row.get(
                            "employment_type"
                        )
                    ),
                    "salary_min": row.get(
                        "salary_min"
                    ),
                    "salary_max": row.get(
                        "salary_max"
                    ),
                    "date_posted": row.get(
                        "date_posted"
                    ),
                    "semantic_score": semantic_score,
                    "skill_score": skill_score,
                    "match_score": final_score,
                    "matched_skills": matched,
                    "missing_skills": missing,
                    "description": safe_text(
                        row.get(
                            "job_description"
                        ),
                        "",
                    ),
                }
            )

    else:

        sample_jobs = jobs.head(
            min(5000, len(jobs))
        )

        for job_index, job_row in (
            sample_jobs.iterrows()
        ):

            job_skills = get_job_skills(
                skill_df,
                job_index,
            )

            skill_score, matched, missing = (
                calculate_skill_match(
                    candidate_skills,
                    job_skills,
                )
            )

            relevance = text_similarity_score(
                candidate_text,
                job_row,
            )

            if job_skills:

                final_score = (
                    relevance * 0.65
                    + skill_score * 0.35
                )

            else:
                final_score = relevance

            results.append(
                {
                    "job_index": job_index,
                    "title": safe_text(
                        job_row.get("title"),
                        "Untitled Job",
                    ),
                    "company": safe_text(
                        job_row.get(
                            "company_name"
                        ),
                        "Unknown Company",
                    ),
                    "country": safe_text(
                        job_row.get("country")
                    ),
                    "work_model": safe_text(
                        job_row.get(
                            "work_model"
                        )
                    ),
                    "experience_level": safe_text(
                        job_row.get(
                            "experience_level"
                        )
                    ),
                    "employment_type": safe_text(
                        job_row.get(
                            "employment_type"
                        )
                    ),
                    "salary_min": job_row.get(
                        "salary_min"
                    ),
                    "salary_max": job_row.get(
                        "salary_max"
                    ),
                    "date_posted": job_row.get(
                        "date_posted"
                    ),
                    "semantic_score": relevance,
                    "skill_score": skill_score,
                    "match_score": final_score,
                    "matched_skills": matched,
                    "missing_skills": missing,
                    "description": safe_text(
                        job_row.get(
                            "job_description"
                        ),
                        "",
                    ),
                }
            )

    if not results:
        return pd.DataFrame()

    result_df = pd.DataFrame(results)

    result_df = (
        result_df
        .sort_values(
            "match_score",
            ascending=False,
        )
        .drop_duplicates(
            subset=["job_index"]
        )
        .reset_index(drop=True)
    )

    return result_df


def format_salary(
    min_salary,
    max_salary,
):

    try:
        min_value = float(min_salary)
    except Exception:
        min_value = None

    try:
        max_value = float(max_salary)
    except Exception:
        max_value = None

    if (
        min_value is None
        and max_value is None
    ):
        return "Salary not available"

    if (
        min_value is not None
        and min_value > 0
        and max_value is not None
        and max_value > 0
    ):
        return (
            f"${min_value:,.0f} – "
            f"${max_value:,.0f}"
        )

    if (
        min_value is not None
        and min_value > 0
    ):
        return f"${min_value:,.0f}+"

    if (
        max_value is not None
        and max_value > 0
    ):
        return f"Up to ${max_value:,.0f}"

    return "Salary not available"


def skill_pills_html(
    skills,
    css_class="",
):

    skills = safe_list(skills)

    if not skills:
        return (
            '<span style="color:#94a3b8;'
            'font-size:12px;">None detected</span>'
        )

    output = ""

    for skill in skills[:18]:

        output += (
            f'<span class="skill-pill {css_class}">'
            f'{html.escape(str(skill))}'
            f'</span>'
        )

    if len(skills) > 18:

        output += (
            f'<span class="skill-pill">'
            f'+{len(skills) - 18} more'
            f'</span>'
        )

    return output


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
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
                🎯
            </div>

            <div style="
                margin-top:12px;
                font-size:18px;
                font-weight:800;
            ">
                Job Matcher
            </div>

            <div style="
                margin-top:5px;
                font-size:12px;
                opacity:.70;
            ">
                Intelligent job matching
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

    st.markdown(
        """
        <div style="
            margin-top:25px;
            padding:15px;
            border-radius:16px;
            background:rgba(255,255,255,.07);
            border:1px solid rgba(255,255,255,.08);
            font-size:11px;
            line-height:1.6;
            color:#cbd5e1;
        ">
            <b>Matching pipeline</b><br><br>
            Resume → Semantic Similarity →
            Skill Coverage → Combined Match
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# HERO
# ============================================================

render_html(
    """
    <div class="hero">

        <div class="hero-orb-one"></div>
        <div class="hero-orb-two"></div>

        <div class="hero-kicker">
            JOBINSIGHT · INTELLIGENT MATCHING
        </div>

        <div class="hero-title">
            Find jobs that match your profile.
        </div>

        <div class="hero-subtitle">
            Compare your resume with the job market using
            semantic relevance and normalized skill coverage.
            Explore where your profile aligns and where you
            can strengthen your skills.
        </div>

    </div>
    """
)


# ============================================================
# LOAD CANDIDATE
# ============================================================

profile = get_candidate_profile()

candidate = extract_candidate_data(profile)


# ============================================================
# CANDIDATE PROFILE
# ============================================================

render_html(
    """
    <div class="section-title">
        👤 Candidate Profile
    </div>

    <div class="section-subtitle">
        Your current resume profile is used as the matching query.
    </div>
    """
)

resume_words = len(
    candidate["resume_text"].split()
)

candidate_name = html.escape(
    candidate["name"]
)

candidate_experience = html.escape(
    candidate["experience"]
)

render_html(
    f"""
    <div class="candidate-card">

        <div class="candidate-name">
            {candidate_name}
        </div>

        <div class="candidate-meta">
            Experience: {candidate_experience}
            &nbsp; • &nbsp;
            {len(candidate["skills"])} detected skills
            &nbsp; • &nbsp;
            {resume_words:,} resume words
        </div>

        <div style="
            margin-top:18px;
            font-size:12px;
            font-weight:800;
            color:#475569;
            text-transform:uppercase;
            letter-spacing:.07em;
        ">
            Your skills
        </div>

        <div class="skill-wrap">
            {skill_pills_html(candidate["skills"])}
        </div>

    </div>
    """
)


# ============================================================
# LOAD DATA
# ============================================================

jobs = load_jobs()

skill_df = load_skill_data()

if jobs.empty:

    st.error(
        f"Job dataset could not be loaded from:\n\n"
        f"{JOBS_PATH}"
    )

    st.stop()


# ============================================================
# MATCH SETTINGS
# ============================================================

render_html(
    """
    <div class="section-title">
        ⚙️ Match Settings
    </div>

    <div class="section-subtitle">
        Adjust the results shown below without changing
        the underlying matching model.
    </div>
    """
)

settings_col1, settings_col2, settings_col3 = (
    st.columns(3)
)

with settings_col1:

    jobs_to_display = st.slider(
        "Jobs to display",
        min_value=5,
        max_value=25,
        value=10,
        step=5,
    )

with settings_col2:

    minimum_score = st.slider(
        "Minimum match score",
        min_value=0,
        max_value=100,
        value=30,
        step=5,
    )

with settings_col3:

    available_models = ["All"]

    if "work_model" in jobs.columns:

        model_values = (
            jobs["work_model"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        model_values = sorted(
            [
                x
                for x in model_values
                if x.strip()
                and x.lower() != "unknown"
            ]
        )

        available_models.extend(
            model_values
        )

    selected_work_model = st.selectbox(
        "Work model",
        available_models,
    )


# ============================================================
# GENERATE MATCHES
# ============================================================

cache_key = (
    "job_matcher_results",
    candidate["name"],
    tuple(sorted(candidate["skills"])),
    candidate["experience"],
)

if (
    "job_matcher_cache_key" not in st.session_state
    or st.session_state[
        "job_matcher_cache_key"
    ] != cache_key
):

    with st.spinner(
        "Analyzing your profile against the job market..."
    ):

        matches = calculate_matches(
            jobs,
            skill_df,
            candidate,
        )

    st.session_state[
        "job_matcher_results"
    ] = matches

    st.session_state[
        "job_matcher_cache_key"
    ] = cache_key

else:

    matches = st.session_state.get(
        "job_matcher_results",
        pd.DataFrame(),
    )


if matches.empty:

    st.warning(
        "No matching jobs could be generated. "
        "Please analyze a resume first."
    )

    st.stop()


# ============================================================
# FILTER RESULTS
# ============================================================

filtered_matches = matches[
    matches["match_score"]
    >= minimum_score
].copy()

if selected_work_model != "All":

    filtered_matches = filtered_matches[
        filtered_matches["work_model"]
        == selected_work_model
    ].copy()

filtered_matches = (
    filtered_matches
    .sort_values(
        "match_score",
        ascending=False,
    )
    .head(jobs_to_display)
    .reset_index(drop=True)
)


# ============================================================
# MATCHING OVERVIEW
# ============================================================

render_html(
    """
    <div class="section-title">
        📊 Matching Overview
    </div>
    """
)

overview_col1, overview_col2, overview_col3, overview_col4 = (
    st.columns(4)
)

if not filtered_matches.empty:

    average_match = (
        filtered_matches["match_score"].mean()
    )

    best_match = (
        filtered_matches["match_score"].max()
    )

else:

    average_match = 0
    best_match = 0


with overview_col1:

    render_html(
        f"""
        <div class="kpi-card">
            <div class="kpi-icon">🗂️</div>
            <div class="kpi-label">Jobs Evaluated</div>
            <div class="kpi-value">
                {len(jobs):,}
            </div>
        </div>
        """
    )


with overview_col2:

    render_html(
        f"""
        <div class="kpi-card">
            <div class="kpi-icon">🎯</div>
            <div class="kpi-label">Matches Found</div>
            <div class="kpi-value">
                {len(filtered_matches):,}
            </div>
        </div>
        """
    )


with overview_col3:

    render_html(
        f"""
        <div class="kpi-card">
            <div class="kpi-icon">📈</div>
            <div class="kpi-label">Average Match</div>
            <div class="kpi-value">
                {average_match:.1f}%
            </div>
        </div>
        """
    )


with overview_col4:

    render_html(
        f"""
        <div class="kpi-card">
            <div class="kpi-icon">🏆</div>
            <div class="kpi-label">Best Match</div>
            <div class="kpi-value">
                {best_match:.1f}%
            </div>
        </div>
        """
    )


# ============================================================
# MATCHING CHART
# ============================================================

if not filtered_matches.empty:

    render_html(
        """
        <div class="section-title">
            📈 Top Matching Jobs
        </div>

        <div class="section-subtitle">
            Combined score = 65% semantic relevance
            + 35% skill coverage when job skills are available.
        </div>
        """
    )

    chart_df = filtered_matches.copy()

    chart_df["display_title"] = (
        chart_df["title"]
        + " — "
        + chart_df["company"]
    )

    chart_df = chart_df.sort_values(
        "match_score",
        ascending=True,
    )

    fig = px.bar(
        chart_df,
        x="match_score",
        y="display_title",
        orientation="h",
        text="match_score",
        labels={
            "match_score": "Match Score (%)",
            "display_title": "Job",
        },
    )

    fig.update_traces(
        texttemplate="%{text:.1f}%",
        textposition="outside",
    )

    fig.update_layout(
        height=max(
            450,
            len(chart_df) * 65,
        ),
        margin=dict(
            l=20,
            r=80,
            t=20,
            b=20,
        ),
        xaxis=dict(
            range=[
                0,
                min(
                    100,
                    max(
                        100,
                        chart_df[
                            "match_score"
                        ].max()
                        + 10,
                    ),
                ),
            ]
        ),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )


# ============================================================
# JOB MATCH CARDS
# ============================================================

render_html(
    """
    <div class="section-title">
        💼 Recommended Job Matches
    </div>

    <div class="section-subtitle">
        Each card shows the signals contributing to the
        matching result and the skills that may need development.
    </div>
    """
)


if filtered_matches.empty:

    st.info(
        "No jobs meet the selected minimum match score."
    )

else:

    for rank, (_, row) in enumerate(
        filtered_matches.iterrows(),
        start=1,
    ):

        title = safe_text(
            row.get("title"),
            "Untitled Job",
        )

        company = safe_text(
            row.get("company"),
            "Unknown Company",
        )

        try:
            match_score = float(
                row.get(
                    "match_score",
                    0,
                )
            )
        except Exception:
            match_score = 0

        try:
            semantic_score = float(
                row.get(
                    "semantic_score",
                    0,
                )
            )
        except Exception:
            semantic_score = 0

        try:
            skill_score = float(
                row.get(
                    "skill_score",
                    0,
                )
            )
        except Exception:
            skill_score = 0

        country = safe_text(
            row.get("country"),
            "Unknown",
        )

        work_model = safe_text(
            row.get("work_model"),
            "Unknown",
        )

        experience_level = safe_text(
            row.get(
                "experience_level"
            ),
            "Unknown",
        )

        employment_type = safe_text(
            row.get(
                "employment_type"
            ),
            "Unknown",
        )

        salary = format_salary(
            row.get("salary_min"),
            row.get("salary_max"),
        )

        description = safe_text(
            row.get("description"),
            "",
        )

        if len(description) > 500:
            description = (
                description[:500]
                + "..."
            )

        matched_skills = safe_list(
            row.get(
                "matched_skills",
                [],
            )
        )

        missing_skills = safe_list(
            row.get(
                "missing_skills",
                [],
            )
        )

        safe_title = html.escape(title)
        safe_company = html.escape(company)
        safe_country = html.escape(country)
        safe_work_model = html.escape(
            work_model
        )
        safe_experience = html.escape(
            experience_level
        )
        safe_employment = html.escape(
            employment_type
        )
        safe_salary = html.escape(salary)
        safe_description = html.escape(
            description
        )

        render_html(
            f"""
            <div class="job-card">

                <div style="
                    display:flex;
                    justify-content:space-between;
                    gap:25px;
                ">

                    <div style="flex:1;">

                        <span class="rank-badge">
                            #{rank} MATCH
                        </span>

                        <div class="job-title">
                            {safe_title}
                        </div>

                        <div class="company-name">
                            🏢 {safe_company}
                        </div>

                    </div>

                    <div style="
                        min-width:105px;
                    ">

                        <div class="match-score">
                            {match_score:.1f}%
                        </div>

                        <div class="match-label">
                            Match Score
                        </div>

                    </div>

                </div>

                <div class="meta-row">

                    <span class="meta-chip">
                        🌍 {safe_country}
                    </span>

                    <span class="meta-chip">
                        💼 {safe_work_model}
                    </span>

                    <span class="meta-chip">
                        🎯 {safe_experience}
                    </span>

                    <span class="meta-chip">
                        📄 {safe_employment}
                    </span>

                </div>

                <div class="salary">
                    💰 {safe_salary} / year
                </div>

                <div style="
                    height:8px;
                    border-radius:999px;
                    background:#e2e8f0;
                    overflow:hidden;
                    margin:14px 0;
                ">

                    <div style="
                        width:{max(
                            0,
                            min(
                                100,
                                match_score
                            )
                        )}%;
                        height:100%;
                        border-radius:999px;
                        background:
                            linear-gradient(
                                90deg,
                                #6366f1,
                                #38bdf8
                            );
                    "></div>

                </div>

                <div class="score-box">

                    <div class="score-row">
                        <span>
                            Semantic relevance
                        </span>

                        <strong>
                            {semantic_score:.1f}%
                        </strong>
                    </div>

                    <div style="
                        height:5px;
                        background:#e2e8f0;
                        border-radius:99px;
                        overflow:hidden;
                    ">
                        <div style="
                            width:{max(
                                0,
                                min(
                                    100,
                                    semantic_score
                                )
                            )}%;
                            height:100%;
                            background:#818cf8;
                        "></div>
                    </div>

                    <div class="score-row"
                         style="margin-top:12px;">
                        <span>
                            Skill coverage
                        </span>

                        <strong>
                            {skill_score:.1f}%
                        </strong>
                    </div>

                    <div style="
                        height:5px;
                        background:#e2e8f0;
                        border-radius:99px;
                        overflow:hidden;
                    ">
                        <div style="
                            width:{max(
                                0,
                                min(
                                    100,
                                    skill_score
                                )
                            )}%;
                            height:100%;
                            background:#34d399;
                        "></div>
                    </div>

                </div>

                <div style="
                    margin-top:18px;
                    font-size:12px;
                    font-weight:800;
                    color:#047857;
                    text-transform:uppercase;
                    letter-spacing:.06em;
                ">
                    ✅ Matched Skills
                </div>

                <div class="skill-wrap">
                    {skill_pills_html(
                        matched_skills,
                        "green",
                    )}
                </div>

                <div style="
                    margin-top:18px;
                    font-size:12px;
                    font-weight:800;
                    color:#c2410c;
                    text-transform:uppercase;
                    letter-spacing:.06em;
                ">
                    📌 Skills to Develop
                </div>

                <div class="skill-wrap">
                    {skill_pills_html(
                        missing_skills,
                        "orange",
                    )}
                </div>

                {
                    f'''
                    <div class="description">
                        {safe_description}
                    </div>
                    '''
                    if description
                    else ""
                }

            </div>
            """
        )

        with st.expander(
            "🔎 View matching details"
        ):

            detail_col1, detail_col2 = (
                st.columns(2)
            )

            with detail_col1:

                st.markdown(
                    "### Matching Signals"
                )

                st.write(
                    f"**Semantic relevance:** "
                    f"{semantic_score:.2f}%"
                )

                st.write(
                    f"**Skill coverage:** "
                    f"{skill_score:.2f}%"
                )

                st.write(
                    f"**Combined match:** "
                    f"{match_score:.2f}%"
                )

            with detail_col2:

                st.markdown(
                    "### Job Information"
                )

                st.write(
                    f"**Country:** {country}"
                )

                st.write(
                    f"**Work model:** "
                    f"{work_model}"
                )

                st.write(
                    f"**Experience:** "
                    f"{experience_level}"
                )

                st.write(
                    f"**Employment:** "
                    f"{employment_type}"
                )


# ============================================================
# METHODOLOGY
# ============================================================

st.markdown("<br>", unsafe_allow_html=True)

with st.expander(
    "🧠 How JobInsight calculates the match"
):

    st.markdown(
        """
        ### Matching methodology

        JobInsight combines multiple signals rather than
        relying on a single keyword search.

        **1. Semantic relevance**

        Resume/job text is represented using the project's
        Sentence Transformer embedding model. This captures
        contextual similarity between the candidate profile
        and job descriptions.

        **2. Skill coverage**

        Candidate skills are compared with normalized skills
        associated with each job.

        **3. Combined match score**

        When job skills are available:

        **65% semantic relevance + 35% skill coverage**

        When explicit job skills are unavailable, semantic
        relevance is used.

        The resulting score is a matching signal for
        exploration. It is not a hiring probability or
        guarantee of suitability.
        """
    )


# ============================================================
# DATA STATUS
# ============================================================

with st.expander(
    "ℹ️ Data and model status"
):

    st.write(
        f"**Jobs dataset:** {JOBS_PATH}"
    )

    st.write(
        f"**Skill dataset:** {SKILLS_PATH}"
    )

    st.write(
        f"**Embedding artifact:** "
        f"{EMBEDDINGS_PATH}"
    )

    st.write(
        f"**Jobs loaded:** "
        f"{len(jobs):,}"
    )

    if not skill_df.empty:

        st.write(
            f"**Skill records loaded:** "
            f"{len(skill_df):,}"
        )

    else:

        st.write(
            "Skill records: unavailable"
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
        Semantic matching · Skill intelligence ·
        Explainable career insights
    </div>
    """
)