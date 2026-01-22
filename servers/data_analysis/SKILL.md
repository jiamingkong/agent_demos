---
name: data_analysis
description: Data analysis capabilities using pandas (aggregation, grouping, pivoting, merging, sorting, filtering, correlation).
allowed-tools:
  - aggregate
  - group_by
  - pivot_table
  - merge_dataframes
  - sort_values
  - filter_rows
  - correlation_matrix
---

# Data Analysis Skill

This skill enables the agent to perform data analysis operations on CSV files using pandas.

## Tools

### aggregate
Compute summary statistics (sum, mean, count, etc.) for numeric columns.

- `file_path`: Absolute path to the CSV file.
- `operations`: Dictionary mapping column names to aggregation functions (e.g., {"col1": "sum", "col2": "mean"}).
- `output_path`: Optional path to save the aggregated results as CSV. If not provided, returns summary as text.

### group_by
Group rows by one or more columns and compute aggregations.

- `file_path`: Absolute path to the CSV file.
- `group_columns`: List of column names to group by.
- `aggregations`: Dictionary mapping column names to aggregation functions (e.g., {"col1": "sum", "col2": "mean"}).
- `output_path`: Optional path to save the grouped results as CSV.

### pivot_table
Create a pivot table from the data.

- `file_path`: Absolute path to the CSV file.
- `index`: Column(s) to use as row labels.
- `columns`: Column(s) to use as column labels.
- `values`: Column(s) to aggregate.
- `aggfunc`: Aggregation function (default "sum").
- `output_path`: Optional path to save the pivot table as CSV.

### merge_dataframes
Merge two CSV files (inner, outer, left, right join).

- `left_file`: Path to the left CSV file.
- `right_file`: Path to the right CSV file.
- `left_on`: Column(s) from left file to join on.
- `right_on`: Column(s) from right file to join on.
- `how`: Type of join: "inner", "outer", "left", "right" (default "inner").
- `output_path`: Optional path to save the merged result as CSV.

### sort_values
Sort rows by one or more columns.

- `file_path`: Absolute path to the CSV file.
- `by`: Column name or list of column names to sort by.
- `ascending`: Boolean or list of booleans (default True).
- `output_path`: Optional path to save the sorted data as CSV.

### filter_rows
Filter rows based on conditions.

- `file_path`: Absolute path to the CSV file.
- `condition`: String expression using column names and operators (e.g., "col1 > 10 and col2 == 'value'"). Uses pandas query syntax.
- `output_path`: Optional path to save the filtered data as CSV.

### correlation_matrix
Compute Pearson correlation matrix for numeric columns in a CSV file.

- `file_path`: Absolute path to the CSV file.
- `output_path`: Optional path to save the correlation matrix as CSV.

Returns correlation matrix as text or saved file message.

## Dependencies

- pandas (already installed via project requirements)
- numpy (already installed)
