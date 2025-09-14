import glob
import os
import re

from src.client_interface import FileStats
from ....util import FileWriterCsv

files_stats = [FileStats(file_path=path) for path in glob.glob("results/preprocessed/threads_*.csv")]
csv_writer = FileWriterCsv(file_path="results/threads_results.csv")
csv_writer.set_columns(columns=["num_threads", "uptime", "cpu_usage", "energy_min", "energy_max", "vms", "ram", "swap", "min_vms", "max_vms", "min_ram", "max_ram", "min_swap", "max_swap", "cores_disparity", "time_not_dominant_core"])

for file in files_stats:
    # Extract thread count from filename
    match = re.search(r"threads_(\d+)_", os.path.basename(file._file_path))
    num_threads = int(match.group(1)) if match else 0

    # Use CPU usage as average of CPUs
    file.replace_cpu_usage_with_core_average()

    uptimes = file.get_times(start_label="start_", finish_label="finish_")
    cpu_usage, vms, ram, swap = file.get_average_between_labels(start_label="start_threads", finish_label="finish_threads")
    min_vms, max_vms, min_ram, max_ram, min_swap, max_swap, energy_min, energy_max = file.get_min_max_memory_stats(start_label="start_threads", finish_label="finish_threads")
    dominant_core, time_dominant_cores, cores_disparity_avg = file.track_dominant_core_changes_between_labels(start_label="start_threads", finish_label="finish_threads")
    time_not_dominant_core = uptimes["threads"] - time_dominant_cores
    csv_writer.append_row(row_data=[num_threads, uptimes["threads"], cpu_usage, energy_min, energy_max, vms, ram, swap, min_vms, max_vms, min_ram, max_ram, min_swap, max_swap, cores_disparity_avg, time_not_dominant_core])

# Order results by test name and number of records
csv_writer.order_by_columns(columns=["num_threads"])
csv_writer.write_to_csv()
