"""
This benchmark <content>.

Benchmark Steps:
1. Load user data into a <structure> with a specified number of records.
2. <Description>
3. Measure and log the execution time for the operation.
"""

import argparse
import time
import os

from src.client_interface import set_tag, set_output_filename

from ...util import logger
from ...data_provider import DataHandler


# Use argparse to get num_records from the terminal
parser = argparse.ArgumentParser(description="Perform a test.")
parser.add_argument("--num_records", required=True, type=int, help="Number of records to process")
args = parser.parse_args()
num_records = args.num_records

# Set output filename
set_output_filename(filename=f"{os.path.splitext(os.path.basename(__file__))[0]}_{num_records}")

# Idle time to ensure that the whole program is profiled
time.sleep(1)
set_tag("start_program")

#------- Extract data
data_handler = DataHandler()
num_records = args.num_records

set_tag("start_reading")
df_users = data_handler.read_data(num_records=num_records, data_type="csv", csv_column_types={"street_number": str, "postcode": str})
set_tag("finish_reading")
logger.info(f"The required information was loaded successfully. Number of records: {len(df_users)}")

#------- Operation
set_tag("start_processing")

# Create address column by concatenating required fields
df_users["address"] = (
    df_users["street_name"] + " " + df_users["street_number"] + ", " +
    df_users["postcode"] + " " + df_users["city"] + ", " +
    df_users["state"] + ", " + df_users["country"]
)

# New DataFrame with username and address columns
df_users_address = df_users[["username", "address"]]

set_tag("finish_processing")

# Idle time to ensure some last measures are taken
set_tag("finish_program")
time.sleep(1)
