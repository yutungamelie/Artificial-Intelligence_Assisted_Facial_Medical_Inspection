"""
tabular_cleaning.py

Portfolio-safe tabular cleaning utilities for the
risk-aware-clinical-ai-screening project.

This module reconstructs the cleaning logic described in the project notes:
- questionnaire and physiological indicator tables were merged into one table;
- questionnaire sub-items were removed when total scores were retained;
- Chinese / inconsistent variable names were normalized into English names;
- duplicate columns were removed;
- clinically meaningful feature groups were retained;
- missing values were handled explicitly instead of silently.

Important:
    This file is designed for synthetic / de-identified demo data only.
    Do not commit patient-level clinical records or hospital raw data to GitHub.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Literal

import numpy as np
import pandas as pd


# ---------------------------------------------------------------------
# 1. Variable groups reconstructed from the project ReadMe
# ---------------------------------------------------------------------

FEATURE_GROUPS: dict[str, list[str]] = {
    "id": ["ID", "patient_id", "subject_id", "synthetic_patient_id"],
    "grouping": ["Group", "Sex", "Age", "Edu<12"],
    "body_vitals": ["BH", "WC", "SBP", "DBP", "BW", "FFM", "BFM", "BFP"],
    "sleep_objective": ["Chrono", "Interrupt", "Nap"],
    "questionnaire_scores": [
        "CES-D",
        "CPSQI",
        "WHO-5",
        "MoCA",
        "Extraversion",
        "Agreeableness",
        "Conscientiousness",
        "Neuroticism",
        "Openness",
    ],
    "blood_urine_markers": [
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
    ],
    "derived_chronic_conditions": [
        "HTN",
        "DM",
        "HL",
        "CKD",
        "LD",
        "Insomnia",
        "Depression",
        "MultiCount",
    ],
}

DEFAULT_KEEP_GROUPS: list[str] = [
    "id",
    "grouping",
    "body_vitals",
    "sleep_objective",
    "questionnaire_scores",
    "blood_urine_markers",
    "derived_chronic_conditions",
]

CORE_MODELING_COLUMNS: list[str] = [
    "Age",
    "Sex",
    "TBW",
    "Plt",
    "FFM",
    "WHO-5",
    "MoCA",
]


# ---------------------------------------------------------------------
# 2. Variable-name normalization
# ---------------------------------------------------------------------

COLUMN_RENAME_MAP: dict[str, str] = {
    # Common punctuation / R-safe variants
    "CES.D": "CES-D",
    "CES_D": "CES-D",
    "CESD": "CES-D",
    "WHO.5": "WHO-5",
    "WHO_5": "WHO-5",
    "WHO5": "WHO-5",
    "CPSQI": "CPSQI",
    "PSQI": "CPSQI",
    "A1c": "A1C",
    "HbA1c": "A1C",
    "HbA1C": "A1C",
    "eGFR": "GFR",
    "EGFR": "GFR",
    "T.Bil": "T-Bil",
    "T_Bil": "T-Bil",
    "DBil": "D-Bil",
    "D.Bil": "D-Bil",
    "D_Bil": "D-Bil",
    "PLT": "Plt",
    "Platelet": "Plt",
    "Platelet_Count": "Plt",
    "hs.CRP": "hsCRP",
    "hs_CRP": "hsCRP",
    # Chinese examples; extend if your local raw data contains more names.
    "年齡": "Age",
    "性別": "Sex",
    "身高": "BH",
    "腰圍": "WC",
    "收縮壓": "SBP",
    "舒張壓": "DBP",
    "體重": "BW",
    "除脂體重": "FFM",
    "脂肪重量": "BFM",
    "體脂百分比": "BFP",
    "身體總水量": "TBW",
    "總體水分": "TBW",
    "血小板": "Plt",
    "血小板數": "Plt",
    "認知量表總分": "MoCA",
    "MoCA總分": "MoCA",
}


SUBJECT_ID_CANDIDATES = [
    "ID",
    "id",
    "SubjectID",
    "subject_id",
    "PatientID",
    "patient_id",
    "synthetic_patient_id",
]


@dataclass
class CleaningReport:
    """Small report returned by `clean_tabular_dataframe`."""

    n_rows_before: int
    n_rows_after: int
    n_columns_before: int
    n_columns_after: int
    duplicated_columns_removed: list[str]
    columns_kept: list[str]
    missing_summary: pd.DataFrame


def read_csv_with_encoding(
    path: str | Path,
    *,
    encodings: Iterable[str] = ("utf-8-sig", "utf-8", "big5", "cp950", "latin1"),
    **read_csv_kwargs,
) -> pd.DataFrame:
    """Read a CSV file with several encoding fallbacks.

    Parameters
    ----------
    path:
        CSV path.
    encodings:
        Encodings to try in order.
    read_csv_kwargs:
        Extra arguments passed to `pandas.read_csv`.

    Returns
    -------
    pd.DataFrame
    """

    last_error: Exception | None = None
    for encoding in encodings:
        try:
            return pd.read_csv(path, encoding=encoding, **read_csv_kwargs)
        except UnicodeDecodeError as exc:
            last_error = exc
    raise UnicodeDecodeError(
        "unknown",
        b"",
        0,
        1,
        f"Unable to read {path} with encodings={list(encodings)}. Last error: {last_error}",
    )


def normalize_column_name(name: object) -> str:
    """Normalize one column name.

    This handles whitespace, common punctuation variants, and known project-specific
    aliases such as `WHO.5` -> `WHO-5`.
    """

    text = str(name).strip()
    text = text.replace("\ufeff", "")
    text = text.replace(" ", "")
    return COLUMN_RENAME_MAP.get(text, text)


def normalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize all column names with `normalize_column_name`."""

    out = df.copy()
    out.columns = [normalize_column_name(col) for col in out.columns]
    return out


def remove_duplicate_columns(df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    """Remove duplicated column names while keeping the first occurrence."""

    duplicated_mask = df.columns.duplicated(keep="first")
    removed = df.columns[duplicated_mask].tolist()
    return df.loc[:, ~duplicated_mask].copy(), removed


def infer_subject_id_column(df: pd.DataFrame) -> str | None:
    """Return the first subject ID column found, if any."""

    for col in SUBJECT_ID_CANDIDATES:
        if col in df.columns:
            return col
    return None


def selected_columns_from_groups(groups: Iterable[str]) -> list[str]:
    """Flatten selected feature groups into an ordered column list."""

    columns: list[str] = []
    for group in groups:
        for col in FEATURE_GROUPS.get(group, []):
            if col not in columns:
                columns.append(col)
    return columns


def keep_selected_feature_groups(
    df: pd.DataFrame,
    groups: Iterable[str] = DEFAULT_KEEP_GROUPS,
    *,
    extra_keep: Iterable[str] | None = None,
) -> pd.DataFrame:
    """Keep only columns listed in project feature groups.

    Columns absent from the dataframe are ignored, so this function works on
    partial synthetic demo datasets.
    """

    selected = selected_columns_from_groups(groups)
    if extra_keep:
        selected.extend([col for col in extra_keep if col not in selected])

    keep_cols = [col for col in selected if col in df.columns]
    return df.loc[:, keep_cols].copy()


def summarize_missingness(df: pd.DataFrame) -> pd.DataFrame:
    """Create a variable-level missingness summary."""

    return (
        pd.DataFrame(
            {
                "variable": df.columns,
                "missing_count": df.isna().sum().to_numpy(),
                "missing_rate": df.isna().mean().to_numpy(),
                "non_missing_count": df.notna().sum().to_numpy(),
                "n_unique": [df[col].nunique(dropna=True) for col in df.columns],
                "dtype": [str(df[col].dtype) for col in df.columns],
            }
        )
        .sort_values(["missing_rate", "variable"], ascending=[False, True])
        .reset_index(drop=True)
    )


def coerce_numeric_when_possible(df: pd.DataFrame, *, exclude: Iterable[str] = ()) -> pd.DataFrame:
    """Convert object columns to numeric when conversion is mostly successful."""

    out = df.copy()
    exclude_set = set(exclude)
    for col in out.columns:
        if col in exclude_set:
            continue
        if out[col].dtype == "object":
            converted = pd.to_numeric(out[col], errors="coerce")
            # Convert only if at least half of the non-missing values were numeric.
            original_non_missing = out[col].notna().sum()
            converted_non_missing = converted.notna().sum()
            if original_non_missing > 0 and converted_non_missing / original_non_missing >= 0.5:
                out[col] = converted
    return out


def handle_missing_values(
    df: pd.DataFrame,
    *,
    strategy: Literal["none", "drop_rows", "median_mode"] = "median_mode",
    critical_columns: Iterable[str] = ("MoCA",),
) -> pd.DataFrame:
    """Handle missing values explicitly.

    Parameters
    ----------
    strategy:
        - "none": leave missing values unchanged.
        - "drop_rows": drop rows with missing values in critical columns.
        - "median_mode": impute numeric columns by median and non-numeric columns by mode.
    critical_columns:
        Columns that must be present when dropping rows.
    """

    out = df.copy()
    critical = [col for col in critical_columns if col in out.columns]

    if strategy == "none":
        return out

    if strategy == "drop_rows":
        if critical:
            out = out.dropna(subset=critical)
        else:
            out = out.dropna()
        return out

    if strategy == "median_mode":
        # Do not impute the target by default; keep target missingness visible.
        for col in out.columns:
            if col in critical:
                continue
            if pd.api.types.is_numeric_dtype(out[col]):
                if out[col].notna().any():
                    out[col] = out[col].fillna(out[col].median())
            else:
                modes = out[col].mode(dropna=True)
                if len(modes) > 0:
                    out[col] = out[col].fillna(modes.iloc[0])
        if critical:
            out = out.dropna(subset=critical)
        return out

    raise ValueError(f"Unknown missing-value strategy: {strategy}")


def standardize_continuous_columns(
    df: pd.DataFrame,
    *,
    exclude: Iterable[str] = ("ID", "patient_id", "subject_id", "synthetic_patient_id", "Sex", "Group", "MoCA"),
) -> pd.DataFrame:
    """Z-score standardize continuous numeric columns.

    This mirrors the thesis preprocessing logic, while preserving binary/category-like
    columns and the MoCA target by default.
    """

    out = df.copy()
    exclude_set = set(exclude)

    for col in out.columns:
        if col in exclude_set:
            continue
        if not pd.api.types.is_numeric_dtype(out[col]):
            continue

        non_missing = out[col].dropna()
        if non_missing.nunique() <= 2:
            # likely binary or constant
            continue

        std = non_missing.std(ddof=0)
        if std and not np.isclose(std, 0):
            out[col] = (out[col] - non_missing.mean()) / std

    return out


def add_data_quality_flags(df: pd.DataFrame) -> pd.DataFrame:
    """Add patient-level data quality flags useful for downstream uncertainty logic."""

    out = df.copy()
    core_present = [col for col in CORE_MODELING_COLUMNS if col in out.columns]

    if core_present:
        out["missing_core_feature_count"] = out[core_present].isna().sum(axis=1)
        out["missing_core_feature_flag"] = out["missing_core_feature_count"] > 0

    if "MoCA" in out.columns:
        out["moca_below_cutoff_flag"] = out["MoCA"] < 26

    return out


def clean_tabular_dataframe(
    df: pd.DataFrame,
    *,
    keep_groups: Iterable[str] = DEFAULT_KEEP_GROUPS,
    extra_keep: Iterable[str] | None = None,
    missing_strategy: Literal["none", "drop_rows", "median_mode"] = "median_mode",
    critical_columns: Iterable[str] = ("MoCA",),
    standardize: bool = False,
    add_quality_flags: bool = True,
) -> tuple[pd.DataFrame, CleaningReport]:
    """Clean a project-style clinical tabular dataframe.

    This is intended as a safe, reusable mock function for public portfolio code.
    """

    n_rows_before, n_cols_before = df.shape

    cleaned = normalize_column_names(df)
    cleaned, removed_duplicates = remove_duplicate_columns(cleaned)
    id_col = infer_subject_id_column(cleaned)

    cleaned = coerce_numeric_when_possible(cleaned, exclude=[id_col] if id_col else [])
    cleaned = keep_selected_feature_groups(cleaned, keep_groups, extra_keep=extra_keep)
    cleaned = handle_missing_values(cleaned, strategy=missing_strategy, critical_columns=critical_columns)

    if standardize:
        cleaned = standardize_continuous_columns(cleaned)

    if add_quality_flags:
        cleaned = add_data_quality_flags(cleaned)

    missing_summary = summarize_missingness(cleaned)

    report = CleaningReport(
        n_rows_before=n_rows_before,
        n_rows_after=cleaned.shape[0],
        n_columns_before=n_cols_before,
        n_columns_after=cleaned.shape[1],
        duplicated_columns_removed=removed_duplicates,
        columns_kept=list(cleaned.columns),
        missing_summary=missing_summary,
    )
    return cleaned, report


def clean_tabular_data(
    input_csv: str | Path,
    output_csv: str | Path | None = None,
    report_csv: str | Path | None = None,
    **kwargs,
) -> pd.DataFrame:
    """Load, clean, and optionally export a CSV file."""

    df = read_csv_with_encoding(input_csv)
    cleaned, report = clean_tabular_dataframe(df, **kwargs)

    if output_csv:
        Path(output_csv).parent.mkdir(parents=True, exist_ok=True)
        cleaned.to_csv(output_csv, index=False)

    if report_csv:
        Path(report_csv).parent.mkdir(parents=True, exist_ok=True)
        report.missing_summary.to_csv(report_csv, index=False)

    return cleaned


def main() -> None:
    """Command-line interface.

    Example:
        python src/data_preprocessing/tabular_cleaning.py \
            --input examples/synthetic_patient_examples.csv \
            --output data/processed/cleaned_patient_examples.csv \
            --report reports/tabular_missingness_summary.csv \
            --standardize
    """

    import argparse

    parser = argparse.ArgumentParser(description="Clean synthetic clinical tabular data.")
    parser.add_argument("--input", required=True, help="Input CSV path.")
    parser.add_argument("--output", required=True, help="Output cleaned CSV path.")
    parser.add_argument("--report", default=None, help="Optional missingness report CSV path.")
    parser.add_argument(
        "--missing-strategy",
        choices=["none", "drop_rows", "median_mode"],
        default="median_mode",
        help="Missing-value handling strategy.",
    )
    parser.add_argument("--standardize", action="store_true", help="Z-score standardize continuous predictors.")
    args = parser.parse_args()

    clean_tabular_data(
        args.input,
        output_csv=args.output,
        report_csv=args.report,
        missing_strategy=args.missing_strategy,
        standardize=args.standardize,
    )


if __name__ == "__main__":
    main()
