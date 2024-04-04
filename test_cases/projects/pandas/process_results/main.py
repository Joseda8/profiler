from src.process_results import FileStats

from .const import *


file_path: str = "/home/josemontoya/work/profiler/results/preprocessed/conversion_outside_1000000_20240322_113150_stats.csv"
file_stats: FileStats = FileStats(file_path)
print(file_stats.get_times(start_label=LABEL_START_PREFIX, finish_label=LABEL_FINISH_PREFIX))
print(file_stats.get_average_between_labels(start_label=LABEL_START_PROGRAM, finish_label=LABEL_FINISH_PROGRAM))
print(file_stats.get_min_max_memory_stats(start_label=LABEL_START_PROGRAM, finish_label=LABEL_FINISH_PROGRAM))
print(file_stats.track_dominant_core_changes_between_labels(start_label=LABEL_START_PROGRAM, finish_label=LABEL_FINISH_PROGRAM))
