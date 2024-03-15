from .util import DatetimeHelper

# Execution datetime
DATETIME_EXECUTION = DatetimeHelper.current_datetime_string()

# Folder paths
RESULTS_FILE_FOLDER = "results"
OUTPUT_FILE_PATH = f"{RESULTS_FILE_FOLDER}/{DATETIME_EXECUTION}_output.txt"
STATS_FILE_PATH = f"{RESULTS_FILE_FOLDER}/{DATETIME_EXECUTION}_stats.csv"

# Measure tag prefix
PREFIX_MEASURE_TAG = "measure_label-"
