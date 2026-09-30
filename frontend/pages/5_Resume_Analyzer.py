from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st


# ============================================================
# PROJECT PATH
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ============================================================
# JOBINSIGHT IMPORTS
# ============================================================

from src.nlp.resume_parser import parse_resume


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Resume Analyzer | JobInsight",
    page_icon="📄",
    layout="wide",
)


# ============================================================
# CUSTOM STYLING
# ============================================================

st.markdown(
    """
    <style>

    .hero-title {
        font-size: 42px;
        font-weight: 750;
        color: #26324a;
        margin-bottom: 8px;
    }

    .hero-subtitle {
        font-size: 18px;
        color: #43546f;
        line-height: 1.6;
        margin-bottom: 25px;
    }

    .section-title {
        font-size: 30px;
        font-weight: 700;
        color: #26324a;
        margin-top: 28px;
        margin-bottom: 16px;
    }

    .skill-chip {
        display: inline-block;
        padding: 8px 14px;
        margin: 4px;
        border-radius: 20px;
        background: #eef2ff;
        color: #27369b;
        font-size: 14px;
        font-weight: 600;
    }

    .profile-card {
        padding: 22px;
        border-radius: 16px;
        background: #f7f9fc;
        border: 1px solid #e3e8f0;
        min-height: 110px;
    }

    .profile-label {
        font-size: 14px;
        color: #667085;
        margin-bottom: 8px;
    }

    .profile-value {
        font-size: 24px;
        font-weight: 650;
        color: #26324a;
    }

    .info-card {
        padding: 20px;
        border-radius: 16px;
        background: #f8fafc;
        border: 1px solid #e3e8f0;
        margin-bottom: 14px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="hero-title">📄 Resume Analyzer</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero-subtitle">
        Upload your resume and let JobInsight extract your profile,
        identify technical skills, detect experience and education
        information, and prepare your profile for job matching.
    </div>
    """,
    unsafe_allow_html=True,
)

st.divider()


# ============================================================
# UPLOAD
# ============================================================

uploaded_file = st.file_uploader(
    "Upload your resume",
    type=["pdf", "docx"],
    help="Upload a PDF or DOCX resume.",
)


if uploaded_file is None:

    st.info(
        "Upload a PDF or DOCX resume to begin the analysis."
    )

    st.markdown(
        """
        ### What JobInsight analyzes

        **Candidate profile**
        - Name
        - Email
        - Phone
        - Experience

        **Skills**
        - Technical skills
        - Data skills
        - Cloud skills
        - Machine learning skills
        - Tools and technologies

        **Resume structure**
        - Summary
        - Experience
        - Education
        - Skills
        - Projects
        - Certifications

        **Next stage**
        - Semantic job matching
        - Skill-gap analysis
        - Career recommendations
        """,
    )

    st.stop()


# ============================================================
# FILE INFORMATION
# ============================================================

file_name = uploaded_file.name
file_size_mb = uploaded_file.size / (1024 * 1024)

st.caption(
    f"Selected file: **{file_name}** · "
    f"{file_size_mb:.2f} MB"
)


# ============================================================
# ANALYZE BUTTON
# ============================================================

analyze = st.button(
    "🔍 Analyze Resume",
    type="primary",
    use_container_width=True,
)


if not analyze:
    st.info(
        "Click **Analyze Resume** to extract your candidate profile."
    )
    st.stop()


# ============================================================
# PARSE RESUME
# ============================================================

with st.spinner(
    "Analyzing your resume..."
):

    try:

        file_bytes = uploaded_file.getvalue()

        profile = parse_resume(
            file_bytes=file_bytes,
            filename=file_name,
        )

    except Exception as exc:

        st.error(
            f"Resume analysis failed: {exc}"
        )

        st.stop()


# ============================================================
# STORE PROFILE
# ============================================================

st.session_state["candidate_profile"] = (
    profile.to_dict()
)

st.session_state["resume_analyzed"] = True


# ============================================================
# CANDIDATE PROFILE
# ============================================================

st.markdown(
    '<div class="section-title">👤 Candidate Profile</div>',
    unsafe_allow_html=True,
)


col1, col2, col3, col4 = st.columns(4)


with col1:

    st.markdown(
        """
        <div class="profile-card">
            <div class="profile-label">Candidate</div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
            <div class="profile-value">
                {profile.name}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


with col2:

    st.markdown(
        """
        <div class="profile-card">
            <div class="profile-label">Experience</div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
            <div class="profile-value">
                {profile.experience}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


with col3:

    st.markdown(
        """
        <div class="profile-card">
            <div class="profile-label">Detected Skills</div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
            <div class="profile-value">
                {len(profile.skills)}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


with col4:

    st.markdown(
        """
        <div class="profile-card">
            <div class="profile-label">Resume Words</div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
            <div class="profile-value">
                {profile.word_count:,}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# CONTACT INFORMATION
# ============================================================

st.markdown(
    '<div class="section-title">📇 Contact Information</div>',
    unsafe_allow_html=True,
)

contact_col1, contact_col2 = st.columns(2)


with contact_col1:

    st.markdown(
        f"""
        <div class="info-card">
            <strong>📧 Email</strong><br><br>
            {profile.email}
        </div>
        """,
        unsafe_allow_html=True,
    )


with contact_col2:

    st.markdown(
        f"""
        <div class="info-card">
            <strong>📱 Phone</strong><br><br>
            {profile.phone}
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# EDUCATION
# ============================================================

st.markdown(
    '<div class="section-title">🎓 Education</div>',
    unsafe_allow_html=True,
)

if profile.education:

    education_html = " • ".join(
        profile.education
    )

    st.markdown(
        f"""
        <div class="info-card">
            <span style="
                font-size:18px;
                color:#0066cc;
                font-weight:600;
            ">
                {education_html}
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

else:

    st.info(
        "No education level was confidently detected."
    )


# ============================================================
# DETECTED SKILLS
# ============================================================

st.markdown(
    '<div class="section-title">🧠 Detected Skills</div>',
    unsafe_allow_html=True,
)

if profile.skills:

    skill_html = ""

    for skill in profile.skills:

        skill_html += (
            f'<span class="skill-chip">'
            f'{skill}'
            f'</span>'
        )

    st.markdown(
        skill_html,
        unsafe_allow_html=True,
    )

else:

    st.warning(
        "No skills were detected from the resume."
    )


# ============================================================
# CERTIFICATIONS
# ============================================================

if profile.certifications:

    st.markdown(
        '<div class="section-title">🏅 Certifications</div>',
        unsafe_allow_html=True,
    )

    for certification in profile.certifications:

        st.markdown(
            f"- {certification}"
        )


# ============================================================
# PROJECTS
# ============================================================

if profile.projects:

    st.markdown(
        '<div class="section-title">🚀 Projects</div>',
        unsafe_allow_html=True,
    )

    for project in profile.projects:

        st.markdown(
            f"- {project}"
        )


# ============================================================
# RESUME SECTIONS
# ============================================================

st.markdown(
    '<div class="section-title">📚 Resume Sections</div>',
    unsafe_allow_html=True,
)


section_rows = []

section_display_names = {
    "summary": "Summary",
    "experience": "Experience",
    "education": "Education",
    "skills": "Skills",
    "projects": "Projects",
    "certifications": "Certifications",
}


for key, display_name in section_display_names.items():

    content = profile.sections.get(
        key,
        "",
    )

    section_rows.append(
        {
            "Section": display_name,
            "Detected": (
                "Yes"
                if content.strip()
                else "No"
            ),
            "Characters": len(content),
        }
    )


section_df = pd.DataFrame(
    section_rows
)

st.dataframe(
    section_df,
    use_container_width=True,
    hide_index=True,
)


# ============================================================
# EXTRACTED TEXT
# ============================================================

with st.expander(
    "📄 View Extracted Resume Text"
):

    st.text_area(
        "Extracted text",
        profile.raw_text,
        height=350,
        disabled=True,
    )


# ============================================================
# DETECTED SECTIONS
# ============================================================

with st.expander(
    "🔎 View Detected Sections"
):

    for key, display_name in section_display_names.items():

        content = profile.sections.get(
            key,
            "",
        )

        st.markdown(
            f"### {display_name}"
        )

        if content.strip():

            st.text(
                content
            )

        else:

            st.caption(
                "Section not detected."
            )


# ============================================================
# ANALYSIS SUMMARY
# ============================================================

with st.expander(
    "© What JobInsight has analyzed"
):

    st.markdown(
        """
        **Document processing**
        - PDF/DOCX text extraction
        - Resume section detection
        - Contact information extraction

        **Candidate profiling**
        - Candidate name
        - Experience level
        - Education level
        - Technical skills
        - Certifications
        - Projects

        **JobInsight integration**
        - Market-derived skill dictionary
        - Candidate profile stored in session state
        - Ready for semantic job matching
        - Ready for skill-gap analysis
        - Ready for career recommendations

        The current parser is a baseline NLP pipeline.
        Future versions can add transformer-based extraction,
        named-entity recognition, contextual skill extraction,
        and stronger experience/education parsing.
        """
    )