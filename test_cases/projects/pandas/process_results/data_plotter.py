import os
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
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

        # Create graphs folder
        create_directory(directory=self._folder_results)

    def _save_plot(self, plot: Figure, file_name: str) -> None:
        """
        Save the current plot to an SVG file.

        Args:
            plot (Figure): The matplotlib plot to save.
            file_name (str): The name of the SVG file to save.
        """
        # Define the full path for saving the SVG file
        svg_file_path = os.path.join(self._folder_results, file_name)
        
        # Save the plot as an SVG file using the specified file path
        plot.savefig(svg_file_path, format="svg")
        
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
        plt.figure(figsize=(10, 6))
        plt.title(title)
        plt.xlabel(x_column)
        plt.ylabel(y_column)

        # Iterate through each group and plot
        for name, group in self._df_grouped:
            plt.plot(group[x_column], group[y_column], marker="o", linestyle="-", label=name)
            plt.xlim(group[x_column].min(), group[x_column].max())
        # Show legend
        plt.legend(loc="best")
        # Save graph
        self._save_plot(plt.gcf(), f"{self._file_stats_name}_{y_column}.svg")

    def plot_pie_charts(self, columns: list, title: str):
        """
        Plot pie charts for specified columns per test_name.

        Args:
            columns (list): List of column names to visualize.
            title (str): Title of the plot.
        """
        for name, group in self._df_grouped:
            # Sum the time components for each test_name
            total_values = group[columns].sum()
            # Plotting configurations
            plt.figure(figsize=(8, 8))
            plt.title(f"{title} for {name}")
            plt.pie(total_values, labels=columns, autopct="%1.1f%%", startangle=140)
            # Save graph
            title_clean = title.lower().replace(" ", "_")
            self._save_plot(plt.gcf(), f"{self._file_stats_name}_{title_clean}_{name}.svg")
