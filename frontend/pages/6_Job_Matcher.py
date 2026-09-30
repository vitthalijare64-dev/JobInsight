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

EMBEDDINGS_PATH = PROJECT_ROOT / "models" / "matching" / "job_embeddings.parquet"


# ============================================================
# HELPERS
# ============================================================

def safe_text(value, default="Unknown"):
    """Convert dataframe values safely to displayable text."""
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
    """Convert skill values into a clean Python list."""
    if value is None:
        return []

    if isinstance(value, (list, tuple, set)):
        return [
            str(x).strip()
            for x in value
            if str(x).strip()
        ]

    # numpy arrays
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

    # Handle comma-separated values
    if "," in text:
        return [
            x.strip()
            for x in text.split(",")
            if x.strip()
        ]

    return [text]


def normalize_skill(skill):
    """Normalize a skill for comparison."""
    return (
        str(skill)
        .strip()
        .lower()
        .replace("-", " ")
        .replace("_", " ")
    )


def get_candidate_profile():
    """
    Retrieve the candidate profile created by Resume Analyzer.

    Supports several possible session-state names so the
    Job Matcher remains compatible with the Resume Analyzer.
    """

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
    """Extract candidate fields from Resume Analyzer output."""

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


def load_jobs():
    """Load the normalized job dataset."""

    if not JOBS_PATH.exists():
        st.error(
            f"Job dataset not found:\n\n{JOBS_PATH}"
        )
        return pd.DataFrame()

    try:
        jobs = pd.read_parquet(JOBS_PATH)
        return jobs
    except Exception as exc:
        st.error(
            f"Could not load job dataset:\n\n{exc}"
        )
        return pd.DataFrame()


def load_skill_data():
    """Load normalized job-skill records."""

    if not SKILLS_PATH.exists():
        return pd.DataFrame()

    try:
        return pd.read_parquet(SKILLS_PATH)
    except Exception:
        return pd.DataFrame()


def get_job_skills(skill_df, job_index):
    """Retrieve normalized skills for a specific job row."""

    if skill_df.empty:
        return []

    # Most likely schema
    if "job_index" in skill_df.columns:
        rows = skill_df[
            skill_df["job_index"].astype(str) == str(job_index)
        ]

        if not rows.empty:
            for column in ["skills", "normalized_skills"]:
                if column in rows.columns:
                    values = []

                    for value in rows[column]:
                        values.extend(safe_list(value))

                    return list(dict.fromkeys(values))

    # Alternative schema
    if "skills" in skill_df.columns:
        try:
            row = skill_df.loc[job_index]

            if isinstance(row, pd.Series):
                return safe_list(row.get("skills"))

        except Exception:
            pass

    return []


def calculate_skill_match(candidate_skills, job_skills):
    """
    Calculate percentage of job skills covered by candidate skills.
    """

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

    matched = sorted(candidate_set.intersection(job_set))
    missing = sorted(job_set.difference(candidate_set))

    score = (len(matched) / len(job_set)) * 100

    return score, matched, missing


def text_similarity_score(candidate_text, job_row):
    """
    Lightweight fallback relevance score.

    The main semantic matcher is used when its artifacts are available.
    This fallback allows the UI to continue functioning even if the
    embedding artifact is unavailable.
    """

    if not candidate_text:
        return 0.0

    candidate_words = set(
        word.lower()
        for word in candidate_text.split()
        if len(word) > 2
    )

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
            value = safe_text(job_row[field], "")
            if value:
                job_text_parts.append(value)

    job_words = set(
        word.lower()
        for word in " ".join(job_text_parts).split()
        if len(word) > 2
    )

    if not job_words:
        return 0.0

    overlap = len(candidate_words.intersection(job_words))

    return min(
        100.0,
        (overlap / max(len(candidate_words), 1)) * 100
    )


def calculate_matches(jobs, skill_df, candidate):
    """
    Generate job matches.

    Uses:
    1. Semantic matcher when available.
    2. Skill matching.
    3. Lightweight fallback relevance.
    """

    if jobs.empty:
        return pd.DataFrame()

    candidate_skills = candidate["skills"]

    # Candidate text for fallback
    candidate_text = (
        " ".join(candidate_skills)
        + " "
        + candidate["experience"]
        + " "
        + candidate["resume_text"]
    )

    # --------------------------------------------------------
    # Try existing semantic matcher
    # --------------------------------------------------------

    semantic_results = None

    try:
        from src.matching.semantic_matcher import semantic_match

        query_text = candidate_text.strip()

        if query_text:
            semantic_results = semantic_match(
                query_text,
                top_k=min(100, len(jobs)),
            )

    except Exception:
        semantic_results = None

    results = []

    # --------------------------------------------------------
    # Semantic results available
    # --------------------------------------------------------

    if isinstance(semantic_results, pd.DataFrame) and not semantic_results.empty:

        for index, row in semantic_results.iterrows():

            job_row = row

            job_index = index

            title = safe_text(
                job_row.get("title"),
                "Untitled Job",
            )

            company = safe_text(
                job_row.get("company_name"),
                "Unknown Company",
            )

            job_skills = get_job_skills(
                skill_df,
                job_index,
            )

            skill_score, matched, missing = calculate_skill_match(
                candidate_skills,
                job_skills,
            )

            raw_semantic = job_row.get(
                "similarity_score",
                0,
            )

            try:
                semantic_score = float(raw_semantic) * 100
            except Exception:
                semantic_score = 0.0

            # Combined score
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
                        job_row.get("country")
                    ),
                    "work_model": safe_text(
                        job_row.get("work_model")
                    ),
                    "experience_level": safe_text(
                        job_row.get("experience_level")
                    ),
                    "employment_type": safe_text(
                        job_row.get("employment_type")
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
                    "semantic_score": semantic_score,
                    "skill_score": skill_score,
                    "match_score": final_score,
                    "matched_skills": matched,
                    "missing_skills": missing,
                    "description": safe_text(
                        job_row.get("job_description"),
                        "",
                    ),
                }
            )

    # --------------------------------------------------------
    # Fallback if semantic matcher unavailable
    # --------------------------------------------------------

    else:

        # Limit fallback processing to a reasonable number
        # for Streamlit responsiveness.
        sample_jobs = jobs.head(min(5000, len(jobs)))

        for job_index, job_row in sample_jobs.iterrows():

            job_skills = get_job_skills(
                skill_df,
                job_index,
            )

            skill_score, matched, missing = calculate_skill_match(
                candidate_skills,
                job_skills,
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
                        job_row.get("company_name"),
                        "Unknown Company",
                    ),
                    "country": safe_text(
                        job_row.get("country")
                    ),
                    "work_model": safe_text(
                        job_row.get("work_model")
                    ),
                    "experience_level": safe_text(
                        job_row.get("experience_level")
                    ),
                    "employment_type": safe_text(
                        job_row.get("employment_type")
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
                        job_row.get("job_description"),
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
            subset=["job_index"],
        )
        .reset_index(drop=True)
    )

    return result_df


def format_salary(min_salary, max_salary):
    """Format salary safely."""

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

    if min_value is not None and min_value > 0:
        return f"${min_value:,.0f}+"

    if max_value is not None and max_value > 0:
        return f"Up to ${max_value:,.0f}"

    return "Salary not available"


def display_skill_chips(skills, empty_text="None"):
    """Display skills as Streamlit pills."""

    if not skills:
        st.caption(empty_text)
        return

    columns = st.columns(
        min(6, max(1, len(skills)))
    )

    for index, skill in enumerate(skills):
        with columns[index % len(columns)]:
            st.markdown(
                f"""
                <div style="
                    background:#eef2ff;
                    color:#243b8f;
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


# ============================================================
# HEADER
# ============================================================

st.title("🎯 Job Matcher")

st.markdown(
    """
    Compare your resume against JobInsight's job market
    using semantic similarity and skill-level matching.
    """
)

st.divider()


# ============================================================
# LOAD CANDIDATE
# ============================================================

profile = get_candidate_profile()

candidate = extract_candidate_data(profile)


# ============================================================
# CANDIDATE PROFILE
# ============================================================

st.header("👤 Candidate Profile")

col1, col2, col3, col4 = st.columns(4)

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
        len(candidate["skills"]),
    )

with col4:
    resume_words = len(
        candidate["resume_text"].split()
    )

    st.metric(
        "Resume Words",
        resume_words,
    )


st.subheader("🧠 Your Skills")

display_skill_chips(
    candidate["skills"],
    "No skills detected.",
)

st.divider()


# ============================================================
# LOAD DATA
# ============================================================

jobs = load_jobs()
skill_df = load_skill_data()

if jobs.empty:
    st.stop()


# ============================================================
# MATCH SETTINGS
# ============================================================

st.header("⚙️ Match Settings")

settings_col1, settings_col2, settings_col3 = st.columns(3)

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
                x for x in model_values
                if x.strip()
                and x.lower() != "unknown"
            ]
        )

        available_models.extend(model_values)

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
    or st.session_state["job_matcher_cache_key"] != cache_key
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
    matches["match_score"] >= minimum_score
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

st.header("📊 Matching Overview")

overview_col1, overview_col2, overview_col3, overview_col4 = st.columns(4)

with overview_col1:
    st.metric(
        "Jobs Evaluated",
        f"{len(jobs):,}",
    )

with overview_col2:
    st.metric(
        "Matches Found",
        len(filtered_matches),
    )

with overview_col3:

    if not filtered_matches.empty:
        average_match = (
            filtered_matches["match_score"]
            .mean()
        )
    else:
        average_match = 0

    st.metric(
        "Average Match",
        f"{average_match:.1f}%",
    )

with overview_col4:

    if not filtered_matches.empty:
        best_match = (
            filtered_matches["match_score"]
            .max()
        )
    else:
        best_match = 0

    st.metric(
        "Best Match",
        f"{best_match:.1f}%",
    )


# ============================================================
# MATCHING CHART
# ============================================================

if not filtered_matches.empty:

    st.header("📈 Top Matching Jobs")

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
            len(chart_df) * 70,
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
                        chart_df["match_score"].max()
                        + 10,
                    ),
                ),
            ]
        ),
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )


# ============================================================
# JOB MATCH CARDS
# ============================================================

st.header("💼 Recommended Job Matches")


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

        match_score = float(
            row.get(
                "match_score",
                0,
            )
        )

        semantic_score = float(
            row.get(
                "semantic_score",
                0,
            )
        )

        skill_score = float(
            row.get(
                "skill_score",
                0,
            )
        )

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

        # ----------------------------------------------------
        # CARD
        # ----------------------------------------------------

        with st.container(border=True):

            header_col1, header_col2 = st.columns(
                [4, 1]
            )

            with header_col1:

                st.subheader(
                    f"#{rank} — {title}"
                )

                st.markdown(
                    f"🏢 **{company}**"
                )

            with header_col2:

                st.metric(
                    "Match",
                    f"{match_score:.1f}%",
                )

            st.markdown(
                f"""
                🌎 **{country}** &nbsp; • &nbsp;
                💼 **{work_model}** &nbsp; • &nbsp;
                🎯 **{experience_level}** &nbsp; • &nbsp;
                📄 **{employment_type}**
                """
            )

            st.markdown(
                f"💰 **{salary} / year**"
            )

            st.progress(
                min(
                    max(match_score / 100, 0),
                    1,
                )
            )

            score_col1, score_col2 = st.columns(2)

            with score_col1:
                st.caption(
                    f"Semantic relevance: "
                    f"{semantic_score:.1f}%"
                )

            with score_col2:
                st.caption(
                    f"Skill coverage: "
                    f"{skill_score:.1f}%"
                )

            if matched_skills:

                st.markdown(
                    "**✅ Matched Skills**"
                )

                display_skill_chips(
                    matched_skills
                )

            if missing_skills:

                st.markdown(
                    "**📌 Skills to Develop**"
                )

                display_skill_chips(
                    missing_skills
                )

            if description:

                st.markdown(
                    description
                )

            with st.expander(
                "🔎 View matching details"
            ):

                detail_col1, detail_col2 = st.columns(
                    2
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

            st.write("")


# ============================================================
# METHODOLOGY
# ============================================================

st.divider()

with st.expander(
    "🧠 How JobInsight calculates the match"
):

    st.markdown(
        """
        ### Matching methodology

        JobInsight combines multiple signals rather than relying
        on a single keyword search.

        **1. Semantic relevance**

        Resume/job text is represented using the project's
        Sentence Transformer embedding model. This captures
        contextual similarity between the candidate profile and
        job descriptions.

        **2. Skill coverage**

        Candidate skills are compared with normalized skills
        associated with each job.

        **3. Combined match score**

        When job skills are available:

        **65% semantic relevance + 35% skill coverage**

        When explicit job skills are unavailable, the semantic
        relevance score is used.

        The resulting score is a matching signal for exploration.
        It is not a hiring probability or guarantee of suitability.
        """
    )


# ============================================================
# DATA STATUS
# ============================================================

with st.expander(
    "ℹ️ Data and model status"
):

    st.write(
        f"**Jobs dataset:** "
        f"{JOBS_PATH}"
    )

    st.write(
        f"**Skill dataset:** "
        f"{SKILLS_PATH}"
    )

    st.write(
        f"**Embedding artifact:** "
        f"{EMBEDDINGS_PATH}"
    )

    st.write(
        f"**Jobs loaded:** "
        f"{len(jobs):,}"
    )

    st.write(
        f"**Skill records loaded:** "
        f"{len(skill_df):,}"
        if not skill_df.empty
        else "Skill records: unavailable"
    )