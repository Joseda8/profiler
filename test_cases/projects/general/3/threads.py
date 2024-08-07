import argparse
import concurrent.futures
import math

from src.client_interface import set_tag, set_output_filename

# Use argparse to get num_records from the terminal
parser = argparse.ArgumentParser(description="Perform a test with threads.")
parser.add_argument("--num_threads", required=True, type=int, help="Number of threads")
args = parser.parse_args()

# Maximum number of threads
max_threads = args.num_threads


# Set output filename
set_output_filename(filename=f"threads_{max_threads}")

# Factorial of a number
def factorial(n):
    result = math.factorial(n)
    return result

# Numbers to compute the factorial of
numbers = list(range(10000))

# Create a thread pool with maximum max_threads threads
with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
    set_tag("start_threads")
    # Submit tasks to the executor
    future_to_task = {executor.submit(factorial, num): num for num in numbers}
    # Wait for the tasks to complete
    for future in concurrent.futures.as_completed(future_to_task):
        num = future_to_task[future]
        try:
            pass
        except Exception as e:
            print(f"An exception occurred for {num}: {e}")
    set_tag("finish_threads")
