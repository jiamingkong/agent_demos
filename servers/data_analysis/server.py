import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import numpy as np
import pandas as pd
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("data_analysis", log_level="ERROR")


def _ensure_output_path(
    input_path: Path, output_path: Optional[str], suffix: str = "_result"
) -> Path:
    """If output_path is None, generate a default by adding suffix before extension."""
    if output_path is None:
        stem = input_path.stem + suffix
        return input_path.parent / (stem + input_path.suffix)
    return Path(output_path)


@mcp.tool()
def aggregate(
    file_path: str,
    operations: Dict[str, str],
    output_path: Optional[str] = None,
) -> str:
    """
    Compute summary statistics (sum, mean, count, etc.) for numeric columns.

    Args:
        file_path: Absolute path to the CSV file.
        operations: Dictionary mapping column names to aggregation functions (e.g., {"col1": "sum", "col2": "mean"}).
        output_path: Optional path to save the aggregated results as CSV. If not provided, returns summary as text.
    """
    try:
        path = Path(file_path)
        if not path.exists():
            return f"Error: File '{file_path}' not found."
        df = pd.read_csv(path)
        # Validate columns
        for col in operations.keys():
            if col not in df.columns:
                return f"Error: Column '{col}' not found in CSV."
        # Perform aggregation
        agg_results = {}
        for col, func in operations.items():
            if func == "sum":
                agg_results[col] = df[col].sum()
            elif func == "mean":
                agg_results[col] = df[col].mean()
            elif func == "median":
                agg_results[col] = df[col].median()
            elif func == "min":
                agg_results[col] = df[col].min()
            elif func == "max":
                agg_results[col] = df[col].max()
            elif func == "count":
                agg_results[col] = df[col].count()
            elif func == "std":
                agg_results[col] = df[col].std()
            elif func == "var":
                agg_results[col] = df[col].var()
            else:
                return f"Error: Unsupported aggregation function '{func}'."
        # Create a DataFrame for output
        agg_df = pd.DataFrame([agg_results])
        if output_path:
            out_path = _ensure_output_path(path, output_path, suffix="_aggregated")
            agg_df.to_csv(out_path, index=False)
            return f"Aggregation completed. Results saved to {out_path}"
        else:
            return f"Aggregation results:\n{agg_df.to_string(index=False)}"
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
def group_by(
    file_path: str,
    group_columns: List[str],
    aggregations: Dict[str, str],
    output_path: Optional[str] = None,
) -> str:
    """
    Group rows by one or more columns and compute aggregations.

    Args:
        file_path: Absolute path to the CSV file.
        group_columns: List of column names to group by.
        aggregations: Dictionary mapping column names to aggregation functions (e.g., {"col1": "sum", "col2": "mean"}).
        output_path: Optional path to save the grouped results as CSV.
    """
    try:
        path = Path(file_path)
        if not path.exists():
            return f"Error: File '{file_path}' not found."
        df = pd.read_csv(path)
        # Validate columns
        for col in group_columns:
            if col not in df.columns:
                return f"Error: Group column '{col}' not found."
        for col in aggregations.keys():
            if col not in df.columns:
                return f"Error: Aggregation column '{col}' not found."
        # Map aggregation strings to pandas functions
        agg_map = {
            "sum": "sum",
            "mean": "mean",
            "median": "median",
            "min": "min",
            "max": "max",
            "count": "count",
            "std": "std",
            "var": "var",
        }
        pandas_agg = {}
        for col, func in aggregations.items():
            if func not in agg_map:
                return f"Error: Unsupported aggregation function '{func}'."
            pandas_agg[col] = agg_map[func]
        # Perform groupby
        grouped = df.groupby(group_columns).agg(pandas_agg).reset_index()
        if output_path:
            out_path = _ensure_output_path(path, output_path, suffix="_grouped")
            grouped.to_csv(out_path, index=False)
            return f"Group‑by completed. Results saved to {out_path}"
        else:
            return f"Group‑by results (first 10 rows):\n{grouped.head(10).to_string(index=False)}"
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
def pivot_table(
    file_path: str,
    index: Union[str, List[str]],
    columns: Union[str, List[str]],
    values: Union[str, List[str]],
    aggfunc: str = "sum",
    output_path: Optional[str] = None,
) -> str:
    """
    Create a pivot table from the data.

    Args:
        file_path: Absolute path to the CSV file.
        index: Column(s) to use as row labels.
        columns: Column(s) to use as column labels.
        values: Column(s) to aggregate.
        aggfunc: Aggregation function (default "sum").
        output_path: Optional path to save the pivot table as CSV.
    """
    try:
        path = Path(file_path)
        if not path.exists():
            return f"Error: File '{file_path}' not found."
        df = pd.read_csv(path)
        # Ensure index, columns, values are lists
        if isinstance(index, str):
            index = [index]
        if isinstance(columns, str):
            columns = [columns]
        if isinstance(values, str):
            values = [values]
        # Validate columns
        for col in index + columns + values:
            if col not in df.columns:
                return f"Error: Column '{col}' not found."
        # Map aggfunc
        agg_map = {
            "sum": "sum",
            "mean": "mean",
            "median": "median",
            "min": "min",
            "max": "max",
            "count": "count",
            "std": "std",
            "var": "var",
        }
        if aggfunc not in agg_map:
            return f"Error: Unsupported aggregation function '{aggfunc}'."
        # Create pivot table
        pivot = pd.pivot_table(
            df, index=index, columns=columns, values=values, aggfunc=agg_map[aggfunc]
        )
        if output_path:
            out_path = _ensure_output_path(path, output_path, suffix="_pivot")
            pivot.to_csv(out_path)
            return f"Pivot table saved to {out_path}"
        else:
            # Flatten multi‑index columns for readability
            pivot = pivot.reset_index()
            return (
                f"Pivot table (first 10 rows):\n{pivot.head(10).to_string(index=False)}"
            )
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
def merge_dataframes(
    left_file: str,
    right_file: str,
    left_on: Union[str, List[str]],
    right_on: Union[str, List[str]],
    how: str = "inner",
    output_path: Optional[str] = None,
) -> str:
    """
    Merge two CSV files (inner, outer, left, right join).

    Args:
        left_file: Path to the left CSV file.
        right_file: Path to the right CSV file.
        left_on: Column(s) from left file to join on.
        right_on: Column(s) from right file to join on.
        how: Type of join: "inner", "outer", "left", "right" (default "inner").
        output_path: Optional path to save the merged result as CSV.
    """
    try:
        left_path = Path(left_file)
        right_path = Path(right_file)
        if not left_path.exists():
            return f"Error: Left file '{left_file}' not found."
        if not right_path.exists():
            return f"Error: Right file '{right_file}' not found."
        left_df = pd.read_csv(left_path)
        right_df = pd.read_csv(right_path)
        # Ensure left_on and right_on are lists
        if isinstance(left_on, str):
            left_on = [left_on]
        if isinstance(right_on, str):
            right_on = [right_on]
        # Validate columns
        for col in left_on:
            if col not in left_df.columns:
                return f"Error: Left column '{col}' not found."
        for col in right_on:
            if col not in right_df.columns:
                return f"Error: Right column '{col}' not found."
        # Merge
        merged = pd.merge(
            left_df, right_df, left_on=left_on, right_on=right_on, how=how
        )
        if output_path:
            out_path = Path(output_path)
            merged.to_csv(out_path, index=False)
            return f"Merged data saved to {out_path}"
        else:
            return f"Merged data (first 10 rows):\n{merged.head(10).to_string(index=False)}"
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
def sort_values(
    file_path: str,
    by: Union[str, List[str]],
    ascending: Union[bool, List[bool]] = True,
    output_path: Optional[str] = None,
) -> str:
    """
    Sort rows by one or more columns.

    Args:
        file_path: Absolute path to the CSV file.
        by: Column name or list of column names to sort by.
        ascending: Boolean or list of booleans (default True).
        output_path: Optional path to save the sorted data as CSV.
    """
    try:
        path = Path(file_path)
        if not path.exists():
            return f"Error: File '{file_path}' not found."
        df = pd.read_csv(path)
        # Ensure by is a list
        if isinstance(by, str):
            by = [by]
        # Validate columns
        for col in by:
            if col not in df.columns:
                return f"Error: Column '{col}' not found."
        # Sort
        sorted_df = df.sort_values(by=by, ascending=ascending)
        if output_path:
            out_path = _ensure_output_path(path, output_path, suffix="_sorted")
            sorted_df.to_csv(out_path, index=False)
            return f"Sorted data saved to {out_path}"
        else:
            return f"Sorted data (first 10 rows):\n{sorted_df.head(10).to_string(index=False)}"
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
def filter_rows(
    file_path: str,
    condition: str,
    output_path: Optional[str] = None,
) -> str:
    """
    Filter rows based on conditions.

    Args:
        file_path: Absolute path to the CSV file.
        condition: String expression using column names and operators (e.g., "col1 > 10 and col2 == 'value'"). Uses pandas query syntax.
        output_path: Optional path to save the filtered data as CSV.
    """
    try:
        path = Path(file_path)
        if not path.exists():
            return f"Error: File '{file_path}' not found."
        df = pd.read_csv(path)
        # Apply query
        filtered = df.query(condition)
        if output_path:
            out_path = _ensure_output_path(path, output_path, suffix="_filtered")
            filtered.to_csv(out_path, index=False)
            return f"Filtered data saved to {out_path}"
        else:
            return f"Filtered data ({len(filtered)} rows):\n{filtered.head(20).to_string(index=False)}"
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
def correlation_matrix(file_path: str, output_path: Optional[str] = None) -> str:
    """
    Compute Pearson correlation matrix for numeric columns in a CSV file.

    Args:
        file_path: Absolute path to the CSV file.
        output_path: Optional path to save the correlation matrix as CSV.

    Returns:
        Correlation matrix as text or saved file message.
    """
    try:
        path = Path(file_path)
        if not path.exists():
            return f"Error: File '{file_path}' not found."
        df = pd.read_csv(path)
        numeric_df = df.select_dtypes(include=[np.number])
        if numeric_df.empty:
            return "Error: No numeric columns found in the dataset."
        corr = numeric_df.corr()
        if output_path:
            out_path = Path(output_path)
            corr.to_csv(out_path)
            return f"Correlation matrix saved to {out_path}"
        else:
            return f"Correlation matrix:\n{corr.to_string()}"
    except Exception as e:
        return f"Error: {str(e)}"


if __name__ == "__main__":
    mcp.run()
