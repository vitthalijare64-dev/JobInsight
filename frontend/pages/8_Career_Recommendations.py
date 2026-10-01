from pathlib import Path
import html

import pandas as pd
import plotly.express as px
import streamlit as st


# ============================================================
# PATH
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RECOMMENDATIONS_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "career_recommendations.csv"
)


# ============================================================
# PAGE
# ============================================================

st.set_page_config(
    page_title="Career Recommendations | JobInsight",
    page_icon="🚀",
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

    .hero {
        position: relative;
        overflow: hidden;
        padding: 36px 40px;
        border-radius: 26px;
        margin-bottom: 25px;
        color: white;

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
        font-size:26px;
        font-weight:800;
        color:#111827;
    }

    .filter-info {
        background:white;
        border:1px solid #e2e8f0;
        border-radius:17px;
        padding:14px 18px;
        margin-top:8px;
        color:#64748b;
        font-size:13px;
    }

    .job-card {
        background:rgba(255,255,255,.97);
        border:1px solid #e2e8f0;
        border-radius:23px;
        padding:25px;
        margin:15px 0;
        box-shadow:
            0 10px 28px rgba(15,23,42,.055);
    }

    .rank-badge {
        display:inline-block;
        padding:5px 10px;
        border-radius:999px;
        background:#eef2ff;
        color:#4338ca;
        font-size:11px;
        font-weight:800;
    }

    .job-title {
        font-size:22px;
        line-height:1.3;
        font-weight:800;
        color:#111827;
        margin-top:10px;
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
        margin-top:17px;
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

    .score-box {
        background:#f8fafc;
        border:1px solid #e2e8f0;
        border-radius:16px;
        padding:16px;
        margin-top:18px;
    }

    .score-number {
        font-size:31px;
        font-weight:850;
        color:#4338ca;
        text-align:right;
    }

    .score-label {
        font-size:10px;
        text-transform:uppercase;
        letter-spacing:.07em;
        color:#64748b;
        text-align:right;
    }

    .score-row {
        display:flex;
        justify-content:space-between;
        font-size:12px;
        color:#475569;
        margin-top:10px;
    }

    .score-row strong {
        color:#111827;
    }

    .track {
        height:7px;
        border-radius:999px;
        background:#e2e8f0;
        overflow:hidden;
        margin-top:6px;
    }

    .semantic-bar {
        height:100%;
        background:#818cf8;
        border-radius:999px;
    }

    .skill-bar {
        height:100%;
        background:#34d399;
        border-radius:999px;
    }

    .skill-label {
        margin-top:18px;
        margin-bottom:9px;
        font-size:11px;
        text-transform:uppercase;
        letter-spacing:.07em;
        font-weight:800;
    }

    .green-label {
        color:#047857;
    }

    .orange-label {
        color:#c2410c;
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
        background:#ecfdf5;
        border:1px solid #a7f3d0;
        color:#047857;
        font-size:12px;
        font-weight:650;
    }

    .missing-chip {
        display:inline-block;
        padding:7px 12px;
        border-radius:999px;
        background:#fff7ed;
        border:1px solid #fed7aa;
        color:#c2410c;
        font-size:12px;
        font-weight:650;
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


def clean_value(value, default="Not specified"):

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


def clean_skills(value):

    if value is None:
        return []

    try:
        if pd.isna(value):
            return []
    except Exception:
        pass

    if isinstance(
        value,
        (list, tuple, set),
    ):
        return [
            str(x).strip()
            for x in value
            if str(x).strip()
        ]

    text = str(value).strip()

    if not text or text.lower() in {
        "nan",
        "none",
        "null",
    }:
        return []

    return [
        x.strip()
        for x in text.split(",")
        if x.strip()
    ]


def safe_number(value):

    try:

        if pd.isna(value):
            return 0.0

        return float(value)

    except (
        TypeError,
        ValueError,
    ):

        return 0.0


def skill_html(
    skills,
    missing=False,
):

    skills = clean_skills(skills)

    if not skills:

        return (
            '<span style="'
            'color:#94a3b8;'
            'font-size:12px;'
            '">None detected</span>'
        )

    css_class = (
        "missing-chip"
        if missing
        else "skill-chip"
    )

    output = ""

    for skill in skills[:20]:

        output += (
            f'<span class="{css_class}">'
            f'{html.escape(skill)}'
            f'</span>'
        )

    if len(skills) > 20:

        output += (
            f'<span class="{css_class}">'
            f'+{len(skills) - 20} more'
            f'</span>'
        )

    return output


# ============================================================
# LOAD DATA
# ============================================================

if not RECOMMENDATIONS_PATH.exists():

    st.error(
        "Career recommendation data was not found."
    )

    st.stop()


try:

    df = pd.read_csv(
        RECOMMENDATIONS_PATH
    )

except Exception as exc:

    st.error(
        f"Could not load recommendation data: {exc}"
    )

    st.stop()


if df.empty:

    st.warning(
        "No career recommendations are available."
    )

    st.stop()


required_columns = [
    "title",
    "company_name",
    "work_model",
    "experience_level",
    "skill_match_percentage",
    "semantic_similarity",
    "recommendation_score",
    "matched_skills",
    "missing_skills",
]


missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
]


if missing_columns:

    st.error(
        "Missing required columns: "
        + ", ".join(missing_columns)
    )

    st.stop()


for column in [
    "title",
    "company_name",
    "work_model",
    "experience_level",
]:

    df[column] = df[column].apply(
        clean_value
    )


for column in [
    "skill_match_percentage",
    "semantic_similarity",
    "recommendation_score",
]:

    df[column] = pd.to_numeric(
        df[column],
        errors="coerce",
    ).fillna(0.0)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    # IMPORTANT:
    # Custom sidebar HTML uses st.html(), not st.markdown().

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
                🚀
            </div>

            <div style="
                margin-top:12px;
                font-size:18px;
                font-weight:800;
            ">
                Career Recommendations
            </div>

            <div style="
                margin-top:5px;
                font-size:12px;
                opacity:.70;
            ">
                AI-assisted opportunity discovery
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
                Recommendation Pipeline
            </div>

            <div>👤 Candidate Profile</div>
            <div>↓</div>
            <div>🧠 Semantic Relevance</div>
            <div>↓</div>
            <div>🧩 Skill Coverage</div>
            <div>↓</div>
            <div>📈 Market Signal</div>
            <div>↓</div>
            <div>🚀 Career Recommendations</div>

        </div>
        """
    )

    st.markdown("---")

    st.markdown(
        "### Recommendation Filters"
    )

    companies = sorted(
        [
            value
            for value in df[
                "company_name"
            ].unique()
            if value != "Not specified"
        ]
    )

    work_models = sorted(
        [
            value
            for value in df[
                "work_model"
            ].unique()
            if value != "Not specified"
        ]
    )

    selected_company = st.selectbox(
        "Company",
        ["All"] + companies,
    )

    selected_work_model = st.selectbox(
        "Work model",
        ["All"] + work_models,
    )

    min_skill_match = st.slider(
        "Minimum skill match (%)",
        min_value=0,
        max_value=100,
        value=0,
        step=5,
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
            JOBINSIGHT · CAREER INTELLIGENCE
        </div>

        <div class="hero-title">
            Discover opportunities aligned with your profile.
        </div>

        <div class="hero-subtitle">
            Explore recommended jobs using semantic relevance,
            skill coverage, and market-demand signals. Each
            recommendation exposes the underlying signals so
            you can understand the result.
        </div>

    </div>
    """
)


# ============================================================
# FILTER
# ============================================================

filtered = df.copy()


if selected_company != "All":

    filtered = filtered[
        filtered["company_name"]
        == selected_company
    ]


if selected_work_model != "All":

    filtered = filtered[
        filtered["work_model"]
        == selected_work_model
    ]


filtered = filtered[
    filtered["skill_match_percentage"]
    >= min_skill_match
]


filtered = filtered.sort_values(
    "recommendation_score",
    ascending=False,
)


filter_text = "All recommendations"

parts = []

if selected_company != "All":
    parts.append(
        f"Company: {selected_company}"
    )

if selected_work_model != "All":
    parts.append(
        f"Work model: {selected_work_model}"
    )

if min_skill_match > 0:
    parts.append(
        f"Skill match ≥ {min_skill_match}%"
    )

if parts:
    filter_text = " · ".join(parts)


render_html(
    f"""
    <div class="filter-info">
        <b>Active view:</b>
        {html.escape(filter_text)}
        &nbsp; • &nbsp;
        {len(filtered):,} recommendations
    </div>
    """
)


# ============================================================
# EMPTY
# ============================================================

if filtered.empty:

    st.info(
        "No recommendations match the selected filters."
    )

    st.stop()


# ============================================================
# KPI
# ============================================================

avg_skill = filtered[
    "skill_match_percentage"
].mean()

avg_semantic = filtered[
    "semantic_similarity"
].mean()

avg_score = filtered[
    "recommendation_score"
].mean()


c1, c2, c3, c4 = st.columns(4)


with c1:

    render_html(
        f"""
        <div class="kpi-card">
            <div class="kpi-icon">🗂️</div>
            <div class="kpi-label">Jobs Analyzed</div>
            <div class="kpi-value">
                {len(filtered):,}
            </div>
        </div>
        """
    )


with c2:

    render_html(
        f"""
        <div class="kpi-card">
            <div class="kpi-icon">🧩</div>
            <div class="kpi-label">Avg. Skill Match</div>
            <div class="kpi-value">
                {avg_skill:.1f}%
            </div>
        </div>
        """
    )


with c3:

    render_html(
        f"""
        <div class="kpi-card">
            <div class="kpi-icon">🧠</div>
            <div class="kpi-label">Avg. Semantic Relevance</div>
            <div class="kpi-value">
                {avg_semantic * 100:.1f}%
            </div>
        </div>
        """
    )


with c4:

    render_html(
        f"""
        <div class="kpi-card">
            <div class="kpi-icon">🚀</div>
            <div class="kpi-label">Avg. Recommendation Score</div>
            <div class="kpi-value">
                {avg_score:.1f}
            </div>
        </div>
        """
    )


# ============================================================
# OVERVIEW
# ============================================================

render_html(
    """
    <div class="section-title">
        📈 Recommendation Overview
    </div>

    <div class="section-subtitle">
        Top recommendation scores in the current result set.
    </div>
    """
)


chart_df = filtered.head(10).copy()

chart_df["job_label"] = (
    chart_df["title"]
    + " — "
    + chart_df["company_name"]
)


fig = px.bar(
    chart_df.sort_values(
        "recommendation_score"
    ),
    x="recommendation_score",
    y="job_label",
    orientation="h",
    text="recommendation_score",
    labels={
        "recommendation_score":
            "Recommendation Score",
        "job_label": "",
    },
)


fig.update_traces(
    texttemplate="%{text:.2f}",
    textposition="outside",
)


fig.update_layout(
    height=max(
        450,
        len(chart_df) * 55,
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
# JOB CARDS
# ============================================================

render_html(
    """
    <div class="section-title">
        💼 Recommended Opportunities
    </div>

    <div class="section-subtitle">
        Review the signals behind each recommendation.
    </div>
    """
)


for rank, (_, row) in enumerate(
    filtered.head(10).iterrows(),
    start=1,
):

    title = clean_value(
        row["title"],
        "Untitled position",
    )

    company = clean_value(
        row["company_name"],
        "Company not specified",
    )

    work_model = clean_value(
        row["work_model"]
    )

    experience = clean_value(
        row["experience_level"]
    )

    score = safe_number(
        row["recommendation_score"]
    )

    semantic = safe_number(
        row["semantic_similarity"]
    )

    skill_match = safe_number(
        row["skill_match_percentage"]
    )

    matched = clean_skills(
        row["matched_skills"]
    )

    missing = clean_skills(
        row["missing_skills"]
    )

    semantic_pct = max(
        0,
        min(
            100,
            semantic * 100,
        ),
    )

    skill_pct = max(
        0,
        min(
            100,
            skill_match,
        ),
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
                        #{rank} RECOMMENDATION
                    </span>

                    <div class="job-title">
                        {html.escape(title)}
                    </div>

                    <div class="company">
                        🏢 {html.escape(company)}
                    </div>

                </div>

                <div style="
                    min-width:125px;
                ">

                    <div class="score-number">
                        {score:.2f}
                    </div>

                    <div class="score-label">
                        Recommendation Score
                    </div>

                </div>

            </div>

            <div class="meta-row">

                <span class="meta-chip">
                    💼 {html.escape(work_model)}
                </span>

                <span class="meta-chip">
                    🎯 {html.escape(experience)}
                </span>

            </div>

            <div class="score-box">

                <div class="score-row">
                    <span>Semantic relevance</span>
                    <strong>
                        {semantic_pct:.1f}%
                    </strong>
                </div>

                <div class="track">
                    <div
                        class="semantic-bar"
                        style="
                            width:{semantic_pct}%;
                        "
                    ></div>
                </div>

                <div class="score-row">
                    <span>Skill coverage</span>
                    <strong>
                        {skill_match:.1f}%
                    </strong>
                </div>

                <div class="track">
                    <div
                        class="skill-bar"
                        style="
                            width:{skill_pct}%;
                        "
                    ></div>
                </div>

            </div>

            <div class="skill-label green-label">
                ✅ Matched Skills
            </div>

            <div class="skill-wrap">
                {skill_html(matched)}
            </div>

            <div class="skill-label orange-label">
                📌 Skills to Develop
            </div>

            <div class="skill-wrap">
                {skill_html(
                    missing,
                    missing=True
                )}
            </div>

        </div>
        """
    )


# ============================================================
# METHODOLOGY
# ============================================================

with st.expander(
    "🧠 How are recommendations calculated?"
):

    st.markdown(
        """
        ### Recommendation Methodology

        The recommendation pipeline combines:

        **Semantic relevance**

        Measures similarity between the candidate profile
        and job information using semantic embeddings.

        **Skill coverage**

        Measures how many detected job skills are already
        present in the candidate profile.

        **Market signal**

        Incorporates market-demand information used by the
        recommendation pipeline.

        The recommendation score is an engineering/research
        ranking signal, not a probability of getting a job.
        """
    )


# ============================================================
# DATA
# ============================================================

with st.expander(
    "ℹ️ Recommendation Data"
):

    st.write(
        f"Recommendation dataset: "
        f"{RECOMMENDATIONS_PATH}"
    )

    st.write(
        f"Total records: {len(df):,}"
    )

    st.write(
        f"Filtered records: {len(filtered):,}"
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

        Semantic relevance · Skill coverage ·
        Market intelligence · Career discovery

    </div>
    """
)