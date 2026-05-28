"""
clinical_triage_rule.py

Clinical triage policy for the risk-aware-clinical-ai-screening project.

This module combines:
- cognitive risk class;
- uncertainty level;
- data-quality status;

and returns a human-in-the-loop triage action.

The core policy is:
    High risk should never be ignored.
    High uncertainty should never be automated.
    High risk + high uncertainty should always trigger clinician review.

Important:
    This is a portfolio demonstration only. It is not a clinical protocol.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Literal

import pandas as pd


RiskClass = Literal["low", "medium", "high", "insufficient_data"]
UncertaintyLevel = Literal["low", "medium", "high"]


@dataclass
class TriageResult:
    """Structured triage output."""

    cognitive_risk_class: str
    uncertainty_level: str
    triage_action: str
    triage_reason: str
    requires_human_review: bool
    clinical_note: str


def apply_clinical_triage_rule(
    *,
    cognitive_risk_class: str,
    uncertainty_level: str,
    data_quality_flag: str = "ok",
) -> TriageResult:
    """Apply uncertainty-aware clinical triage rule."""

    if data_quality_flag in {"insufficient", "failed", "do_not_predict"}:
        return TriageResult(
            cognitive_risk_class=cognitive_risk_class,
            uncertainty_level=uncertainty_level,
            triage_action="insufficient_data",
            triage_reason=f"data quality flag indicates unusable input: {data_quality_flag}",
            requires_human_review=True,
            clinical_note="Request additional data; screening signal only, not a diagnosis.",
        )

    if cognitive_risk_class == "insufficient_data":
        return TriageResult(
            cognitive_risk_class=cognitive_risk_class,
            uncertainty_level=uncertainty_level,
            triage_action="insufficient_data",
            triage_reason="cognitive risk could not be computed",
            requires_human_review=True,
            clinical_note="Request additional data; screening signal only, not a diagnosis.",
        )

    if cognitive_risk_class == "high" and uncertainty_level == "low":
        return TriageResult(
            cognitive_risk_class=cognitive_risk_class,
            uncertainty_level=uncertainty_level,
            triage_action="formal_cognitive_assessment_recommended",
            triage_reason="high-risk prediction with low uncertainty",
            requires_human_review=True,
            clinical_note="Recommend formal cognitive assessment; not an automated diagnosis.",
        )

    if cognitive_risk_class == "high" and uncertainty_level in {"medium", "high"}:
        return TriageResult(
            cognitive_risk_class=cognitive_risk_class,
            uncertainty_level=uncertainty_level,
            triage_action="clinician_review_required",
            triage_reason="high-risk prediction with uncertainty",
            requires_human_review=True,
            clinical_note="Clinician review required before action; screening signal only.",
        )

    if cognitive_risk_class == "medium" and uncertainty_level == "low":
        return TriageResult(
            cognitive_risk_class=cognitive_risk_class,
            uncertainty_level=uncertainty_level,
            triage_action="follow_up_monitoring",
            triage_reason="medium-risk prediction with low uncertainty",
            requires_human_review=False,
            clinical_note="Consider follow-up monitoring; screening signal only.",
        )

    if cognitive_risk_class == "medium" and uncertainty_level in {"medium", "high"}:
        return TriageResult(
            cognitive_risk_class=cognitive_risk_class,
            uncertainty_level=uncertainty_level,
            triage_action="clinician_review_required",
            triage_reason="medium-risk borderline or uncertain case",
            requires_human_review=True,
            clinical_note="Clinician review recommended because uncertainty may change interpretation.",
        )

    if cognitive_risk_class == "low" and uncertainty_level == "high":
        return TriageResult(
            cognitive_risk_class=cognitive_risk_class,
            uncertainty_level=uncertainty_level,
            triage_action="request_additional_data_or_manual_review",
            triage_reason="low-risk prediction but high uncertainty",
            requires_human_review=True,
            clinical_note="Do not rely on low-risk output when uncertainty is high.",
        )

    if cognitive_risk_class == "low" and uncertainty_level == "medium":
        return TriageResult(
            cognitive_risk_class=cognitive_risk_class,
            uncertainty_level=uncertainty_level,
            triage_action="routine_monitoring_or_follow_up",
            triage_reason="low-risk prediction with mild uncertainty",
            requires_human_review=False,
            clinical_note="Routine monitoring is reasonable; follow-up if clinically indicated.",
        )

    return TriageResult(
        cognitive_risk_class=cognitive_risk_class,
        uncertainty_level=uncertainty_level,
        triage_action="routine_monitoring",
        triage_reason="low-risk prediction with low uncertainty",
        requires_human_review=False,
        clinical_note="Screening signal only; not a diagnosis.",
    )


def add_triage_columns(
    df: pd.DataFrame,
    *,
    risk_col: str = "cognitive_risk_class",
    uncertainty_col: str = "uncertainty_level",
    data_quality_col: str = "data_quality_flag",
) -> pd.DataFrame:
    """Add triage action columns to a dataframe."""

    out = df.copy()
    results: list[TriageResult] = []

    for _, row in out.iterrows():
        results.append(
            apply_clinical_triage_rule(
                cognitive_risk_class=str(row.get(risk_col, "insufficient_data")),
                uncertainty_level=str(row.get(uncertainty_col, "high")),
                data_quality_flag=str(row.get(data_quality_col, "ok")),
            )
        )

    out["triage_action"] = [r.triage_action for r in results]
    out["triage_reason"] = [r.triage_reason for r in results]
    out["requires_human_review"] = [r.requires_human_review for r in results]
    out["triage_clinical_note"] = [r.clinical_note for r in results]
    return out


def main() -> None:
    """Command-line interface."""

    import argparse

    parser = argparse.ArgumentParser(description="Apply clinical triage rules to risk / uncertainty table.")
    parser.add_argument("--input", required=True, help="CSV input.")
    parser.add_argument("--output", required=True, help="CSV output.")
    parser.add_argument("--risk-col", default="cognitive_risk_class")
    parser.add_argument("--uncertainty-col", default="uncertainty_level")
    parser.add_argument("--data-quality-col", default="data_quality_flag")
    args = parser.parse_args()

    df = pd.read_csv(args.input)
    out = add_triage_columns(
        df,
        risk_col=args.risk_col,
        uncertainty_col=args.uncertainty_col,
        data_quality_col=args.data_quality_col,
    )

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(output, index=False)


if __name__ == "__main__":
    from pathlib import Path

    main()
