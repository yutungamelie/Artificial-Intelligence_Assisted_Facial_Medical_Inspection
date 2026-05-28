"""
physiological_target_prediction.py

Portfolio-safe physiological target prediction from image features for the
risk-aware-clinical-ai-screening project.

This module reconstructs the tongue-image downstream modeling idea:
- load synthetic image features;
- load synthetic physiological targets;
- train regression or classification models;
- output predicted physiological markers.

Original project context:
    The tongue-image slides state that image features were used to predict roughly
    90 physiological targets, including regression and classification tasks. Example
    exploratory findings included SVM classification for Insomnia and SVR regression
    for TBW.

Public portfolio design:
    This module uses sklearn SVR / SVC or simple linear / logistic models on
    synthetic feature tables. It is not a clinical model and should not be used for
    medical decision-making.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Literal

import joblib
import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    r2_score,
    roc_auc_score,
)
from sklearn.model_selection import KFold, StratifiedKFold, cross_val_predict, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC, SVR
from sklearn.linear_model import LinearRegression, LogisticRegression


TaskType = Literal["regression", "classification"]
ModelType = Literal["svr", "svc", "linear", "logistic"]


@dataclass
class TargetModelReport:
    """Model report for one physiological target."""

    target_name: str
    task_type: str
    model_type: str
    n_samples: int
    n_features: int
    metric_primary_name: str
    metric_primary_value: float | None
    rmse: float | None
    mae: float | None
    r2: float | None
    accuracy: float | None
    f1: float | None
    auc: float | None
    clinical_note: str


def load_feature_table(csv_path: str | Path, *, id_col: str = "image_id") -> pd.DataFrame:
    """Load image feature table."""

    return pd.read_csv(csv_path)


def load_target_table(csv_path: str | Path) -> pd.DataFrame:
    """Load synthetic physiological target table."""

    return pd.read_csv(csv_path)


def merge_features_and_targets(
    features_df: pd.DataFrame,
    targets_df: pd.DataFrame,
    *,
    id_col: str = "image_id",
) -> pd.DataFrame:
    """Merge image features with physiological target table.

    If `image_id` is absent in either table, this function aligns by row order.
    """

    if id_col in features_df.columns and id_col in targets_df.columns:
        return features_df.merge(targets_df, on=id_col, how="inner")

    features = features_df.reset_index(drop=True).copy()
    targets = targets_df.reset_index(drop=True).copy()
    n = min(len(features), len(targets))
    return pd.concat([features.iloc[:n], targets.iloc[:n]], axis=1)


def infer_task_type(y: pd.Series, *, max_unique_for_classification: int = 5) -> TaskType:
    """Infer regression vs classification from target values."""

    y_non_missing = y.dropna()
    unique_values = y_non_missing.nunique()

    if unique_values <= max_unique_for_classification:
        return "classification"
    return "regression"


def select_feature_columns(df: pd.DataFrame, *, id_col: str = "image_id", target_name: str) -> list[str]:
    """Select numeric feature columns excluding ID and target."""

    exclude = {id_col, target_name}
    candidate_cols = [col for col in df.columns if col not in exclude]

    feature_cols: list[str] = []
    for col in candidate_cols:
        converted = pd.to_numeric(df[col], errors="coerce")
        if converted.notna().sum() > 0:
            feature_cols.append(col)

    return feature_cols


def build_target_model(
    *,
    task_type: TaskType,
    model_type: ModelType | None = None,
    random_state: int = 42,
) -> Pipeline:
    """Build sklearn model for physiological target prediction."""

    if model_type is None:
        model_type = "svr" if task_type == "regression" else "svc"

    if task_type == "regression":
        if model_type == "svr":
            model = SVR(kernel="rbf", C=1.0, epsilon=0.1)
        elif model_type == "linear":
            model = LinearRegression()
        else:
            raise ValueError(f"Unsupported regression model_type: {model_type}")
    else:
        if model_type == "svc":
            model = SVC(kernel="rbf", C=1.0, probability=True, random_state=random_state)
        elif model_type == "logistic":
            model = LogisticRegression(max_iter=5000, random_state=random_state)
        else:
            raise ValueError(f"Unsupported classification model_type: {model_type}")

    return Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
            ("model", model),
        ]
    )


def prepare_target_xy(
    merged_df: pd.DataFrame,
    *,
    target_name: str,
    id_col: str = "image_id",
) -> tuple[pd.DataFrame, pd.Series, list[str]]:
    """Prepare feature matrix and one target."""

    if target_name not in merged_df.columns:
        raise ValueError(f"Target column not found: {target_name}")

    feature_cols = select_feature_columns(merged_df, id_col=id_col, target_name=target_name)
    if not feature_cols:
        raise ValueError("No feature columns available.")

    working = merged_df[feature_cols + [target_name]].copy()
    for col in feature_cols:
        working[col] = pd.to_numeric(working[col], errors="coerce")

    working[target_name] = pd.to_numeric(working[target_name], errors="coerce")
    working = working.dropna(subset=[target_name])

    return working[feature_cols], working[target_name], feature_cols


def evaluate_regression(y_true: pd.Series, y_pred: np.ndarray) -> dict[str, float | None]:
    """Compute regression metrics."""

    return {
        "rmse": float(mean_squared_error(y_true, y_pred, squared=False)),
        "mae": float(mean_absolute_error(y_true, y_pred)),
        "r2": float(r2_score(y_true, y_pred)) if len(y_true) > 1 else None,
    }


def evaluate_classification(y_true: pd.Series, y_pred: np.ndarray, y_score: np.ndarray | None = None) -> dict[str, float | None]:
    """Compute classification metrics."""

    out = {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "f1": float(f1_score(y_true, y_pred, average="weighted", zero_division=0)),
        "auc": None,
    }

    if y_score is not None and y_true.nunique() == 2:
        try:
            if y_score.ndim == 2:
                score = y_score[:, 1]
            else:
                score = y_score
            out["auc"] = float(roc_auc_score(y_true, score))
        except Exception:
            out["auc"] = None

    return out


def fit_physiological_target_model(
    merged_df: pd.DataFrame,
    *,
    target_name: str,
    task_type: TaskType | None = None,
    model_type: ModelType | None = None,
    id_col: str = "image_id",
    random_state: int = 42,
) -> tuple[Pipeline, list[str], TargetModelReport]:
    """Fit one physiological target model and return report."""

    X, y, feature_cols = prepare_target_xy(merged_df, target_name=target_name, id_col=id_col)
    if task_type is None:
        task_type = infer_task_type(y)

    pipeline = build_target_model(task_type=task_type, model_type=model_type, random_state=random_state)
    resolved_model_type = model_type or ("svr" if task_type == "regression" else "svc")

    # Cross-validated demo metrics. For tiny synthetic datasets, fit and evaluate in-sample.
    try:
        if task_type == "classification":
            min_class_count = int(y.value_counts().min())
            if len(y) >= 10 and min_class_count >= 2:
                cv = StratifiedKFold(n_splits=min(5, min_class_count), shuffle=True, random_state=random_state)
                y_pred = cross_val_predict(pipeline, X, y, cv=cv, method="predict")
                try:
                    y_score = cross_val_predict(pipeline, X, y, cv=cv, method="predict_proba")
                except Exception:
                    y_score = None
            else:
                pipeline.fit(X, y)
                y_pred = pipeline.predict(X)
                y_score = pipeline.predict_proba(X) if hasattr(pipeline.named_steps["model"], "predict_proba") else None

            metrics = evaluate_classification(y, y_pred, y_score=y_score)
            report = TargetModelReport(
                target_name=target_name,
                task_type=task_type,
                model_type=resolved_model_type,
                n_samples=int(len(X)),
                n_features=int(len(feature_cols)),
                metric_primary_name="accuracy",
                metric_primary_value=metrics["accuracy"],
                rmse=None,
                mae=None,
                r2=None,
                accuracy=metrics["accuracy"],
                f1=metrics["f1"],
                auc=metrics["auc"],
                clinical_note="Exploratory image-to-physiology signal only; not a diagnosis.",
            )

        else:
            if len(y) >= 10:
                cv = KFold(n_splits=min(5, len(y)), shuffle=True, random_state=random_state)
                y_pred = cross_val_predict(pipeline, X, y, cv=cv)
            else:
                pipeline.fit(X, y)
                y_pred = pipeline.predict(X)

            metrics = evaluate_regression(y, y_pred)
            report = TargetModelReport(
                target_name=target_name,
                task_type=task_type,
                model_type=resolved_model_type,
                n_samples=int(len(X)),
                n_features=int(len(feature_cols)),
                metric_primary_name="r2",
                metric_primary_value=metrics["r2"],
                rmse=metrics["rmse"],
                mae=metrics["mae"],
                r2=metrics["r2"],
                accuracy=None,
                f1=None,
                auc=None,
                clinical_note="Exploratory image-to-physiology signal only; not a diagnosis.",
            )

    except Exception:
        pipeline.fit(X, y)
        if task_type == "classification":
            y_pred = pipeline.predict(X)
            y_score = pipeline.predict_proba(X) if hasattr(pipeline.named_steps["model"], "predict_proba") else None
            metrics = evaluate_classification(y, y_pred, y_score=y_score)
            report = TargetModelReport(
                target_name=target_name,
                task_type=task_type,
                model_type=resolved_model_type,
                n_samples=int(len(X)),
                n_features=int(len(feature_cols)),
                metric_primary_name="accuracy",
                metric_primary_value=metrics["accuracy"],
                rmse=None,
                mae=None,
                r2=None,
                accuracy=metrics["accuracy"],
                f1=metrics["f1"],
                auc=metrics["auc"],
                clinical_note="Exploratory image-to-physiology signal only; not a diagnosis.",
            )
        else:
            y_pred = pipeline.predict(X)
            metrics = evaluate_regression(y, y_pred)
            report = TargetModelReport(
                target_name=target_name,
                task_type=task_type,
                model_type=resolved_model_type,
                n_samples=int(len(X)),
                n_features=int(len(feature_cols)),
                metric_primary_name="r2",
                metric_primary_value=metrics["r2"],
                rmse=metrics["rmse"],
                mae=metrics["mae"],
                r2=metrics["r2"],
                accuracy=None,
                f1=None,
                auc=None,
                clinical_note="Exploratory image-to-physiology signal only; not a diagnosis.",
            )

    pipeline.fit(X, y)
    return pipeline, feature_cols, report


def predict_physiological_target(
    model: Pipeline,
    feature_df: pd.DataFrame,
    *,
    feature_cols: list[str],
) -> np.ndarray:
    """Predict a physiological target from image features."""

    X = feature_df[feature_cols].copy()
    for col in X.columns:
        X[col] = pd.to_numeric(X[col], errors="coerce")
    return model.predict(X)


def train_multiple_targets(
    features_df: pd.DataFrame,
    targets_df: pd.DataFrame,
    *,
    target_names: list[str],
    id_col: str = "image_id",
) -> tuple[dict[str, Pipeline], pd.DataFrame]:
    """Train multiple target models and return reports."""

    merged = merge_features_and_targets(features_df, targets_df, id_col=id_col)
    models: dict[str, Pipeline] = {}
    reports: list[dict] = []

    for target in target_names:
        model, feature_cols, report = fit_physiological_target_model(
            merged,
            target_name=target,
            id_col=id_col,
        )
        models[target] = model
        report_dict = asdict(report)
        report_dict["feature_columns"] = feature_cols
        reports.append(report_dict)

    return models, pd.DataFrame(reports)


def save_target_model_bundle(
    model: Pipeline,
    feature_cols: list[str],
    report: TargetModelReport,
    path: str | Path,
) -> None:
    """Save model, feature columns, and report together."""

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({"model": model, "feature_cols": feature_cols, "report": asdict(report)}, path)


def load_target_model_bundle(path: str | Path) -> dict:
    """Load saved target model bundle."""

    return joblib.load(path)


def main() -> None:
    """Command-line interface.

    Example:
        python src/modeling/physiological_target_prediction.py \
            --features-csv examples/synthetic_image_features.csv \
            --targets-csv examples/synthetic_physiological_targets.csv \
            --target TBW \
            --report-out reports/tbw_prediction_report.json \
            --predictions-out examples/sample_tbw_predictions.csv \
            --model-out models/image_to_tbw_svr.joblib
    """

    import argparse
    import json

    parser = argparse.ArgumentParser(description="Train image-feature physiological target predictor.")
    parser.add_argument("--features-csv", required=True, help="Image feature CSV.")
    parser.add_argument("--targets-csv", required=True, help="Physiological target CSV.")
    parser.add_argument("--target", required=True, help="Target column name, e.g. TBW or Insomnia.")
    parser.add_argument("--task-type", choices=["regression", "classification"], default=None)
    parser.add_argument("--model-type", choices=["svr", "svc", "linear", "logistic"], default=None)
    parser.add_argument("--id-col", default="image_id")
    parser.add_argument("--report-out", required=True, help="JSON report output path.")
    parser.add_argument("--predictions-out", default=None, help="Optional CSV output for fitted predictions.")
    parser.add_argument("--model-out", default=None, help="Optional joblib model bundle output path.")
    args = parser.parse_args()

    features_df = load_feature_table(args.features_csv, id_col=args.id_col)
    targets_df = load_target_table(args.targets_csv)
    merged = merge_features_and_targets(features_df, targets_df, id_col=args.id_col)

    model, feature_cols, report = fit_physiological_target_model(
        merged,
        target_name=args.target,
        task_type=args.task_type,
        model_type=args.model_type,
        id_col=args.id_col,
    )

    report_path = Path(args.report_out)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_payload = asdict(report)
    report_payload["feature_columns"] = feature_cols
    report_path.write_text(json.dumps(report_payload, indent=2, ensure_ascii=False), encoding="utf-8")

    if args.predictions_out:
        preds = predict_physiological_target(model, merged, feature_cols=feature_cols)
        pred_df = pd.DataFrame(
            {
                args.id_col: merged[args.id_col] if args.id_col in merged.columns else np.arange(len(preds)),
                f"predicted_{args.target}": preds,
            }
        )
        pred_path = Path(args.predictions_out)
        pred_path.parent.mkdir(parents=True, exist_ok=True)
        pred_df.to_csv(pred_path, index=False)

    if args.model_out:
        save_target_model_bundle(model, feature_cols, report, args.model_out)


if __name__ == "__main__":
    main()
