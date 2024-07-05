# Label tags
LABEL_START_PREFIX = "start_"
LABEL_FINISH_PREFIX = "finish_"
LABEL_PROGRAM = "program"
LABEL_PROCESSING = "processing"
LABEL_START_PROGRAM = f"{LABEL_START_PREFIX}{LABEL_PROGRAM}"
LABEL_FINISH_PROGRAM = f"{LABEL_FINISH_PREFIX}{LABEL_PROGRAM}"
LABEL_START_PROCESSING = f"{LABEL_START_PREFIX}{LABEL_PROCESSING}"
LABEL_FINISH_PROCESSING = f"{LABEL_FINISH_PREFIX}{LABEL_PROCESSING}"

# Files
FOLDER_RESULTS = "results"
FILE_PATH_RESULTS_PREPROCESSED = f"{FOLDER_RESULTS}/preprocessed"
FOLDER_RESULTS_GRAPHS = f"{FOLDER_RESULTS}/processed/graphs"

# Stats
STATS_TIMES_ID = "time_tags"
STATS_COLUMNS = ["test_name", "num_records", STATS_TIMES_ID, "avg_cpu_usage", "avg_vm", "avg_ram", "avg_swap",
                 "min_vm", "max_vm", "min_ram", "max_ram", "min_swap", "max_swap", "dominant_core_changes", "core_changes_by_time", "time_with_dominant_core", "time_not_dominant_core", "cores_disparity_avg", "energy_consumption"]
STATS_TIMES_ID_IDX = STATS_COLUMNS.index(STATS_TIMES_ID)
