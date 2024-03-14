"""
This benchmark replaces all values in the "password" column with "XXXXXXXX" in a Pandas DataFrame.

Benchmark Steps:
1. Load user data into a Pandas DataFrame with a specified number of records.
2. Replace all values in the "password" column with "XXXXXXXX".
3. Measure and log the execution time for the operation.
"""

import argparse
import time

from ...util import logger, DatetimeHelper
from ...data_provider import DataHandler

# Use argparse to get num_records from the terminal
parser = argparse.ArgumentParser(description="Perform a test.")
parser.add_argument("--num_records", required=True, type=int, help="Number of records to process")
args = parser.parse_args()

#------- Extract data
data_handler = DataHandler()
num_records = args.num_records

print(f"Start reading: {DatetimeHelper.current_datetime()}")
df_users = data_handler.read_data(num_records=num_records, data_type="csv")
print(f"Finished reading: {DatetimeHelper.current_datetime()}")
logger.info(f"The required information was loaded successfully. Number of records: {len(df_users)}")

#------- Operation

print(f"Start processing: {DatetimeHelper.current_datetime()}")

# Replace all values in the "password" column with "XXXXXXXX" in the DataFrame
df_users["password"] = "XXXXXXXX"

print(f"Finished processing: {DatetimeHelper.current_datetime()}")

# Idle to ensure some last measures are taken
time.sleep(1)
