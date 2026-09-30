from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "salary_normalized.parquet"
)

OUTPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "salary_model_data.parquet"
)


def main():
    df = pd.read_parquet(INPUT_PATH)

    salary = pd.to_numeric(
        df["annual_salary_min_usd"],
        errors="coerce",
    )

    valid_salary = salary[
        salary.notna() & (salary > 0)
    ]

    lower_bound = valid_salary.quantile(0.01)
    upper_bound = valid_salary.quantile(0.99)

    model_df = df[
        salary.between(
            lower_bound,
            upper_bound
        )
    ].copy()

    print("=" * 60)
    print("JobInsight - Salary Modeling Dataset")
    print("=" * 60)

    print(
        f"Original valid salaries: "
        f"{len(valid_salary):,}"
    )

    print(
        f"Lower boundary (1%): "
        f"${lower_bound:,.2f}"
    )

    print(
        f"Upper boundary (99%): "
        f"${upper_bound:,.2f}"
    )

    print(
        f"Modeling records: "
        f"{len(model_df):,}"
    )

    removed = (
        len(valid_salary) - len(model_df)
    )

    print(
        f"Excluded extreme records: "
        f"{removed:,}"
    )

    print("\nModeling salary statistics:")

    print(
        model_df[
            "annual_salary_min_usd"
        ]
        .describe()
        .to_string()
    )

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    model_df.to_parquet(
        OUTPUT_PATH,
        index=False
    )

    print("\nSaved:")
    print(OUTPUT_PATH)

    print("=" * 60)
    print(
        "Salary modeling dataset created successfully."
    )
    print("=" * 60)


if __name__ == "__main__":
    main()