import os

import matplotlib.pyplot as plt
import pandas as pd


class DataPlotter:
    """
    Class to plot graphs based on test data stored in a CSV file.
    """

    def __init__(self):
        """
        Initialize DataPlotter.
        """
        pass

    def plot_data(self, csv_file_path: str):
        """
        Plot graphs for each test_name based on num_records vs. time_processing.

        Args:
            csv_file_path (str): Path to the CSV file containing test data.
        """
        df = pd.read_csv(csv_file_path)

        # Group the DataFrame by test_name
        grouped = df.groupby("test_name")

        # Plotting configurations
        plt.figure(figsize=(10, 6))
        plt.title("Processing Time vs Number of Records")
        plt.xlabel("Number of Records")
        plt.ylabel("Time Processing")

        # Iterate through each group (test_name) and plot
        for name, group in grouped:
            # Find the minimum and maximum num_records values for the current group
            min_num_records = group["num_records"].min()
            max_num_records = group["num_records"].max()

            # Plot, starting from the minimum num_records value
            plt.plot(
                group["num_records"],
                group["time_processing"],
                marker="o",
                linestyle="-",
                label=name,
            )

            # Set x-axis limits to start from the minimum num_records value
            plt.xlim(min_num_records, max_num_records)

        # Show legend
        plt.legend()

        # Get Y-axis label and save the plot as SVG file
        # Get the current Axes instance
        ax = plt.gca()
        y_axis_label = ax.get_ylabel().replace(" ", "_").lower()  # Get Y-axis label
        file_name = os.path.basename(csv_file_path).replace(".csv", "")
        svg_file_path = f"{file_name}_{y_axis_label}.svg"
        plt.savefig(svg_file_path, format="svg")

        # Clear the current figure to release memory
        plt.clf()
