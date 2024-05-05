from src.client_interface import FileStats
from ....util import FileWriterCsv

stats_threads_1 = FileStats(file_path="//preprocessed/threads_1__stats.csv")
stats_threads_2 = FileStats(file_path="//preprocessed/threads_2__stats.csv")
stats_threads_4 = FileStats(file_path="//preprocessed/threads_4__stats.csv")
stats_threads_6 = FileStats(file_path="//preprocessed/threads_6__stats.csv")
files_stats = [stats_threads_1, stats_threads_2, stats_threads_4, stats_threads_6]

csv_writer = FileWriterCsv(file_path="results/threads_results.csv")
csv_writer.set_columns(columns=["num_threads", "uptime", "cpu_usage", "vms", "ram", "swap", "min_vms", "max_vms", "min_ram", "max_ram", "min_swap", "max_swap", "cores_disparity", "time_not_dominant_core"])

for file in files_stats:
    uptimes = file.get_times(start_label="start_", finish_label="finish_")
    cpu_usage, vms, ram, swap = file.get_average_between_labels(start_label="start_threads", finish_label="finish_threads")
    min_vms, max_vms, min_ram, max_ram, min_swap, max_swap = file.get_min_max_memory_stats(start_label="start_threads", finish_label="finish_threads")
    dominant_core, time_dominant_cores, cores_disparity_avg = file.track_dominant_core_changes_between_labels(start_label="start_threads", finish_label="finish_threads")
    time_not_dominant_core = uptimes["threads"] - time_dominant_cores
    csv_writer.append_row(row_data=[0, uptimes["threads"], cpu_usage, vms, ram, swap, min_vms, max_vms, min_ram, max_ram, min_swap, max_swap, cores_disparity_avg, time_not_dominant_core])

# Order results by test name and number of records
csv_writer.order_by_columns(columns=["num_threads"])
csv_writer.write_to_csv()
