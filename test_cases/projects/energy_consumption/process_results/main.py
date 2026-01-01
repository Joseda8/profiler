import argparse
import glob
import math
import os
import re
from typing import List, Optional

import pandas as pd

from src.client_interface.process_results import FileStats
from ....util import FileWriterCsv, logger
from .data_plotter import DataPlotter

RUN_SUMMARIES_DIRNAME = "summaries"
RUN_GRAPHS_DIRNAME = "graphs"
COMBINED_DIRNAME = "combined"
RATIOS_DIRNAME = "ratios"
NORMALIZED_DIRNAME = "normalized"

# Two-sided 95% critical values for Student's t by degrees of freedom
T_CRITICAL_95 = {
    1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571,
    6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228,
    11: 2.201, 12: 2.179, 13: 2.160, 14: 2.145, 15: 2.131,
    16: 2.120, 17: 2.110, 18: 2.101, 19: 2.093, 20: 2.086,
    21: 2.080, 22: 2.074, 23: 2.069, 24: 2.064, 25: 2.060,
    26: 2.056, 27: 2.052, 28: 2.048, 29: 2.045, 30: 2.042,
}

# Filename helpers
def _extract_variant(path: str, pattern: str) -> Optional[int]:
    match = re.search(pattern, os.path.basename(path))
    return int(match.group(1)) if match and match.group(1) else None


def _extract_run_id(path: str) -> Optional[str]:
    match = re.search(r"_run([^_]+)_", os.path.basename(path))
    return match.group(1) if match else None


def _extract_flavor(path: str) -> str:
    match = re.search(r"_(nogil|gil)_", os.path.basename(path))
    if not match:
        raise ValueError(f"Unable to infer flavor from filename: {path}")
    return match.group(1)


def _cv(std: float, mean: float) -> float:
    return (std / mean) if mean else 0.0


def _run_root_from_output_path(output_path: str) -> str:
    # Parent of summaries/<file>.csv keeps per-run artifacts grouped
    summaries_dir = os.path.abspath(os.path.dirname(output_path))
    return os.path.abspath(os.path.join(summaries_dir, os.pardir))


def _aggregate_file_row(file_stats: FileStats, task_label: str, start_label: str, finish_label: str, variant_regex: str, run_id: Optional[str]) -> List[object]:
    # Pull per-file metrics needed for aggregation
    file_path = file_stats._file_path
    flavor = _extract_flavor(file_path)
    variant_value = _extract_variant(file_path, variant_regex)

    try:
        # keyed by task label
        uptime_by_task = file_stats.get_times(start_label="start_", finish_label="finish_")
        # focused on the task of interest
        uptime = uptime_by_task[task_label]

        # mean metrics
        cpu_usage, vms, ram, _swap = file_stats.get_average_between_labels(start_label=start_label, finish_label=finish_label)
        # std dev for CVs
        cpu_usage_std, vms_std, ram_std = file_stats.get_std_between_labels(start_label=start_label, finish_label=finish_label)
        # peak energy within window
        *_, energy_max = file_stats.get_min_max_memory_stats(start_label=start_label, finish_label=finish_label)
        # imbalance across cores
        *_ignored, cores_disparity_avg = file_stats.track_dominant_core_changes_between_labels(start_label=start_label, finish_label=finish_label)
    except Exception as exc:
        raise RuntimeError(f"Failed to process stats from {file_path}") from exc

    return [
        variant_value,
        flavor,
        run_id,
        uptime,
        cpu_usage, _cv(cpu_usage_std, cpu_usage),
        energy_max,
        vms, _cv(vms_std, vms),
        ram, _cv(ram_std, ram),
        cores_disparity_avg,
    ]


def _generate_run_plots(output_path: str, run_root: str, variant_column: str) -> None:
    # Quick per-run plots grouped by flavor
    graphs_dir = os.path.join(run_root, RUN_GRAPHS_DIRNAME)
    plotter = DataPlotter(path_file_stats=output_path, folder_results=graphs_dir, group_by="flavor")

    # Basic relationships per run
    plotter.plot_lines(x_column="uptime", y_columns=["energy_max"], title="Energy vs Uptime", annotate_variant=True, variant_column=variant_column)
    plotter.plot_lines(x_column="uptime", y_columns=["cpu_usage"], title="CPU Usage vs Uptime", annotate_variant=True, variant_column=variant_column)
    plotter.plot_lines(x_column="cpu_usage", y_columns=["energy_max"], title="Energy vs CPU Usage", annotate_variant=True, variant_column=variant_column)

    # Variant-based views when available
    if variant_column in plotter.stats_columns:
        plotter.plot_lines(x_column=variant_column, y_columns=["energy_max"], title="Energy vs Variant")
        plotter.plot_lines(x_column=variant_column, y_columns=["cpu_usage"], title="CPU Usage vs Variant")
        plotter.plot_lines(x_column=variant_column, y_columns=["vms"], title="VMS vs Variant")
        plotter.plot_lines(x_column=variant_column, y_columns=["ram"], title="RAM vs Variant")


def stage_collect(pattern: str) -> List[FileStats]:
    # Load and wrap each matched CSV into a FileStats helper
    paths = sorted(glob.glob(pattern))
    if not paths:
        logger.warning(f"No result files found matching pattern: {pattern}")
        return []
    return [FileStats(file_path=p) for p in paths]


def stage_aggregate(files_stats: List[FileStats], output_path: str, task_label: str, variant_regex: str, variant_column: str, run_id: Optional[str] = None) -> FileWriterCsv:
    # Build a per-run summary plus normalization and plots
    start_label, finish_label = f"start_{task_label}", f"finish_{task_label}"

    run_root = _run_root_from_output_path(output_path)

    # Define output schema and build rows for each input stats file
    columns = [variant_column, "flavor", "run_id", "uptime", "cpu_usage", "cpu_usage_cv", "energy_max", "vms", "vms_cv", "ram", "ram_cv", "cores_disparity"]
    rows = [
        _aggregate_file_row(file_stats=file_stats, task_label=task_label, start_label=start_label, finish_label=finish_label, variant_regex=variant_regex, run_id=run_id)
        for file_stats in files_stats
    ]

    csv_writer = FileWriterCsv(file_path=output_path)
    csv_writer.set_columns(columns)
    csv_writer.append_rows(rows)
    # deterministic ordering for downstream steps
    csv_writer.order_by_columns(columns=["flavor", variant_column, "run_id"])
    csv_writer.write_to_csv()
    logger.info(f"Aggregated results written to {output_path}")

    # Normalize file and plot per-run views
    _write_normalized(csv_writer.df_data, output_path, variant_column, norm_root=run_root)

    _generate_run_plots(output_path=output_path, run_root=run_root, variant_column=variant_column)

    return csv_writer


def _write_normalized(df: pd.DataFrame, output_path: str, variant_column: str, norm_root: Optional[str] = None) -> Optional[pd.DataFrame]:
    # Normalize each metric relative to the best (min) per variant
    # avoid divide-by-zero and NaNs
    df_norm = df.replace(0, 0.1).fillna(0.1)

    base_cols = [variant_column] + [col for col in ("flavor", "run_id") if col in df_norm.columns]
    # numeric metrics only
    metric_cols = [col for col in df_norm.columns if col not in base_cols and not col.endswith("_cv")]

    processed_root = (
        os.path.abspath(norm_root) if norm_root is not None else os.path.abspath(os.path.dirname(output_path))
    )
    # keep normalized files alongside run outputs
    norm_dir = os.path.join(processed_root, NORMALIZED_DIRNAME)
    os.makedirs(norm_dir, exist_ok=True)
    base_name = os.path.basename(output_path)
    energy_col = "energy_max"

    # force numeric and stabilize zeros
    numeric_metrics = df_norm[metric_cols].apply(pd.to_numeric, errors="coerce").fillna(0.1).replace(0, 0.1)
    # best per variant baseline
    min_by_variant = numeric_metrics.groupby(df_norm[variant_column]).transform("min")
    normalized_metrics = numeric_metrics / min_by_variant

    # Compare across flavors but grouped by variant.
    norm_combined = pd.concat([df_norm[base_cols], normalized_metrics], axis=1)

    # keep variants grouped in output
    sort_cols = [variant_column] + ([energy_col] if energy_col in norm_combined.columns else [])
    norm_combined = norm_combined.sort_values(by=sort_cols)

    norm_path = os.path.join(norm_dir, base_name)
    norm_writer = FileWriterCsv(file_path=norm_path)
    norm_writer.set_data_frame(df=norm_combined)
    norm_writer.write_to_csv()
    logger.info(f"Normalized results written to {norm_path}")
    return norm_combined


def _compute_per_run_ratios(df: pd.DataFrame, variant_column: str) -> pd.DataFrame:
    # Build a row per (run_id, variant) with nogil/gil ratios, diffs, and logs
    metric_columns = [col for col in ["uptime", "cpu_usage", "energy_max", "vms", "ram", "cores_disparity"] if col in df.columns]

    rows = []
    for (run_id, variant_value), group in df.groupby(["run_id", variant_column]):
        gil_row = group[group["flavor"] == "gil"]
        nogil_row = group[group["flavor"] == "nogil"]
        if gil_row.empty or nogil_row.empty:
            continue
        gil_stats = gil_row.iloc[0]
        nogil_stats = nogil_row.iloc[0]
        # anchor identifiers
        row = {variant_column: variant_value, "run_id": run_id}
        for metric in metric_columns:
            denom = gil_stats[metric]
            ratio = (nogil_stats[metric] / denom) if denom else None
            row[f"{metric}_ratio_nogil_over_gil"] = ratio
            row[f"{metric}_diff_nogil_minus_gil"] = abs(nogil_stats[metric] - gil_stats[metric])
            row[f"{metric}_log_ratio_nogil_over_gil"] = math.log(ratio) if ratio and ratio > 0 else None
        rows.append(row)

    if not rows:
        logger.warning("No nogil/gil pairs found to compute per-run ratios.")
        return pd.DataFrame()

    return pd.DataFrame(rows).sort_values(by=["run_id", variant_column]).reset_index(drop=True)

def _t_multiplier(sample_count: int) -> float:
    df = sample_count - 1
    return T_CRITICAL_95[df]

def _compute_ratio_confidence(per_run_ratios: pd.DataFrame, variant_column: str) -> pd.DataFrame:
    # Compute geometric mean ratios and 95% CIs in log space, per variant
    metric_columns = [
        column_name
        for column_name in per_run_ratios.columns
        if column_name.endswith("_ratio_nogil_over_gil") and "_log_" not in column_name
    ]
    rows = []
    for variant_value, group in per_run_ratios.groupby(variant_column):
        for metric_col in metric_columns:
            # ignore zeros/negatives
            log_values = group[metric_col].apply(lambda val: math.log(val) if val and val > 0 else None).dropna()
            mean_log = log_values.mean()
            sd_log = log_values.std(ddof=1) if len(log_values) > 1 else 0.0
            se_log = sd_log / math.sqrt(len(log_values)) if len(log_values) else 0.0
            # Student's t adapts to the number of runs
            t_multiplier = _t_multiplier(len(log_values))
            ci_low_log = mean_log - t_multiplier * se_log
            ci_high_log = mean_log + t_multiplier * se_log
            rows.append(
                {
                    variant_column: variant_value,
                    "metric": metric_col.replace("_ratio_nogil_over_gil", ""),
                    "ci_low": math.exp(ci_low_log),
                    "ci_high": math.exp(ci_high_log),
                    "geo_mean_ratio": math.exp(mean_log),
                }
            )
    return (
        pd.DataFrame(rows)[[variant_column, "metric", "ci_low", "ci_high", "geo_mean_ratio"]]
        .sort_values(by=[variant_column, "metric"])
        .reset_index(drop=True)
    )


def _write_ratio_outputs(df_combined: pd.DataFrame, variant_column: str, base_name: str, global_root: str) -> None:
    # Persist per-run ratios/diffs and their confidence intervals
    ratios_dir = os.path.join(global_root, RATIOS_DIRNAME)
    per_run = _compute_per_run_ratios(df=df_combined, variant_column=variant_column)
    os.makedirs(ratios_dir, exist_ok=True)
    # drop log helpers for CSV
    ratio_cols = [col for col in per_run.columns if not col.endswith("_log_ratio_nogil_over_gil")]
    ratios_clean = per_run[ratio_cols].sort_values(by=[variant_column, "run_id"]).reset_index(drop=True)
    metric_names = ["uptime", "cpu_usage", "energy_max", "vms", "ram", "cores_disparity"]
    ordered_cols = [variant_column, "run_id"]
    for metric in metric_names:
        ratio_col = f"{metric}_ratio_nogil_over_gil"
        diff_col = f"{metric}_diff_nogil_minus_gil"
        if ratio_col in ratios_clean.columns:
            # scalar ratio
            ratios_clean[f"{metric}_ratio"] = ratios_clean[ratio_col]
            # percent view
            ratios_clean[f"{metric}_pct"] = ratios_clean[ratio_col] * 100
            ordered_cols.extend([f"{metric}_ratio", f"{metric}_pct"])
            if diff_col in ratios_clean.columns:
                # absolute difference to show magnitude
                ratios_clean[f"{metric}_diff"] = ratios_clean[diff_col]
                ordered_cols.append(f"{metric}_diff")
    ratios_output = ratios_clean[ordered_cols]
    ratios_output.to_csv(
        os.path.join(ratios_dir, f"{os.path.splitext(base_name)[0]}_ratios_nogil_over_gil.csv"),
        index=False,
    )

    ratio_confidence = _compute_ratio_confidence(per_run_ratios=per_run, variant_column=variant_column)
    metric_order = ["uptime", "cpu_usage", "energy_max", "vms", "ram", "cores_disparity"]
    ratio_confidence["metric"] = pd.Categorical(ratio_confidence["metric"], categories=metric_order, ordered=True)
    ratio_confidence.sort_values(by=[variant_column, "metric"]).reset_index(drop=True).to_csv(
        os.path.join(ratios_dir, f"{os.path.splitext(base_name)[0]}_ratio_confidence.csv"),
        index=False,
    )


def _plot_combined_graphs(summary_path: str, variant_column: str, global_root: str) -> None:
    # Combined plots: one line per (run_id, flavor) for key metric relationships
    plotter = DataPlotter(
        path_file_stats=summary_path,
        folder_results=os.path.join(global_root, RUN_GRAPHS_DIRNAME),
        group_by=["run_id", "flavor"],
    )
    # CPU and energy views across uptime/variant dimensions
    plotter.plot_lines(x_column="uptime", y_columns=["cpu_usage"], title="CPU Usage vs Uptime (runs)", annotate_variant=True, variant_column=variant_column)
    plotter.plot_lines(x_column=variant_column, y_columns=["cpu_usage"], title="CPU Usage vs Variant (runs)")
    plotter.plot_lines(x_column="cpu_usage", y_columns=["energy_max"], title="Energy vs CPU Usage (runs)", annotate_variant=True, variant_column=variant_column)
    plotter.plot_lines(x_column="uptime", y_columns=["energy_max"], title="Energy vs Uptime (runs)", annotate_variant=True, variant_column=variant_column)
    plotter.plot_lines(x_column=variant_column, y_columns=["energy_max"], title="Energy vs Variant (runs)")
    plotter.plot_lines(x_column=variant_column, y_columns=["vms"], title="VMS vs Variant (runs)")
    plotter.plot_lines(x_column=variant_column, y_columns=["ram"], title="RAM vs Variant (runs)")


def _infer_base_root(output_file: str) -> str:
    """
    Infer the directory where per-run folders should be created.

    If `output_file` is under a `summaries/` directory, the base root is the parent of
    that directory (so outputs become `<base_root>/runXXX/summaries/<file>.csv`).
    """
    output_dir = os.path.abspath(os.path.dirname(output_file))
    if os.path.basename(output_dir) == RUN_SUMMARIES_DIRNAME:
        return os.path.abspath(os.path.join(output_dir, os.pardir))
    return output_dir


def _group_files_by_run_id(stats_files: List[FileStats]) -> dict[Optional[str], List[FileStats]]:
    grouped: dict[Optional[str], List[FileStats]] = {}
    for file_stats in stats_files:
        # filenames may or may not contain run id
        run_id = _extract_run_id(file_stats._file_path)
        # accumulate per run
        grouped.setdefault(run_id, []).append(file_stats)
    return grouped


def _run_summary_output_path(base_root: str, run_id: Optional[str], base_name: str) -> str:
    # keep runs isolated
    run_dir = os.path.join(base_root, f"run{run_id}") if run_id is not None else base_root
    # where per-run CSV lands
    summaries_dir = os.path.join(run_dir, RUN_SUMMARIES_DIRNAME)
    os.makedirs(summaries_dir, exist_ok=True)
    return os.path.join(summaries_dir, base_name)


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

    # Collect per-run summaries
    # keyed by inferred run id
    grouped = _group_files_by_run_id(stage_collect(pattern=args.pattern))
    # root that will hold runs/combined folders
    base_root = _infer_base_root(args.output_file)
    os.makedirs(base_root, exist_ok=True)
    base_name = os.path.basename(args.output_file)
    run_results = []
    for run_id, files in grouped.items():
        # per-run summary file
        summary_path = _run_summary_output_path(base_root=base_root, run_id=run_id, base_name=base_name)
        aggregated_writer = stage_aggregate(
            files_stats=files,
            output_path=summary_path,
            task_label=args.task_label,
            variant_regex=variant_regex,
            variant_column=args.variant_column,
            run_id=run_id,
        )
        # keep in-memory for combined
        run_results.append({"run_id": run_id, "aggregated": aggregated_writer.df_data})

    # Combine all runs into one DataFrame and write summary
    # preserve per-run rows
    df_combined = pd.concat([run["aggregated"].copy() for run in run_results], ignore_index=True)
    global_root = os.path.join(base_root, COMBINED_DIRNAME)
    summaries_dir = os.path.join(global_root, RUN_SUMMARIES_DIRNAME)
    os.makedirs(summaries_dir, exist_ok=True)
    combined_summary_path = os.path.join(summaries_dir, base_name)
    combined_writer = FileWriterCsv(file_path=combined_summary_path)
    combined_writer.set_data_frame(df=df_combined.sort_values(by=["flavor", args.variant_column, "run_id"]).reset_index(drop=True))
    combined_writer.write_to_csv()
    logger.info(f"Combined (all runs) summary written to {combined_summary_path}")
    # Ratios/CI outputs and combined plots
    _write_ratio_outputs(df_combined=df_combined, variant_column=args.variant_column, base_name=base_name, global_root=global_root)
    _plot_combined_graphs(summary_path=combined_summary_path, variant_column=args.variant_column, global_root=global_root)
