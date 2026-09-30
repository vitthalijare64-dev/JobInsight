from pathlib import Path

import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
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


def load_salary_data():
    df = pd.read_parquet(DATA_PATH)

    df[TARGET] = pd.to_numeric(
        df[TARGET],
        errors="coerce",
    )

    df = df[
        df[TARGET].notna()
        & (df[TARGET] > 0)
    ].copy()

    return df


def build_model():
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

    model = RandomForestRegressor(
        n_estimators=200,
        max_depth=20,
        random_state=42,
        n_jobs=-1,
    )

    pipeline = Pipeline(
        steps=[
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

    return pipeline


if __name__ == "__main__":
    print("=" * 60)
    print("JobInsight - Salary Prediction Model")
    print("=" * 60)

    df = load_salary_data()

    print(
        f"Valid salary records: {len(df):,}"
    )

    X = df[FEATURES]
    y = df[TARGET]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42,
    )

    print(
        f"Training records: {len(X_train):,}"
    )

    print(
        f"Testing records: {len(X_test):,}"
    )

    model = build_model()

    print("\nTraining model...")

    model.fit(
        X_train,
        y_train,
    )

    predictions = model.predict(
        X_test
    )

    mae = mean_absolute_error(
        y_test,
        predictions,
    )

    rmse = mean_squared_error(
        y_test,
        predictions,
    ) ** 0.5

    r2 = r2_score(
        y_test,
        predictions,
    )

    print("\n" + "=" * 60)
    print("SALARY MODEL RESULTS")
    print("=" * 60)

    print(
        f"MAE : ${mae:,.2f}"
    )

    print(
        f"RMSE: ${rmse:,.2f}"
    )

    print(
        f"R²  : {r2:.4f}"
    )

    print("\nExample predictions:")

    results = pd.DataFrame(
        {
            "actual_salary_usd": y_test.values,
            "predicted_salary_usd": predictions,
        }
    )

    print(
        results.head(10).to_string(
            index=False
        )
    )

    print("=" * 60)
    print(
        "Salary model training completed."
    )
    print("=" * 60)