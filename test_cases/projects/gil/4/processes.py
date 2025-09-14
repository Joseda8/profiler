import argparse
import concurrent.futures
import math

from src.client_interface import set_tag, set_output_filename

# Use argparse to get num_records from the terminal
parser = argparse.ArgumentParser(description="Perform a test with processes.")
parser.add_argument("--num_processes", required=True, type=int, help="Number of processes")
args = parser.parse_args()

# Maximum number of processes
max_processes = args.num_processes

# Set output filename
set_output_filename(filename=f"processes_{max_processes}")

# Factorial of a number
def factorial(n):
    result = math.factorial(n)
    return result

# Numbers to compute the factorial of
numbers = list(range(10000))

# Create a process pool with maximum max_processes processes
with concurrent.futures.ProcessPoolExecutor(max_workers=max_processes) as executor:
    set_tag("start_processes")
    # Submit tasks to the executor
    future_to_task = {executor.submit(factorial, num): num for num in numbers}
    # Wait for the tasks to complete
    for future in concurrent.futures.as_completed(future_to_task):
        num = future_to_task[future]
        try:
            # Retrieve the result of the computation
            result = future.result()
        except Exception as e:
            print(f"An exception occurred for {num}: {e}")
    set_tag("finish_processes")
