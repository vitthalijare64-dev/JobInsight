import html

import pandas as pd
import streamlit as st


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Profile | JobInsight",
    page_icon="👤",
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
        max-width:850px;
        font-size:16px;
        line-height:1.7;
        color:#dbeafe;
        position:relative;
        z-index:2;
    }

    .identity-card {
        background:rgba(255,255,255,.97);
        border:1px solid #e2e8f0;
        border-radius:24px;
        padding:28px;
        box-shadow:
            0 10px 30px rgba(15,23,42,.06);
    }

    .avatar {
        width:82px;
        height:82px;
        border-radius:24px;
        display:flex;
        align-items:center;
        justify-content:center;

        background:
            linear-gradient(
                135deg,
                #6366f1,
                #38bdf8
            );

        color:white;
        font-size:34px;
        font-weight:800;

        box-shadow:
            0 14px 30px
            rgba(99,102,241,.25);
    }

    .identity-name {
        font-size:30px;
        font-weight:850;
        color:#111827;
    }

    .identity-role {
        color:#64748b;
        font-size:14px;
        margin-top:4px;
    }

    .status {
        display:inline-block;
        margin-top:12px;
        padding:7px 12px;
        border-radius:999px;
        background:#ecfdf5;
        border:1px solid #a7f3d0;
        color:#047857;
        font-size:11px;
        font-weight:800;
    }

    .kpi-card {
        background:rgba(255,255,255,.96);
        border:1px solid #e2e8f0;
        border-radius:20px;
        padding:20px;
        min-height:110px;
        box-shadow:
            0 8px 24px rgba(15,23,42,.05);
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
        font-size:24px;
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
        background:rgba(255,255,255,.97);
        border:1px solid #e2e8f0;
        border-radius:20px;
        padding:22px;
        box-shadow:
            0 8px 24px rgba(15,23,42,.045);
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
        margin-bottom:14px;
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

    .section-chip {
        display:inline-block;
        padding:8px 13px;
        margin:4px;
        border-radius:999px;
        background:#f0fdf4;
        border:1px solid #bbf7d0;
        color:#166534;
        font-size:12px;
        font-weight:700;
    }

    .pipeline-card {
        background:white;
        border:1px solid #e2e8f0;
        border-radius:20px;
        padding:22px;
        min-height:145px;
        box-shadow:
            0 8px 24px rgba(15,23,42,.045);
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

    .empty-card {
        background:white;
        border:1px dashed #cbd5e1;
        border-radius:22px;
        padding:40px;
        text-align:center;
        color:#64748b;
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


def get_profile_object():

    keys = [
        "candidate_profile",
        "resume_profile",
        "parsed_resume",
        "resume_analysis",
    ]

    for key in keys:

        value = st.session_state.get(
            key
        )

        if value is not None:
            return value

    return None


def get_profile_value(
    profile,
    field,
    default=None,
):

    if profile is None:
        return default

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


def normalize_list(value):

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

    if isinstance(
        value,
        dict,
    ):

        return [
            str(key).strip()
            for key in value.keys()
            if str(key).strip()
        ]

    text = str(value).strip()

    if not text or text.lower() in {
        "nan",
        "none",
        "null",
    }:
        return []

    return [
        item.strip()
        for item in text.split(",")
        if item.strip()
    ]


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


def skills_html(skills):

    if not skills:

        return (
            '<span style="'
            'color:#94a3b8;'
            'font-size:13px;'
            '">No skills detected.</span>'
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
                👤
            </div>

            <div style="
                margin-top:12px;
                font-size:18px;
                font-weight:800;
            ">
                Candidate Profile
            </div>

            <div style="
                margin-top:5px;
                font-size:12px;
                opacity:.70;
            ">
                Your JobInsight career identity
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
                Profile Pipeline
            </div>

            <div>📄 Resume Upload</div>
            <div>↓</div>
            <div>🧠 NLP Extraction</div>
            <div>↓</div>
            <div>👤 Candidate Profile</div>
            <div>↓</div>
            <div>🎯 Job Matching</div>
            <div>↓</div>
            <div>🚀 Recommendations</div>

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
            JOBINSIGHT · CANDIDATE INTELLIGENCE
        </div>

        <div class="hero-title">
            Your career profile, extracted and ready to use.
        </div>

        <div class="hero-subtitle">
            Review the information JobInsight extracted from
            your resume. This profile powers job matching,
            skill-gap analysis, and career recommendations.
        </div>

    </div>
    """
)


# ============================================================
# PROFILE
# ============================================================

profile = get_profile_object()


if profile is None:

    render_html(
        """
        <div class="empty-card">

            <div style="
                font-size:44px;
                margin-bottom:10px;
            ">
                📄
            </div>

            <div style="
                font-size:21px;
                font-weight:800;
                color:#111827;
            ">
                No candidate profile available yet
            </div>

            <div style="
                margin-top:8px;
                line-height:1.6;
            ">
                Upload and analyze your resume first.
                Your extracted candidate profile will
                appear here.
            </div>

        </div>
        """
    )

    st.write("")

    st.page_link(
        "pages/5_Resume_Analyzer.py",
        label="📄 Open Resume Analyzer",
    )

    st.stop()


# ============================================================
# PROFILE FIELDS
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

    sections = [
        key
        for key, value in sections_raw.items()
        if value
    ]

else:

    sections = normalize_list(
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
# INITIALS
# ============================================================

parts = [
    x
    for x in name.split()
    if x
]

if len(parts) >= 2:

    initials = (
        parts[0][0]
        + parts[-1][0]
    ).upper()

elif parts:

    initials = (
        parts[0][0]
    ).upper()

else:

    initials = "C"


# ============================================================
# IDENTITY
# ============================================================

render_html(
    f"""
    <div class="identity-card">

        <div style="
            display:flex;
            align-items:center;
            gap:22px;
        ">

            <div class="avatar">
                {html.escape(initials)}
            </div>

            <div style="flex:1;">

                <div class="identity-name">
                    {html.escape(name)}
                </div>

                <div class="identity-role">
                    Extracted candidate profile
                </div>

                <span class="status">
                    ✓ PROFILE READY
                </span>

            </div>

        </div>

    </div>
    """
)


# ============================================================
# KPIs
# ============================================================

c1, c2, c3, c4 = st.columns(4)


with c1:

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


with c2:

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


with c3:

    render_html(
        f"""
        <div class="kpi-card">
            <div class="kpi-icon">🎓</div>
            <div class="kpi-label">Education Entries</div>
            <div class="kpi-value">
                {len(education)}
            </div>
        </div>
        """
    )


with c4:

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
        📇 Contact & Profile Details
    </div>

    <div class="section-subtitle">
        Core information extracted from your analyzed resume.
    </div>
    """
)


contact1, contact2 = st.columns(2)


with contact1:

    render_html(
        f"""
        <div class="content-card">

            <div class="card-heading">
                📧 Contact Information
            </div>

            <div class="info-label">
                Email
            </div>

            <div class="info-value">
                {html.escape(email)}
            </div>

            <div class="info-label">
                Phone
            </div>

            <div class="info-value">
                {html.escape(phone)}
            </div>

        </div>
        """
    )


with contact2:

    render_html(
        f"""
        <div class="content-card">

            <div class="card-heading">
                💼 Professional Experience
            </div>

            <div class="info-label">
                Experience
            </div>

            <div class="info-value">
                {html.escape(experience)}
            </div>

            <div class="info-label">
                Resume Length
            </div>

            <div class="info-value">
                {word_count:,} words
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
        Skills extracted from the resume and used by the
        Job Matcher, Skill Gap and Recommendation modules.
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

education_html = list_html(
    education,
    "No education information detected.",
)


experience_html = (
    '<div class="list-item">'
    f'{html.escape(experience)}'
    '</div>'
)


education_col, experience_col = (
    st.columns(2)
)


with education_col:

    render_html(
        f"""
        <div class="content-card">

            <div class="card-heading">
                🎓 Education
            </div>

            {education_html}

        </div>
        """
    )


with experience_col:

    render_html(
        f"""
        <div class="content-card">

            <div class="card-heading">
                💼 Experience
            </div>

            {experience_html}

        </div>
        """
    )


# ============================================================
# CERTIFICATIONS / PROJECTS
# ============================================================

cert_html = list_html(
    certifications,
    "No certifications detected.",
)

project_html = list_html(
    projects,
    "No projects detected.",
)


cert_col, project_col = (
    st.columns(2)
)


with cert_col:

    render_html(
        f"""
        <div class="content-card">

            <div class="card-heading">
                🏆 Certifications
            </div>

            {cert_html}

        </div>
        """
    )


with project_col:

    render_html(
        f"""
        <div class="content-card">

            <div class="card-heading">
                🚀 Projects
            </div>

            {project_html}

        </div>
        """
    )


# ============================================================
# RESUME SECTIONS
# ============================================================

render_html(
    """
    <div class="section-title">
        📚 Resume Structure
    </div>

    <div class="section-subtitle">
        Sections identified during resume parsing.
    </div>
    """
)


if sections:

    section_html = ""

    for section in sections:

        section_html += (
            '<span class="section-chip">'
            f'{html.escape(str(section))}'
            '</span>'
        )

    render_html(
        f"""
        <div class="content-card">
            {section_html}
        </div>
        """
    )

else:

    render_html(
        """
        <div class="content-card">

            <span style="
                color:#94a3b8;
                font-size:13px;
            ">
                No resume sections detected.
            </span>

        </div>
        """
    )


# ============================================================
# PROFILE PIPELINE
# ============================================================

render_html(
    """
    <div class="section-title">
        🔗 How Your Profile Powers JobInsight
    </div>

    <div class="section-subtitle">
        Your extracted profile flows through the platform's
        career intelligence pipeline.
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
                Extracts candidate information,
                skills, education, projects and
                resume sections.
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
                Compares your profile with jobs using
                semantic relevance and skill coverage.
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
                Identifies missing capabilities against
                target jobs and market demand.
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
                Combines profile and job signals to
                generate career recommendation results.
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
            "No extracted resume text is available."
        )


# ============================================================
# METHODOLOGY
# ============================================================

with st.expander(
    "🧠 Profile & Analysis Methodology"
):

    st.markdown(
        """
        ### Candidate Profile

        JobInsight extracts structured information from
        the uploaded resume, including:

        - Candidate name
        - Contact information
        - Experience
        - Education
        - Skills
        - Certifications
        - Projects
        - Resume sections
        - Resume word count

        ### Downstream Integration

        The profile is used by:

        **Job Matcher**

        Semantic similarity and skill coverage compare
        the candidate profile with job opportunities.

        **Skill Gap**

        Candidate skills are compared with job requirements
        and broader market skill demand.

        **Career Recommendations**

        Candidate and job signals contribute to the
        recommendation pipeline.

        The recommendation score is an engineering/research
        ranking signal, not a probability of getting a job.
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

        Resume intelligence · Candidate profiling ·
        Job matching · Skill-gap analysis

    </div>
    """
)