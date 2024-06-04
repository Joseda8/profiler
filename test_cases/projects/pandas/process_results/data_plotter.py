from typing import List
import os

from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from ....util import create_directory


class DataPlotter:
    """
    Class to plot graphs based on test data stored in a CSV file.
    """

    def __init__(self, path_file_stats: str, folder_results: str):
        """
        Initialize DataPlotter.

        Args:
            path_file_stats (str): Path to the path with the stats to graph.
            folder_results (str): Folder to store the graphs.
        """
        self._path_file_stats = path_file_stats
        self._file_stats_name = os.path.basename(self._path_file_stats).replace(".csv", "")
        self._folder_results = f"{folder_results}/{self._file_stats_name}"

        # DataFrame of the stats
        self._df = pd.read_csv(path_file_stats)
        # Group the DataFrame by test_name
        self._df_grouped = self._df.groupby("test_name")
        # List of number of records
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
        Plot line graphs for each test_name based on specified axis_x and y columns.

        Args:
            x_column (str): Column name for the axis_x-axis.
            y_column (str): Column name for the y-axis.
            title (str): Title of the plot.
        """
        # Plotting configurations
        plt.figure(figsize=(14, 9))
        plt.title(title, fontsize=25)
        plt.xlabel(x_column, fontsize=15)
        plt.ylabel(y_column, fontsize=15)

        # Iterate through each group and plot
        for name, group in self._df_grouped:
            group = group.sort_values(by=x_column)
            plt.plot(group[x_column], group[y_column], marker="o", linestyle="-", label=name)
            plt.xlim(group[x_column].min(), group[x_column].max())
        # Extra configurations
        plt.xticks(self._num_records, fontsize=14)
        plt.yticks(fontsize=14)
        plt.xscale("log")
        plt.legend(loc="best", fontsize=15)
        plt.grid(True)
        # Save graph
        self._save_plot(plt.gcf(), f"{self._file_stats_name}_{y_column}.png")

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

        for name, group in self._df_grouped:
            # Create a larger figure
            plt.figure(figsize=(14, 9))
            group = group.sort_values(by=x_column)
            # Update each column in the list with proportions scaled to percentage
            total_time = group[y_columns].sum(axis=1)
            for col in y_columns:
                group[col] = (group[col] / total_time) * 100

            # Set positions of bars on X axis
            bar_groups = np.arange(len(group))

            # Plot grouped bars for each column in y_columns
            for idx, column in enumerate(y_columns):
                # Calculate positions for grouped bars
                current_bar_group = bar_groups + (idx - num_columns/2 + 0.5) * bar_width
                plt.bar(current_bar_group, group[column], width=bar_width, label=column)
            
            # Add graph configurations
            plt.xlabel(x_column, fontsize=15)
            plt.xticks(bar_groups, self._num_records, fontsize=14)
            plt.yticks(fontsize=14)
            plt.title(title, fontsize=25)
            plt.legend(loc="best", fontsize=15)

            # Save graph
            title_clean = title.lower().replace(" ", "_")
            self._save_plot(plt.gcf(), f"{self._file_stats_name}_{title_clean}_{name}.png")
