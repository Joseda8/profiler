import argparse
import glob
import os
import re
from typing import List, Optional

from src.client_interface.process_results import FileStats
from ....util import FileWriterCsv, logger


def _extract_variant(path: str, pattern: str) -> Optional[int]:
    """
    Extract a numeric variant from the filename using the given regex pattern.
    """
    match = re.search(pattern, os.path.basename(path))
    return int(match.group(1)) if match and match.group(1) else None


def stage_collect(pattern: str) -> List[FileStats]:
    """
    Gather all preprocessed files that match the glob pattern.

    Args:
        pattern: Glob pattern to match preprocessed CSV files.

    Returns:
        List of FileStats objects for each matching file.
    """
    paths = glob.glob(pattern)
    if not paths:
        logger.warning(f"No result files found matching pattern: {pattern}")
        return []
    return [FileStats(file_path=p) for p in paths]


def stage_aggregate(files_stats: List[FileStats], output_path: str, task_label: str, variant_regex: str, variant_column: str) -> Optional[FileWriterCsv]:
    """
    Aggregate metrics from each file into a single results CSV.

    Args:
        files_stats: Loaded FileStats objects.
        output_path: Path where the aggregated CSV will be written.
        task_label: Label used in tags (start_<label>, finish_<label>).
        variant_regex: Regex with a capture group to extract the variant from filenames.
        variant_column: Column name to store the extracted variant.

    Returns:
        FileWriterCsv if aggregation succeeds; None otherwise.
    """
    if not files_stats:
        logger.warning("No files to aggregate.")
        return None

    start_label, finish_label = f"start_{task_label}", f"finish_{task_label}"
    csv_writer = FileWriterCsv(file_path=output_path)
    csv_writer.set_columns([variant_column, "uptime", "cpu_usage", "energy_min", "energy_max", "vms", "ram", "swap", "min_vms", "max_vms", "min_ram", "max_ram", "min_swap", "max_swap", "cores_disparity", "time_not_dominant_core"])

    for file in files_stats:
        variant_value = _extract_variant(file._file_path, variant_regex)
        if variant_value is None:
            logger.warning(f"Could not extract variant from {file._file_path}; skipping.")
            continue

        uptimes = file.get_times(start_label="start_", finish_label="finish_")
        if task_label not in uptimes:
            logger.warning(f"Missing task label '{task_label}' in {file._file_path}; skipping.")
            continue

        cpu_usage, vms, ram, swap = file.get_average_between_labels(start_label=start_label, finish_label=finish_label)
        min_vms, max_vms, min_ram, max_ram, min_swap, max_swap, energy_min, energy_max = file.get_min_max_memory_stats(start_label=start_label, finish_label=finish_label)
        _, time_dominant_cores, cores_disparity_avg = file.track_dominant_core_changes_between_labels(start_label=start_label, finish_label=finish_label)
        time_not_dominant_core = uptimes[task_label] - time_dominant_cores

        csv_writer.append_row([variant_value, uptimes[task_label], cpu_usage, energy_min, energy_max, vms, ram, swap, min_vms, max_vms, min_ram, max_ram, min_swap, max_swap, cores_disparity_avg, time_not_dominant_core])

    csv_writer.order_by_columns(columns=[variant_column])
    csv_writer.write_to_csv()
    logger.info(f"Aggregated results written to {output_path}")
    return csv_writer


def stage_plot_results(csv_writer: Optional[FileWriterCsv]) -> None:
    """
    Placeholder for plotting stage. Extend this to generate graphs from csv_writer.df_data.
    """
    if csv_writer is None:
        logger.warning("No data available for plotting stage.")
        return
    logger.info("Plotting stage not implemented yet. Hook here for graphs.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Aggregate profiler results for energy consumption experiments.")
    parser.add_argument("--pattern", required=True, help="Glob pattern to find preprocessed CSV files")
    parser.add_argument("--output_file", required=True, help="Path for aggregated CSV output")
    parser.add_argument("--task_label", required=True, help="Task label used in tags (start_<label>, finish_<label>)")
    parser.add_argument("--variant_column", required=True, help="Column name for the varying parameter")
    parser.add_argument("--variant_regex", help="Regex capture group for variant; defaults to f'{task_label}_(\\d+)_'.")
    args = parser.parse_args()

    # Build pipeline inputs
    variant_regex = args.variant_regex or rf"{args.task_label}_(\d+)_"
    
    # Collect result files
    stats_files = stage_collect(pattern=args.pattern)

    # Aggregation
    csv_writer = stage_aggregate(
        files_stats=stats_files,
        output_path=args.output_file,
        task_label=args.task_label,
        variant_regex=variant_regex,
        variant_column=args.variant_column,
    )

    # Plot results
    stage_plot_results(csv_writer)
