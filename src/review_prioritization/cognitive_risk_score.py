"""
cognitive_risk_score.py

Portfolio-safe cognitive risk scoring utilities for the
risk-aware-clinical-ai-screening project.

This module converts a predicted MoCA score into:
- cognitive risk class;
- normalized risk score;
- near-threshold flag;
- JSON-ready risk summary.

Research / portfolio context:
    The thesis uses MoCA as the cognitive assessment outcome. Scores >= 26 are
    generally interpreted as normal cognitive function, while scores below 26 may
    indicate possible mild cognitive impairment risk.

Important:
    These thresholds are for portfolio demonstration only. This module is not a
    medical device and must not be used for diagnosis or medical decision-making.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Iterable

import numpy as np
import pandas as pd


MOCA_NORMAL_CUTOFF = 26.0
DEFAULT_MEDIUM_HIGH_CUTOFF = 23.0


@dataclass
class CognitiveRiskResult:
    """Structured risk score output."""

    predicted_moca_score: float | None
    cognitive_risk_class: str
    risk_score: float | None
    distance_to_cutoff: float | None
    near_threshold: bool
    threshold: float
    medium_high_cutoff: float
    clinical_note: str


def _to_optional_float(value: float | int | str | None) -> float | None:
    """Convert a value to float or None."""

    if value is None:
        return None
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return None
    if not np.isfinite(numeric):
        return None
    return numeric


def assign_cognitive_risk(
    predicted_moca: float | int | str | None,
    *,
    threshold: float = MOCA_NORMAL_CUTOFF,
    medium_high_cutoff: float = DEFAULT_MEDIUM_HIGH_CUTOFF,
) -> str:
    """Assign cognitive risk class from predicted MoCA.

    Demo policy:
        predicted_moca >= 26   -> low
        23 <= predicted_moca < 26 -> medium
        predicted_moca < 23    -> high

    Returns
    -------
    str
        "low", "medium", "high", or "insufficient_data".
    """

    score = _to_optional_float(predicted_moca)
    if score is None:
        return "insufficient_data"

    if score >= threshold:
        return "low"
    if score >= medium_high_cutoff:
        return "medium"
    return "high"


def compute_normalized_risk_score(
    predicted_moca: float | int | str | None,
    *,
    threshold: float = MOCA_NORMAL_CUTOFF,
    scale: float = 8.0,
) -> float | None:
    """Compute a normalized cognitive risk score in [0, 1].

    The score increases as predicted MoCA moves below the cutoff.
    """

    score = _to_optional_float(predicted_moca)
    if score is None:
        return None

    return float(np.clip((threshold - score) / scale, 0.0, 1.0))


def compute_distance_to_cutoff(
    predicted_moca: float | int | str | None,
    *,
    threshold: float = MOCA_NORMAL_CUTOFF,
) -> float | None:
    """Absolute distance from MoCA cutoff."""

    score = _to_optional_float(predicted_moca)
    if score is None:
        return None
    return float(abs(score - threshold))


def is_near_threshold(
    predicted_moca: float | int | str | None,
    *,
    threshold: float = MOCA_NORMAL_CUTOFF,
    margin: float = 1.0,
) -> bool:
    """Whether a prediction is close enough to the cutoff to require caution."""

    distance = compute_distance_to_cutoff(predicted_moca, threshold=threshold)
    if distance is None:
        return False
    return distance <= margin


def score_cognitive_risk(
    predicted_moca: float | int | str | None,
    *,
    threshold: float = MOCA_NORMAL_CUTOFF,
    medium_high_cutoff: float = DEFAULT_MEDIUM_HIGH_CUTOFF,
    near_threshold_margin: float = 1.0,
) -> CognitiveRiskResult:
    """Return a structured cognitive-risk result."""

    score = _to_optional_float(predicted_moca)
    return CognitiveRiskResult(
        predicted_moca_score=score,
        cognitive_risk_class=assign_cognitive_risk(
            score,
            threshold=threshold,
            medium_high_cutoff=medium_high_cutoff,
        ),
        risk_score=compute_normalized_risk_score(score, threshold=threshold),
        distance_to_cutoff=compute_distance_to_cutoff(score, threshold=threshold),
        near_threshold=is_near_threshold(score, threshold=threshold, margin=near_threshold_margin),
        threshold=threshold,
        medium_high_cutoff=medium_high_cutoff,
        clinical_note="Screening signal only; not a diagnosis.",
    )


def score_cognitive_risk_dataframe(
    df: pd.DataFrame,
    *,
    prediction_col: str = "predicted_moca_score",
    threshold: float = MOCA_NORMAL_CUTOFF,
    medium_high_cutoff: float = DEFAULT_MEDIUM_HIGH_CUTOFF,
    near_threshold_margin: float = 1.0,
) -> pd.DataFrame:
    """Add risk-score columns to a dataframe."""

    if prediction_col not in df.columns:
        raise ValueError(f"Prediction column not found: {prediction_col}")

    out = df.copy()
    results = [
        score_cognitive_risk(
            value,
            threshold=threshold,
            medium_high_cutoff=medium_high_cutoff,
            near_threshold_margin=near_threshold_margin,
        )
        for value in out[prediction_col]
    ]

    out["cognitive_risk_class"] = [r.cognitive_risk_class for r in results]
    out["risk_score"] = [r.risk_score for r in results]
    out["distance_to_cutoff"] = [r.distance_to_cutoff for r in results]
    out["near_threshold"] = [r.near_threshold for r in results]
    out["clinical_note"] = [r.clinical_note for r in results]
    return out


def main() -> None:
    """Command-line interface.

    Example:
        python src/risk_triage/cognitive_risk_score.py \
            --input reports/sample_moca_predictions.csv \
            --prediction-col predicted_moca_score \
            --output reports/sample_cognitive_risk_scores.csv
    """

    import argparse

    parser = argparse.ArgumentParser(description="Assign cognitive risk from predicted MoCA.")
    parser.add_argument("--input", required=True, help="CSV file with predicted MoCA column.")
    parser.add_argument("--prediction-col", default="predicted_moca_score")
    parser.add_argument("--output", required=True, help="Output CSV path.")
    parser.add_argument("--threshold", type=float, default=MOCA_NORMAL_CUTOFF)
    parser.add_argument("--medium-high-cutoff", type=float, default=DEFAULT_MEDIUM_HIGH_CUTOFF)
    parser.add_argument("--near-threshold-margin", type=float, default=1.0)
    args = parser.parse_args()

    df = pd.read_csv(args.input)
    scored = score_cognitive_risk_dataframe(
        df,
        prediction_col=args.prediction_col,
        threshold=args.threshold,
        medium_high_cutoff=args.medium_high_cutoff,
        near_threshold_margin=args.near_threshold_margin,
    )

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    scored.to_csv(out_path, index=False)


if __name__ == "__main__":
    from pathlib import Path

    main()
