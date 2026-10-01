from pathlib import Path
import html

import pandas as pd
import plotly.express as px
import streamlit as st


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

SKILL_DEMAND_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "skill_demand.csv"
)

ROLE_SKILL_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "role_skill_demand.csv"
)

COOCCURRENCE_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "skill_cooccurrence.csv"
)

JOB_SKILLS_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "job_skills_normalized.parquet"
)


# ============================================================
# PAGE
# ============================================================

st.set_page_config(
    page_title="Skills Intelligence | JobInsight",
    page_icon="🧠",
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

    .skill-card {
        background:white;
        border:1px solid #e2e8f0;
        border-radius:20px;
        padding:25px;
        box-shadow:0 8px 24px rgba(15,23,42,.05);
    }

    .skill-name {
        font-size:23px;
        font-weight:800;
        color:#111827;
    }

    .skill-number {
        margin-top:10px;
        font-size:34px;
        font-weight:850;
        color:#4338ca;
    }

    .skill-caption {
        color:#64748b;
        font-size:12px;
    }

    .insight-card {
        background:white;
        border:1px solid #e2e8f0;
        border-radius:20px;
        padding:22px;
        min-height:140px;
        box-shadow:0 8px 24px rgba(15,23,42,.045);
    }

    .insight-title {
        font-size:15px;
        font-weight:800;
        color:#111827;
        margin-bottom:9px;
    }

    .insight-text {
        color:#64748b;
        font-size:13px;
        line-height:1.65;
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


def find_column(
    df,
    candidates,
):

    for candidate in candidates:

        if candidate in df.columns:
            return candidate

    return None


def clean_text(
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

    return text


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_data():

    skill_demand = pd.read_csv(
        SKILL_DEMAND_PATH
    )

    role_skill = pd.read_csv(
        ROLE_SKILL_PATH
    )

    cooccurrence = pd.read_csv(
        COOCCURRENCE_PATH
    )

    job_skills = pd.read_parquet(
        JOB_SKILLS_PATH
    )

    return (
        skill_demand,
        role_skill,
        cooccurrence,
        job_skills,
    )


try:

    (
        skill_demand,
        role_skill,
        cooccurrence,
        job_skills,
    ) = load_data()

except Exception as exc:

    st.error(
        f"Could not load skills data: {exc}"
    )

    st.stop()


# ============================================================
# NORMALIZE COLUMNS
# ============================================================

for dataframe in [
    skill_demand,
    role_skill,
    cooccurrence,
]:

    dataframe.columns = [
        str(column).strip()
        for column in dataframe.columns
    ]


# ============================================================
# COLUMN DETECTION
# ============================================================

skill_column = find_column(
    skill_demand,
    [
        "skill",
        "Skill",
        "canonical_skill",
        "normalized_skill",
    ],
)

count_column = find_column(
    skill_demand,
    [
        "job_count",
        "count",
        "frequency",
        "demand",
        "jobs",
    ],
)

role_column = find_column(
    role_skill,
    [
        "title",
        "role",
        "normalized_title",
        "job_title",
    ],
)

role_skill_column = find_column(
    role_skill,
    [
        "skill",
        "Skill",
        "canonical_skill",
        "normalized_skill",
    ],
)

role_count_column = find_column(
    role_skill,
    [
        "job_count",
        "count",
        "frequency",
        "demand",
        "jobs",
    ],
)

co_skill_a = find_column(
    cooccurrence,
    [
        "skill_a",
        "Skill A",
        "skill1",
        "skill_1",
    ],
)

co_skill_b = find_column(
    cooccurrence,
    [
        "skill_b",
        "Skill B",
        "skill2",
        "skill_2",
    ],
)

co_count = find_column(
    cooccurrence,
    [
        "job_count",
        "cooccurrence_count",
        "count",
        "frequency",
        "jobs",
    ],
)


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
                🧠
            </div>

            <div style="
                margin-top:12px;
                font-size:18px;
                font-weight:800;
            ">
                Skills Intelligence
            </div>

            <div style="
                margin-top:5px;
                font-size:12px;
                opacity:.70;
            ">
                Understand market skill demand
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
                Skills Pipeline
            </div>

            <div>📄 Job descriptions</div>
            <div>↓</div>
            <div>🧠 Skill extraction</div>
            <div>↓</div>
            <div>🔗 Normalization</div>
            <div>↓</div>
            <div>📊 Demand analysis</div>

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
            JOBINSIGHT · SKILLS INTELLIGENCE
        </div>

        <div class="hero-title">
            Understand which skills the market demands.
        </div>

        <div class="hero-subtitle">
            Explore skill demand across job postings, inspect
            skill requirements by role, and discover skills
            that frequently appear together.
        </div>

    </div>
    """
)


# ============================================================
# KPI
# ============================================================

unique_skills = (
    skill_demand[skill_column]
    .nunique()
    if skill_column
    else 0
)

skill_detections = 0

if count_column:

    skill_detections = pd.to_numeric(
        skill_demand[count_column],
        errors="coerce",
    ).fillna(0).sum()

relationship_count = len(
    role_skill
)

job_skill_records = len(
    job_skills
)


k1, k2, k3, k4 = st.columns(4)


with k1:

    render_html(
        f"""
        <div class="kpi-card">
            <div class="kpi-icon">🧠</div>
            <div class="kpi-label">Unique Skills</div>
            <div class="kpi-value">
                {unique_skills:,}
            </div>
        </div>
        """
    )


with k2:

    render_html(
        f"""
        <div class="kpi-card">
            <div class="kpi-icon">📈</div>
            <div class="kpi-label">Skill Detections</div>
            <div class="kpi-value">
                {skill_detections:,.0f}
            </div>
        </div>
        """
    )


with k3:

    render_html(
        f"""
        <div class="kpi-card">
            <div class="kpi-icon">🔗</div>
            <div class="kpi-label">Role-Skill Records</div>
            <div class="kpi-value">
                {relationship_count:,}
            </div>
        </div>
        """
    )


with k4:

    render_html(
        f"""
        <div class="kpi-card">
            <div class="kpi-icon">💼</div>
            <div class="kpi-label">Job-Skill Records</div>
            <div class="kpi-value">
                {job_skill_records:,}
            </div>
        </div>
        """
    )


# ============================================================
# TOP DEMAND
# ============================================================

render_html(
    """
    <div class="section-title">
        📈 Most Demanded Skills
    </div>

    <div class="section-subtitle">
        Skills ranked by the number of job records in which
        they were detected.
    </div>
    """
)


if skill_column and count_column:

    demand_chart = skill_demand.copy()

    demand_chart[count_column] = pd.to_numeric(
        demand_chart[count_column],
        errors="coerce",
    )

    demand_chart = (
        demand_chart
        .dropna(
            subset=[count_column]
        )
        .sort_values(
            count_column,
            ascending=False,
        )
        .head(20)
        .sort_values(
            count_column,
            ascending=True,
        )
    )

    fig = px.bar(
        demand_chart,
        x=count_column,
        y=skill_column,
        orientation="h",
        labels={
            count_column: "Jobs",
            skill_column: "Skill",
        },
    )

    fig.update_layout(
        height=600,
        margin=dict(
            l=20,
            r=20,
            t=25,
            b=20,
        ),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )

else:

    st.warning(
        "Skill demand columns could not be detected."
    )


# ============================================================
# SKILL EXPLORER
# ============================================================

render_html(
    """
    <div class="section-title">
        🔎 Explore a Skill
    </div>

    <div class="section-subtitle">
        Select an individual skill to inspect its market demand.
    </div>
    """
)


if skill_column:

    available_skills = sorted(
        skill_demand[
            skill_column
        ]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    if available_skills:

        selected_skill = st.selectbox(
            "Select a skill",
            available_skills,
        )

        selected_rows = skill_demand[
            skill_demand[
                skill_column
            ].astype(str)
            == selected_skill
        ]

        demand_value = 0

        if (
            not selected_rows.empty
            and count_column
        ):

            demand_value = pd.to_numeric(
                selected_rows.iloc[0][
                    count_column
                ],
                errors="coerce",
            )

            if pd.isna(
                demand_value
            ):
                demand_value = 0

        render_html(
            f"""
            <div class="skill-card">

                <div class="skill-name">
                    {html.escape(selected_skill)}
                </div>

                <div class="skill-caption">
                    Detected in approximately
                </div>

                <div class="skill-number">
                    {demand_value:,.0f}
                </div>

                <div class="skill-caption">
                    job records
                </div>

            </div>
            """
        )


# ============================================================
# ROLE SKILL
# ============================================================

render_html(
    """
    <div class="section-title">
        💼 Skill Demand by Role
    </div>

    <div class="section-subtitle">
        Inspect which skills appear most frequently for a
        selected role.
    </div>
    """
)


if (
    role_column
    and role_skill_column
    and role_count_column
):

    role_options = sorted(
        role_skill[
            role_column
        ]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    if role_options:

        selected_role = st.selectbox(
            "Select a job role",
            role_options,
        )

        role_data = role_skill[
            role_skill[
                role_column
            ].astype(str)
            == selected_role
        ].copy()

        role_data[
            role_count_column
        ] = pd.to_numeric(
            role_data[
                role_count_column
            ],
            errors="coerce",
        )

        role_data = (
            role_data
            .dropna(
                subset=[
                    role_count_column
                ]
            )
            .sort_values(
                role_count_column,
                ascending=False,
            )
            .head(15)
            .sort_values(
                role_count_column,
                ascending=True,
            )
        )

        fig_role = px.bar(
            role_data,
            x=role_count_column,
            y=role_skill_column,
            orientation="h",
            labels={
                role_count_column:
                    "Jobs",
                role_skill_column:
                    "Skill",
            },
        )

        fig_role.update_layout(
            height=500,
            margin=dict(
                l=20,
                r=20,
                t=20,
                b=20,
            ),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
        )

        st.plotly_chart(
            fig_role,
            use_container_width=True,
        )

else:

    st.info(
        "Role-skill columns could not be detected."
    )


# ============================================================
# CO-OCCURRENCE
# ============================================================

render_html(
    """
    <div class="section-title">
        🔗 Skill Co-occurrence
    </div>

    <div class="section-subtitle">
        Skill pairs that frequently appear together in
        job requirements.
    </div>
    """
)


if (
    co_skill_a
    and co_skill_b
    and co_count
):

    co_data = cooccurrence.copy()

    co_data[co_count] = pd.to_numeric(
        co_data[co_count],
        errors="coerce",
    )

    co_data = (
        co_data
        .dropna(
            subset=[co_count]
        )
        .sort_values(
            co_count,
            ascending=False,
        )
        .head(20)
    )

    co_data["skill_pair"] = (
        co_data[co_skill_a].astype(str)
        + " + "
        + co_data[co_skill_b].astype(str)
    )

    chart = co_data.copy()

    chart = chart.sort_values(
        co_count,
        ascending=True,
    )

    fig_co = px.bar(
        chart,
        x=co_count,
        y="skill_pair",
        orientation="h",
        labels={
            co_count: "Job Count",
            "skill_pair": "Skill Pair",
        },
    )

    fig_co.update_layout(
        height=600,
        margin=dict(
            l=20,
            r=20,
            t=20,
            b=20,
        ),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )

    st.plotly_chart(
        fig_co,
        use_container_width=True,
    )

    display_df = co_data[
        [
            co_skill_a,
            co_skill_b,
            co_count,
        ]
    ].copy()

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
    )

else:

    st.warning(
        "Co-occurrence columns could not be detected."
    )


# ============================================================
# INSIGHTS
# ============================================================

render_html(
    """
    <div class="section-title">
        💡 Skills Intelligence Insights
    </div>

    <div class="section-subtitle">
        How this analysis supports the broader JobInsight
        career intelligence pipeline.
    </div>
    """
)


i1, i2, i3 = st.columns(3)


with i1:

    render_html(
        """
        <div class="insight-card">

            <div class="insight-title">
                📈 Demand
            </div>

            <div class="insight-text">
                Skill demand counts show which capabilities
                occur most frequently across the analyzed
                job market.
            </div>

        </div>
        """
    )


with i2:

    render_html(
        """
        <div class="insight-card">

            <div class="insight-title">
                💼 Role Alignment
            </div>

            <div class="insight-text">
                Role-level skill analysis connects individual
                skills to specific job families and positions.
            </div>

        </div>
        """
    )


with i3:

    render_html(
        """
        <div class="insight-card">

            <div class="insight-title">
                🔗 Skill Relationships
            </div>

            <div class="insight-text">
                Co-occurrence analysis reveals capabilities
                that frequently appear together in job
                requirements.
            </div>

        </div>
        """
    )


# ============================================================
# METHODOLOGY
# ============================================================

with st.expander(
    "🧠 Skills Intelligence Methodology"
):

    st.markdown(
        """
        ### Skill Demand

        Normalized job-skill records are aggregated to
        estimate how frequently each skill appears.

        ### Role-Skill Analysis

        Job roles are connected to detected skills to
        understand role-specific demand.

        ### Co-occurrence

        Skill pairs are counted when they appear together
        in the same job-skill record.

        These measures describe patterns in the analyzed
        dataset and should not be interpreted as causal
        relationships.
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

        Skill demand · Role intelligence ·
        Skill relationships

    </div>
    """
)