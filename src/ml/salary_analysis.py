from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "salary_normalized.parquet"
)


def main():
    df = pd.read_parquet(DATA_PATH)

    salary = pd.to_numeric(
        df["annual_salary_min_usd"],
        errors="coerce",
    ).dropna()

    salary = salary[salary > 0]

    print("=" * 60)
    print("JobInsight - Salary Distribution Analysis")
    print("=" * 60)

    print(f"Valid salaries: {len(salary):,}")

    print("\nBasic statistics:")
    print(
        salary.describe(
            percentiles=[
                0.01,
                0.05,
                0.25,
                0.50,
                0.75,
                0.95,
                0.99,
            ]
        ).to_string()
    )

    print("\nExtreme salary values:")
    print(
        salary.nlargest(10)
        .to_string(index=False)
    )

    print("\nLowest salary values:")
    print(
        salary.nsmallest(10)
        .to_string(index=False)
    )

    print("\nSalary ranges:")

    ranges = pd.cut(
        salary,
        bins=[
            0,
            20_000,
            40_000,
            60_000,
            80_000,
            100_000,
            150_000,
            200_000,
            300_000,
            float("inf"),
        ],
        labels=[
            "< $20K",
            "$20K-$40K",
            "$40K-$60K",
            "$60K-$80K",
            "$80K-$100K",
            "$100K-$150K",
            "$150K-$200K",
            "$200K-$300K",
            "$300K+",
        ],
    )

    distribution = (
        ranges
        .value_counts()
        .sort_index()
    )

    for salary_range, count in distribution.items():
        percentage = (
            count / len(salary) * 100
        )

        print(
            f"{salary_range:12} "
            f"{count:6,} jobs "
            f"({percentage:5.2f}%)"
        )

    print("=" * 60)


if __name__ == "__main__":
    main()