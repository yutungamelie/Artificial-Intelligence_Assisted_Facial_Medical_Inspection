"""
model_agreement_check.py

Model agreement / disagreement checks for the
risk-aware-clinical-ai-screening project.

The thesis used multiple modeling approaches:
- best subset regression;
- Lasso regression;
- neural network with SHAP;
- mediation analysis for mechanism-oriented interpretation.

This module turns multiple model predictions into a reliability signal:
    high agreement / moderate agreement / low agreement

Low agreement should increase uncertainty and trigger more cautious triage.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Iterable

import numpy as np
import pandas as pd


@dataclass
class ModelAgreementResult:
    """Agreement summary for one patient."""

    n_models: int
    mean_prediction: float | None
    prediction_std: float | None
    prediction_range: float | None
    risk_classes: list[str]
    agreement_level: str
    disagreement_reason: str
    clinical_note: str


def assign_risk_class(predicted_moca: float, threshold: float = 26.0, medium_high_cutoff: float = 23.0) -> str:
    """Classify MoCA prediction into low / medium / high."""

    if not np.isfinite(predicted_moca):
        return "insufficient_data"
    if predicted_moca >= threshold:
        return "low"
    if predicted_moca >= medium_high_cutoff:
        return "medium"
    return "high"


def summarize_prediction_agreement(
    predictions: Iterable[float],
    *,
    threshold: float = 26.0,
    medium_high_cutoff: float = 23.0,
    low_spread_margin: float = 1.0,
    moderate_spread_margin: float = 3.0,
) -> ModelAgreementResult:
    """Summarize agreement across multiple model predictions."""

    values = np.asarray([float(x) for x in predictions if x is not None and np.isfinite(float(x))], dtype=float)

    if len(values) == 0:
        return ModelAgreementResult(
            n_models=0,
            mean_prediction=None,
            prediction_std=None,
            prediction_range=None,
            risk_classes=[],
            agreement_level="unknown",
            disagreement_reason="no valid model predictions",
            clinical_note="Model agreement unavailable; increase uncertainty.",
        )

    risk_classes = [assign_risk_class(x, threshold=threshold, medium_high_cutoff=medium_high_cutoff) for x in values]
    unique_classes = sorted(set(risk_classes))

    pred_range = float(values.max() - values.min())
    pred_std = float(values.std(ddof=0))
    mean_pred = float(values.mean())

    crosses_cutoff = values.min() < threshold <= values.max()

    if len(unique_classes) == 1 and pred_range <= low_spread_margin:
        level = "high"
        reason = "all models predict same risk class with small spread"
    elif len(unique_classes) == 1 and pred_range <= moderate_spread_margin:
        level = "moderate"
        reason = "all models predict same risk class but spread is moderate"
    elif crosses_cutoff:
        level = "low"
        reason = "model predictions cross MoCA cutoff"
    elif len(unique_classes) == 2 and pred_range <= moderate_spread_margin:
        level = "moderate"
        reason = "models differ by neighboring risk classes"
    else:
        level = "low"
        reason = "models strongly disagree"

    return ModelAgreementResult(
        n_models=int(len(values)),
        mean_prediction=mean_pred,
        prediction_std=pred_std,
        prediction_range=pred_range,
        risk_classes=risk_classes,
        agreement_level=level,
        disagreement_reason=reason,
        clinical_note="Agreement level is a reliability signal, not clinical validation.",
    )


def add_model_agreement_columns(
    df: pd.DataFrame,
    *,
    prediction_cols: list[str],
    threshold: float = 26.0,
) -> pd.DataFrame:
    """Add agreement columns to dataframe with multiple prediction columns."""

    missing = [col for col in prediction_cols if col not in df.columns]
    if missing:
        raise ValueError(f"Prediction columns missing: {missing}")

    out = df.copy()
    results = [
        summarize_prediction_agreement(row[prediction_cols].to_list(), threshold=threshold)
        for _, row in out.iterrows()
    ]

    out["ensemble_mean_predicted_moca"] = [r.mean_prediction for r in results]
    out["model_prediction_std"] = [r.prediction_std for r in results]
    out["model_prediction_range"] = [r.prediction_range for r in results]
    out["model_agreement_level"] = [r.agreement_level for r in results]
    out["model_agreement_reason"] = [r.disagreement_reason for r in results]
    out["model_risk_classes"] = [";".join(r.risk_classes) for r in results]
    out["model_agreement_note"] = [r.clinical_note for r in results]
    return out


def model_agreement_from_prediction_dict(prediction_dict: dict[str, float]) -> dict:
    """Convenience helper for API-style usage."""

    result = summarize_prediction_agreement(prediction_dict.values())
    payload = asdict(result)
    payload["model_predictions"] = prediction_dict
    return payload


def main() -> None:
    """Command-line interface."""

    import argparse

    parser = argparse.ArgumentParser(description="Check agreement across model predictions.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--prediction-cols", nargs="+", required=True)
    args = parser.parse_args()

    df = pd.read_csv(args.input)
    out = add_model_agreement_columns(df, prediction_cols=args.prediction_cols)

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(output, index=False)


if __name__ == "__main__":
    from pathlib import Path

    main()
