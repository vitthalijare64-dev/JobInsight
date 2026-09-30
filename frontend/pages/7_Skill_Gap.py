from pathlib import Path
import sys

import pandas as pd
import streamlit as st
import plotly.express as px


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

SKILLS_PATH = PROCESSED_DIR / "job_skills_normalized.parquet"
SKILL_DEMAND_PATH = PROCESSED_DIR / "skill_demand.csv"


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="JobInsight - Skill Gap",
    page_icon="🧩",
    layout="wide",
)


# ============================================================
# HELPERS
# ============================================================

def safe_text(value, default="Unknown"):
    if value is None:
        return default

    try:
        if pd.isna(value):
            return default
    except Exception:
        pass

    text = str(value).strip()

    if not text or text.lower() in {
        "nan",
        "none",
        "null",
    }:
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


def display_skill_chips(
    skills,
    background="#eef2ff",
    text_color="#243b8f",
):
    if not skills:
        st.caption("None detected.")
        return

    cols = st.columns(
        min(6, max(1, len(skills)))
    )

    for index, skill in enumerate(skills):
        with cols[index % len(cols)]:
            st.markdown(
                f"""
                <div style="
                    background:{background};
                    color:{text_color};
                    border-radius:18px;
                    padding:7px 12px;
                    margin:4px 0;
                    text-align:center;
                    font-size:14px;
                    font-weight:500;
                ">
                    {skill}
                </div>
                """,
                unsafe_allow_html=True,
            )


def get_candidate_profile():
    keys = [
        "resume_analysis",
        "candidate_profile",
        "resume_profile",
        "parsed_resume",
    ]

    for key in keys:
        value = st.session_state.get(key)

        if isinstance(value, dict):
            return value

    return None


def extract_candidate(profile):
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

    return {
        "name": safe_text(
            name,
            "Candidate",
        ),
        "experience": safe_text(
            experience,
            "Not detected",
        ),
        "skills": safe_list(skills),
    }


def load_skill_data():
    if not SKILLS_PATH.exists():
        return pd.DataFrame()

    try:
        return pd.read_parquet(SKILLS_PATH)
    except Exception:
        return pd.DataFrame()


def load_skill_demand():
    if not SKILL_DEMAND_PATH.exists():
        return pd.DataFrame()

    try:
        return pd.read_csv(SKILL_DEMAND_PATH)
    except Exception:
        return pd.DataFrame()


def get_job_skills(skill_df, job_index):
    if skill_df.empty:
        return []

    # --------------------------------------------------------
    # job_index schema
    # --------------------------------------------------------

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

                    skills = []

                    for value in rows[column]:
                        skills.extend(
                            safe_list(value)
                        )

                    return list(
                        dict.fromkeys(skills)
                    )

    # --------------------------------------------------------
    # Original index schema
    # --------------------------------------------------------

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


def calculate_gap(candidate_skills, job_skills):
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

    matched_normalized = (
        candidate_set.intersection(job_set)
    )

    missing_normalized = (
        job_set.difference(candidate_set)
    )

    # Preserve readable names
    candidate_lookup = {
        normalize_skill(skill): skill
        for skill in candidate_skills
    }

    job_lookup = {
        normalize_skill(skill): skill
        for skill in job_skills
    }

    matched = sorted(
        [
            candidate_lookup.get(
                skill,
                skill,
            )
            for skill in matched_normalized
        ]
    )

    missing = sorted(
        [
            job_lookup.get(
                skill,
                skill,
            )
            for skill in missing_normalized
        ]
    )

    score = (
        len(matched_normalized)
        / len(job_set)
    ) * 100

    return score, matched, missing


def get_market_demand(skill_demand):
    if skill_demand.empty:
        return {}

    # Find likely skill column
    skill_column = None

    for column in [
        "skill",
        "Skill",
        "skills",
    ]:

        if column in skill_demand.columns:
            skill_column = column
            break

    if skill_column is None:
        return {}

    # Find likely demand/count column
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
            row.get(skill_column),
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
# HEADER
# ============================================================

st.title("🧩 Skill Gap Analysis")

st.markdown(
    """
    Identify the skills you already have, the skills required by
    target jobs, and the capabilities you may want to develop
    to improve your job-market alignment.
    """
)

st.divider()


# ============================================================
# CANDIDATE
# ============================================================

profile = get_candidate_profile()
candidate = extract_candidate(profile)

candidate_skills = candidate["skills"]


st.header("👤 Candidate Profile")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Candidate",
        candidate["name"],
    )

with col2:
    st.metric(
        "Experience",
        candidate["experience"],
    )

with col3:
    st.metric(
        "Detected Skills",
        len(candidate_skills),
    )


st.subheader("🧠 Your Current Skills")

display_skill_chips(
    candidate_skills
)

st.divider()


# ============================================================
# LOAD DATA
# ============================================================

skill_df = load_skill_data()
skill_demand = load_skill_demand()

market_demand = get_market_demand(
    skill_demand
)


# ============================================================
# GET JOB MATCHES
# ============================================================

matches = st.session_state.get(
    "job_matcher_results",
    pd.DataFrame(),
)


# ============================================================
# JOB SELECTION
# ============================================================

st.header("🎯 Target Job")

if (
    isinstance(matches, pd.DataFrame)
    and not matches.empty
):

    display_matches = matches.copy()

    display_matches = (
        display_matches
        .sort_values(
            "match_score",
            ascending=False,
        )
        .reset_index(drop=True)
    )

    job_options = []

    for index, row in display_matches.iterrows():

        title = safe_text(
            row.get(
                "title"
            ),
            "Untitled Job",
        )

        company = safe_text(
            row.get(
                "company"
            ),
            "Unknown Company",
        )

        score = float(
            row.get(
                "match_score",
                0,
            )
        )

        job_options.append(
            f"{index + 1}. "
            f"{title} — "
            f"{company} "
            f"({score:.1f}% match)"
        )

    selected_label = st.selectbox(
        "Select a matched job to analyze",
        job_options,
    )

    selected_position = job_options.index(
        selected_label
    )

    selected_job = display_matches.iloc[
        selected_position
    ]

    selected_job_index = selected_job.get(
        "job_index"
    )

    selected_title = safe_text(
        selected_job.get(
            "title"
        ),
        "Untitled Job",
    )

    selected_company = safe_text(
        selected_job.get(
            "company"
        ),
        "Unknown Company",
    )

    selected_match = float(
        selected_job.get(
            "match_score",
            0,
        )
    )

else:

    st.info(
        """
        No Job Matcher results are currently available.

        You can still use the market-level skill-gap analysis below,
        or go to **Job Matcher** after analyzing your resume.
        """
    )

    selected_job = None
    selected_job_index = None
    selected_title = None
    selected_company = None
    selected_match = 0


# ============================================================
# JOB-SPECIFIC GAP
# ============================================================

if selected_job is not None:

    st.divider()

    st.header("🔍 Job-Specific Skill Gap")

    job_skills = get_job_skills(
        skill_df,
        selected_job_index,
    )

    if not job_skills:

        # Try skill information already stored
        # by Job Matcher.
        job_skills = (
            safe_list(
                selected_job.get(
                    "matched_skills",
                    [],
                )
            )
            + safe_list(
                selected_job.get(
                    "missing_skills",
                    [],
                )
            )
        )

    gap_score, matched, missing = calculate_gap(
        candidate_skills,
        job_skills,
    )

    # --------------------------------------------------------
    # JOB SUMMARY
    # --------------------------------------------------------

    job_col1, job_col2, job_col3 = st.columns(3)

    with job_col1:
        st.metric(
            "Job",
            selected_title,
        )

    with job_col2:
        st.metric(
            "Company",
            selected_company,
        )

    with job_col3:
        st.metric(
            "Current Skill Coverage",
            f"{gap_score:.1f}%",
        )

    # --------------------------------------------------------
    # PROGRESS
    # --------------------------------------------------------

    st.progress(
        min(
            max(gap_score / 100, 0),
            1,
        )
    )

    # --------------------------------------------------------
    # MATCHED / MISSING
    # --------------------------------------------------------

    matched_col, missing_col = st.columns(2)

    with matched_col:

        st.subheader(
            "✅ Skills You Have"
        )

        if matched:
            display_skill_chips(
                matched,
                background="#e8f7ee",
                text_color="#176b3a",
            )
        else:
            st.info(
                "No overlapping skills detected."
            )

    with missing_col:

        st.subheader(
            "📌 Skills to Develop"
        )

        if missing:
            display_skill_chips(
                missing,
                background="#fff1f1",
                text_color="#a62a2a",
            )
        else:
            st.success(
                "No missing skills detected "
                "for this job's extracted skill set."
            )


# ============================================================
# MARKET-LEVEL GAP
# ============================================================

st.divider()

st.header("🌎 Market-Level Skill Gap")

st.markdown(
    """
    This section compares your current skills with the skills
    appearing most frequently across the JobInsight job market.
    """
)


# ============================================================
# TOP MARKET SKILLS
# ============================================================

market_skills = []

if not skill_demand.empty:

    skill_column = None

    for column in [
        "skill",
        "Skill",
        "skills",
    ]:

        if column in skill_demand.columns:
            skill_column = column
            break

    if skill_column:

        market_skills = (
            skill_demand[
                skill_column
            ]
            .dropna()
            .astype(str)
            .tolist()
        )

        # Remove duplicates while preserving order
        market_skills = list(
            dict.fromkeys(
                market_skills
            )
        )


# Fallback from existing market skills
if not market_skills:

    market_skills = [
        "Microsoft Excel",
        "Project Management",
        "Data Analysis",
        "Python",
        "SQL",
        "Agile",
        "AWS",
        "Microsoft Azure",
        "API",
        "Java",
    ]


# Top 15
market_skills = market_skills[:15]


market_gap_score, market_matched, market_missing = calculate_gap(
    candidate_skills,
    market_skills,
)


market_col1, market_col2, market_col3 = st.columns(3)

with market_col1:
    st.metric(
        "Market Skills Considered",
        len(market_skills),
    )

with market_col2:
    st.metric(
        "Skills Already Covered",
        len(market_matched),
    )

with market_col3:
    st.metric(
        "Market Skills Missing",
        len(market_missing),
    )


st.progress(
    min(
        max(market_gap_score / 100, 0),
        1,
    )
)

st.caption(
    f"Coverage of the selected top market skills: "
    f"{market_gap_score:.1f}%"
)


# ============================================================
# MARKET SKILL VISUALIZATION
# ============================================================

if market_skills:

    visualization_rows = []

    candidate_normalized = {
        normalize_skill(skill)
        for skill in candidate_skills
    }

    for skill in market_skills:

        normalized = normalize_skill(
            skill
        )

        demand_value = market_demand.get(
            normalized,
            0,
        )

        visualization_rows.append(
            {
                "Skill": skill,
                "Demand": demand_value,
                "Status": (
                    "Have"
                    if normalized
                    in candidate_normalized
                    else "Gap"
                ),
            }
        )

    visualization_df = pd.DataFrame(
        visualization_rows
    )

    if visualization_df["Demand"].sum() > 0:

        st.subheader(
            "📊 Market Skills and Your Coverage"
        )

        fig = px.bar(
            visualization_df,
            x="Demand",
            y="Skill",
            color="Status",
            orientation="h",
            labels={
                "Demand": "Job Demand",
                "Skill": "Skill",
            },
        )

        fig.update_layout(
            height=550,
            margin=dict(
                l=20,
                r=30,
                t=20,
                b=20,
            ),
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )


# ============================================================
# PRIORITY SKILL GAPS
# ============================================================

st.header("🚀 Priority Skill Gaps")

if market_missing:

    priority_rows = []

    for skill in market_missing:

        demand = market_demand.get(
            normalize_skill(skill),
            0,
        )

        priority_rows.append(
            {
                "Skill": skill,
                "Market Demand": demand,
            }
        )

    priority_df = pd.DataFrame(
        priority_rows
    )

    if not priority_df.empty:

        priority_df = (
            priority_df
            .sort_values(
                "Market Demand",
                ascending=False,
            )
            .reset_index(drop=True)
        )

        # Add priority rank
        priority_df.insert(
            0,
            "Priority",
            range(
                1,
                len(priority_df) + 1,
            ),
        )

        st.dataframe(
            priority_df,
            use_container_width=True,
            hide_index=True,
        )

else:

    st.success(
        "Your current skills cover the selected "
        "top market skills."
    )


# ============================================================
# DEVELOPMENT PLAN
# ============================================================

st.divider()

st.header("🗺️ Suggested Development Path")

if market_missing:

    top_priority = market_missing[:5]

    for index, skill in enumerate(
        top_priority,
        start=1,
    ):

        demand = market_demand.get(
            normalize_skill(skill),
            0,
        )

        if demand > 0:
            demand_text = (
                f"{demand:,.0f} observed "
                f"job records"
            )
        else:
            demand_text = (
                "Demand data unavailable"
            )

        st.markdown(
            f"""
            **{index}. {skill}**

            Focus on building practical capability in
            **{skill}**. Current JobInsight market data
            contains approximately **{demand_text}**
            associated with this skill.
            """
        )

else:

    st.info(
        "No immediate market-level skill gaps were identified."
    )


# ============================================================
# METHODOLOGY
# ============================================================

with st.expander(
    "🧠 How Skill Gap Analysis works"
):

    st.markdown(
        """
        ### Skill Gap Methodology

        JobInsight uses the normalized skill vocabulary produced
        by the NLP pipeline.

        **Candidate skills**

        Skills are extracted from the uploaded resume and
        normalized before comparison.

        **Job-specific gap**

        Candidate skills are compared against the skills extracted
        for the selected job.

        **Market-level gap**

        Candidate skills are compared against frequently detected
        skills in the JobInsight job market.

        **Coverage**

        Skill coverage is calculated as:

        `matched required skills / total required skills × 100`

        The result is an analytical signal intended to help
        candidates understand skill alignment. It is not a
        guarantee of employment or hiring outcome.
        """
    )


# ============================================================
# DATA STATUS
# ============================================================

with st.expander(
    "ℹ️ Data sources"
):

    st.write(
        f"**Job-skill dataset:** {SKILLS_PATH}"
    )

    st.write(
        f"**Skill-demand dataset:** "
        f"{SKILL_DEMAND_PATH}"
    )

    st.write(
        f"**Normalized skill records:** "
        f"{len(skill_df):,}"
        if not skill_df.empty
        else "Unavailable"
    )

    st.write(
        f"**Market skills available:** "
        f"{len(market_skills):,}"
    )