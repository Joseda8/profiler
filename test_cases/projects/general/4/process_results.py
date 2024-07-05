import glob

from src.client_interface import FileStats
from ....util import FileWriterCsv

files_stats = [FileStats(file_path=path) for path in glob.glob("results/preprocessed/processes_*.csv")]
csv_writer = FileWriterCsv(file_path="results/processes_results.csv")
csv_writer.set_columns(columns=["num_processes", "uptime", "cpu_usage", "vms", "ram", "swap", "min_vms", "max_vms", "min_ram", "max_ram", "min_swap", "max_swap", "cores_disparity", "time_not_dominant_core"])

for file in files_stats:
    uptimes = file.get_times(start_label="start_", finish_label="finish_")
    cpu_usage, vms, ram, swap = file.get_average_between_labels(start_label="start_processes", finish_label="finish_processes")
    min_vms, max_vms, min_ram, max_ram, min_swap, max_swap = file.get_min_max_memory_stats(start_label="start_processes", finish_label="finish_processes")
    dominant_core, time_dominant_cores, cores_disparity_avg = file.track_dominant_core_changes_between_labels(start_label="start_processes", finish_label="finish_processes")
    time_not_dominant_core = uptimes["processes"] - time_dominant_cores
    csv_writer.append_row(row_data=[0, uptimes["processes"], cpu_usage, vms, ram, swap, min_vms, max_vms, min_ram, max_ram, min_swap, max_swap, cores_disparity_avg, time_not_dominant_core])

# Order results by test name and number of records
csv_writer.order_by_columns(columns=["num_processes"])
csv_writer.write_to_csv()
