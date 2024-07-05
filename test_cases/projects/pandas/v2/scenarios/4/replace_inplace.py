"""
This benchmark substitutes the values in the `gender` column by using the replace method with inplace operation.

Benchmark Steps:
1. Load user data into a Pandas DataFrame with a specified number of records.
2. Replace "female" with "F" and "male" with "M" in the `gender` column using the `replace` method with inplace operation.
3. Measure and log the execution time for the operation.
"""

import argparse
import time
import os

from src.client_interface import set_tag, set_output_filename

from ......util import DataHandler, logger, get_scenario_name


# Use argparse to get num_records from the terminal
parser = argparse.ArgumentParser(description="Perform a test.")
parser.add_argument("--num_records", required=True, type=int, help="Number of records to process")
args = parser.parse_args()
num_records = args.num_records

# Set output filename
file_path = os.path.abspath(__file__)
scenario_name = get_scenario_name(file_path=file_path)
set_output_filename(filename=f"{scenario_name}_{num_records}")

# Idle time to ensure that the whole program is profiled
time.sleep(1)
set_tag("start_program")

#------- Extract data
data_handler = DataHandler()
num_records = args.num_records

set_tag("start_reading")
df_users = data_handler.read_data(num_records=num_records, data_type="csv")
set_tag("finish_reading")
logger.info(f"The required information was loaded successfully. Number of records: {len(df_users)}")

#------- Operation
set_tag("start_processing")

# Replace "female" with "F" and "male" with "M" in the "gender" column
df_users["gender"].replace({"female": "F", "male": "M"}, inplace=True)

set_tag("finish_processing")

# Idle time to ensure some last measures are taken
set_tag("finish_program")
time.sleep(1)
