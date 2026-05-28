"""
correlation_grouping.py

Pairwise correlation and feature grouping utilities for the
risk-aware-clinical-ai-screening project.

This module reconstructs the R workflow:
- select numeric variables;
- remove constant columns;
- standardize values before correlation-oriented inspection;
- compute Pearson pairwise correlations with pairwise-complete observations;
- flag variable pairs with |correlation| >= 0.3;
- group connected variables into correlation groups;
- export correlation matrix, pair summary, and group summary.

Important:
    This module is intended for synthetic / de-identified demo data only.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd


DEFAULT_EXCLUDE_COLUMNS: set[str] = {
    "ID",
    "id",
    "patient_id",
    "subject_id",
    "synthetic_patient_id",
    "Name",
    "姓名",
    "病歷號",
}


@dataclass
class CorrelationGroupingResult:
    """Output of `run_correlation_grouping`."""

    correlation_matrix: pd.DataFrame
    high_correlation_pairs: pd.DataFrame
    correlation_groups: pd.DataFrame
    dropped_constant_columns: list[str]


def select_numeric_columns(
    df: pd.DataFrame,
    *,
    exclude_columns: Iterable[str] = DEFAULT_EXCLUDE_COLUMNS,
) -> pd.DataFrame:
    """Convert possible numeric columns and keep numeric analysis columns."""

    exclude = set(exclude_columns)
    out = pd.DataFrame(index=df.index)

    for col in df.columns:
        if col in exclude:
            continue

        if pd.api.types.is_numeric_dtype(df[col]):
            out[col] = df[col]
            continue

        converted = pd.to_numeric(df[col], errors="coerce")
        original_non_missing = df[col].notna().sum()
        converted_non_missing = converted.notna().sum()

        # Keep object columns only when most non-missing values can be parsed as numeric.
        if original_non_missing > 0 and converted_non_missing / original_non_missing >= 0.8:
            out[col] = converted

    return out


def remove_constant_columns(df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    """Remove columns with <= 1 unique non-missing value."""

    dropped = [col for col in df.columns if df[col].nunique(dropna=True) <= 1]
    return df.drop(columns=dropped), dropped


def zscore_standardize(df: pd.DataFrame) -> pd.DataFrame:
    """Z-score standardize numeric dataframe columns.

    Constant columns should already be removed before calling this function.
    """

    out = df.copy()
    for col in out.columns:
        mean = out[col].mean(skipna=True)
        std = out[col].std(skipna=True, ddof=0)
        if std and not np.isclose(std, 0):
            out[col] = (out[col] - mean) / std
    return out


def compute_pairwise_correlation(
    df: pd.DataFrame,
    *,
    method: str = "pearson",
    standardize: bool = True,
) -> pd.DataFrame:
    """Compute a pairwise-complete correlation matrix.

    Pandas `.corr()` uses pairwise complete observations by default, matching
    the R workflow: `cor(x, use = "pairwise.complete.obs")`.
    """

    numeric = select_numeric_columns(df)
    numeric, _ = remove_constant_columns(numeric)

    if standardize:
        numeric = zscore_standardize(numeric)

    return numeric.corr(method=method, min_periods=2)


def extract_high_correlation_pairs(
    corr: pd.DataFrame,
    *,
    threshold: float = 0.30,
    include_self: bool = False,
) -> pd.DataFrame:
    """Extract upper-triangle variable pairs with absolute correlation >= threshold."""

    rows: list[dict] = []
    cols = list(corr.columns)

    for i, var_a in enumerate(cols):
        start_j = i if include_self else i + 1
        for j in range(start_j, len(cols)):
            var_b = cols[j]
            value = corr.iloc[i, j]
            if pd.isna(value):
                continue
            if abs(value) >= threshold:
                rows.append(
                    {
                        "variable_a": var_a,
                        "variable_b": var_b,
                        "correlation": float(value),
                        "abs_correlation": float(abs(value)),
                        "direction": "positive" if value > 0 else "negative",
                    }
                )

    return (
        pd.DataFrame(rows)
        .sort_values("abs_correlation", ascending=False)
        .reset_index(drop=True)
        if rows
        else pd.DataFrame(columns=["variable_a", "variable_b", "correlation", "abs_correlation", "direction"])
    )


def _connected_components(nodes: Iterable[str], edges: Iterable[tuple[str, str]]) -> list[list[str]]:
    """Compute connected components without external graph libraries."""

    adjacency: dict[str, set[str]] = {node: set() for node in nodes}

    for a, b in edges:
        adjacency.setdefault(a, set()).add(b)
        adjacency.setdefault(b, set()).add(a)

    visited: set[str] = set()
    components: list[list[str]] = []

    for node in adjacency:
        if node in visited:
            continue

        stack = [node]
        component: list[str] = []

        while stack:
            current = stack.pop()
            if current in visited:
                continue
            visited.add(current)
            component.append(current)
            stack.extend(sorted(adjacency[current] - visited))

        components.append(sorted(component))

    return components


def build_correlation_groups(
    pairs: pd.DataFrame,
    *,
    all_variables: Iterable[str],
    min_group_size: int = 2,
) -> pd.DataFrame:
    """Group variables connected by high-correlation pairs."""

    if pairs.empty:
        return pd.DataFrame(columns=["group_id", "n_variables", "variables"])

    edges = list(zip(pairs["variable_a"], pairs["variable_b"]))
    components = _connected_components(all_variables, edges)

    rows: list[dict] = []
    group_id = 1

    for component in components:
        if len(component) < min_group_size:
            continue

        rows.append(
            {
                "group_id": f"corr_group_{group_id:02d}",
                "n_variables": len(component),
                "variables": ", ".join(component),
            }
        )
        group_id += 1

    return pd.DataFrame(rows)


def run_correlation_grouping(
    df: pd.DataFrame,
    *,
    threshold: float = 0.30,
    method: str = "pearson",
    standardize: bool = True,
    exclude_columns: Iterable[str] = DEFAULT_EXCLUDE_COLUMNS,
) -> CorrelationGroupingResult:
    """Run full pairwise correlation grouping workflow."""

    numeric = select_numeric_columns(df, exclude_columns=exclude_columns)
    numeric, dropped_constants = remove_constant_columns(numeric)

    working = zscore_standardize(numeric) if standardize else numeric
    corr = working.corr(method=method, min_periods=2)

    pairs = extract_high_correlation_pairs(corr, threshold=threshold)
    groups = build_correlation_groups(pairs, all_variables=corr.columns)

    return CorrelationGroupingResult(
        correlation_matrix=corr,
        high_correlation_pairs=pairs,
        correlation_groups=groups,
        dropped_constant_columns=dropped_constants,
    )


def export_correlation_outputs(
    result: CorrelationGroupingResult,
    *,
    matrix_csv: str | Path,
    pairs_csv: str | Path,
    groups_csv: str | Path,
    dropped_columns_csv: str | Path | None = None,
) -> None:
    """Export correlation matrix, high-correlation pairs, and groups."""

    Path(matrix_csv).parent.mkdir(parents=True, exist_ok=True)
    Path(pairs_csv).parent.mkdir(parents=True, exist_ok=True)
    Path(groups_csv).parent.mkdir(parents=True, exist_ok=True)

    result.correlation_matrix.to_csv(matrix_csv)
    result.high_correlation_pairs.to_csv(pairs_csv, index=False)
    result.correlation_groups.to_csv(groups_csv, index=False)

    if dropped_columns_csv:
        Path(dropped_columns_csv).parent.mkdir(parents=True, exist_ok=True)
        pd.DataFrame({"dropped_constant_column": result.dropped_constant_columns}).to_csv(
            dropped_columns_csv, index=False
        )


def plot_correlation_heatmap(
    corr: pd.DataFrame,
    output_png: str | Path,
    *,
    figsize: tuple[int, int] = (12, 10),
) -> None:
    """Create a simple matplotlib correlation heatmap.

    This is intentionally lightweight and avoids seaborn so the portfolio repo
    remains easy to run.
    """

    import matplotlib.pyplot as plt

    Path(output_png).parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=figsize)
    im = ax.imshow(corr.values, vmin=-1, vmax=1)
    ax.set_xticks(range(len(corr.columns)))
    ax.set_yticks(range(len(corr.index)))
    ax.set_xticklabels(corr.columns, rotation=90, fontsize=6)
    ax.set_yticklabels(corr.index, fontsize=6)
    ax.set_title("Pairwise Correlation Matrix")
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    fig.tight_layout()
    fig.savefig(output_png, dpi=300)
    plt.close(fig)


def main() -> None:
    """Command-line interface.

    Example:
        python src/data_preprocessing/correlation_grouping.py \
            --input data/processed/filtered_patient_examples.csv \
            --matrix-output reports/correlation_matrix.csv \
            --pairs-output reports/high_correlation_pairs.csv \
            --groups-output reports/correlation_groups.csv \
            --threshold 0.3
    """

    import argparse

    parser = argparse.ArgumentParser(description="Compute pairwise correlations and group related variables.")
    parser.add_argument("--input", required=True, help="Input CSV path.")
    parser.add_argument("--matrix-output", required=True, help="Correlation matrix CSV output path.")
    parser.add_argument("--pairs-output", required=True, help="High-correlation pair CSV output path.")
    parser.add_argument("--groups-output", required=True, help="Correlation group CSV output path.")
    parser.add_argument("--dropped-output", default=None, help="Optional dropped constant columns CSV path.")
    parser.add_argument("--plot-output", default=None, help="Optional heatmap PNG output path.")
    parser.add_argument("--threshold", type=float, default=0.30, help="Absolute correlation threshold.")
    parser.add_argument("--method", default="pearson", choices=["pearson", "spearman", "kendall"])
    parser.add_argument("--no-standardize", action="store_true", help="Disable Z-score standardization before corr.")
    args = parser.parse_args()

    df = pd.read_csv(args.input)
    result = run_correlation_grouping(
        df,
        threshold=args.threshold,
        method=args.method,
        standardize=not args.no_standardize,
    )
    export_correlation_outputs(
        result,
        matrix_csv=args.matrix_output,
        pairs_csv=args.pairs_output,
        groups_csv=args.groups_output,
        dropped_columns_csv=args.dropped_output,
    )

    if args.plot_output:
        plot_correlation_heatmap(result.correlation_matrix, args.plot_output)


if __name__ == "__main__":
    main()
