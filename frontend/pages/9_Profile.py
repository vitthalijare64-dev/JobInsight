from pathlib import Path

import streamlit as st


# ============================================================
# Page configuration
# ============================================================

st.set_page_config(
    page_title="Profile | JobInsight",
    page_icon="👤",
    layout="wide",
)


# ============================================================
# Styling
# ============================================================

st.markdown(
    """
    <style>
    .profile-header {
        padding: 1.5rem 0 1rem 0;
    }

    .profile-title {
        font-size: 2.4rem;
        font-weight: 700;
        margin-bottom: 0.3rem;
    }

    .profile-subtitle {
        color: #6b7280;
        font-size: 1.05rem;
    }

    .profile-card {
        padding: 1.3rem;
        border-radius: 16px;
        border: 1px solid #e5e7eb;
        background: #ffffff;
        margin-bottom: 1rem;
    }

    .section-title {
        font-size: 1.25rem;
        font-weight: 650;
        margin-bottom: 0.8rem;
    }

    .skill-chip {
        display: inline-block;
        padding: 0.35rem 0.7rem;
        margin: 0.2rem;
        border-radius: 999px;
        background: #eef2ff;
        font-size: 0.85rem;
    }

    .info-label {
        color: #6b7280;
        font-size: 0.85rem;
        margin-bottom: 0.15rem;
    }

    .info-value {
        font-size: 1rem;
        margin-bottom: 0.8rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# Helpers
# ============================================================

def clean_value(value, default="Not specified"):
    if value is None:
        return default

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


def get_profile_object():
    """
    Retrieve whichever candidate profile object was created
    by Resume Analyzer.
    """

    possible_keys = [
        "candidate_profile",
        "resume_profile",
        "parsed_resume",
        "resume_analysis",
    ]

    for key in possible_keys:
        value = st.session_state.get(key)

        if value is not None:
            return value

    return None


def get_profile_value(profile, field, default=None):
    """
    Supports both dataclass/object profiles and dictionaries.
    """

    if profile is None:
        return default

    if isinstance(profile, dict):
        return profile.get(field, default)

    return getattr(profile, field, default)


def normalize_list(value):
    """
    Convert a profile field into a clean list.
    """

    if value is None:
        return []

    if isinstance(value, (list, tuple, set)):
        return [
            str(item).strip()
            for item in value
            if str(item).strip()
        ]

    text = str(value).strip()

    if not text or text.lower() in {
        "nan",
        "none",
        "null",
    }:
        return []

    # Handle comma-separated values.
    return [
        item.strip()
        for item in text.split(",")
        if item.strip()
    ]


# ============================================================
# Header
# ============================================================

st.markdown(
    """
    <div class="profile-header">
        <div class="profile-title">
            👤 Candidate Profile
        </div>
        <div class="profile-subtitle">
            Your extracted career profile used by JobInsight
            for matching, skill-gap analysis, and recommendations.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# Get candidate profile
# ============================================================

profile = get_profile_object()


# ============================================================
# No profile yet
# ============================================================

if profile is None:

    st.info(
        "No candidate profile is available yet."
    )

    st.markdown(
        """
        ### How to create your profile

        1. Open **Resume Analyzer** from the sidebar.
        2. Upload a PDF or DOCX resume.
        3. Click **Analyze Resume**.
        4. Return to **Profile**.

        Your extracted candidate information will then appear here.
        """
    )

    st.stop()


# ============================================================
# Extract profile fields
# ============================================================

name = clean_value(
    get_profile_value(
        profile,
        "name",
        "Candidate",
    ),
    "Candidate",
)

email = clean_value(
    get_profile_value(
        profile,
        "email",
    )
)

phone = clean_value(
    get_profile_value(
        profile,
        "phone",
    )
)

experience = clean_value(
    get_profile_value(
        profile,
        "experience",
    )
)

education = normalize_list(
    get_profile_value(
        profile,
        "education",
    )
)

skills = normalize_list(
    get_profile_value(
        profile,
        "skills",
    )
)

certifications = normalize_list(
    get_profile_value(
        profile,
        "certifications",
    )
)

projects = normalize_list(
    get_profile_value(
        profile,
        "projects",
    )
)

sections = normalize_list(
    get_profile_value(
        profile,
        "sections",
    )
)

word_count = get_profile_value(
    profile,
    "word_count",
    0,
)

try:
    word_count = int(word_count)
except (TypeError, ValueError):
    word_count = 0


# ============================================================
# Profile summary
# ============================================================

st.subheader("Profile Overview")


col1, col2, col3, col4 = st.columns(4)


with col1:
    st.metric(
        "Candidate",
        name,
    )


with col2:
    st.metric(
        "Experience",
        experience,
    )


with col3:
    st.metric(
        "Detected Skills",
        len(skills),
    )


with col4:
    st.metric(
        "Resume Words",
        word_count,
    )


st.divider()


# ============================================================
# Contact information
# ============================================================

st.subheader("Contact Information")


contact_col1, contact_col2 = st.columns(2)


with contact_col1:

    st.markdown(
        '<div class="info-label">Email</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f'<div class="info-value">{email}</div>',
        unsafe_allow_html=True,
    )


with contact_col2:

    st.markdown(
        '<div class="info-label">Phone</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f'<div class="info-value">{phone}</div>',
        unsafe_allow_html=True,
    )


st.divider()


# ============================================================
# Skills
# ============================================================

st.subheader("Skills")


if skills:

    skill_html = " ".join(
        [
            f'<span class="skill-chip">{skill}</span>'
            for skill in skills
        ]
    )

    st.markdown(
        skill_html,
        unsafe_allow_html=True,
    )

else:

    st.info(
        "No skills were detected from the resume."
    )


st.divider()


# ============================================================
# Education and Experience
# ============================================================

col1, col2 = st.columns(2)


with col1:

    st.markdown(
        '<div class="section-title">🎓 Education</div>',
        unsafe_allow_html=True,
    )

    if education:

        for item in education:
            st.markdown(
                f"- {item}"
            )

    else:

        st.caption(
            "No education information detected."
        )


with col2:

    st.markdown(
        '<div class="section-title">💼 Experience</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        experience
    )


st.divider()


# ============================================================
# Certifications and Projects
# ============================================================

col1, col2 = st.columns(2)


with col1:

    st.markdown(
        '<div class="section-title">🏆 Certifications</div>',
        unsafe_allow_html=True,
    )

    if certifications:

        for item in certifications:
            st.markdown(
                f"- {item}"
            )

    else:

        st.caption(
            "No certifications detected."
        )


with col2:

    st.markdown(
        '<div class="section-title">🚀 Projects</div>',
        unsafe_allow_html=True,
    )

    if projects:

        for item in projects:
            st.markdown(
                f"- {item}"
            )

    else:

        st.caption(
            "No projects detected."
        )


st.divider()


# ============================================================
# Detected resume sections
# ============================================================

st.subheader(
    "Resume Sections Detected"
)


if sections:

    section_text = " • ".join(
        [
            section
            for section in sections
            if section
        ]
    )

    st.info(
        section_text
    )

else:

    st.caption(
        "No resume sections detected."
    )


# ============================================================
# Profile usage
# ============================================================

with st.expander(
    "How JobInsight uses this profile"
):

    st.markdown(
        """
        Your extracted profile is used across the JobInsight
        platform:

        **Resume Analyzer**
        - Extracts candidate information from the uploaded resume.

        **Job Matcher**
        - Compares your profile with job descriptions using
          semantic similarity and skill coverage.

        **Skill Gap**
        - Identifies skills missing from selected jobs and
          from broader market demand.

        **Career Recommendations**
        - Combines semantic relevance, skill coverage, and
          market demand into a recommendation score.

        The recommendation score is an engineering/research
        ranking signal, not a probability of getting a job.
        """
    )