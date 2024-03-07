from .util import DatetimeHelper

DATETIME_EXECUTION = DatetimeHelper.current_datetime_string()
RESULTS_FILE_FOLDER = "results"
OUTPUT_FILE_PATH = f"{RESULTS_FILE_FOLDER}/{DATETIME_EXECUTION}_output.txt"
STATS_FILE_PATH = f"{RESULTS_FILE_FOLDER}/{DATETIME_EXECUTION}_stats.txt"
