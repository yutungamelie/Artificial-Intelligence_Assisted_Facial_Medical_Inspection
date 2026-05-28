"""
error_analysis.py

Synthetic demo error analysis utilities for the
risk-aware-clinical-ai-screening project.

This module helps inspect:
1. high-error cases;
2. missing feature cases;
3. near-threshold cases;
4. subgroup performance placeholders;
5. clinical risk implications.

This is designed for portfolio reporting and synthetic data. It should not be used
as a validated clinical audit without real-world validation and governance.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Iterable

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


@dataclass
class ErrorAnalysisSummary:
    """Dataset-level error analysis summary."""

    n_cases: int
    rmse: float | None
    mae: float | None
    r2: float | None
    n_high_error_cases: int
    n_near_threshold_cases: int
    n_missing_feature_cases: int
    clinical_note: str


def compute_prediction_errors(
    df: pd.DataFrame,
    *,
    true_col: str = "MoCA",
    pred_col: str = "predicted_moca_score",
) -> pd.DataFrame:
    """Add prediction error columns."""

    if true_col not in df.columns or pred_col not in df.columns:
        raise ValueError(f"Required columns missing: {true_col}, {pred_col}")

    out = df.copy()
    out[true_col] = pd.to_numeric(out[true_col], errors="coerce")
    out[pred_col] = pd.to_numeric(out[pred_col], errors="coerce")
    out["prediction_error"] = out[pred_col] - out[true_col]
    out["absolute_error"] = out["prediction_error"].abs()
    out["squared_error"] = out["prediction_error"] ** 2
    return out


def flag_high_error_cases(
    df: pd.DataFrame,
    *,
    absolute_error_col: str = "absolute_error",
    error_threshold: float = 3.0,
) -> pd.DataFrame:
    """Flag high-error cases."""

    out = df.copy()
    out["high_error_flag"] = pd.to_numeric(out[absolute_error_col], errors="coerce") >= error_threshold
    return out


def flag_near_threshold_cases(
    df: pd.DataFrame,
    *,
    prediction_col: str = "predicted_moca_score",
    threshold: float = 26.0,
    margin: float = 1.0,
) -> pd.DataFrame:
    """Flag predictions close to MoCA threshold."""

    out = df.copy()
    pred = pd.to_numeric(out[prediction_col], errors="coerce")
    out["near_threshold_flag"] = (pred - threshold).abs() <= margin
    out["distance_to_threshold"] = (pred - threshold).abs()
    return out


def flag_missing_feature_cases(
    df: pd.DataFrame,
    *,
    core_features: Iterable[str] = ("Age", "Sex", "TBW", "Plt", "FFM", "WHO-5"),
) -> pd.DataFrame:
    """Flag rows with missing core predictors."""

    out = df.copy()
    core = [col for col in core_features if col in out.columns]

    if not core:
        out["missing_core_feature_count"] = 0
        out["missing_core_feature_flag"] = False
        return out

    out["missing_core_feature_count"] = out[core].isna().sum(axis=1)
    out["missing_core_feature_flag"] = out["missing_core_feature_count"] > 0
    return out


def add_clinical_risk_implication(
    df: pd.DataFrame,
    *,
    high_error_col: str = "high_error_flag",
    near_threshold_col: str = "near_threshold_flag",
    missing_col: str = "missing_core_feature_flag",
) -> pd.DataFrame:
    """Add a plain-language clinical risk implication for each case."""

    out = df.copy()
    implications: list[str] = []

    for _, row in out.iterrows():
        flags: list[str] = []

        if bool(row.get(high_error_col, False)):
            flags.append("large prediction error")

        if bool(row.get(near_threshold_col, False)):
            flags.append("near MoCA cutoff")

        if bool(row.get(missing_col, False)):
            flags.append("missing core predictors")

        if not flags:
            implications.append("no major demo error-analysis flag")
        else:
            implications.append("; ".join(flags) + " -> review or increase uncertainty")

    out["clinical_risk_implication"] = implications
    return out


def summarize_error_analysis(
    df: pd.DataFrame,
    *,
    true_col: str = "MoCA",
    pred_col: str = "predicted_moca_score",
) -> ErrorAnalysisSummary:
    """Compute dataset-level error summary."""

    valid = df[[true_col, pred_col]].apply(pd.to_numeric, errors="coerce").dropna()

    if valid.empty:
        rmse = mae = r2 = None
    else:
        y_true = valid[true_col]
        y_pred = valid[pred_col]
        rmse = float(mean_squared_error(y_true, y_pred, squared=False))
        mae = float(mean_absolute_error(y_true, y_pred))
        r2 = float(r2_score(y_true, y_pred)) if len(valid) > 1 else None

    return ErrorAnalysisSummary(
        n_cases=int(len(df)),
        rmse=rmse,
        mae=mae,
        r2=r2,
        n_high_error_cases=int(df.get("high_error_flag", pd.Series(False, index=df.index)).sum()),
        n_near_threshold_cases=int(df.get("near_threshold_flag", pd.Series(False, index=df.index)).sum()),
        n_missing_feature_cases=int(df.get("missing_core_feature_flag", pd.Series(False, index=df.index)).sum()),
        clinical_note="Error analysis is for synthetic portfolio demo and model debugging only.",
    )


def subgroup_performance_placeholder(
    df: pd.DataFrame,
    *,
    subgroup_col: str,
    true_col: str = "MoCA",
    pred_col: str = "predicted_moca_score",
) -> pd.DataFrame:
    """Compute subgroup metrics when a subgroup column exists.

    This is intentionally a simple placeholder. In a real system, subgroup audit
    needs prespecified groups, sample-size checks, and clinical governance.
    """

    if subgroup_col not in df.columns:
        return pd.DataFrame(
            columns=[
                "subgroup",
                "n",
                "rmse",
                "mae",
                "r2",
                "clinical_note",
            ]
        )

    rows: list[dict] = []
    for subgroup, group in df.groupby(subgroup_col, dropna=False):
        valid = group[[true_col, pred_col]].apply(pd.to_numeric, errors="coerce").dropna()

        if valid.empty:
            rows.append({"subgroup": subgroup, "n": 0, "rmse": None, "mae": None, "r2": None})
            continue

        y_true = valid[true_col]
        y_pred = valid[pred_col]
        rows.append(
            {
                "subgroup": subgroup,
                "n": int(len(valid)),
                "rmse": float(mean_squared_error(y_true, y_pred, squared=False)),
                "mae": float(mean_absolute_error(y_true, y_pred)),
                "r2": float(r2_score(y_true, y_pred)) if len(valid) > 1 else None,
                "clinical_note": "Subgroup metric is exploratory and requires sufficient sample size.",
            }
        )

    return pd.DataFrame(rows)


def run_error_analysis(
    df: pd.DataFrame,
    *,
    true_col: str = "MoCA",
    pred_col: str = "predicted_moca_score",
    error_threshold: float = 3.0,
    threshold: float = 26.0,
    near_threshold_margin: float = 1.0,
) -> tuple[pd.DataFrame, ErrorAnalysisSummary]:
    """Run full synthetic error analysis."""

    out = compute_prediction_errors(df, true_col=true_col, pred_col=pred_col)
    out = flag_high_error_cases(out, error_threshold=error_threshold)
    out = flag_near_threshold_cases(out, prediction_col=pred_col, threshold=threshold, margin=near_threshold_margin)
    out = flag_missing_feature_cases(out)
    out = add_clinical_risk_implication(out)

    summary = summarize_error_analysis(out, true_col=true_col, pred_col=pred_col)
    return out, summary


def main() -> None:
    """Command-line interface."""

    import argparse
    import json

    parser = argparse.ArgumentParser(description="Run synthetic MoCA prediction error analysis.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--summary-output", default=None)
    parser.add_argument("--true-col", default="MoCA")
    parser.add_argument("--pred-col", default="predicted_moca_score")
    parser.add_argument("--error-threshold", type=float, default=3.0)
    args = parser.parse_args()

    df = pd.read_csv(args.input)
    analyzed, summary = run_error_analysis(
        df,
        true_col=args.true_col,
        pred_col=args.pred_col,
        error_threshold=args.error_threshold,
    )

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    analyzed.to_csv(output, index=False)

    if args.summary_output:
        summary_output = Path(args.summary_output)
        summary_output.parent.mkdir(parents=True, exist_ok=True)
        summary_output.write_text(json.dumps(asdict(summary), indent=2, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    from pathlib import Path

    main()
