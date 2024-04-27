import os
from src.client_interface import set_tag, set_output_filename

# Set output filename
set_output_filename(filename="fib_test")

# Define function
fib = lambda n: n if n <= 1 else fib(n-1) + fib(n-2)

# Run - 30
set_tag("start_30")
fib_30 = fib(30)
print(f"Fibonacci of 30: {fib_30}")
set_tag("finish_30")

# Run - 35
set_tag("start_35")
fib_35 = fib(35)
print(f"Fibonacci of 35: {fib_35}")
set_tag("finish_35")
