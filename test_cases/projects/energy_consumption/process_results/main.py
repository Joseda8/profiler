import argparse
import glob
import os
import re
from typing import List, Optional

import pandas as pd

from src.client_interface.process_results import FileStats
from ....util import FileWriterCsv, logger
from .data_plotter import DataPlotter


def _extract_variant(path: str, pattern: str) -> Optional[int]:
    """
    Extract a numeric variant from the filename using the given regex pattern.
    """
    match = re.search(pattern, os.path.basename(path))
    return int(match.group(1)) if match and match.group(1) else None


def _extract_run_id(path: str) -> Optional[str]:
    """
    Extract run id from filenames that contain `_run<id>_`.
    """
    match = re.search(r"_run([^_]+)_", os.path.basename(path))
    return match.group(1) if match else None


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


def stage_aggregate(
    files_stats: List[FileStats],
    output_path: str,
    task_label: str,
    variant_regex: str,
    variant_column: str,
    flavor: str,
    run_id: Optional[str] = None,
) -> Optional[FileWriterCsv]:
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
    # Load existing data (to allow merging gil/nogil into one file)
    existing_df = None
    if os.path.exists(output_path):
        try:
            existing_df = pd.read_csv(output_path)
            existing_df = existing_df[existing_df["flavor"] != flavor]
        except Exception as excep:
            logger.warning(f"Failed to read existing output {output_path}: {excep}")
            existing_df = None

    # Keep artifacts under the run root (parent of summaries)
    summaries_dir = os.path.abspath(os.path.dirname(output_path))
    run_root = os.path.abspath(os.path.join(summaries_dir, os.pardir))
    processed_root = run_root
    csv_writer = FileWriterCsv(file_path=output_path)
    if existing_df is not None and not existing_df.empty:
        csv_writer.set_data_frame(existing_df)
    else:
        columns = [variant_column, "flavor"]
        if run_id is not None:
            columns.append("run_id")
        columns += ["uptime", "cpu_usage", "cpu_usage_cv", "energy_max", "vms", "vms_cv", "ram", "ram_cv", "cores_disparity"]
        csv_writer.set_columns(columns)

    for file in files_stats:
        variant_value = _extract_variant(file._file_path, variant_regex)
        if variant_value is None:
            logger.warning(f"Could not extract variant from {file._file_path}; skipping.")
            continue

        uptimes = file.get_times(start_label="start_", finish_label="finish_")
        if task_label not in uptimes:
            logger.warning(f"Missing task label '{task_label}' in {file._file_path}; skipping.")
            continue

        averages = file.get_average_between_labels(start_label=start_label, finish_label=finish_label)
        if averages is None:
            logger.warning(f"Could not compute averages for {file._file_path}; skipping.")
            continue
        cpu_usage, vms, ram, _ = averages
        stds = file.get_std_between_labels(start_label=start_label, finish_label=finish_label)
        if stds is None:
            logger.warning(f"Could not compute stds for {file._file_path}; skipping.")
            continue
        cpu_usage_std, vms_std, ram_std = stds
        _, _, _, _, _, _, _, energy_max = file.get_min_max_memory_stats(start_label=start_label, finish_label=finish_label)
        _, time_dominant_cores, cores_disparity_avg = file.track_dominant_core_changes_between_labels(start_label=start_label, finish_label=finish_label)
        _ = uptimes[task_label] - time_dominant_cores

        cpu_cv = cpu_usage_std / cpu_usage if cpu_usage else 0
        vms_cv = vms_std / vms if vms else 0
        ram_cv = ram_std / ram if ram else 0

        row = [variant_value, flavor]
        if run_id is not None:
            row.append(run_id)
        row += [uptimes[task_label], cpu_usage, cpu_cv, energy_max, vms, vms_cv, ram, ram_cv, cores_disparity_avg]
        csv_writer.append_row(row)

    order_cols = ["flavor", variant_column]
    if run_id is not None:
        order_cols.append("run_id")
    csv_writer.order_by_columns(columns=order_cols)
    csv_writer.write_to_csv()
    logger.info(f"Aggregated results written to {output_path}")

    # Global CVs
    def _cv(series):
        series = pd.to_numeric(series, errors="coerce").dropna()
        if series.empty:
            return 0.0
        mean_val = series.mean()
        return series.std() / mean_val if mean_val else 0.0

    cv_path = output_path.replace(".csv", "_cv.csv")
    cv_writer = FileWriterCsv(file_path=cv_path)
    cv_writer.set_columns(["metric", "cv"])
    cv_writer.append_row(["uptime", _cv(csv_writer.df_data["uptime"])])
    cv_writer.append_row(["cpu_usage", _cv(csv_writer.df_data["cpu_usage"])])
    cv_writer.append_row(["vms", _cv(csv_writer.df_data["vms"])])
    cv_writer.append_row(["ram", _cv(csv_writer.df_data["ram"])])
    cv_dir = os.path.join(processed_root, "cvs")
    os.makedirs(cv_dir, exist_ok=True)
    cv_writer._file_path = os.path.join(cv_dir, os.path.basename(cv_path))
    cv_writer.write_to_csv()
    logger.info(f"Global CVs written to {cv_writer._file_path}")

    # Per-flavor summary and CVs (independent)
    if "flavor" in csv_writer.df_data.columns:
        flavor_dir = os.path.dirname(output_path)
        os.makedirs(flavor_dir, exist_ok=True)
        base_name = os.path.splitext(os.path.basename(output_path))[0]
        for flv, sub in csv_writer.df_data.groupby("flavor"):
            flavor_summary_path = os.path.join(flavor_dir, f"{base_name}_{flv}.csv")
            sub_sorted = sub.sort_values(by=[variant_column]).drop(columns=["flavor"], errors="ignore")
            flavor_writer = FileWriterCsv(file_path=flavor_summary_path)
            flavor_writer.set_data_frame(df=sub_sorted)
            flavor_writer.write_to_csv()
            logger.info(f"Flavor summary written to {flavor_summary_path}")

            flavor_cv_writer = FileWriterCsv(
                file_path=os.path.join(cv_dir, f"{os.path.splitext(os.path.basename(flavor_summary_path))[0]}_cv.csv")
            )
            flavor_cv_writer.set_columns(["metric", "cv"])
            flavor_cv_writer.append_row(["uptime", _cv(sub["uptime"])])
            flavor_cv_writer.append_row(["cpu_usage", _cv(sub["cpu_usage"])])
            flavor_cv_writer.append_row(["vms", _cv(sub["vms"])])
            flavor_cv_writer.append_row(["ram", _cv(sub["ram"])])
            flavor_cv_writer.write_to_csv()
            logger.info(f"Flavor CVs written to {flavor_cv_writer._file_path}")

    # Normalized file: set best (minimum) per metric as 1.0
    _write_normalized(csv_writer.df_data, output_path, variant_column)

    # Generate requested plots using DataPlotter
    graphs_dir = os.path.join(run_root, "graphs")
    plotter = DataPlotter(path_file_stats=output_path, folder_results=graphs_dir, group_by="flavor")
    plotter.plot_lines(x_column="uptime", y_columns=["energy_max"], title="Energy vs Uptime", annotate_variant=True, variant_column=variant_column)
    plotter.plot_lines(x_column="cpu_usage", y_columns=["energy_max"], title="Energy vs CPU Usage", annotate_variant=True, variant_column=variant_column)
    if variant_column in plotter.stats_columns:
        plotter.plot_lines(x_column=variant_column, y_columns=["cpu_usage"], title="CPU Usage vs Variant")
        plotter.plot_lines(x_column=variant_column, y_columns=["vms", "ram"], title="Memory vs Variant")

    return csv_writer


def stage_plot_results(csv_writer: Optional[FileWriterCsv]) -> None:
    """
    Placeholder for plotting stage. Extend this to generate graphs from csv_writer.df_data.
    """
    if csv_writer is None:
        logger.warning("No data available for plotting stage.")
        return
    logger.info("Plotting stage handled during aggregation.")


def _write_normalized(df: pd.DataFrame, output_path: str, variant_column: str) -> None:
    """
    Normalize metrics so the best (minimum) value per column becomes 1.0.
    """
    if df.empty:
        logger.warning("No data to normalize.")
        return

    df_norm = df.copy()
    # Replace NaNs/zeros with 0.1 for normalization purposes only
    df_norm = df_norm.replace(0, 0.1).fillna(0.1)

    base_cols = [variant_column] + [c for c in ["flavor", "run_id"] if c in df_norm.columns]
    metric_cols = [col for col in df_norm.columns if col not in base_cols and not col.endswith("_cv")]

    processed_root = os.path.abspath(os.path.dirname(output_path))
    norm_dir = os.path.join(processed_root, "normalized")
    os.makedirs(norm_dir, exist_ok=True)
    base_name = os.path.basename(output_path)
    energy_col = "energy_max"

    # Combined normalization: compare across flavors but grouped by variant
    norm_combined = df_norm[base_cols].copy()
    for col in metric_cols:
        numeric = pd.to_numeric(df_norm[col], errors="coerce")
        numeric_filled = numeric.fillna(0.1).replace(0, 0.1)
        if numeric_filled.empty:
            logger.warning(f"No data to normalize for {col}.")
            continue
        min_by_variant = numeric_filled.groupby(df_norm[variant_column]).transform("min")
        norm_combined[col] = numeric_filled / min_by_variant
    sort_cols = [variant_column] + ([energy_col] if energy_col in norm_combined.columns else [])
    norm_combined = norm_combined.sort_values(by=sort_cols)

    norm_path = os.path.join(norm_dir, base_name)
    norm_writer = FileWriterCsv(file_path=norm_path)
    norm_writer.set_data_frame(df=norm_combined)
    norm_writer.write_to_csv()
    logger.info(f"Normalized results written to {norm_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Aggregate profiler results for energy consumption experiments.")
    parser.add_argument("--pattern", required=True, help="Glob pattern to find preprocessed CSV files")
    parser.add_argument("--output_file", required=True, help="Path for aggregated CSV output")
    parser.add_argument("--task_label", required=True, help="Task label used in tags (start_<label>, finish_<label>)")
    parser.add_argument("--variant_column", required=True, help="Column name for the varying parameter")
    parser.add_argument("--variant_regex", help="Regex capture group for variant; defaults to f'{task_label}_(\\d+)_'.")
    parser.add_argument("--flavor", required=True, help="Execution flavor (e.g., gil or nogil)")
    args = parser.parse_args()

    # Build pipeline inputs
    variant_regex = args.variant_regex or rf"{args.task_label}_(\d+)_"
    
    # Collect result files
    stats_files = stage_collect(pattern=args.pattern)

    # Group files by run_id in filename (if present)
    grouped: dict[Optional[str], List[FileStats]] = {}
    for fs in stats_files:
        rid = _extract_run_id(fs._file_path)
        grouped.setdefault(rid, []).append(fs)

    # Base root for runs; if caller uses a summaries path, place runs above it
    output_dir = os.path.abspath(os.path.dirname(args.output_file))
    parent_dir = os.path.abspath(os.path.join(output_dir, os.pardir))
    base_root = parent_dir if os.path.basename(output_dir) == "summaries" else output_dir
    os.makedirs(base_root, exist_ok=True)

    for rid, files in grouped.items():
        base_name = os.path.basename(args.output_file)
        run_dir = os.path.join(base_root, f"run{rid}") if rid is not None else base_root
        summaries_dir = os.path.join(run_dir, "summaries")
        os.makedirs(summaries_dir, exist_ok=True)
        out_path = os.path.join(summaries_dir, base_name)
        csv_writer = stage_aggregate(
            files_stats=files,
            output_path=out_path,
            task_label=args.task_label,
            variant_regex=variant_regex,
            variant_column=args.variant_column,
            flavor=args.flavor,
            run_id=rid,
        )
        stage_plot_results(csv_writer)
