from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

PROCESSED_DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "jobs_processed.parquet"
)

OUTPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "salary_normalized.parquet"
)


# Approximate reference rates to USD.
# These are intended for project normalization, not
# financial or real-time currency conversion.
CURRENCY_TO_USD = {
    "USD": 1.00,
    "CAD": 0.73,
    "EUR": 1.08,
    "GBP": 1.27,
    "AUD": 0.65,
    "NZD": 0.60,
    "INR": 0.012,
    "JPY": 0.0067,
    "CNY": 0.138,
    "CHF": 1.13,
    "SGD": 0.74,
    "HKD": 0.128,
    "MYR": 0.22,
    "PHP": 0.017,
    "PKR": 0.0036,
    "MXN": 0.049,
    "BRL": 0.19,
    "ZAR": 0.055,
    "NOK": 0.094,
    "SEK": 0.095,
    "DKK": 0.145,
    "CZK": 0.043,
    "PLN": 0.25,
    "UAH": 0.024,
    "RUB": 0.012,
}


def normalize_rate_unit(value):
    """Normalize salary rate-unit labels."""

    if pd.isna(value):
        return None

    value = str(value).strip().lower()

    mapping = {
        "hour": "hour",
        "hourly": "hour",
        "hr": "hour",

        "day": "day",
        "daily": "day",

        "week": "week",
        "weekly": "week",

        "month": "month",
        "monthly": "month",

        "year": "year",
        "yearly": "year",
        "annual": "year",
        "annually": "year",
    }

    return mapping.get(value, value)


def convert_to_annual_salary(
    salary,
    rate_unit
):
    """
    Convert salary to an approximate annual amount
    based on the stated rate unit.
    """

    if pd.isna(salary):
        return None

    try:
        salary = float(salary)
    except (TypeError, ValueError):
        return None

    rate_unit = normalize_rate_unit(
        rate_unit
    )

    multipliers = {
        "hour": 2080,
        "day": 260,
        "week": 52,
        "month": 12,
        "year": 1,
    }

    multiplier = multipliers.get(
        rate_unit
    )

    if multiplier is None:
        return None

    return salary * multiplier


def normalize_salary_data(
    df: pd.DataFrame
) -> pd.DataFrame:
    """Create normalized annual salary values in USD."""

    data = df.copy()

    data["salary_min"] = pd.to_numeric(
        data["salary_min"],
        errors="coerce"
    )

    data["salary_max"] = pd.to_numeric(
        data["salary_max"],
        errors="coerce"
    )

    data["annual_salary_min_local"] = data.apply(
        lambda row: convert_to_annual_salary(
            row["salary_min"],
            row["salary_rate_unit"]
        ),
        axis=1
    )

    data["annual_salary_max_local"] = data.apply(
        lambda row: convert_to_annual_salary(
            row["salary_max"],
            row["salary_rate_unit"]
        ),
        axis=1
    )

    data["currency_to_usd"] = (
        data["salary_currency"]
        .astype(str)
        .str.upper()
        .map(CURRENCY_TO_USD)
    )

    data["annual_salary_min_usd"] = (
        data["annual_salary_min_local"]
        * data["currency_to_usd"]
    )

    data["annual_salary_max_usd"] = (
        data["annual_salary_max_local"]
        * data["currency_to_usd"]
    )

    # Remove impossible/non-positive values.
    data.loc[
        data["annual_salary_min_usd"] <= 0,
        "annual_salary_min_usd"
    ] = None

    data.loc[
        data["annual_salary_max_usd"] <= 0,
        "annual_salary_max_usd"
    ] = None

    return data


if __name__ == "__main__":
    print("=" * 60)
    print("JobInsight - Salary Normalization")
    print("=" * 60)

    if not PROCESSED_DATA_PATH.exists():
        raise FileNotFoundError(
            f"Processed dataset not found at: "
            f"{PROCESSED_DATA_PATH}"
        )

    jobs = pd.read_parquet(
        PROCESSED_DATA_PATH
    )

    print(
        f"Input jobs: {len(jobs):,}"
    )

    normalized = normalize_salary_data(
        jobs
    )

    valid_min = normalized[
        "annual_salary_min_usd"
    ].notna().sum()

    valid_max = normalized[
        "annual_salary_max_usd"
    ].notna().sum()

    print(
        f"Valid normalized minimum salaries: "
        f"{valid_min:,}"
    )

    print(
        f"Valid normalized maximum salaries: "
        f"{valid_max:,}"
    )

    print("\nExample normalized salaries:")

    example_columns = [
        "title",
        "salary_min",
        "salary_max",
        "salary_currency",
        "salary_rate_unit",
        "annual_salary_min_usd",
        "annual_salary_max_usd",
    ]

    print(
        normalized[
            example_columns
        ]
        .dropna(
            subset=["annual_salary_min_usd"]
        )
        .head(10)
        .to_string(index=False)
    )

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    normalized.to_parquet(
        OUTPUT_PATH,
        index=False
    )

    print("\nSaved:")
    print(OUTPUT_PATH)

    print("=" * 60)
    print(
        "Salary normalization completed successfully."
    )
    print("=" * 60)