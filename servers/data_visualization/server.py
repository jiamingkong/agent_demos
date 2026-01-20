from mcp.server.fastmcp import FastMCP
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os

mcp = FastMCP("data_visualization", log_level="ERROR")

# Store the current figure globally (simple approach)
_current_fig = None

def _ensure_figure():
    """Ensure there is an active figure."""
    global _current_fig
    if _current_fig is None or plt.fignum_exists(_current_fig.number) == False:
        _current_fig = plt.figure()

@mcp.tool()
def plot_line(x_data: list, y_data: list, title: str = "", xlabel: str = "", ylabel: str = "") -> str:
    """
    Create a line plot from x and y data.

    Args:
        x_data: List of x values.
        y_data: List of y values.
        title: Plot title (optional).
        xlabel: X-axis label (optional).
        ylabel: Y-axis label (optional).
    """
    if len(x_data) != len(y_data):
        return "Error: x_data and y_data must have the same length."
    _ensure_figure()
    plt.clf()
    plt.plot(x_data, y_data, marker='o')
    if title:
        plt.title(title)
    if xlabel:
        plt.xlabel(xlabel)
    if ylabel:
        plt.ylabel(ylabel)
    plt.grid(True)
    return f"Created line plot with {len(x_data)} points."

@mcp.tool()
def plot_bar(categories: list, values: list, title: str = "", xlabel: str = "", ylabel: str = "") -> str:
    """
    Create a bar chart from categories and values.

    Args:
        categories: List of category labels.
        values: List of corresponding values.
        title: Plot title (optional).
        xlabel: X-axis label (optional).
        ylabel: Y-axis label (optional).
    """
    if len(categories) != len(values):
        return "Error: categories and values must have the same length."
    _ensure_figure()
    plt.clf()
    plt.bar(categories, values)
    if title:
        plt.title(title)
    if xlabel:
        plt.xlabel(xlabel)
    if ylabel:
        plt.ylabel(ylabel)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    return f"Created bar chart with {len(categories)} categories."

@mcp.tool()
def plot_scatter(x_data: list, y_data: list, title: str = "", xlabel: str = "", ylabel: str = "") -> str:
    """
    Create a scatter plot.

    Args:
        x_data: List of x values.
        y_data: List of y values.
        title: Plot title (optional).
        xlabel: X-axis label (optional).
        ylabel: Y-axis label (optional).
    """
    if len(x_data) != len(y_data):
        return "Error: x_data and y_data must have the same length."
    _ensure_figure()
    plt.clf()
    plt.scatter(x_data, y_data)
    if title:
        plt.title(title)
    if xlabel:
        plt.xlabel(xlabel)
    if ylabel:
        plt.ylabel(ylabel)
    plt.grid(True)
    return f"Created scatter plot with {len(x_data)} points."

@mcp.tool()
def plot_histogram(data: list, bins: int = 10, title: str = "", xlabel: str = "", ylabel: str = "") -> str:
    """
    Create a histogram from data.

    Args:
        data: List of numerical values.
        bins: Number of bins (optional, default=10).
        title: Plot title (optional).
        xlabel: X-axis label (optional).
        ylabel: Y-axis label (optional).
    """
    if not data:
        return "Error: data list cannot be empty."
    _ensure_figure()
    plt.clf()
    plt.hist(data, bins=bins, edgecolor='black')
    if title:
        plt.title(title)
    if xlabel:
        plt.xlabel(xlabel)
    if ylabel:
        plt.ylabel(ylabel)
    return f"Created histogram with {len(data)} data points and {bins} bins."

@mcp.tool()
def plot_box(data_series: list, labels: list = None, title: str = "", xlabel: str = "", ylabel: str = "") -> str:
    """
    Create a box plot from multiple data series.

    Args:
        data_series: List of lists, each inner list is a series of values.
        labels: List of labels for each series (optional). If not provided, default labels are used.
        title: Plot title (optional).
        xlabel: X-axis label (optional).
        ylabel: Y-axis label (optional).
    """
    if not data_series:
        return "Error: data_series cannot be empty."
    _ensure_figure()
    plt.clf()
    plt.boxplot(data_series, labels=labels)
    if title:
        plt.title(title)
    if xlabel:
        plt.xlabel(xlabel)
    if ylabel:
        plt.ylabel(ylabel)
    plt.grid(True)
    return f"Created box plot with {len(data_series)} series."

@mcp.tool()
def save_plot(filename: str, dpi: int = 100) -> str:
    """
    Save the current plot to a file.

    Args:
        filename: Output file path (should end with .png, .jpg, or .pdf).
        dpi: Dots per inch (optional, default=100).
    """
    global _current_fig
    if _current_fig is None:
        return "Error: No plot to save. Create a plot first."
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        _current_fig.savefig(filename, dpi=dpi, bbox_inches='tight')
        return f"Plot saved to {filename}"
    except Exception as e:
        return f"Error saving plot: {e}"

if __name__ == "__main__":
    mcp.run()
