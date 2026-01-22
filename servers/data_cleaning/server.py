from pathlib import Path
from typing import List, Optional, Union

import pandas as pd
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("data_cleaning", log_level="ERROR")


def _ensure_output_path(
    input_path: Path, output_path: Optional[str], suffix: str = "_cleaned"
) -> Path:
    """If output_path is None, generate a default by adding suffix before extension."""
    if output_path is None:
        stem = input_path.stem + suffix
        return input_path.parent / (stem + input_path.suffix)
    return Path(output_path)


@mcp.tool()
def drop_missing_values(
    file_path: str, output_path: Optional[str] = None, axis: int = 0, how: str = "any"
) -> str:
    """
    Drop rows with missing values from a CSV file.

    Args:
        file_path: Path to the input CSV file.
        output_path: Path to save the cleaned CSV (optional).
        axis: Drop rows (0) or columns (1). Default 0.
        how: 'any' or 'all'. Default 'any'.

    Returns:
        Success message with path to saved file.
    """
    try:
        path = Path(file_path)
        if not path.exists():
            return f"Error: File '{file_path}' not found."
        df = pd.read_csv(path)
        df_cleaned = df.dropna(axis=axis, how=how)
        out_path = _ensure_output_path(path, output_path, suffix="_dropped")
        df_cleaned.to_csv(out_path, index=False)
        return f"Missing values dropped. Saved to {out_path}"
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
def fill_missing(
    file_path: str,
    output_path: Optional[str] = None,
    method: str = "mean",
    columns: Optional[List[str]] = None,
) -> str:
    """
    Fill missing values in a CSV file.

    Args:
        file_path: Path to the input CSV file.
        output_path: Path to save the filled CSV (optional).
        method: 'mean', 'median', 'mode', or a constant value.
        columns: List of column names to fill (optional, fill all columns if not specified).

    Returns:
        Success message.
    """
    try:
        path = Path(file_path)
        if not path.exists():
            return f"Error: File '{file_path}' not found."
        df = pd.read_csv(path)
        if columns is None:
            columns = df.columns.tolist()
        for col in columns:
            if col not in df.columns:
                return f"Error: Column '{col}' not found."
            if method == "mean":
                fill_val = df[col].mean()
            elif method == "median":
                fill_val = df[col].median()
            elif method == "mode":
                fill_val = df[col].mode().iloc[0] if not df[col].mode().empty else None
            else:
                # try to interpret as constant
                try:
                    fill_val = float(method)
                except ValueError:
                    fill_val = method  # string constant
            df[col] = df[col].fillna(fill_val)
        out_path = _ensure_output_path(path, output_path, suffix="_filled")
        df.to_csv(out_path, index=False)
        return f"Missing values filled using {method}. Saved to {out_path}"
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
def remove_duplicates(
    file_path: str,
    output_path: Optional[str] = None,
    subset: Optional[List[str]] = None,
    keep: str = "first",
) -> str:
    """
    Remove duplicate rows from a CSV file.

    Args:
        file_path: Path to the input CSV file.
        output_path: Path to save the deduplicated CSV (optional).
        subset: List of column names to consider for duplicates (optional, all columns).
        keep: 'first', 'last', or False (drop all duplicates). Default 'first'.

    Returns:
        Success message.
    """
    try:
        path = Path(file_path)
        if not path.exists():
            return f"Error: File '{file_path}' not found."
        df = pd.read_csv(path)
        df_dedup = df.drop_duplicates(subset=subset, keep=keep)
        out_path = _ensure_output_path(path, output_path, suffix="_deduplicated")
        df_dedup.to_csv(out_path, index=False)
        return f"Duplicates removed. Saved to {out_path}"
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
def normalize_column(
    file_path: str,
    column: str,
    output_path: Optional[str] = None,
    method: str = "minmax",
) -> str:
    """
    Normalize a numeric column using min‑max scaling or standardization.

    Args:
        file_path: Path to the input CSV file.
        column: Name of the column to normalize.
        output_path: Path to save the normalized CSV (optional).
        method: 'minmax' (scale to [0,1]) or 'standard' (z‑score). Default 'minmax'.

    Returns:
        Success message.
    """
    try:
        path = Path(file_path)
        if not path.exists():
            return f"Error: File '{file_path}' not found."
        df = pd.read_csv(path)
        if column not in df.columns:
            return f"Error: Column '{column}' not found."
        if method == "minmax":
            col_min = df[column].min()
            col_max = df[column].max()
            if col_max == col_min:
                df[column + "_normalized"] = 0.0
            else:
                df[column + "_normalized"] = (df[column] - col_min) / (
                    col_max - col_min
                )
        elif method == "standard":
            col_mean = df[column].mean()
            col_std = df[column].std()
            if col_std == 0:
                df[column + "_normalized"] = 0.0
            else:
                df[column + "_normalized"] = (df[column] - col_mean) / col_std
        else:
            return f"Error: Unknown method '{method}'. Use 'minmax' or 'standard'."
        out_path = _ensure_output_path(path, output_path, suffix="_normalized")
        df.to_csv(out_path, index=False)
        return f"Column '{column}' normalized using {method}. Saved to {out_path}"
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
def encode_categorical(
    file_path: str,
    column: str,
    output_path: Optional[str] = None,
    method: str = "onehot",
    drop_first: bool = False,
) -> str:
    """
    Encode a categorical column using one‑hot encoding or label encoding.

    Args:
        file_path: Path to the input CSV file.
        column: Name of the categorical column to encode.
        output_path: Path to save the encoded CSV (optional).
        method: 'onehot' or 'label'. Default 'onehot'.
        drop_first: Whether to drop the first category in one‑hot encoding (avoid dummy trap).

    Returns:
        Success message.
    """
    try:
        path = Path(file_path)
        if not path.exists():
            return f"Error: File '{file_path}' not found."
        df = pd.read_csv(path)
        if column not in df.columns:
            return f"Error: Column '{column}' not found."

        if method == "label":
            from sklearn.preprocessing import LabelEncoder

            le = LabelEncoder()
            df[column + "_encoded"] = le.fit_transform(df[column])
            out_path = _ensure_output_path(path, output_path, suffix="_label_encoded")
            df.to_csv(out_path, index=False)
            return f"Label encoding applied to column '{column}'. Saved to {out_path}"
        elif method == "onehot":
            dummies = pd.get_dummies(df[column], prefix=column, drop_first=drop_first)
            df = pd.concat([df, dummies], axis=1)
            # Optionally drop original column? Could add parameter, but for simplicity keep.
            out_path = _ensure_output_path(path, output_path, suffix="_onehot_encoded")
            df.to_csv(out_path, index=False)
            return f"One‑hot encoding applied to column '{column}'. Saved to {out_path}"
        else:
            return f"Error: Unknown method '{method}'. Use 'onehot' or 'label'."
    except Exception as e:
        return f"Error: {str(e)}"


if __name__ == "__main__":
    mcp.run()
