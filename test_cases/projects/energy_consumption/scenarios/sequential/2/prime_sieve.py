"""
Sequential prime sieve benchmark for energy consumption tests.

Uses the Sieve of Eratosthenes to count primes up to a limit.
"""

import argparse
from typing import List

from src.client_interface import set_output_filename, set_tag
from test_cases.util import runtime_flavor_suffix


def sieve(limit: int) -> List[int]:
    """Return a list of primes up to the given limit."""
    if limit < 2:
        return []
    is_prime = [True] * (limit + 1)
    is_prime[0] = is_prime[1] = False
    factor = 2
    while factor * factor <= limit:
        if is_prime[factor]:
            for multiple in range(factor * factor, limit + 1, factor):
                is_prime[multiple] = False
        factor += 1
    return [idx for idx, prime in enumerate(is_prime) if prime]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sequential prime sieve benchmark.")
    parser.add_argument("--limit", type=int, default=1_000_000, help="Upper bound for the sieve.")
    parser.add_argument("--run_idx", help="Optional run index to tag outputs.")
    args = parser.parse_args()

    limit = args.limit
    runtime_flavor = runtime_flavor_suffix()
    run_suffix = f"run{args.run_idx}" if args.run_idx else ""

    set_output_filename(filename=f"prime_sieve_{limit}_{runtime_flavor}_{run_suffix}")

    set_tag("start_prime_sieve")
    primes = sieve(limit)
    prime_count = len(primes)
    primes_checksum = sum(primes)
    set_tag("finish_prime_sieve")

    print(f"primes: {prime_count}, checksum: {primes_checksum}")
