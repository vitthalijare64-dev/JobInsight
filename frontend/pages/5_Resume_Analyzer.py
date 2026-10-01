from pathlib import Path
import html
import sys

import pandas as pd
import streamlit as st


# ============================================================
# PROJECT PATH
# ============================================================

PROJECT_ROOT = Path(
    __file__
).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:

    sys.path.insert(
        0,
        str(PROJECT_ROOT),
    )


from src.nlp.resume_parser import parse_resume


# ============================================================
# PAGE
# ============================================================

st.set_page_config(
    page_title="Resume Analyzer | JobInsight",
    page_icon="📄",
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

    .upload-card {
        background:white;
        border:1px solid #e2e8f0;
        border-radius:22px;
        padding:25px;
        box-shadow:0 10px 28px rgba(15,23,42,.05);
    }

    .upload-title {
        font-size:18px;
        font-weight:800;
        color:#111827;
    }

    .upload-text {
        margin-top:7px;
        color:#64748b;
        font-size:13px;
        line-height:1.6;
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
        font-size:23px;
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

    .content-card {
        background:white;
        border:1px solid #e2e8f0;
        border-radius:20px;
        padding:22px;
        box-shadow:0 8px 24px rgba(15,23,42,.045);
    }

    .card-heading {
        font-size:15px;
        font-weight:800;
        color:#111827;
        margin-bottom:14px;
    }

    .info-label {
        color:#64748b;
        font-size:11px;
        text-transform:uppercase;
        letter-spacing:.07em;
        font-weight:700;
        margin-bottom:4px;
    }

    .info-value {
        color:#111827;
        font-size:14px;
        font-weight:600;
        margin-bottom:15px;
        word-break:break-word;
    }

    .skill-wrap {
        display:flex;
        flex-wrap:wrap;
        gap:8px;
    }

    .skill-chip {
        display:inline-block;
        padding:7px 12px;
        border-radius:999px;
        background:#eef2ff;
        border:1px solid #c7d2fe;
        color:#4338ca;
        font-size:12px;
        font-weight:650;
    }

    .list-item {
        background:#f8fafc;
        border:1px solid #e2e8f0;
        border-radius:12px;
        padding:11px 13px;
        margin-bottom:8px;
        color:#334155;
        font-size:13px;
        line-height:1.5;
    }

    .pipeline-card {
        background:white;
        border:1px solid #e2e8f0;
        border-radius:20px;
        padding:22px;
        min-height:145px;
        box-shadow:0 8px 24px rgba(15,23,42,.045);
    }

    .pipeline-title {
        font-size:15px;
        font-weight:800;
        color:#111827;
        margin-bottom:10px;
    }

    .pipeline-text {
        color:#64748b;
        font-size:13px;
        line-height:1.6;
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


def clean_value(
    value,
    default="Not specified",
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


def normalize_list(value):

    if value is None:
        return []

    if isinstance(
        value,
        (list, tuple, set),
    ):

        return [
            str(item).strip()
            for item in value
            if str(item).strip()
        ]

    if isinstance(
        value,
        dict,
    ):

        return [
            str(key).strip()
            for key in value.keys()
            if str(key).strip()
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


def get_profile_value(
    profile,
    field,
    default=None,
):

    if isinstance(
        profile,
        dict,
    ):

        return profile.get(
            field,
            default,
        )

    return getattr(
        profile,
        field,
        default,
    )


def list_html(
    items,
    empty_text,
):

    if not items:

        return (
            '<div style="'
            'color:#94a3b8;'
            'font-size:13px;'
            '">'
            f'{html.escape(empty_text)}'
            '</div>'
        )

    output = ""

    for item in items:

        output += (
            '<div class="list-item">'
            f'{html.escape(str(item))}'
            '</div>'
        )

    return output


def skills_html(
    skills,
):

    if not skills:

        return (
            '<span style="'
            'color:#94a3b8;'
            'font-size:13px;'
            '">'
            'No skills detected.'
            '</span>'
        )

    output = ""

    for skill in skills:

        output += (
            '<span class="skill-chip">'
            f'{html.escape(str(skill))}'
            '</span>'
        )

    return output


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
                📄
            </div>

            <div style="
                margin-top:12px;
                font-size:18px;
                font-weight:800;
            ">
                Resume Analyzer
            </div>

            <div style="
                margin-top:5px;
                font-size:12px;
                opacity:.70;
            ">
                Convert your resume into a career profile
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
                Resume Pipeline
            </div>

            <div>📄 Upload resume</div>
            <div>↓</div>
            <div>🔍 Extract text</div>
            <div>↓</div>
            <div>🧠 Detect skills</div>
            <div>↓</div>
            <div>👤 Build profile</div>

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
            JOBINSIGHT · RESUME INTELLIGENCE
        </div>

        <div class="hero-title">
            Turn your resume into a structured career profile.
        </div>

        <div class="hero-subtitle">
            Upload a PDF or DOCX resume. JobInsight extracts
            candidate information, skills, education, experience,
            certifications, projects and resume sections for
            downstream job intelligence.
        </div>

    </div>
    """
)


# ============================================================
# UPLOAD
# ============================================================

render_html(
    """
    <div class="upload-card">

        <div class="upload-title">
            📤 Upload Your Resume
        </div>

        <div class="upload-text">
            Supported formats: PDF and DOCX.
            The extracted profile will be stored in the
            current JobInsight session and used by the
            matching and recommendation modules.
        </div>

    </div>
    """
)


uploaded_file = st.file_uploader(
    "Choose your resume",
    type=[
        "pdf",
        "docx",
    ],
    help=(
        "Upload a PDF or DOCX resume."
    ),
)


if uploaded_file is None:

    render_html(
        """
        <div class="content-card">

            <div class="card-heading">
                What JobInsight analyzes
            </div>

            <div class="list-item">
                👤 Candidate name and contact information
            </div>

            <div class="list-item">
                💼 Experience information
            </div>

            <div class="list-item">
                🧠 Technical and professional skills
            </div>

            <div class="list-item">
                🎓 Education
            </div>

            <div class="list-item">
                🏆 Certifications
            </div>

            <div class="list-item">
                🚀 Projects
            </div>

            <div class="list-item">
                📚 Resume sections and extracted text
            </div>

        </div>
        """
    )

    st.stop()


# ============================================================
# FILE INFO
# ============================================================

file_name = uploaded_file.name

file_size_mb = (
    uploaded_file.size
    / (1024 * 1024)
)


render_html(
    f"""
    <div class="content-card">

        <div class="info-label">
            Selected Resume
        </div>

        <div class="info-value">
            📄 {html.escape(file_name)}
        </div>

        <div class="info-label">
            File Size
        </div>

        <div class="info-value">
            {file_size_mb:.2f} MB
        </div>

    </div>
    """
)


# ============================================================
# ANALYZE
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
# PARSE
# ============================================================

with st.spinner(
    "Analyzing your resume..."
):

    try:

        file_bytes = (
            uploaded_file.getvalue()
        )

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
# SESSION STATE
# ============================================================

st.session_state[
    "candidate_profile"
] = profile.to_dict()

st.session_state[
    "resume_analyzed"
] = True


# ============================================================
# EXTRACTED VALUES
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

sections_raw = get_profile_value(
    profile,
    "sections",
)


if isinstance(
    sections_raw,
    dict,
):

    section_names = [
        key
        for key, value
        in sections_raw.items()
        if value
    ]

else:

    section_names = normalize_list(
        sections_raw
    )


raw_text = clean_value(
    get_profile_value(
        profile,
        "raw_text",
        "",
    ),
    "",
)


word_count = get_profile_value(
    profile,
    "word_count",
    0,
)


try:

    word_count = int(
        word_count
    )

except (
    TypeError,
    ValueError,
):

    word_count = (
        len(raw_text.split())
        if raw_text
        else 0
    )


# ============================================================
# SUCCESS
# ============================================================

st.success(
    "Resume analyzed successfully. Your candidate profile is ready."
)


# ============================================================
# PROFILE KPIs
# ============================================================

render_html(
    """
    <div class="section-title">
        👤 Candidate Profile
    </div>

    <div class="section-subtitle">
        Structured information extracted from the uploaded resume.
    </div>
    """
)


k1, k2, k3, k4 = st.columns(4)


with k1:

    render_html(
        f"""
        <div class="kpi-card">
            <div class="kpi-icon">👤</div>
            <div class="kpi-label">Candidate</div>
            <div class="kpi-value">
                {html.escape(name)}
            </div>
        </div>
        """
    )


with k2:

    render_html(
        f"""
        <div class="kpi-card">
            <div class="kpi-icon">💼</div>
            <div class="kpi-label">Experience</div>
            <div class="kpi-value">
                {html.escape(experience)}
            </div>
        </div>
        """
    )


with k3:

    render_html(
        f"""
        <div class="kpi-card">
            <div class="kpi-icon">🧠</div>
            <div class="kpi-label">Detected Skills</div>
            <div class="kpi-value">
                {len(skills)}
            </div>
        </div>
        """
    )


with k4:

    render_html(
        f"""
        <div class="kpi-card">
            <div class="kpi-icon">📝</div>
            <div class="kpi-label">Resume Words</div>
            <div class="kpi-value">
                {word_count:,}
            </div>
        </div>
        """
    )


# ============================================================
# CONTACT
# ============================================================

render_html(
    """
    <div class="section-title">
        📇 Contact Information
    </div>
    """
)


c1, c2 = st.columns(2)


with c1:

    render_html(
        f"""
        <div class="content-card">

            <div class="card-heading">
                📧 Email
            </div>

            <div class="info-value">
                {html.escape(email)}
            </div>

        </div>
        """
    )


with c2:

    render_html(
        f"""
        <div class="content-card">

            <div class="card-heading">
                📱 Phone
            </div>

            <div class="info-value">
                {html.escape(phone)}
            </div>

        </div>
        """
    )


# ============================================================
# SKILLS
# ============================================================

render_html(
    """
    <div class="section-title">
        🧠 Detected Skills
    </div>

    <div class="section-subtitle">
        Skills extracted from the resume and passed into the
        Job Matcher, Skill Gap and Career Recommendation modules.
    </div>
    """
)


render_html(
    f"""
    <div class="content-card">

        <div class="skill-wrap">
            {skills_html(skills)}
        </div>

    </div>
    """
)


# ============================================================
# EDUCATION / EXPERIENCE
# ============================================================

education_block = list_html(
    education,
    "No education information detected.",
)


experience_block = (
    '<div class="list-item">'
    f'{html.escape(experience)}'
    '</div>'
)


c1, c2 = st.columns(2)


with c1:

    render_html(
        f"""
        <div class="content-card">

            <div class="card-heading">
                🎓 Education
            </div>

            {education_block}

        </div>
        """
    )


with c2:

    render_html(
        f"""
        <div class="content-card">

            <div class="card-heading">
                💼 Experience
            </div>

            {experience_block}

        </div>
        """
    )


# ============================================================
# CERTIFICATIONS / PROJECTS
# ============================================================

certification_block = list_html(
    certifications,
    "No certifications detected.",
)

project_block = list_html(
    projects,
    "No projects detected.",
)


c1, c2 = st.columns(2)


with c1:

    render_html(
        f"""
        <div class="content-card">

            <div class="card-heading">
                🏆 Certifications
            </div>

            {certification_block}

        </div>
        """
    )


with c2:

    render_html(
        f"""
        <div class="content-card">

            <div class="card-heading">
                🚀 Projects
            </div>

            {project_block}

        </div>
        """
    )


# ============================================================
# RESUME SECTIONS
# ============================================================

render_html(
    """
    <div class="section-title">
        📚 Resume Sections Detected
    </div>
    """
)


if section_names:

    section_html = ""

    for section in section_names:

        section_html += (
            '<span class="skill-chip">'
            f'{html.escape(str(section))}'
            '</span>'
        )

    render_html(
        f"""
        <div class="content-card">

            <div class="skill-wrap">
                {section_html}
            </div>

        </div>
        """
    )

else:

    st.info(
        "No resume sections were detected."
    )


# ============================================================
# PIPELINE
# ============================================================

render_html(
    """
    <div class="section-title">
        🔗 Your Profile in JobInsight
    </div>

    <div class="section-subtitle">
        The extracted candidate profile becomes the input
        for the remaining career intelligence modules.
    </div>
    """
)


p1, p2, p3, p4 = st.columns(4)


with p1:

    render_html(
        """
        <div class="pipeline-card">

            <div class="pipeline-title">
                📄 Resume Analyzer
            </div>

            <div class="pipeline-text">
                Extracts structured candidate information
                from the uploaded document.
            </div>

        </div>
        """
    )


with p2:

    render_html(
        """
        <div class="pipeline-card">

            <div class="pipeline-title">
                🎯 Job Matcher
            </div>

            <div class="pipeline-text">
                Uses the profile as a query against
                the semantic job embedding index.
            </div>

        </div>
        """
    )


with p3:

    render_html(
        """
        <div class="pipeline-card">

            <div class="pipeline-title">
                🧩 Skill Gap
            </div>

            <div class="pipeline-text">
                Compares detected candidate skills with
                job and market requirements.
            </div>

        </div>
        """
    )


with p4:

    render_html(
        """
        <div class="pipeline-card">

            <div class="pipeline-title">
                🚀 Recommendations
            </div>

            <div class="pipeline-text">
                Uses candidate and job signals to produce
                career recommendation results.
            </div>

        </div>
        """
    )


# ============================================================
# EXTRACTED TEXT
# ============================================================

with st.expander(
    "📄 View Extracted Resume Text"
):

    if raw_text:

        st.text_area(
            "Extracted text",
            raw_text,
            height=350,
            disabled=True,
        )

    else:

        st.info(
            "No extracted text is available."
        )


# ============================================================
# DETECTED SECTIONS
# ============================================================

with st.expander(
    "🔎 View Detected Resume Sections"
):

    if isinstance(
        sections_raw,
        dict,
    ):

        for key, content in (
            sections_raw.items()
        ):

            st.markdown(
                f"### {key.title()}"
            )

            if content:

                st.text(
                    str(content)
                )

            else:

                st.caption(
                    "Section not detected."
                )

    else:

        st.write(
            section_names
        )


# ============================================================
# METHODOLOGY
# ============================================================

with st.expander(
    "🧠 What JobInsight Analyzes"
):

    st.markdown(
        """
        ### Candidate Profile

        - Candidate name
        - Email
        - Phone
        - Experience

        ### Skills

        - Technical skills
        - Data skills
        - Cloud skills
        - Machine-learning skills
        - Tools and technologies

        ### Resume Structure

        - Summary
        - Experience
        - Education
        - Skills
        - Projects
        - Certifications

        ### Next Stage

        - Semantic job matching
        - Skill-gap analysis
        - Career recommendations

        The current resume parser is a baseline NLP pipeline.
        Future versions can extend it with transformer-based
        extraction, contextual skill recognition and stronger
        experience and education parsing.
        """
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

        Resume extraction · Candidate profiling ·
        Job matching · Skill-gap analysis

    </div>
    """
)