"""
uncertainty_score.py

Uncertainty scoring utilities for the risk-aware-clinical-ai-screening project.

The uncertainty score combines several clinically meaningful signals:
1. prediction near MoCA threshold;
2. bootstrap interval crossing the threshold;
3. model disagreement;
4. missingness / data quality;
5. image quality flags.

This module follows the repository's uncertainty triage policy:
    risk signal + uncertainty level + suggested downstream triage action

Important:
    This is a portfolio demonstration using synthetic or mock data only.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Iterable, Literal

import numpy as np
import pandas as pd


UncertaintyLevel = Literal["low", "medium", "high"]
AgreementLevel = Literal["high", "moderate", "low", "unknown"]


LEVEL_TO_SCORE = {"low": 0, "medium": 1, "high": 2}
SCORE_TO_LEVEL = {0: "low", 1: "medium", 2: "high"}


@dataclass
class UncertaintyResult:
    """Structured uncertainty output."""

    uncertainty_level: str
    uncertainty_score: float
    near_threshold: bool
    threshold_crossing_ci: bool
    model_agreement_level: str
    missing_key_predictor_count: int
    image_quality_flag: str | None
    data_quality_flag: str
    reasons: list[str]
    clinical_note: str


def _max_level(*levels: str) -> str:
    """Return the maximum severity uncertainty level."""

    valid = [LEVEL_TO_SCORE.get(level, 0) for level in levels]
    return SCORE_TO_LEVEL[max(valid)]


def _to_float_or_none(value) -> float | None:
    """Convert value to finite float when possible."""

    try:
        x = float(value)
    except (TypeError, ValueError):
        return None
    if not np.isfinite(x):
        return None
    return x


def check_near_threshold(
    predicted_moca: float | None,
    *,
    threshold: float = 26.0,
    margin: float = 1.0,
) -> bool:
    """Return True when prediction is near the MoCA cutoff."""

    score = _to_float_or_none(predicted_moca)
    if score is None:
        return False
    return abs(score - threshold) <= margin


def check_ci_crosses_threshold(
    ci_lower: float | None,
    ci_upper: float | None,
    *,
    threshold: float = 26.0,
) -> bool:
    """Return True when a confidence interval crosses the MoCA cutoff."""

    lo = _to_float_or_none(ci_lower)
    hi = _to_float_or_none(ci_upper)

    if lo is None or hi is None:
        return False

    lower, upper = min(lo, hi), max(lo, hi)
    return lower < threshold <= upper


def uncertainty_from_model_agreement(model_agreement_level: AgreementLevel) -> tuple[str, list[str]]:
    """Convert model agreement into uncertainty level and reasons."""

    if model_agreement_level == "low":
        return "high", ["low model agreement"]
    if model_agreement_level == "moderate":
        return "medium", ["moderate model agreement"]
    if model_agreement_level == "unknown":
        return "medium", ["model agreement unknown"]
    return "low", []


def uncertainty_from_missingness(
    *,
    missing_key_predictor_count: int = 0,
    missing_rate: float | None = None,
) -> tuple[str, list[str]]:
    """Convert missingness indicators into uncertainty level and reasons."""

    reasons: list[str] = []

    if missing_key_predictor_count >= 2:
        reasons.append(f"{missing_key_predictor_count} key predictors missing")
        return "high", reasons

    if missing_key_predictor_count == 1:
        reasons.append("one key predictor missing")
        return "medium", reasons

    if missing_rate is not None and missing_rate >= 0.40:
        reasons.append(f"high missingness rate: {missing_rate:.2f}")
        return "high", reasons

    if missing_rate is not None and missing_rate >= 0.15:
        reasons.append(f"moderate missingness rate: {missing_rate:.2f}")
        return "medium", reasons

    return "low", reasons


def uncertainty_from_quality_flags(
    *,
    data_quality_flag: str = "ok",
    image_quality_flag: str | None = None,
) -> tuple[str, list[str]]:
    """Convert data / image quality flags into uncertainty level."""

    reasons: list[str] = []
    level = "low"

    severe_data_flags = {"insufficient", "failed", "do_not_predict"}
    caution_data_flags = {"review", "review_recommended", "usable_with_caution", "increase"}

    if data_quality_flag in severe_data_flags:
        reasons.append(f"data quality flag: {data_quality_flag}")
        level = "high"
    elif data_quality_flag in caution_data_flags:
        reasons.append(f"data quality flag: {data_quality_flag}")
        level = "medium"

    if image_quality_flag:
        severe_image_flags = {"unusable", "failed", "do_not_predict"}
        caution_image_flags = {"usable_with_caution", "increase", "manual_review", "review_recommended"}

        if image_quality_flag in severe_image_flags:
            reasons.append(f"image quality flag: {image_quality_flag}")
            level = _max_level(level, "high")
        elif image_quality_flag in caution_image_flags:
            reasons.append(f"image quality flag: {image_quality_flag}")
            level = _max_level(level, "medium")

    return level, reasons


def compute_uncertainty(
    *,
    predicted_moca: float | None = None,
    ci_lower: float | None = None,
    ci_upper: float | None = None,
    model_agreement_level: AgreementLevel = "unknown",
    missing_key_predictor_count: int = 0,
    missing_rate: float | None = None,
    data_quality_flag: str = "ok",
    image_quality_flag: str | None = None,
    threshold: float = 26.0,
    near_threshold_margin: float = 1.0,
) -> UncertaintyResult:
    """Compute a combined uncertainty result.

    Policy:
        - near threshold -> at least medium uncertainty;
        - CI crosses cutoff -> high uncertainty;
        - low model agreement -> high uncertainty;
        - missing key variables / poor image quality -> increase uncertainty.
    """

    reasons: list[str] = []

    near_threshold = check_near_threshold(
        predicted_moca,
        threshold=threshold,
        margin=near_threshold_margin,
    )
    threshold_crossing_ci = check_ci_crosses_threshold(ci_lower, ci_upper, threshold=threshold)

    level = "low"

    if predicted_moca is None or _to_float_or_none(predicted_moca) is None:
        level = "high"
        reasons.append("predicted MoCA missing or invalid")

    if near_threshold:
        level = _max_level(level, "medium")
        reasons.append("prediction near MoCA cutoff")

    if threshold_crossing_ci:
        level = _max_level(level, "high")
        reasons.append("bootstrap confidence interval crosses MoCA cutoff")

    agreement_level, agreement_reasons = uncertainty_from_model_agreement(model_agreement_level)
    level = _max_level(level, agreement_level)
    reasons.extend(agreement_reasons)

    missing_level, missing_reasons = uncertainty_from_missingness(
        missing_key_predictor_count=missing_key_predictor_count,
        missing_rate=missing_rate,
    )
    level = _max_level(level, missing_level)
    reasons.extend(missing_reasons)

    quality_level, quality_reasons = uncertainty_from_quality_flags(
        data_quality_flag=data_quality_flag,
        image_quality_flag=image_quality_flag,
    )
    level = _max_level(level, quality_level)
    reasons.extend(quality_reasons)

    if not reasons:
        reasons.append("no major uncertainty signal detected")

    score = LEVEL_TO_SCORE[level] / 2.0

    return UncertaintyResult(
        uncertainty_level=level,
        uncertainty_score=float(score),
        near_threshold=near_threshold,
        threshold_crossing_ci=threshold_crossing_ci,
        model_agreement_level=model_agreement_level,
        missing_key_predictor_count=int(missing_key_predictor_count),
        image_quality_flag=image_quality_flag,
        data_quality_flag=data_quality_flag,
        reasons=reasons,
        clinical_note="Uncertainty score is a portfolio reliability signal, not clinical validation.",
    )


def add_uncertainty_columns(
    df: pd.DataFrame,
    *,
    prediction_col: str = "predicted_moca_score",
    ci_lower_col: str | None = "ci_lower",
    ci_upper_col: str | None = "ci_upper",
    agreement_col: str | None = "model_agreement_level",
    missing_key_col: str | None = "missing_key_predictor_count",
    missing_rate_col: str | None = "missing_rate",
    data_quality_col: str | None = "data_quality_flag",
    image_quality_col: str | None = "image_quality_flag",
) -> pd.DataFrame:
    """Add uncertainty scoring columns to a dataframe."""

    out = df.copy()
    results: list[UncertaintyResult] = []

    for _, row in out.iterrows():
        results.append(
            compute_uncertainty(
                predicted_moca=row.get(prediction_col),
                ci_lower=row.get(ci_lower_col) if ci_lower_col in out.columns else None,
                ci_upper=row.get(ci_upper_col) if ci_upper_col in out.columns else None,
                model_agreement_level=row.get(agreement_col, "unknown") if agreement_col in out.columns else "unknown",
                missing_key_predictor_count=int(row.get(missing_key_col, 0)) if missing_key_col in out.columns else 0,
                missing_rate=row.get(missing_rate_col) if missing_rate_col in out.columns else None,
                data_quality_flag=row.get(data_quality_col, "ok") if data_quality_col in out.columns else "ok",
                image_quality_flag=row.get(image_quality_col) if image_quality_col in out.columns else None,
            )
        )

    out["uncertainty_level"] = [r.uncertainty_level for r in results]
    out["uncertainty_score"] = [r.uncertainty_score for r in results]
    out["near_threshold"] = [r.near_threshold for r in results]
    out["threshold_crossing_ci"] = [r.threshold_crossing_ci for r in results]
    out["uncertainty_reasons"] = ["; ".join(r.reasons) for r in results]
    out["uncertainty_note"] = [r.clinical_note for r in results]
    return out


def main() -> None:
    """Command-line interface."""

    import argparse

    parser = argparse.ArgumentParser(description="Compute uncertainty scores for predicted MoCA records.")
    parser.add_argument("--input", required=True, help="CSV input with prediction / reliability columns.")
    parser.add_argument("--output", required=True, help="CSV output path.")
    parser.add_argument("--prediction-col", default="predicted_moca_score")
    args = parser.parse_args()

    df = pd.read_csv(args.input)
    out = add_uncertainty_columns(df, prediction_col=args.prediction_col)

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(output, index=False)


if __name__ == "__main__":
    from pathlib import Path

    main()
