"""
variable_filtering.py

Variable filtering utilities for the risk-aware-clinical-ai-screening project.

This module reconstructs the filtering logic described in the project notes:
- remove variables with too many missing values;
- remove constant / near-constant variables;
- flag extreme-value risk rather than silently editing values;
- protect clinically interpretable variables such as MoCA, TBW, Plt, Age, and Sex.

Important:
    This module is intended for synthetic / de-identified demo data only.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd


PROTECTED_COLUMNS: set[str] = {
    "ID",
    "patient_id",
    "subject_id",
    "synthetic_patient_id",
    "Age",
    "Sex",
    "MoCA",
    "TBW",
    "Plt",
    "FFM",
    "WHO-5",
    "CES-D",
    "CPSQI",
}

CLINICALLY_INTERPRETABLE_COLUMNS: set[str] = {
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
    "TBW",
    "FIB4",
    "A1C",
    "GluAC",
    "Insulin",
    "TCHO",
    "LDL",
    "TG",
    "HDL",
    "Cr",
    "GFR",
    "UACR",
    "UA",
    "ALT",
    "AST",
    "T-Bil",
    "D-Bil",
    "Hb",
    "Plt",
    "hsCRP",
    "Ferritin",
    "CES-D",
    "CPSQI",
    "WHO-5",
    "MoCA",
    "Extraversion",
    "Agreeableness",
    "Conscientiousness",
    "Neuroticism",
    "Openness",
}


@dataclass
class FilteringResult:
    """Output of `filter_variables`."""

    filtered_df: pd.DataFrame
    summary: pd.DataFrame
    dropped_columns: list[str]
    retained_columns: list[str]


def _safe_numeric(series: pd.Series) -> pd.Series:
    """Convert a series to numeric when possible."""

    if pd.api.types.is_numeric_dtype(series):
        return series
    return pd.to_numeric(series, errors="coerce")


def missing_rate(series: pd.Series) -> float:
    """Fraction of missing values in a series."""

    return float(series.isna().mean())


def is_constant(series: pd.Series) -> bool:
    """Whether a column has zero or one unique non-missing values."""

    return series.nunique(dropna=True) <= 1


def low_variance_flag(series: pd.Series, threshold: float = 0.01) -> bool:
    """Flag near-constant numeric columns.

    The threshold is applied to normalized variance. For categorical variables,
    this function flags columns where the dominant category takes >= 99% by default
    when threshold = 0.01.
    """

    non_missing = series.dropna()
    if non_missing.empty:
        return True

    if pd.api.types.is_numeric_dtype(non_missing):
        if non_missing.nunique() <= 1:
            return True

        numeric = pd.to_numeric(non_missing, errors="coerce").dropna()
        if numeric.empty or numeric.nunique() <= 1:
            return True

        value_range = numeric.max() - numeric.min()
        if np.isclose(value_range, 0):
            return True

        normalized_variance = float(numeric.var(ddof=0) / (value_range**2))
        return normalized_variance < threshold

    top_share = float(non_missing.value_counts(normalize=True).iloc[0])
    return top_share >= (1 - threshold)


def extreme_value_summary(series: pd.Series, z_threshold: float = 4.0) -> dict[str, float | int]:
    """Return simple extreme-value diagnostics for numeric columns.

    Extreme values are flagged but not removed automatically. This is intentional:
    in clinical data, unusual values may be real and should be reviewed.
    """

    numeric = _safe_numeric(series).dropna()
    if numeric.empty or numeric.nunique() <= 1:
        return {
            "extreme_count_iqr": 0,
            "extreme_count_z": 0,
            "min": np.nan,
            "max": np.nan,
        }

    q1 = numeric.quantile(0.25)
    q3 = numeric.quantile(0.75)
    iqr = q3 - q1
    if np.isclose(iqr, 0):
        extreme_iqr = pd.Series(False, index=numeric.index)
    else:
        lower = q1 - 3 * iqr
        upper = q3 + 3 * iqr
        extreme_iqr = (numeric < lower) | (numeric > upper)

    std = numeric.std(ddof=0)
    if std and not np.isclose(std, 0):
        z = (numeric - numeric.mean()) / std
        extreme_z = z.abs() > z_threshold
    else:
        extreme_z = pd.Series(False, index=numeric.index)

    return {
        "extreme_count_iqr": int(extreme_iqr.sum()),
        "extreme_count_z": int(extreme_z.sum()),
        "min": float(numeric.min()),
        "max": float(numeric.max()),
    }


def summarize_variables(
    df: pd.DataFrame,
    *,
    missing_threshold: float = 0.40,
    low_variance_threshold: float = 0.01,
    protected_columns: Iterable[str] = PROTECTED_COLUMNS,
) -> pd.DataFrame:
    """Create variable filtering summary."""

    protected = set(protected_columns)
    rows: list[dict] = []

    for col in df.columns:
        series = df[col]
        numeric_series = _safe_numeric(series)

        miss = missing_rate(series)
        const = is_constant(series)
        low_var = low_variance_flag(series, threshold=low_variance_threshold)
        ext = extreme_value_summary(numeric_series)

        is_protected = col in protected
        is_interpretable = col in CLINICALLY_INTERPRETABLE_COLUMNS

        drop_reasons: list[str] = []
        if miss > missing_threshold:
            drop_reasons.append("high_missingness")
        if const:
            drop_reasons.append("constant")
        elif low_var:
            drop_reasons.append("near_constant_or_low_variance")

        if is_protected:
            # Do not drop protected clinical anchors by default; flag them instead.
            decision = "retain_protected_review_needed" if drop_reasons else "retain_protected"
        elif drop_reasons:
            decision = "drop"
        elif is_interpretable:
            decision = "retain_clinically_interpretable"
        else:
            decision = "retain"

        rows.append(
            {
                "variable": col,
                "dtype": str(series.dtype),
                "missing_rate": miss,
                "missing_count": int(series.isna().sum()),
                "non_missing_count": int(series.notna().sum()),
                "n_unique": int(series.nunique(dropna=True)),
                "is_protected": is_protected,
                "is_clinically_interpretable": is_interpretable,
                "is_constant": const,
                "is_low_variance": low_var,
                "drop_reasons": ";".join(drop_reasons),
                "decision": decision,
                **ext,
            }
        )

    return pd.DataFrame(rows).sort_values(["decision", "missing_rate", "variable"]).reset_index(drop=True)


def filter_variables(
    df: pd.DataFrame,
    *,
    missing_threshold: float = 0.40,
    low_variance_threshold: float = 0.01,
    protected_columns: Iterable[str] = PROTECTED_COLUMNS,
    allow_drop_protected: bool = False,
) -> FilteringResult:
    """Filter columns based on missingness and low information content.

    Parameters
    ----------
    df:
        Input dataframe.
    missing_threshold:
        Drop columns above this missingness rate, unless protected.
    low_variance_threshold:
        Threshold for near-constant detection.
    protected_columns:
        Columns to keep even if they are missing or low-variance.
    allow_drop_protected:
        If True, protected columns may be dropped when they fail filters.
        Default False is safer for clinical portfolio demos.
    """

    protected = set(protected_columns)
    summary = summarize_variables(
        df,
        missing_threshold=missing_threshold,
        low_variance_threshold=low_variance_threshold,
        protected_columns=protected,
    )

    drop_mask = summary["decision"].eq("drop")
    if allow_drop_protected:
        protected_failed = summary["decision"].eq("retain_protected_review_needed")
        drop_mask = drop_mask | protected_failed

    dropped_columns = summary.loc[drop_mask, "variable"].tolist()
    retained_columns = [col for col in df.columns if col not in dropped_columns]

    return FilteringResult(
        filtered_df=df.loc[:, retained_columns].copy(),
        summary=summary,
        dropped_columns=dropped_columns,
        retained_columns=retained_columns,
    )


def flag_patient_level_missingness(
    df: pd.DataFrame,
    *,
    core_columns: Iterable[str] = ("Age", "Sex", "MoCA", "TBW", "Plt"),
) -> pd.DataFrame:
    """Add patient-level missingness flags for downstream uncertainty scoring."""

    out = df.copy()
    core = [col for col in core_columns if col in out.columns]
    if not core:
        out["missing_core_feature_count"] = 0
        out["missing_core_feature_flag"] = False
        return out

    out["missing_core_feature_count"] = out[core].isna().sum(axis=1)
    out["missing_core_feature_flag"] = out["missing_core_feature_count"] > 0
    return out


def export_filtering_outputs(
    result: FilteringResult,
    *,
    filtered_csv: str | Path,
    summary_csv: str | Path,
) -> None:
    """Export filtered dataframe and variable-level summary."""

    Path(filtered_csv).parent.mkdir(parents=True, exist_ok=True)
    Path(summary_csv).parent.mkdir(parents=True, exist_ok=True)
    result.filtered_df.to_csv(filtered_csv, index=False)
    result.summary.to_csv(summary_csv, index=False)


def main() -> None:
    """Command-line interface.

    Example:
        python src/data_preprocessing/variable_filtering.py \
            --input data/processed/cleaned_patient_examples.csv \
            --output data/processed/filtered_patient_examples.csv \
            --summary reports/variable_filtering_summary.csv
    """

    import argparse

    parser = argparse.ArgumentParser(description="Filter clinical tabular variables for portfolio demo data.")
    parser.add_argument("--input", required=True, help="Input CSV path.")
    parser.add_argument("--output", required=True, help="Filtered CSV output path.")
    parser.add_argument("--summary", required=True, help="Variable filtering summary output path.")
    parser.add_argument("--missing-threshold", type=float, default=0.40)
    parser.add_argument("--low-variance-threshold", type=float, default=0.01)
    parser.add_argument("--allow-drop-protected", action="store_true")
    args = parser.parse_args()

    df = pd.read_csv(args.input)
    result = filter_variables(
        df,
        missing_threshold=args.missing_threshold,
        low_variance_threshold=args.low_variance_threshold,
        allow_drop_protected=args.allow_drop_protected,
    )
    result.filtered_df = flag_patient_level_missingness(result.filtered_df)
    export_filtering_outputs(result, filtered_csv=args.output, summary_csv=args.summary)


if __name__ == "__main__":
    main()
