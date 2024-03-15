"""
This benchmark <content>.

Benchmark Steps:
1. Load user data into a <structure> with a specified number of records.
2. <Description>
3. Measure and log the execution time for the operation.
"""

import argparse
import time

from src.client_interface import set_tag

from ...util import logger
from ...data_provider import DataHandler


# Use argparse to get num_records from the terminal
parser = argparse.ArgumentParser(description="Perform a test.")
parser.add_argument("--num_records", required=True, type=int, help="Number of records to process")
args = parser.parse_args()

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

##########
#  Code  #
##########

set_tag("finish_processing")

# Idle time to ensure some last measures are taken
set_tag("finish_program")
time.sleep(1)
