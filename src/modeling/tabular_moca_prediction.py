"""
tabular_moca_prediction.py

Portfolio-safe tabular MoCA prediction pipeline for the
risk-aware-clinical-ai-screening project.

This module reconstructs the thesis modeling direction in a simplified public form:
- load a synthetic patient table;
- select clinically meaningful predictors;
- train a demo regression model;
- predict MoCA total score;
- convert predicted MoCA into a cognitive-risk class;
- export prediction records that can be passed into the uncertainty / triage layer.

Original research context:
    The thesis used best subset regression, mediation analysis, Lasso regression,
    and a neural network with SHAP to model MoCA from physiological, biochemical,
    psychological, and chronic-disease indicators. The public repository uses a
    simpler sklearn implementation so the code can run on synthetic demo data.

Important:
    This file is for portfolio demonstration only.
    It is not a diagnostic tool and must not be used for medical decision-making.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Literal

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LassoCV, LinearRegression, RidgeCV
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import KFold, LeaveOneOut, cross_val_predict, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


# Project variables repeatedly used in the thesis / code notes.
DEFAULT_PREDICTORS: list[str] = [
    "Age",
    "Sex",
    "BH",
    "WC",
    "SBP",
    "DBP",
    "BW",
    "FFM",
    "BFM",
    "BFP",
    "CES-D",
    "Extraversion",
    "Agreeableness",
    "Conscientiousness",
    "Neuroticism",
    "Openness",
    "WHO-5",
    "TBW",
    "FIB4",
    "A1C",
    "Insulin",
    "TCHO",
    "LDL",
    "TG",
    "HDL",
    "Cr",
    "GFR",
    "UACR",
    "UA",
    "T-Bil",
    "D-Bil",
    "Hb",
    "Plt",
    "hsCRP",
    "Ferritin",
    "GluAC",
    "ALT",
    "AST",
]

CORE_INTERPRETABLE_PREDICTORS: list[str] = [
    "Age",
    "Sex",
    "TBW",
    "Plt",
    "FFM",
    "WHO-5",
    "GluAC",
    "TCHO",
    "HDL",
    "Hb",
]

COLUMN_RENAME_MAP: dict[str, str] = {
    "CES.D": "CES-D",
    "CESD": "CES-D",
    "WHO.5": "WHO-5",
    "WHO5": "WHO-5",
    "T.Bil": "T-Bil",
    "D.Bil": "D-Bil",
    "HbA1c": "A1C",
    "A1c": "A1C",
    "PLT": "Plt",
    "Platelet": "Plt",
    "eGFR": "GFR",
}


@dataclass
class ModelMetrics:
    """Regression metrics for portfolio reporting."""

    n_samples: int
    n_features: int
    model_type: str
    rmse: float
    mae: float
    r2: float | None


@dataclass
class PatientPrediction:
    """One patient-level prediction record."""

    patient_id: str | None
    predicted_moca: float
    risk_class: str
    risk_score: float
    key_predictors_available: list[str]
    clinical_note: str


def normalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize known project-specific column aliases."""

    out = df.copy()
    out.columns = [COLUMN_RENAME_MAP.get(str(col).strip(), str(col).strip()) for col in out.columns]
    return out


def load_patient_table(csv_path: str | Path) -> pd.DataFrame:
    """Load synthetic patient table from CSV."""

    return normalize_column_names(pd.read_csv(csv_path))


def select_available_predictors(
    df: pd.DataFrame,
    predictors: Iterable[str] = DEFAULT_PREDICTORS,
    *,
    target: str = "MoCA",
) -> list[str]:
    """Return predictors that are available in the dataframe."""

    return [col for col in predictors if col in df.columns and col != target]


def build_regression_pipeline(
    *,
    model_type: Literal["lasso", "ridge", "linear"] = "lasso",
    random_state: int = 42,
) -> Pipeline:
    """Build a simple sklearn regression pipeline.

    The thesis R scripts standardized all variables except Sex before Lasso / best
    subset regression. This sklearn version imputes missing values, standardizes
    numeric features, and then fits a regression model.
    """

    if model_type == "lasso":
        model = LassoCV(
            alphas=np.logspace(-3, 1, 50),
            cv=5,
            random_state=random_state,
            max_iter=50_000,
        )
    elif model_type == "ridge":
        model = RidgeCV(alphas=np.logspace(-3, 3, 25))
    elif model_type == "linear":
        model = LinearRegression()
    else:
        raise ValueError(f"Unsupported model_type: {model_type}")

    # Because the selected features are numeric after preprocessing, one numeric
    # transformer is enough for the public demo. Sex remains numeric 0/1 and will
    # be scaled unless you remove it before calling this function.
    preprocessor = ColumnTransformer(
        transformers=[
            (
                "num",
                Pipeline(
                    steps=[
                        ("imputer", SimpleImputer(strategy="median")),
                        ("scaler", StandardScaler()),
                    ]
                ),
                "numeric",
            )
        ],
        remainder="drop",
    )

    return Pipeline(
        steps=[
            ("preprocess", preprocessor),
            ("model", model),
        ]
    )


def prepare_xy(
    df: pd.DataFrame,
    *,
    target: str = "MoCA",
    predictors: Iterable[str] = DEFAULT_PREDICTORS,
) -> tuple[pd.DataFrame, pd.Series, list[str]]:
    """Prepare X / y from a patient table."""

    df = normalize_column_names(df)
    if target not in df.columns:
        raise ValueError(f"Target column not found: {target}")

    available_predictors = select_available_predictors(df, predictors, target=target)
    if not available_predictors:
        raise ValueError("No requested predictors are available in the dataframe.")

    modeling_df = df[available_predictors + [target]].copy()

    # Convert all modeling columns to numeric where possible.
    for col in modeling_df.columns:
        modeling_df[col] = pd.to_numeric(modeling_df[col], errors="coerce")

    modeling_df = modeling_df.dropna(subset=[target])

    X = modeling_df[available_predictors]
    y = modeling_df[target]
    return X, y, available_predictors


def fit_tabular_moca_model(
    df: pd.DataFrame,
    *,
    target: str = "MoCA",
    predictors: Iterable[str] = DEFAULT_PREDICTORS,
    model_type: Literal["lasso", "ridge", "linear"] = "lasso",
    random_state: int = 42,
) -> tuple[Pipeline, list[str], ModelMetrics]:
    """Fit a demo MoCA prediction model."""

    X, y, selected_predictors = prepare_xy(df, target=target, predictors=predictors)
    pipeline = build_regression_pipeline(model_type=model_type, random_state=random_state)

    # Cross-validated prediction is used only to provide a transparent demo metric.
    if len(X) >= 10:
        cv = KFold(n_splits=min(5, len(X)), shuffle=True, random_state=random_state)
    else:
        cv = LeaveOneOut()

    try:
        cv_pred = cross_val_predict(pipeline, X, y, cv=cv)
        r2 = float(r2_score(y, cv_pred)) if len(y) > 1 else None
        rmse = float(mean_squared_error(y, cv_pred, squared=False))
        mae = float(mean_absolute_error(y, cv_pred))
    except Exception:
        # If synthetic data are too small for CV, still fit and report training metrics.
        pipeline.fit(X, y)
        pred = pipeline.predict(X)
        r2 = float(r2_score(y, pred)) if len(y) > 1 else None
        rmse = float(mean_squared_error(y, pred, squared=False))
        mae = float(mean_absolute_error(y, pred))

    pipeline.fit(X, y)

    metrics = ModelMetrics(
        n_samples=int(len(X)),
        n_features=int(len(selected_predictors)),
        model_type=model_type,
        rmse=rmse,
        mae=mae,
        r2=r2,
    )
    return pipeline, selected_predictors, metrics


def predict_moca(
    model: Pipeline,
    patient_df: pd.DataFrame,
    *,
    predictors: Iterable[str],
) -> np.ndarray:
    """Predict MoCA scores for new patients."""

    df = normalize_column_names(patient_df)
    X = df[list(predictors)].copy()

    for col in X.columns:
        X[col] = pd.to_numeric(X[col], errors="coerce")

    return model.predict(X)


def classify_cognitive_risk(predicted_moca: float) -> str:
    """Convert predicted MoCA into portfolio demo risk class.

    These thresholds are demo rules only. Real clinical thresholds require validation.
    """

    if predicted_moca >= 26:
        return "low"
    if predicted_moca >= 23:
        return "medium"
    return "high"


def cognitive_risk_score(predicted_moca: float, cutoff: float = 26.0, scale: float = 8.0) -> float:
    """Normalize predicted cognitive risk to [0, 1]."""

    return float(np.clip((cutoff - predicted_moca) / scale, 0.0, 1.0))


def build_prediction_records(
    patient_df: pd.DataFrame,
    predictions: np.ndarray,
    *,
    predictors: Iterable[str],
    patient_id_col: str | None = None,
) -> list[PatientPrediction]:
    """Build patient-level JSON-ready prediction records."""

    df = normalize_column_names(patient_df)
    selected_predictors = list(predictors)

    if patient_id_col is None:
        for candidate in ["synthetic_patient_id", "patient_id", "subject_id", "ID"]:
            if candidate in df.columns:
                patient_id_col = candidate
                break

    records: list[PatientPrediction] = []
    for i, pred in enumerate(predictions):
        patient_id = str(df.iloc[i][patient_id_col]) if patient_id_col and patient_id_col in df.columns else None
        available_core = [col for col in CORE_INTERPRETABLE_PREDICTORS if col in selected_predictors and col in df.columns]

        records.append(
            PatientPrediction(
                patient_id=patient_id,
                predicted_moca=float(pred),
                risk_class=classify_cognitive_risk(float(pred)),
                risk_score=cognitive_risk_score(float(pred)),
                key_predictors_available=available_core,
                clinical_note="Screening signal only; not a diagnosis.",
            )
        )

    return records


def get_linear_feature_importance(
    model: Pipeline,
    predictors: Iterable[str],
    *,
    top_k: int = 15,
) -> pd.DataFrame:
    """Extract coefficient-style feature importance when available."""

    fitted_model = model.named_steps["model"]
    if not hasattr(fitted_model, "coef_"):
        return pd.DataFrame(columns=["feature", "coefficient", "abs_coefficient"])

    coefs = np.asarray(fitted_model.coef_).ravel()
    features = list(predictors)

    # ColumnTransformer with numeric passthrough preserves predictor order here.
    n = min(len(features), len(coefs))
    out = pd.DataFrame(
        {
            "feature": features[:n],
            "coefficient": coefs[:n],
            "abs_coefficient": np.abs(coefs[:n]),
        }
    ).sort_values("abs_coefficient", ascending=False)

    return out.head(top_k).reset_index(drop=True)


def save_model(model: Pipeline, path: str | Path) -> None:
    """Persist sklearn model pipeline."""

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, path)


def load_model(path: str | Path) -> Pipeline:
    """Load persisted sklearn model pipeline."""

    return joblib.load(path)


def main() -> None:
    """Command-line interface.

    Example:
        python src/modeling/tabular_moca_prediction.py \
            --train-csv examples/synthetic_patient_examples.csv \
            --predict-csv examples/synthetic_patient_examples.csv \
            --predictions-out reports/sample_moca_predictions.json \
            --model-out models/tabular_lasso_moca.joblib
    """

    import argparse
    import json

    parser = argparse.ArgumentParser(description="Train demo tabular MoCA model and export predictions.")
    parser.add_argument("--train-csv", required=True, help="Synthetic training CSV with MoCA column.")
    parser.add_argument("--predict-csv", required=True, help="Synthetic patient CSV for prediction.")
    parser.add_argument("--predictions-out", required=True, help="JSON output path.")
    parser.add_argument("--metrics-out", default=None, help="Optional metrics JSON path.")
    parser.add_argument("--feature-importance-out", default=None, help="Optional coefficient CSV path.")
    parser.add_argument("--model-out", default=None, help="Optional model joblib output path.")
    parser.add_argument("--model-type", choices=["lasso", "ridge", "linear"], default="lasso")
    args = parser.parse_args()

    train_df = load_patient_table(args.train_csv)
    model, predictors, metrics = fit_tabular_moca_model(train_df, model_type=args.model_type)

    predict_df = load_patient_table(args.predict_csv)
    predictions = predict_moca(model, predict_df, predictors=predictors)
    records = build_prediction_records(predict_df, predictions, predictors=predictors)

    out_path = Path(args.predictions_out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps([asdict(record) for record in records], indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    if args.metrics_out:
        metrics_path = Path(args.metrics_out)
        metrics_path.parent.mkdir(parents=True, exist_ok=True)
        metrics_path.write_text(json.dumps(asdict(metrics), indent=2, ensure_ascii=False), encoding="utf-8")

    if args.feature_importance_out:
        fi = get_linear_feature_importance(model, predictors)
        fi_path = Path(args.feature_importance_out)
        fi_path.parent.mkdir(parents=True, exist_ok=True)
        fi.to_csv(fi_path, index=False)

    if args.model_out:
        save_model(model, args.model_out)


if __name__ == "__main__":
    main()
