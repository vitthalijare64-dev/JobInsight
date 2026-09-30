from pathlib import Path
import math
import pandas as pd
import streamlit as st


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

JOBS_PATH = PROJECT_ROOT / "data" / "processed" / "jobs_normalized.parquet"
SALARY_PATH = PROJECT_ROOT / "data" / "processed" / "salary_normalized.parquet"
SKILLS_PATH = PROJECT_ROOT / "data" / "processed" / "job_skills_normalized.parquet"


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Job Explorer | JobInsight",
    page_icon="🔎",
    layout="wide",
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>
    .job-card {
        padding: 22px;
        border: 1px solid #e5e7eb;
        border-radius: 16px;
        margin-bottom: 18px;
        background: white;
    }

    .job-title {
        font-size: 22px;
        font-weight: 700;
        margin-bottom: 5px;
    }

    .company {
        font-size: 15px;
        color: #64748b;
        margin-bottom: 12px;
    }

    .job-meta {
        font-size: 14px;
        color: #475569;
        margin-bottom: 12px;
    }

    .skill-chip {
        display: inline-block;
        padding: 5px 10px;
        margin: 3px;
        border-radius: 999px;
        background: #eef2ff;
        color: #3730a3;
        font-size: 12px;
        font-weight: 600;
    }

    .salary {
        font-size: 17px;
        font-weight: 700;
        color: #166534;
    }

    .description {
        color: #475569;
        line-height: 1.6;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_jobs():

    if not JOBS_PATH.exists():
        st.error(f"Job dataset not found: {JOBS_PATH}")
        st.stop()

    jobs = pd.read_parquet(JOBS_PATH)

    # Make sure date is datetime
    if "date_posted" in jobs.columns:
        jobs["date_posted"] = pd.to_datetime(
            jobs["date_posted"],
            errors="coerce"
        )

    # --------------------------------------------------------
    # Add normalized annual salary
    # --------------------------------------------------------

    if SALARY_PATH.exists():

        salary = pd.read_parquet(SALARY_PATH)

        if len(salary) == len(jobs):

            if "annual_salary_min_usd" in salary.columns:
                jobs["annual_salary_min_usd"] = (
                    pd.to_numeric(
                        salary["annual_salary_min_usd"],
                        errors="coerce"
                    ).values
                )

            if "annual_salary_max_usd" in salary.columns:
                jobs["annual_salary_max_usd"] = (
                    pd.to_numeric(
                        salary["annual_salary_max_usd"],
                        errors="coerce"
                    ).values
                )

    # --------------------------------------------------------
    # Add normalized skills
    # --------------------------------------------------------

    if SKILLS_PATH.exists():

        skills = pd.read_parquet(SKILLS_PATH)

        if len(skills) == len(jobs) and "skills" in skills.columns:
            jobs["normalized_skills"] = skills["skills"].values

        else:
            jobs["normalized_skills"] = [[] for _ in range(len(jobs))]

    else:
        jobs["normalized_skills"] = [[] for _ in range(len(jobs))]

    return jobs


jobs = load_jobs()


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def clean_list(value):

    if value is None:
        return []

    if isinstance(value, (list, tuple, set)):
        return [str(x) for x in value if str(x).strip()]

    # Handle numpy arrays without importing numpy
    if hasattr(value, "tolist"):
        try:
            converted = value.tolist()

            if isinstance(converted, list):
                return [
                    str(x)
                    for x in converted
                    if str(x).strip()
                ]
        except Exception:
            pass

    if pd.isna(value):
        return []

    text = str(value).strip()

    if not text:
        return []

    return [text]


def format_salary(row):

    minimum = row.get("annual_salary_min_usd")
    maximum = row.get("annual_salary_max_usd")

    # Safely convert values to numbers
    try:
        minimum = float(minimum)
        if pd.isna(minimum):
            minimum = None
    except (TypeError, ValueError):
        minimum = None

    try:
        maximum = float(maximum)
        if pd.isna(maximum):
            maximum = None
    except (TypeError, ValueError):
        maximum = None

    # Both values available
    if minimum is not None and maximum is not None:
        return f"${minimum:,.0f} – ${maximum:,.0f} / year"

    # Only minimum available
    if minimum is not None:
        return f"From ${minimum:,.0f} / year"

    # Only maximum available
    if maximum is not None:
        return f"Up to ${maximum:,.0f} / year"

    # No salary information
    return "Salary not specified"


def format_date(value):

    if pd.isna(value):
        return "Date not available"

    try:
        return pd.to_datetime(value).strftime("%b %d, %Y")
    except Exception:
        return "Date not available"


def truncate_text(text, length=350):

    if pd.isna(text):
        return ""

    text = str(text).strip()

    if len(text) <= length:
        return text

    return text[:length].rsplit(" ", 1)[0] + "..."


# ============================================================
# HEADER
# ============================================================

st.title("🔎 Job Explorer")

st.markdown(
    """
    Explore the job market using JobInsight's normalized job dataset.
    Search across job titles, companies, descriptions, and detected skills.
    """
)


# ============================================================
# KPI ROW
# ============================================================

total_jobs = len(jobs)

salary_count = (
    jobs["annual_salary_min_usd"].notna().sum()
    if "annual_salary_min_usd" in jobs.columns
    else 0
)

remote_count = (
    (jobs["work_model"] == "Remote").sum()
    if "work_model" in jobs.columns
    else 0
)

company_count = (
    jobs["company_name"].nunique()
    if "company_name" in jobs.columns
    else 0
)

k1, k2, k3, k4 = st.columns(4)

k1.metric("Jobs Available", f"{total_jobs:,}")
k2.metric(
    "Salary Records",
    f"{salary_count:,}"
)
k3.metric(
    "Remote Jobs",
    f"{remote_count:,}"
)
k4.metric(
    "Companies",
    f"{company_count:,}"
)


st.divider()


# ============================================================
# SEARCH + FILTERS
# ============================================================

st.subheader("Search & Filters")

search_query = st.text_input(
    "🔍 Search jobs",
    placeholder="Try: Data Scientist, Python, AWS, Project Manager...",
)


col1, col2, col3, col4 = st.columns(4)


with col1:

    countries = ["All"] + sorted(
        jobs["country"]
        .dropna()
        .unique()
        .tolist()
    )

    selected_country = st.selectbox(
        "Country",
        countries
    )


with col2:

    experiences = ["All"] + sorted(
        jobs["experience_level"]
        .dropna()
        .unique()
        .tolist()
    )

    selected_experience = st.selectbox(
        "Experience Level",
        experiences
    )


with col3:

    work_models = ["All"] + sorted(
        jobs["work_model"]
        .dropna()
        .unique()
        .tolist()
    )

    selected_work_model = st.selectbox(
        "Work Model",
        work_models
    )


with col4:

    employment_types = ["All"] + sorted(
        jobs["employment_type"]
        .dropna()
        .unique()
        .tolist()
    )

    selected_employment = st.selectbox(
        "Employment Type",
        employment_types
    )


# ============================================================
# SECOND FILTER ROW
# ============================================================

col5, col6, col7, col8 = st.columns(4)


with col5:

    min_salary_filter = st.number_input(
        "Minimum annual salary ($)",
        min_value=0,
        max_value=1_000_000,
        value=0,
        step=5_000,
    )


with col6:

    max_salary_filter = st.number_input(
        "Maximum annual salary ($)",
        min_value=0,
        max_value=1_000_000,
        value=0,
        step=5_000,
        help="Set to 0 to disable this filter."
    )


with col7:

    sort_options = {
        "Relevance": "relevance",
        "Newest": "newest",
        "Salary: High to Low": "salary_high",
        "Salary: Low to High": "salary_low",
    }

    sort_label = st.selectbox(
        "Sort By",
        list(sort_options.keys())
    )

    sort_mode = sort_options[sort_label]


with col8:

    page_size = st.selectbox(
        "Jobs per page",
        [10, 20, 30, 50],
        index=1
    )


# ============================================================
# APPLY FILTERS
# ============================================================

filtered = jobs.copy()


# ------------------------------------------------------------
# Text search
# ------------------------------------------------------------

if search_query.strip():

    query = search_query.strip().lower()

    searchable_columns = [
        "title",
        "normalized_title",
        "company_name",
        "industry",
        "function",
        "job_description",
        "skills_required",
        "minimum_qualifications",
        "preferred_qualifications",
        "responsibilities",
    ]

    existing_columns = [
        c for c in searchable_columns
        if c in filtered.columns
    ]

    mask = pd.Series(
        False,
        index=filtered.index
    )

    for column in existing_columns:

        mask = mask | (
            filtered[column]
            .fillna("")
            .astype(str)
            .str.lower()
            .str.contains(
                query,
                regex=False
            )
        )

    # Also search normalized skills
    if "normalized_skills" in filtered.columns:

        skill_mask = filtered["normalized_skills"].apply(
            lambda skills: query in " ".join(
                clean_list(skills)
            ).lower()
        )

        mask = mask | skill_mask

    filtered = filtered[mask]


# ------------------------------------------------------------
# Country
# ------------------------------------------------------------

if selected_country != "All":

    filtered = filtered[
        filtered["country"] == selected_country
    ]


# ------------------------------------------------------------
# Experience
# ------------------------------------------------------------

if selected_experience != "All":

    filtered = filtered[
        filtered["experience_level"] == selected_experience
    ]


# ------------------------------------------------------------
# Work model
# ------------------------------------------------------------

if selected_work_model != "All":

    filtered = filtered[
        filtered["work_model"] == selected_work_model
    ]


# ------------------------------------------------------------
# Employment type
# ------------------------------------------------------------

if selected_employment != "All":

    filtered = filtered[
        filtered["employment_type"] == selected_employment
    ]


# ------------------------------------------------------------
# Salary filters
# ------------------------------------------------------------

if "annual_salary_min_usd" in filtered.columns:

    if min_salary_filter > 0:

        filtered = filtered[
            filtered["annual_salary_min_usd"].fillna(0)
            >= min_salary_filter
        ]

    if max_salary_filter > 0:

        filtered = filtered[
            filtered["annual_salary_min_usd"].fillna(
                float("inf")
            )
            <= max_salary_filter
        ]


# ============================================================
# SORTING
# ============================================================

if sort_mode == "newest":

    filtered = filtered.sort_values(
        "date_posted",
        ascending=False,
        na_position="last"
    )

elif sort_mode == "salary_high":

    if "annual_salary_min_usd" in filtered.columns:

        filtered = filtered.sort_values(
            "annual_salary_min_usd",
            ascending=False,
            na_position="last"
        )

elif sort_mode == "salary_low":

    if "annual_salary_min_usd" in filtered.columns:

        filtered = filtered.sort_values(
            "annual_salary_min_usd",
            ascending=True,
            na_position="last"
        )

else:

    # Relevance is primarily driven by text search.
    # If no search is supplied, show newest jobs.
    if search_query.strip() and "title" in filtered.columns:

        query_words = [
            word.lower()
            for word in search_query.split()
            if word.strip()
        ]

        def relevance_score(row):

            title = str(
                row.get("title", "")
            ).lower()

            company = str(
                row.get("company_name", "")
            ).lower()

            description = str(
                row.get("job_description", "")
            ).lower()

            score = 0

            for word in query_words:

                if word in title:
                    score += 5

                if word in company:
                    score += 2

                if word in description:
                    score += 1

            return score

        filtered = filtered.copy()

        filtered["_relevance"] = filtered.apply(
            relevance_score,
            axis=1
        )

        filtered = filtered.sort_values(
            "_relevance",
            ascending=False
        )

    elif "date_posted" in filtered.columns:

        filtered = filtered.sort_values(
            "date_posted",
            ascending=False,
            na_position="last"
        )


# ============================================================
# RESULT SUMMARY
# ============================================================

result_count = len(filtered)

st.markdown(
    f"### {result_count:,} jobs found"
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
    math.ceil(result_count / page_size)
)

if "job_explorer_page" not in st.session_state:
    st.session_state.job_explorer_page = 1

current_page = st.number_input(
    "Page",
    min_value=1,
    max_value=total_pages,
    value=min(
        st.session_state.job_explorer_page,
        total_pages
    ),
    step=1
)

st.session_state.job_explorer_page = current_page


start = (
    current_page - 1
) * page_size

end = start + page_size

page_jobs = filtered.iloc[start:end]


st.caption(
    f"Showing {start + 1:,}–"
    f"{min(end, result_count):,} "
    f"of {result_count:,} matching jobs"
)


# ============================================================
# JOB CARDS
# ============================================================

for _, row in page_jobs.iterrows():

    title = str(
        row.get(
            "title",
            "Untitled Position"
        )
    )

    company = str(
        row.get(
            "company_name",
            "Company not specified"
        )
    )

    country = str(
        row.get(
            "country",
            "Unknown"
        )
    )

    work_model = str(
        row.get(
            "work_model",
            "Unknown"
        )
    )

    experience = str(
        row.get(
            "experience_level",
            "Unknown"
        )
    )

    employment = str(
        row.get(
            "employment_type",
            "Unknown"
        )
    )

    salary = format_salary(row)

    date_posted = format_date(
        row.get("date_posted")
    )

    description = truncate_text(
        row.get(
            "job_description",
            ""
        )
    )

    skills = clean_list(
        row.get(
            "normalized_skills",
            []
        )
    )

    st.markdown(
        '<div class="job-card">',
        unsafe_allow_html=True
    )

    st.markdown(
        f'<div class="job-title">{title}</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        f'<div class="company">🏢 {company}</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <div class="job-meta">
        🌍 {country}
        &nbsp;&nbsp;•&nbsp;&nbsp;
        💼 {work_model}
        &nbsp;&nbsp;•&nbsp;&nbsp;
        🎯 {experience}
        &nbsp;&nbsp;•&nbsp;&nbsp;
        📋 {employment}
        &nbsp;&nbsp;•&nbsp;&nbsp;
        📅 {date_posted}
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        f'<div class="salary">💰 {salary}</div>',
        unsafe_allow_html=True
    )

    if skills:

        displayed_skills = skills[:12]

        chips = "".join(
            f'<span class="skill-chip">{skill}</span>'
            for skill in displayed_skills
        )

        st.markdown(
            f"""
            <div style="margin-top:12px;">
                <strong>Skills</strong><br>
                {chips}
            </div>
            """,
            unsafe_allow_html=True
        )

    if description:

        st.markdown(
            f"""
            <div class="description" style="margin-top:14px;">
                {description}
            </div>
            """,
            unsafe_allow_html=True
        )

    # --------------------------------------------------------
    # Expandable details
    # --------------------------------------------------------

    with st.expander("View full job details"):

        detail_col1, detail_col2 = st.columns(2)

        with detail_col1:

            st.markdown("**Job Information**")

            st.write(
                f"**Title:** {title}"
            )

            st.write(
                f"**Company:** {company}"
            )

            st.write(
                f"**Industry:** "
                f"{row.get('industry', 'Not specified')}"
            )

            st.write(
                f"**Function:** "
                f"{row.get('function', 'Not specified')}"
            )

            st.write(
                f"**Location:** "
                f"{row.get('location_resolved', country)}"
            )

        with detail_col2:

            st.markdown("**Requirements**")

            st.write(
                f"**Experience:** {experience}"
            )

            st.write(
                f"**Education:** "
                f"{row.get('education_level', 'Not specified')}"
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

        st.markdown("---")

        qualifications = row.get(
            "minimum_qualifications",
            ""
        )

        if pd.notna(qualifications) and str(qualifications).strip():

            st.markdown("**Minimum Qualifications**")

            st.write(
                str(qualifications)
            )

        preferred = row.get(
            "preferred_qualifications",
            ""
        )

        if pd.notna(preferred) and str(preferred).strip():

            st.markdown("**Preferred Qualifications**")

            st.write(
                str(preferred)
            )

        responsibilities = row.get(
            "responsibilities",
            ""
        )

        if pd.notna(responsibilities) and str(responsibilities).strip():

            st.markdown("**Responsibilities**")

            st.write(
                str(responsibilities)
            )

        full_description = row.get(
            "job_description",
            ""
        )

        if pd.notna(full_description) and str(full_description).strip():

            st.markdown("**Full Job Description**")

            st.write(
                str(full_description)
            )

    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )


# ============================================================
# PAGINATION CONTROLS
# ============================================================

st.divider()

previous_col, info_col, next_col = st.columns(
    [1, 2, 1]
)

with previous_col:

    if current_page > 1:

        if st.button(
            "← Previous",
            use_container_width=True
        ):
            st.session_state.job_explorer_page = (
                current_page - 1
            )
            st.rerun()

with info_col:

    st.markdown(
        f"<center>Page {current_page} of {total_pages}</center>",
        unsafe_allow_html=True
    )

with next_col:

    if current_page < total_pages:

        if st.button(
            "Next →",
            use_container_width=True
        ):
            st.session_state.job_explorer_page = (
                current_page + 1
            )
            st.rerun()