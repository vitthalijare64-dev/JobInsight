from pathlib import Path

import pandas as pd
from xgboost import XGBRegressor

from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "salary_model_data.parquet"
)

OUTPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "salary_feature_importance.csv"
)

FEATURES = [
    "title",
    "industry",
    "function",
    "employment_type",
    "work_model",
    "experience_level",
    "education_level",
    "country",
]

TARGET = "annual_salary_min_usd"


def main():
    print("=" * 60)
    print("JobInsight - Salary Feature Importance")
    print("=" * 60)

    df = pd.read_parquet(DATA_PATH)

    df[TARGET] = pd.to_numeric(
        df[TARGET],
        errors="coerce",
    )

    df = df[
        df[TARGET].notna()
        & (df[TARGET] > 0)
    ].copy()

    X = df[FEATURES]
    y = df[TARGET]

    X_train, _, y_train, _ = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42,
    )

    categorical_pipeline = Pipeline(
        steps=[
            (
                "imputer",
                SimpleImputer(
                    strategy="most_frequent"
                ),
            ),
            (
                "encoder",
                OneHotEncoder(
                    handle_unknown="ignore"
                ),
            ),
        ]
    )

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "categorical",
                categorical_pipeline,
                FEATURES,
            )
        ]
    )

    X_train_encoded = preprocessor.fit_transform(
        X_train
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

    print(
        f"Training records: {len(X_train):,}"
    )

    print("\nTraining XGBoost...")

    model.fit(
        X_train_encoded,
        y_train,
    )

    feature_names = (
        preprocessor
        .get_feature_names_out()
    )

    importance = model.feature_importances_

    result = pd.DataFrame(
        {
            "feature": feature_names,
            "importance": importance,
        }
    )

    result = result.sort_values(
        "importance",
        ascending=False,
    ).reset_index(drop=True)

    result["importance_percent"] = (
        result["importance"]
        / result["importance"].sum()
        * 100
    )

    print("\nTop 20 encoded features:")

    print(
        result.head(20).to_string(
            index=False
        )
    )

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    result.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    print("\nSaved:")
    print(OUTPUT_PATH)

    print("=" * 60)
    print(
        "Feature importance analysis completed."
    )
    print("=" * 60)


if __name__ == "__main__":
    main()