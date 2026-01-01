from typing import List, Optional, Sequence
import os

from matplotlib.figure import Figure
import matplotlib
matplotlib.rcParams["svg.fonttype"] = "none"
matplotlib.rcParams["font.family"] = "DejaVu Sans"
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from ....util import create_directory


class DataPlotter:
    """
    Class to plot graphs based on test data stored in a CSV file.
    """

    def __init__(self, path_file_stats: str, folder_results: str, group_by: Optional[Sequence[str] | str] = None):
        """
        Initialize DataPlotter.

        Args:
            path_file_stats (str): Path to the path with the stats to graph.
            folder_results (str): Folder to store the graphs.
            group_by (str | sequence, optional): Column(s) to group data by for plotting.
        """
        self._path_file_stats = path_file_stats
        self._file_stats_name = os.path.basename(self._path_file_stats).replace(".csv", "")
        self._folder_results = f"{folder_results}/{self._file_stats_name}"

        # DataFrame of the stats
        self._df = pd.read_csv(path_file_stats)
        self._group_by = None
        if group_by:
            if isinstance(group_by, str):
                if group_by in self._df.columns:
                    self._group_by = [group_by]
            elif isinstance(group_by, (list, tuple)):
                if all(col in self._df.columns for col in group_by):
                    self._group_by = list(group_by)
        self._df_grouped = self._df.groupby(self._group_by) if self._group_by else None
        self._num_records = []
        if "num_records" in self._df.columns:
            self._num_records = self._df["num_records"].unique().tolist()
            self._num_records.sort()
        # Create graphs folder
        create_directory(directory=self._folder_results)

    @property
    def stats_columns(self):
        """Getter method for accessing self._x"""
        return self._df.columns

    def _save_plot(self, plot: Figure, file_name: str) -> None:
        """
        Save the current plot to an PNG file.

        Args:
            plot (Figure): The matplotlib plot to save.
            file_name (str): The name of the PNG file to save.
        """
        # Define the full path for saving the PNG file
        png_file_path = os.path.join(self._folder_results, file_name)
        
        # Save the plot as an PNG file using the specified file path
        plot.savefig(png_file_path, format="png")
        
        # Close the plot to release memory resources
        plt.close(plot)

    def plot_line_graph(self, x_column: str, y_column: str, title: str):
        """
        Plot line graphs for each group based on specified x and y columns.

        Args:
            x_column (str): Column name for the axis_x-axis.
            y_column (str): Column name for the y-axis.
            title (str): Title of the plot.
        """
        # Plotting configurations
        plt.figure(figsize=(16, 9))
        plt.title(title, fontsize=25)
        plt.xlabel(x_column, fontsize=20)
        plt.ylabel(y_column, fontsize=20)

        if self._df_grouped is not None:
            for name, group in self._df_grouped:
                group = group.sort_values(by=x_column)
                plt.plot(group[x_column], group[y_column], marker="o", linestyle="-", label=name)
                plt.xlim(group[x_column].min(), group[x_column].max())
            plt.legend(loc="best", fontsize=20)
        else:
            sorted_df = self._df.sort_values(by=x_column)
            plt.plot(sorted_df[x_column], sorted_df[y_column], marker="o", linestyle="-")
            plt.xlim(sorted_df[x_column].min(), sorted_df[x_column].max())
        # Extra configurations
        plt.yticks(fontsize=16)
        plt.grid(True)
        # Save graph
        self._save_plot(plt.gcf(), f"{self._file_stats_name}_{y_column}.png")

    def plot_scatter(self, x_column: str, y_column: str, title: str):
        """
        Scatter plot of two columns, optionally grouped.
        """
        plt.figure(figsize=(10, 7))
        plt.title(title, fontsize=18)
        plt.xlabel(x_column, fontsize=14)
        plt.ylabel(y_column, fontsize=14)

        if self._df_grouped is not None:
            for name, group in self._df_grouped:
                plt.scatter(group[x_column], group[y_column], alpha=0.7, label=str(name))
            plt.legend(loc="best")
        else:
            plt.scatter(self._df[x_column], self._df[y_column], alpha=0.7)

        plt.grid(True)
        self._save_plot(plt.gcf(), f"{self._file_stats_name}_{y_column}_vs_{x_column}.png")

    def plot_lines(self, x_column: str, y_columns: List[str], title: str, annotate_variant: bool = False, variant_column: str = None):
        """
        Plot multiple lines against a shared x axis.
        """
        plt.figure(figsize=(12, 8))
        # Warm vs cold palettes: warm for gil, cold for nogil; vary per run_id
        warm_palette = ["#ffd700", "#ff0000", "#ff69b4"]  # yellow, red, pink
        cold_palette = ["#1f77b4", "#2ca02c", "#c0c0c0"]  # blue, green, silver
        warm_idx = 0
        cold_idx = 0
        marker_cycle = ["o", "s", "D", "^", "v", "P"]
        marker_map: dict[str, str] = {}
        color_map: dict[tuple[str, str], str] = {}

        if self._df_grouped is not None:
            for group_name, group in self._df_grouped:
                group = group.sort_values(by=x_column)
                # Determine a marker per run_id (if present)
                marker = None
                if "run_id" in group.columns:
                    run_key = str(group["run_id"].iloc[0])
                    marker = marker_map.setdefault(run_key, marker_cycle[len(marker_map) % len(marker_cycle)])
                flavor = group["flavor"].iloc[0] if "flavor" in group.columns else None
                label_prefix = " ".join(str(g) for g in group_name) if isinstance(group_name, tuple) else str(group_name)
                # Assign a color per run_id within flavor
                color_key = (flavor or "unknown", run_key)
                if flavor == "gil":
                    if color_key not in color_map:
                        color_map[color_key] = warm_palette[warm_idx % len(warm_palette)]
                        warm_idx += 1
                elif flavor == "nogil":
                    if color_key not in color_map:
                        color_map[color_key] = cold_palette[cold_idx % len(cold_palette)]
                        cold_idx += 1
                color = color_map.get(color_key, "#555555")
                for y in y_columns:
                    plt.plot(
                        group[x_column],
                        group[y],
                        marker=marker or "o",
                        linestyle="-",
                        color=color,
                        label=f"{label_prefix} {y}" if len(y_columns) > 1 else label_prefix,
                    )
                    if annotate_variant and variant_column and variant_column in group.columns:
                        for _, row in group.iterrows():
                            raw_val = row[variant_column]
                            if isinstance(raw_val, (int, float)) and float(raw_val).is_integer():
                                label_val = str(int(raw_val))
                            else:
                                label_val = str(raw_val)
                            plt.annotate(label_val, (row[x_column], row[y]), textcoords="offset points", xytext=(5,5), fontsize=8)
        else:
            for y in y_columns:
                plt.plot(self._df[x_column], self._df[y], marker="o", linestyle="-", label=y)
                if annotate_variant and variant_column and variant_column in self._df.columns:
                    for _, row in self._df.iterrows():
                        raw_val = row[variant_column]
                        if isinstance(raw_val, (int, float)) and float(raw_val).is_integer():
                            label_val = str(int(raw_val))
                        else:
                            label_val = str(raw_val)
                        plt.annotate(label_val, (row[x_column], row[y]), textcoords="offset points", xytext=(5,5), fontsize=8)
        plt.xlabel(x_column, fontsize=14)
        plt.ylabel("value", fontsize=14)
        plt.title(title, fontsize=18)
        plt.legend(loc="best")
        plt.grid(True)
        self._save_plot(plt.gcf(), f"{self._file_stats_name}_{title.lower().replace(' ', '_')}.png")

    def plot_bar_graphs(self, x_column: str, y_columns: List[str], title: str):
        """
        Plot grouped bar chart for specified y_columns per group of x_column values.

        Args:
            x_column (str): Column name for the stats_columns-axis (grouping variable).
            y_columns (list): List of column names to visualize as grouped bars.
            title (str): Title of the plot.
        """
        # Set width of each bar
        bar_width = 0.2
        num_columns = len(y_columns)

        if self._df_grouped is None:
            return

        for name, group in self._df_grouped:
            plt.figure(figsize=(16, 9))
            group = group.sort_values(by=x_column)
            total_time = group[y_columns].sum(axis=1)
            for col in y_columns:
                group[col] = (group[col] / total_time) * 100

            bar_groups = np.arange(len(group))

            for idx, column in enumerate(y_columns):
                current_bar_group = bar_groups + (idx - num_columns/2 + 0.5) * bar_width
                plt.bar(current_bar_group, group[column], width=bar_width, label=column)
            
            plt.xlabel(x_column, fontsize=20)
            plt.xticks(bar_groups, self._num_records, fontsize=16)
            plt.yticks(fontsize=16)
            plt.title(title, fontsize=25)
            plt.legend(loc="best", fontsize=20)

            title_clean = title.lower().replace(" ", "_")
            self._save_plot(plt.gcf(), f"{self._file_stats_name}_{title_clean}_{name}.png")
