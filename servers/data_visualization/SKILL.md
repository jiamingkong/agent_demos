---
name: data_visualization
description: Data visualization capabilities using matplotlib and pandas.
allowed-tools:
  - plot_line
  - plot_bar
  - plot_scatter
  - plot_histogram
  - plot_box
  - save_plot
---

# Data Visualization Skill

This skill enables the agent to create various types of plots and charts using matplotlib.

## Tools

### plot_line
Create a line plot from x and y data.
- `x_data`: List of x values.
- `y_data`: List of y values.
- `title`: Plot title (optional).
- `xlabel`: X-axis label (optional).
- `ylabel`: Y-axis label (optional).

### plot_bar
Create a bar chart from categories and values.
- `categories`: List of category labels.
- `values`: List of corresponding values.
- `title`: Plot title (optional).
- `xlabel`: X-axis label (optional).
- `ylabel`: Y-axis label (optional).

### plot_scatter
Create a scatter plot.
- `x_data`: List of x values.
- `y_data`: List of y values.
- `title`: Plot title (optional).
- `xlabel`: X-axis label (optional).
- `ylabel`: Y-axis label (optional).

### plot_histogram
Create a histogram from data.
- `data`: List of numerical values.
- `bins`: Number of bins (optional, default=10).
- `title`: Plot title (optional).
- `xlabel`: X-axis label (optional).
- `ylabel`: Y-axis label (optional).

### plot_box
Create a box plot from multiple data series.
- `data_series`: List of lists, each inner list is a series of values.
- `labels`: List of labels for each series (optional). If not provided, default labels are used.
- `title`: Plot title (optional).
- `xlabel`: X-axis label (optional).
- `ylabel`: Y-axis label (optional).

### save_plot
Save the current plot to a file.
- `filename`: Output file path (should end with .png, .jpg, or .pdf).
- `dpi`: Dots per inch (optional, default=100).
