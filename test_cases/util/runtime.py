"""
Runtime-related helpers for benchmarks.
"""

import sys


def runtime_flavor_suffix() -> str:
    """
    Return 'gil' or 'nogil' based on the interpreter's threading mode.

    Requires Python builds that expose sys._is_gil_enabled.
    """
    gil_detector = getattr(sys, "_is_gil_enabled", None)
    if gil_detector is None:
        raise RuntimeError("sys._is_gil_enabled is not available in this interpreter")
    return "gil" if gil_detector() else "nogil"
