from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

SALARY_PATH = PROCESSED_DIR / "salary_normalized.parquet"
NORMALIZED_JOBS_PATH = PROCESSED_DIR / "jobs_normalized.parquet"
MODEL_DATA_PATH = PROCESSED_DIR / "salary_model_data.parquet"
FEATURE_IMPORTANCE_PATH = PROCESSED_DIR / "salary_feature_importance.csv"


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Salary Intelligence | JobInsight",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# GLOBAL STYLE
# ============================================================

st.markdown(
    """
    <style>
    [data-testid="stAppViewContainer"] {
        background: #f5f7fb;
    }

    [data-testid="stHeader"] {
        background: transparent;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #111827 0%, #1e293b 100%);
    }

    [data-testid="stSidebar"] * {
        color: #e5e7eb;
    }

    .block-container {
        max-width: 1450px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    div[data-testid="stMetric"] {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 18px;
        padding: 18px 20px;
        box-shadow: 0 8px 24px rgba(15, 23, 42, .05);
    }

    div[data-testid="stMetricLabel"] {
        color: #64748b;
    }

    div[data-testid="stMetricValue"] {
        color: #0f172a;
    }

    .section-title {
        font-size: 1.35rem;
        font-weight: 800;
        color: #0f172a;
        margin: 1.5rem 0 .25rem 0;
    }

    .section-subtitle {
        color: #64748b;
        font-size: .94rem;
        margin-bottom: 1rem;
        line-height: 1.6;
    }

    .salary-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 20px;
        padding: 24px;
        box-shadow: 0 8px 24px rgba(15, 23, 42, .05);
    }

    .salary-card-title {
        font-size: 1.25rem;
        font-weight: 800;
        color: #0f172a;
    }

    .salary-card-label {
        color: #64748b;
        font-size: .9rem;
        margin-top: 10px;
    }

    .salary-card-value {
        color: #2563eb;
        font-size: 2.15rem;
        font-weight: 900;
        margin: 6px 0;
    }

    .model-card {
        background: linear-gradient(135deg, #0f172a, #1e3a8a);
        border-radius: 20px;
        padding: 24px;
        color: white;
        box-shadow: 0 12px 30px rgba(15, 23, 42, .14);
    }

    .model-card-title {
        font-size: 1.15rem;
        font-weight: 800;
        margin-bottom: 6px;
    }

    .model-card-text {
        color: #cbd5e1;
        font-size: .9rem;
        line-height: 1.6;
    }

    .footer {
        text-align: center;
        color: #94a3b8;
        font-size: .82rem;
        padding: 30px 0 10px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# DATA LOADING
# ============================================================

@st.cache_data
def load_salary_data():

    if not SALARY_PATH.exists():
        st.error(f"Salary dataset not found:\n{SALARY_PATH}")
        st.stop()

    if not NORMALIZED_JOBS_PATH.exists():
        st.error(
            f"Normalized job dataset not found:\n"
            f"{NORMALIZED_JOBS_PATH}"
        )
        st.stop()

    salary = pd.read_parquet(SALARY_PATH)
    jobs = pd.read_parquet(NORMALIZED_JOBS_PATH)

    if "annual_salary_min_usd" not in salary.columns:
        st.error(
            "annual_salary_min_usd was not found "
            "in salary_normalized.parquet."
        )
        st.stop()

    salary = salary.reset_index(drop=True)
    jobs = jobs.reset_index(drop=True)

    if len(salary) != len(jobs):
        st.error(
            "Salary and normalized job datasets have different "
            "row counts. They cannot be safely combined."
        )
        st.stop()

    salary["annual_salary_min_usd"] = pd.to_numeric(
        salary["annual_salary_min_usd"],
        errors="coerce",
    )

    if "annual_salary_max_usd" in salary.columns:
        salary["annual_salary_max_usd"] = pd.to_numeric(
            salary["annual_salary_max_usd"],
            errors="coerce",
        )

    normalized_columns = [
        "title",
        "normalized_title",
        "company_name",
        "industry",
        "function",
        "country",
        "work_model",
        "experience_level",
        "employment_type",
        "education_level",
        "date_posted",
    ]

    for column in normalized_columns:
        if column in jobs.columns:
            salary[column] = jobs[column].values

    return salary


@st.cache_data
def load_model_data():

    if not MODEL_DATA_PATH.exists():
        return pd.DataFrame()

    data = pd.read_parquet(MODEL_DATA_PATH)

    if "annual_salary_min_usd" in data.columns:
        data["annual_salary_min_usd"] = pd.to_numeric(
            data["annual_salary_min_usd"],
            errors="coerce",
        )

    return data


@st.cache_data
def load_feature_importance():

    if not FEATURE_IMPORTANCE_PATH.exists():
        return pd.DataFrame()

    return pd.read_csv(FEATURE_IMPORTANCE_PATH)


with st.spinner("Loading salary intelligence..."):
    salary = load_salary_data()
    model_data = load_model_data()
    feature_importance = load_feature_importance()


# ============================================================
# VALID SALARY DATA
# ============================================================

valid_salary = salary[
    salary["annual_salary_min_usd"].notna()
].copy()


if not valid_salary.empty:

    lower_bound = valid_salary[
        "annual_salary_min_usd"
    ].quantile(.01)

    upper_bound = valid_salary[
        "annual_salary_min_usd"
    ].quantile(.99)

    visualization_salary = valid_salary[
        valid_salary["annual_salary_min_usd"].between(
            lower_bound,
            upper_bound,
        )
    ].copy()

else:

    lower_bound = 0
    upper_bound = 0
    visualization_salary = valid_salary.copy()


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
                💰
            </div>

            <div style="
                margin-top:12px;
                font-size:18px;
                font-weight:800;
            ">
                Salary Intelligence
            </div>

            <div style="
                margin-top:5px;
                font-size:12px;
                opacity:.70;
            ">
                Compensation & salary analytics
            </div>

        </div>
        """
    )

    st.markdown("### Salary Filters")

    if "experience_level" in valid_salary.columns:

        experience_options = ["All"] + sorted(
            valid_salary["experience_level"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        selected_experience = st.selectbox(
            "Experience Level",
            experience_options,
        )

    else:
        selected_experience = "All"

    if "work_model" in valid_salary.columns:

        work_options = ["All"] + sorted(
            valid_salary["work_model"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        selected_work_model = st.selectbox(
            "Work Model",
            work_options,
        )

    else:
        selected_work_model = "All"

    st.markdown("---")

    st.caption(
        "Filters affect the salary comparisons shown below."
    )


# ============================================================
# FILTERED DATA
# ============================================================

filtered_salary = valid_salary.copy()

if (
    selected_experience != "All"
    and "experience_level" in filtered_salary.columns
):

    filtered_salary = filtered_salary[
        filtered_salary["experience_level"]
        == selected_experience
    ]


if (
    selected_work_model != "All"
    and "work_model" in filtered_salary.columns
):

    filtered_salary = filtered_salary[
        filtered_salary["work_model"]
        == selected_work_model
    ]


# ============================================================
# HERO
# ============================================================

st.html(
    """
    <div style="
        position:relative;
        overflow:hidden;
        border-radius:28px;
        padding:38px 42px;
        margin-bottom:24px;
        background:
            radial-gradient(
                circle at 90% 15%,
                rgba(96,165,250,.25),
                transparent 28%
            ),
            radial-gradient(
                circle at 70% 100%,
                rgba(129,140,248,.18),
                transparent 30%
            ),
            linear-gradient(
                135deg,
                #0f172a 0%,
                #1e3a8a 55%,
                #312e81 100%
            );
        box-shadow:0 20px 50px rgba(15,23,42,.16);
    ">

        <div style="
            display:inline-block;
            padding:6px 12px;
            border-radius:999px;
            background:rgba(255,255,255,.12);
            color:#dbeafe;
            font-size:.78rem;
            font-weight:700;
            margin-bottom:14px;
        ">
            SALARY MARKET ANALYTICS
        </div>

        <div style="
            font-size:2.6rem;
            line-height:1.1;
            font-weight:900;
            color:white;
            letter-spacing:-.04em;
        ">
            Salary Intelligence
        </div>

        <div style="
            color:#cbd5e1;
            font-size:1rem;
            max-width:820px;
            margin-top:10px;
            line-height:1.7;
        ">
            Explore salary distributions, compensation patterns across
            job characteristics, and the machine-learning model developed
            to estimate annual minimum salary.
        </div>
    </div>
    """
)


# ============================================================
# KPI SECTION
# ============================================================

salary_count = len(valid_salary)

median_salary = (
    valid_salary["annual_salary_min_usd"].median()
    if salary_count
    else 0
)

mean_salary = (
    valid_salary["annual_salary_min_usd"].mean()
    if salary_count
    else 0
)

p75_salary = (
    valid_salary["annual_salary_min_usd"].quantile(.75)
    if salary_count
    else 0
)


k1, k2, k3, k4 = st.columns(4)

k1.metric(
    "Valid Salary Records",
    f"{salary_count:,}",
)

k2.metric(
    "Median Salary",
    f"${median_salary:,.0f}",
)

k3.metric(
    "Mean Salary",
    f"${mean_salary:,.0f}",
)

k4.metric(
    "75th Percentile",
    f"${p75_salary:,.0f}",
)


# ============================================================
# SALARY DISTRIBUTION
# ============================================================

st.html(
    """
    <div class="section-title">📊 Salary Distribution</div>
    <div class="section-subtitle">
        Distribution of annual minimum salary after annualization and
        currency normalization. Extreme values are excluded from the
        visualization range.
    </div>
    """
)

if not visualization_salary.empty:

    fig = px.histogram(
        visualization_salary,
        x="annual_salary_min_usd",
        nbins=40,
        labels={
            "annual_salary_min_usd":
                "Annual Minimum Salary (USD)"
        },
    )

    fig.update_traces(
        hovertemplate=(
            "Salary: $%{x:,.0f}"
            "<br>Job records: %{y:,}"
            "<extra></extra>"
        )
    )

    fig.update_layout(
        height=500,
        margin=dict(l=20, r=25, t=20, b=30),
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(
            family="Inter, Arial, sans-serif",
            color="#334155",
        ),
        xaxis=dict(
            showgrid=True,
            gridcolor="#e2e8f0",
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="#e2e8f0",
        ),
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )

st.caption(
    f"Visualization range: ${lower_bound:,.0f} – "
    f"${upper_bound:,.0f}. Extreme salary values outside the "
    "1st–99th percentile are excluded from this visualization."
)


# ============================================================
# SALARY PERCENTILES
# ============================================================

st.html(
    """
    <div class="section-title">📈 Salary Percentiles</div>
    <div class="section-subtitle">
        Reference points showing how annual minimum salaries are
        distributed across the available salary records.
    </div>
    """
)

if not valid_salary.empty:

    percentiles = [
        .01,
        .05,
        .25,
        .50,
        .75,
        .95,
        .99,
    ]

    percentile_values = []

    for p in percentiles:

        value = valid_salary[
            "annual_salary_min_usd"
        ].quantile(p)

        percentile_values.append(
            {
                "Percentile": f"{int(p * 100)}th",
                "Annual Salary (USD)": round(
                    value,
                    2,
                ),
            }
        )

    percentile_df = pd.DataFrame(
        percentile_values
    )

    st.dataframe(
        percentile_df,
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# ACTIVE FILTER
# ============================================================

filter_text = []

if selected_experience != "All":
    filter_text.append(
        f"Experience: {selected_experience}"
    )

if selected_work_model != "All":
    filter_text.append(
        f"Work model: {selected_work_model}"
    )

if filter_text:

    st.caption(
        "Active filters — " + " · ".join(filter_text)
    )


# ============================================================
# SALARY BY EXPERIENCE
# ============================================================

st.html(
    """
    <div class="section-title">🎯 Salary by Experience Level</div>
    <div class="section-subtitle">
        Compare median annual minimum salary across experience levels.
    </div>
    """
)

if (
    "experience_level" in filtered_salary.columns
    and not filtered_salary.empty
):

    experience_salary = (
        filtered_salary
        .groupby("experience_level")[
            "annual_salary_min_usd"
        ]
        .agg(
            Median="median",
            Average="mean",
            Jobs="count",
        )
        .reset_index()
    )

    experience_order = [
        "Intern",
        "Entry",
        "Junior",
        "Mid",
        "Senior",
        "Lead",
        "Director",
        "Executive",
        "Unknown",
    ]

    experience_salary["sort_order"] = (
        experience_salary["experience_level"]
        .map(
            {
                value: index
                for index, value
                in enumerate(experience_order)
            }
        )
        .fillna(999)
    )

    experience_salary = (
        experience_salary
        .sort_values("sort_order")
        .drop(columns=["sort_order"])
    )

    fig_exp = px.bar(
        experience_salary,
        x="experience_level",
        y="Median",
        labels={
            "experience_level":
                "Experience Level",
            "Median":
                "Median Annual Salary (USD)",
        },
        category_orders={
            "experience_level":
                experience_order
        },
    )

    fig_exp.update_traces(
        hovertemplate=(
            "<b>%{x}</b>"
            "<br>Median salary: $%{y:,.0f}"
            "<extra></extra>"
        )
    )

    fig_exp.update_layout(
        height=450,
        margin=dict(l=20, r=25, t=20, b=30),
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(
            family="Inter, Arial, sans-serif",
            color="#334155",
        ),
        xaxis=dict(showgrid=False),
        yaxis=dict(
            showgrid=True,
            gridcolor="#e2e8f0",
        ),
    )

    st.plotly_chart(
        fig_exp,
        use_container_width=True,
    )

    display_experience = experience_salary.copy()

    display_experience["Median"] = (
        display_experience["Median"].round(0)
    )

    display_experience["Average"] = (
        display_experience["Average"].round(0)
    )

    st.dataframe(
        display_experience,
        use_container_width=True,
        hide_index=True,
    )

else:
    st.info("No salary records match the selected filters.")


# ============================================================
# SALARY BY WORK MODEL
# ============================================================

st.html(
    """
    <div class="section-title">🏢 Salary by Work Model</div>
    <div class="section-subtitle">
        Compare observed median salary across remote, hybrid,
        on-site, and unknown work arrangements.
    </div>
    """
)

if (
    "work_model" in filtered_salary.columns
    and not filtered_salary.empty
):

    work_salary = (
        filtered_salary
        .groupby("work_model")[
            "annual_salary_min_usd"
        ]
        .agg(
            Median="median",
            Average="mean",
            Jobs="count",
        )
        .reset_index()
    )

    work_order = [
        "Remote",
        "Hybrid",
        "On-site",
        "Unknown",
    ]

    work_salary["sort_order"] = (
        work_salary["work_model"]
        .map(
            {
                value: index
                for index, value
                in enumerate(work_order)
            }
        )
        .fillna(999)
    )

    work_salary = (
        work_salary
        .sort_values("sort_order")
        .drop(columns=["sort_order"])
    )

    fig_work = px.bar(
        work_salary,
        x="work_model",
        y="Median",
        labels={
            "work_model": "Work Model",
            "Median":
                "Median Annual Salary (USD)",
        },
        category_orders={
            "work_model": work_order
        },
    )

    fig_work.update_traces(
        hovertemplate=(
            "<b>%{x}</b>"
            "<br>Median salary: $%{y:,.0f}"
            "<extra></extra>"
        )
    )

    fig_work.update_layout(
        height=450,
        margin=dict(l=20, r=25, t=20, b=30),
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(
            family="Inter, Arial, sans-serif",
            color="#334155",
        ),
        xaxis=dict(showgrid=False),
        yaxis=dict(
            showgrid=True,
            gridcolor="#e2e8f0",
        ),
    )

    st.plotly_chart(
        fig_work,
        use_container_width=True,
    )


# ============================================================
# COUNTRY NORMALIZATION
# ============================================================

COUNTRY_MAP = {
    "us": "United States",
    "usa": "United States",
    "u.s.": "United States",
    "u.s.a.": "United States",
    "united states": "United States",
    "united states of america": "United States",
    "america": "United States",

    "ca": "Canada",
    "can": "Canada",
    "canada": "Canada",

    "uk": "United Kingdom",
    "gb": "United Kingdom",
    "great britain": "United Kingdom",
    "england": "United Kingdom",
    "united kingdom": "United Kingdom",

    "nl": "Netherlands",
    "netherlands": "Netherlands",
    "the netherlands": "Netherlands",
    "holland": "Netherlands",

    "de": "Germany",
    "ger": "Germany",
    "germany": "Germany",

    "fr": "France",
    "fra": "France",
    "france": "France",

    "au": "Australia",
    "aus": "Australia",
    "australia": "Australia",

    "in": "India",
    "ind": "India",
    "india": "India",

    "mx": "Mexico",
    "mex": "Mexico",
    "mexico": "Mexico",

    "es": "Spain",
    "esp": "Spain",
    "spain": "Spain",

    "it": "Italy",
    "ita": "Italy",
    "italy": "Italy",

    "cn": "China",
    "chn": "China",
    "china": "China",

    "ph": "Philippines",
    "phl": "Philippines",
    "philippines": "Philippines",

    "br": "Brazil",
    "bra": "Brazil",
    "brazil": "Brazil",

    "my": "Malaysia",
    "mys": "Malaysia",
    "malaysia": "Malaysia",

    "ie": "Ireland",
    "irl": "Ireland",
    "ireland": "Ireland",

    "za": "South Africa",
    "zaf": "South Africa",
    "south africa": "South Africa",

    "id": "Indonesia",
    "idn": "Indonesia",
    "indonesia": "Indonesia",

    "ae": "United Arab Emirates",
    "are": "United Arab Emirates",
    "uae": "United Arab Emirates",
    "united arab emirates": "United Arab Emirates",

    "ch": "Switzerland",
    "che": "Switzerland",
    "switzerland": "Switzerland",

    "sg": "Singapore",
    "sgp": "Singapore",
    "singapore": "Singapore",

    "co": "Colombia",
    "col": "Colombia",
    "colombia": "Colombia",

    "gr": "Greece",
    "grc": "Greece",
    "greece": "Greece",

    "jp": "Japan",
    "jpn": "Japan",
    "japan": "Japan",

    "at": "Austria",
    "aut": "Austria",
    "austria": "Austria",

    "pl": "Poland",
    "pol": "Poland",
    "poland": "Poland",

    "lt": "Lithuania",
    "ltu": "Lithuania",
    "lithuania": "Lithuania",

    "unknown": "Unknown",
    "nan": "Unknown",
    "none": "Unknown",
    "": "Unknown",
}


def normalize_country(value):

    if pd.isna(value):
        return "Unknown"

    value = str(value).strip()

    if not value:
        return "Unknown"

    return COUNTRY_MAP.get(
        value.lower(),
        value,
    )


# ============================================================
# SALARY BY COUNTRY
# ============================================================

st.html(
    """
    <div class="section-title">🌍 Salary by Country</div>
    <div class="section-subtitle">
        Countries with at least 20 salary records are included in
        the comparison to reduce the effect of very small groups.
    </div>
    """
)

if (
    "country" in filtered_salary.columns
    and not filtered_salary.empty
):

    country_salary_data = filtered_salary.copy()

    country_salary_data["country"] = (
        country_salary_data["country"]
        .apply(normalize_country)
    )

    country_salary = (
        country_salary_data
        .groupby("country")[
            "annual_salary_min_usd"
        ]
        .agg(
            Median="median",
            Jobs="count",
        )
        .reset_index()
    )

    country_salary = country_salary[
        country_salary["Jobs"] >= 20
    ]

    country_salary = (
        country_salary
        .sort_values(
            "Median",
            ascending=False,
        )
        .head(20)
    )

    fig_country = px.bar(
        country_salary.sort_values(
            "Median",
            ascending=True,
        ),
        x="Median",
        y="country",
        orientation="h",
        labels={
            "Median":
                "Median Annual Salary (USD)",
            "country": "Country",
        },
    )

    fig_country.update_traces(
        hovertemplate=(
            "<b>%{y}</b>"
            "<br>Median salary: $%{x:,.0f}"
            "<extra></extra>"
        )
    )

    fig_country.update_layout(
        height=600,
        margin=dict(l=20, r=25, t=20, b=30),
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(
            family="Inter, Arial, sans-serif",
            color="#334155",
        ),
        xaxis=dict(
            showgrid=True,
            gridcolor="#e2e8f0",
        ),
        yaxis=dict(showgrid=False),
    )

    st.plotly_chart(
        fig_country,
        use_container_width=True,
    )

    display_country = country_salary.copy()

    display_country["Median"] = (
        display_country["Median"].round(0)
    )

    display_country = display_country.rename(
        columns={
            "country": "Country",
            "Median": "Median Salary (USD)",
            "Jobs": "Job Records",
        }
    )

    st.dataframe(
        display_country,
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# SALARY BY JOB ROLE
# ============================================================

st.html(
    """
    <div class="section-title">💼 Salary by Job Role</div>
    <div class="section-subtitle">
        Compare the highest observed median salaries among roles
        with at least 20 salary records.
    </div>
    """
)

role_column = None

for candidate in [
    "normalized_title",
    "title",
]:

    if candidate in filtered_salary.columns:
        role_column = candidate
        break


if role_column:

    role_salary = (
        filtered_salary
        .groupby(role_column)[
            "annual_salary_min_usd"
        ]
        .agg(
            Median="median",
            Jobs="count",
        )
        .reset_index()
    )

    role_salary = role_salary[
        role_salary["Jobs"] >= 20
    ]

    role_salary = (
        role_salary
        .sort_values(
            "Median",
            ascending=False,
        )
        .head(20)
    )

    fig_role = px.bar(
        role_salary.sort_values(
            "Median",
            ascending=True,
        ),
        x="Median",
        y=role_column,
        orientation="h",
        labels={
            "Median":
                "Median Annual Salary (USD)",
            role_column:
                "Job Role",
        },
    )

    fig_role.update_traces(
        hovertemplate=(
            "<b>%{y}</b>"
            "<br>Median salary: $%{x:,.0f}"
            "<extra></extra>"
        )
    )

    fig_role.update_layout(
        height=650,
        margin=dict(l=20, r=25, t=20, b=30),
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(
            family="Inter, Arial, sans-serif",
            color="#334155",
        ),
        xaxis=dict(
            showgrid=True,
            gridcolor="#e2e8f0",
        ),
        yaxis=dict(showgrid=False),
    )

    st.plotly_chart(
        fig_role,
        use_container_width=True,
    )


# ============================================================
# MACHINE LEARNING MODEL
# ============================================================

st.html(
    """
    <div class="section-title">🤖 Salary Prediction Model</div>
    <div class="section-subtitle">
        JobInsight uses XGBoost regression to estimate annual minimum
        salary from selected job characteristics.
    </div>
    """
)

metric1, metric2, metric3 = st.columns(3)

metric1.metric(
    "XGBoost MAE",
    "$20,824.75",
)

metric2.metric(
    "XGBoost RMSE",
    "$29,318.75",
)

metric3.metric(
    "XGBoost R²",
    "0.3837",
)

st.caption(
    "Evaluation on the held-out test set from the salary-modeling "
    "dataset. R² indicates the proportion of variance explained "
    "by the model on that test split."
)


# ============================================================
# FEATURE IMPORTANCE
# ============================================================

st.html(
    """
    <div class="section-title">🔍 Model Feature Importance</div>
    <div class="section-subtitle">
        Encoded features with the largest model importance values.
        Importance indicates model contribution, not causation.
    </div>
    """
)

if not feature_importance.empty:

    importance_column = None

    for candidate in [
        "importance",
        "feature_importance",
        "Importance",
    ]:

        if candidate in feature_importance.columns:
            importance_column = candidate
            break

    feature_column = None

    for candidate in [
        "feature",
        "Feature",
        "feature_name",
    ]:

        if candidate in feature_importance.columns:
            feature_column = candidate
            break

    if importance_column and feature_column:

        importance_plot = feature_importance.copy()

        importance_plot[importance_column] = pd.to_numeric(
            importance_plot[importance_column],
            errors="coerce",
        )

        importance_plot = (
            importance_plot
            .dropna(
                subset=[importance_column]
            )
            .sort_values(
                importance_column,
                ascending=False,
            )
            .head(15)
        )

        fig_importance = px.bar(
            importance_plot.sort_values(
                importance_column,
                ascending=True,
            ),
            x=importance_column,
            y=feature_column,
            orientation="h",
            labels={
                importance_column: "Importance",
                feature_column: "Feature",
            },
        )

        fig_importance.update_traces(
            hovertemplate=(
                "<b>%{y}</b>"
                "<br>Importance: %{x:.3f}"
                "<extra></extra>"
            )
        )

        fig_importance.update_layout(
            height=600,
            margin=dict(l=20, r=25, t=20, b=30),
            plot_bgcolor="white",
            paper_bgcolor="white",
            font=dict(
                family="Inter, Arial, sans-serif",
                color="#334155",
            ),
            xaxis=dict(
                showgrid=True,
                gridcolor="#e2e8f0",
            ),
            yaxis=dict(showgrid=False),
        )

        st.plotly_chart(
            fig_importance,
            use_container_width=True,
        )

        st.dataframe(
            importance_plot[
                [
                    feature_column,
                    importance_column,
                ]
            ].reset_index(drop=True),
            use_container_width=True,
            hide_index=True,
        )


# ============================================================
# INTERACTIVE SALARY PREDICTION
# ============================================================

st.html(
    """
    <div class="section-title">🧮 Try a Salary Prediction</div>
    <div class="section-subtitle">
        Enter job characteristics and generate an estimated annual
        minimum salary using the JobInsight XGBoost model.
    </div>
    """
)

st.info(
    "The prediction is an estimate based on patterns in the "
    "JobInsight salary-modeling dataset."
)


prediction_col1, prediction_col2 = st.columns(2)


with prediction_col1:

    prediction_title = st.text_input(
        "Job Title",
        value="Data Scientist",
    )

    prediction_industry = st.text_input(
        "Industry",
        value="Technology",
    )

    prediction_function = st.text_input(
        "Function",
        value="Data Science",
    )

    prediction_employment = st.selectbox(
        "Employment Type",
        [
            "Full-time",
            "Part-time",
            "Contract",
            "Internship",
            "Temporary",
            "Freelance",
        ],
    )


with prediction_col2:

    prediction_work_model = st.selectbox(
        "Work Model",
        [
            "On-site",
            "Hybrid",
            "Remote",
            "Unknown",
        ],
    )

    prediction_experience = st.selectbox(
        "Experience Level",
        [
            "Entry",
            "Junior",
            "Mid",
            "Senior",
            "Lead",
            "Director",
            "Executive",
            "Intern",
            "Unknown",
        ],
        index=2,
    )

    prediction_education = st.selectbox(
        "Education Level",
        [
            "High School",
            "Associate",
            "Bachelor",
            "Master",
            "Doctorate",
            "Diploma / Certificate",
            "Unknown",
        ],
        index=2,
    )

    prediction_country = st.text_input(
        "Country",
        value="United States",
    )


# ============================================================
# TRAIN PREDICTION MODEL
# ============================================================

@st.cache_resource
def train_prediction_model():

    from sklearn.compose import ColumnTransformer
    from sklearn.metrics import mean_absolute_error
    from sklearn.model_selection import train_test_split
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import OneHotEncoder
    from xgboost import XGBRegressor

    if model_data.empty:
        return None

    feature_columns = [
        "title",
        "industry",
        "function",
        "employment_type",
        "work_model",
        "experience_level",
        "education_level",
        "country",
    ]

    missing_columns = [
        column
        for column in feature_columns
        if column not in model_data.columns
    ]

    if missing_columns:
        return None

    training_data = model_data[
        feature_columns
        + ["annual_salary_min_usd"]
    ].copy()

    training_data = training_data.dropna(
        subset=["annual_salary_min_usd"]
    )

    if len(training_data) < 100:
        return None

    X = training_data[
        feature_columns
    ].fillna("Unknown")

    y = training_data[
        "annual_salary_min_usd"
    ]

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "categorical",
                OneHotEncoder(
                    handle_unknown="ignore"
                ),
                feature_columns,
            )
        ]
    )

    model = XGBRegressor(
        n_estimators=300,
        max_depth=6,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        objective="reg:squarederror",
        random_state=42,
        n_jobs=-1,
    )

    pipeline = Pipeline(
        [
            (
                "preprocessor",
                preprocessor,
            ),
            (
                "model",
                model,
            ),
        ]
    )

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=.20,
        random_state=42,
    )

    pipeline.fit(
        X_train,
        y_train,
    )

    predictions = pipeline.predict(
        X_test
    )

    mae = mean_absolute_error(
        y_test,
        predictions,
    )

    return pipeline, mae


# ============================================================
# PREDICT
# ============================================================

if st.button(
    "🔮 Predict Salary",
    use_container_width=True,
):

    with st.spinner(
        "Preparing the salary prediction model..."
    ):

        result = train_prediction_model()

    if result is None:

        st.error(
            "The salary prediction model could not be prepared "
            "from the available model data."
        )

    else:

        model, current_mae = result

        prediction_input = pd.DataFrame(
            [
                {
                    "title": prediction_title,
                    "industry": prediction_industry,
                    "function": prediction_function,
                    "employment_type": prediction_employment,
                    "work_model": prediction_work_model,
                    "experience_level": prediction_experience,
                    "education_level": prediction_education,
                    "country": prediction_country,
                }
            ]
        )

        prediction = model.predict(
            prediction_input
        )[0]

        prediction = max(
            0,
            float(prediction),
        )

        st.html(
            f"""
            <div class="salary-card"
                 style="margin-top:18px;text-align:center;">

                <div class="salary-card-label">
                    Estimated Annual Minimum Salary
                </div>

                <div class="salary-card-value">
                    ${prediction:,.0f}
                </div>

                <div class="salary-card-label">
                    Model estimate based on JobInsight salary data
                </div>

            </div>
            """
        )

        st.caption(
            "This is a model estimate based on patterns in the "
            "JobInsight dataset. It is not a guaranteed salary "
            "offer or market quote."
        )


# ============================================================
# METHODOLOGY
# ============================================================

with st.expander("📘 Salary Intelligence Methodology"):

    st.markdown(
        """
        ### Salary normalization

        Salary values from different pay frequencies and currencies
        were converted into an annualized USD representation for
        analytical modeling.

        ### Outlier handling

        The salary modeling dataset uses the 1st and 99th percentile
        boundaries to reduce the influence of extreme salary values.

        ### Machine learning

        The primary advanced model is XGBoost regression.

        ### Features

        - Job title
        - Industry
        - Function
        - Employment type
        - Work model
        - Experience level
        - Education level
        - Country

        ### Interpretation

        Model feature importance indicates which encoded features
        contributed most to the model's predictions. It does not
        establish causation.

        Salary predictions should therefore be treated as estimates
        rather than guarantees.
        """
    )


# ============================================================
# FOOTER
# ============================================================

st.html(
    """
    <div class="footer">
        JobInsight · Salary Intelligence · AI-Powered Job Market Analytics
    </div>
    """
)