"""
bootstrap_ci.py

Bootstrap confidence interval demo for the risk-aware-clinical-ai-screening project.

This module estimates prediction intervals for MoCA prediction by repeatedly:
1. resampling training data with replacement;
2. refitting a model;
3. predicting MoCA for patient rows;
4. summarizing percentile intervals;
5. checking whether the interval crosses the MoCA cutoff.

This is a portfolio reliability extension. It was not required as the original thesis
analysis output, but it is a useful engineering layer for uncertainty-aware clinical AI.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Callable

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.pipeline import Pipeline
from sklearn.utils import resample


@dataclass
class BootstrapCIResult:
    """Bootstrap CI result for one prediction."""

    point_prediction: float
    ci_lower: float
    ci_upper: float
    ci_level: float
    threshold_crossing: bool
    n_bootstrap: int
    threshold: float
    clinical_note: str


def percentile_interval(
    values: np.ndarray,
    *,
    ci_level: float = 0.95,
) -> tuple[float, float]:
    """Return percentile confidence interval."""

    alpha = 1.0 - ci_level
    lower = np.percentile(values, 100 * alpha / 2)
    upper = np.percentile(values, 100 * (1 - alpha / 2))
    return float(lower), float(upper)


def interval_crosses_threshold(
    ci_lower: float,
    ci_upper: float,
    *,
    threshold: float = 26.0,
) -> bool:
    """Check if interval crosses MoCA threshold."""

    lower, upper = min(ci_lower, ci_upper), max(ci_lower, ci_upper)
    return lower < threshold <= upper


def bootstrap_prediction_intervals(
    model: Pipeline,
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_predict: pd.DataFrame,
    *,
    n_bootstrap: int = 500,
    ci_level: float = 0.95,
    threshold: float = 26.0,
    random_state: int = 42,
) -> tuple[pd.DataFrame, np.ndarray]:
    """Estimate bootstrap prediction intervals.

    Parameters
    ----------
    model:
        Any sklearn-style estimator or pipeline with fit / predict.
    X_train, y_train:
        Training data.
    X_predict:
        Rows to predict.
    n_bootstrap:
        Number of bootstrap refits.
    ci_level:
        Percentile CI level.
    threshold:
        MoCA cutoff.

    Returns
    -------
    tuple[pd.DataFrame, np.ndarray]
        Summary dataframe and raw bootstrap predictions with shape
        [n_bootstrap, n_prediction_rows].
    """

    if len(X_train) != len(y_train):
        raise ValueError("X_train and y_train must have same number of rows.")

    rng = np.random.default_rng(random_state)
    boot_predictions: list[np.ndarray] = []

    for _ in range(n_bootstrap):
        sample_idx = rng.integers(0, len(X_train), size=len(X_train))
        X_b = X_train.iloc[sample_idx]
        y_b = y_train.iloc[sample_idx] if hasattr(y_train, "iloc") else np.asarray(y_train)[sample_idx]

        estimator = clone(model)
        estimator.fit(X_b, y_b)
        boot_predictions.append(np.asarray(estimator.predict(X_predict), dtype=float))

    boot_array = np.vstack(boot_predictions)
    point_model = clone(model).fit(X_train, y_train)
    point_predictions = np.asarray(point_model.predict(X_predict), dtype=float)

    rows: list[dict] = []
    for i, point in enumerate(point_predictions):
        lower, upper = percentile_interval(boot_array[:, i], ci_level=ci_level)
        result = BootstrapCIResult(
            point_prediction=float(point),
            ci_lower=lower,
            ci_upper=upper,
            ci_level=ci_level,
            threshold_crossing=interval_crosses_threshold(lower, upper, threshold=threshold),
            n_bootstrap=n_bootstrap,
            threshold=threshold,
            clinical_note="Bootstrap CI is a portfolio reliability estimate, not clinical validation.",
        )
        rows.append(asdict(result))

    return pd.DataFrame(rows), boot_array


def add_bootstrap_ci_to_predictions(
    prediction_df: pd.DataFrame,
    ci_df: pd.DataFrame,
    *,
    prediction_col: str = "predicted_moca_score",
) -> pd.DataFrame:
    """Attach CI columns to an existing prediction dataframe."""

    out = prediction_df.reset_index(drop=True).copy()
    ci = ci_df.reset_index(drop=True).copy()

    if len(out) != len(ci):
        raise ValueError("prediction_df and ci_df must have the same number of rows.")

    out[prediction_col] = ci["point_prediction"]
    out["ci_lower"] = ci["ci_lower"]
    out["ci_upper"] = ci["ci_upper"]
    out["ci_level"] = ci["ci_level"]
    out["threshold_crossing_ci"] = ci["threshold_crossing"]
    out["bootstrap_note"] = ci["clinical_note"]
    return out


def demo_bootstrap_with_sklearn_csv(
    train_csv: str,
    predict_csv: str,
    *,
    target_col: str = "MoCA",
    model_factory: Callable[[], Pipeline],
    n_bootstrap: int = 500,
    threshold: float = 26.0,
) -> pd.DataFrame:
    """Convenience function for simple CSV demos."""

    train_df = pd.read_csv(train_csv)
    pred_df = pd.read_csv(predict_csv)

    feature_cols = [col for col in train_df.columns if col != target_col and col in pred_df.columns]
    X_train = train_df[feature_cols]
    y_train = train_df[target_col]
    X_predict = pred_df[feature_cols]

    ci_df, _ = bootstrap_prediction_intervals(
        model_factory(),
        X_train,
        y_train,
        X_predict,
        n_bootstrap=n_bootstrap,
        threshold=threshold,
    )
    return ci_df


def main() -> None:
    """CLI placeholder.

    This module is usually imported by modeling scripts because it needs a fitted
    sklearn model factory. The CLI provides a minimal Ridge demo.
    """

    import argparse
    from sklearn.compose import ColumnTransformer
    from sklearn.impute import SimpleImputer
    from sklearn.linear_model import Ridge
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import StandardScaler

    parser = argparse.ArgumentParser(description="Run bootstrap CI demo on synthetic CSV data.")
    parser.add_argument("--train-csv", required=True)
    parser.add_argument("--predict-csv", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--target-col", default="MoCA")
    parser.add_argument("--n-bootstrap", type=int, default=300)
    args = parser.parse_args()

    train_df = pd.read_csv(args.train_csv)
    feature_cols = [c for c in train_df.columns if c != args.target_col]

    def factory():
        return Pipeline(
            [
                ("imputer", SimpleImputer(strategy="median")),
                ("scaler", StandardScaler()),
                ("model", Ridge(alpha=1.0)),
            ]
        )

    ci_df = demo_bootstrap_with_sklearn_csv(
        args.train_csv,
        args.predict_csv,
        target_col=args.target_col,
        model_factory=factory,
        n_bootstrap=args.n_bootstrap,
    )
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    ci_df.to_csv(out, index=False)


if __name__ == "__main__":
    from pathlib import Path

    main()
