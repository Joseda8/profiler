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


_FLAVOR_RE = re.compile(r"_(nogil|gil)_")
_RUN_ID_RE = re.compile(r"_run([^_]+)_")

_AGG_METRIC_COLUMNS = [
    "uptime",
    "cpu_usage",
    "cpu_usage_cv",
    "energy_max",
    "vms",
    "vms_cv",
    "ram",
    "ram_cv",
    "cores_disparity",
]


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
    match = _RUN_ID_RE.search(os.path.basename(path))
    return match.group(1) if match else None


def _extract_flavor(path: str) -> str:
    """
    Extract `gil`/`nogil` from filenames that contain `_(gil|nogil)_`.
    """
    match = _FLAVOR_RE.search(os.path.basename(path))
    if not match:
        raise ValueError(f"Unable to infer flavor from filename: {path}")
    return match.group(1)


def _cv(std: float, mean: float) -> float:
    """
    Coefficient of variation (std/mean), returning 0.0 when mean is 0.
    """
    return (std / mean) if mean else 0.0


def _run_root_from_output_path(output_path: str) -> str:
    """
    Infer the run root directory from a `.../summaries/<file>.csv` output path.
    """
    summaries_dir = os.path.abspath(os.path.dirname(output_path))
    return os.path.abspath(os.path.join(summaries_dir, os.pardir))


def _aggregate_file_row(
    file_stats: FileStats,
    task_label: str,
    start_label: str,
    finish_label: str,
    variant_regex: str,
    run_id: Optional[str],
) -> List[object]:
    """
    Convert a single input FileStats into a row for the aggregated output CSV.
    """
    file_path = file_stats._file_path
    flavor = _extract_flavor(file_path)
    variant_value = _extract_variant(file_path, variant_regex)

    try:
        uptime_by_task = file_stats.get_times(start_label="start_", finish_label="finish_")
        uptime = uptime_by_task[task_label]

        cpu_usage, vms, ram, _swap = file_stats.get_average_between_labels(
            start_label=start_label, finish_label=finish_label
        )
        cpu_usage_std, vms_std, ram_std = file_stats.get_std_between_labels(
            start_label=start_label, finish_label=finish_label
        )
        *_, energy_max = file_stats.get_min_max_memory_stats(
            start_label=start_label, finish_label=finish_label
        )
        *_ignored, cores_disparity_avg = file_stats.track_dominant_core_changes_between_labels(
            start_label=start_label, finish_label=finish_label
        )
    except Exception as exc:
        raise RuntimeError(f"Failed to process stats from {file_path}") from exc

    return [
        variant_value,
        flavor,
        run_id,
        uptime,
        cpu_usage,
        _cv(cpu_usage_std, cpu_usage),
        energy_max,
        vms,
        _cv(vms_std, vms),
        ram,
        _cv(ram_std, ram),
        cores_disparity_avg,
    ]


def _generate_run_plots(output_path: str, run_root: str, variant_column: str) -> None:
    graphs_dir = os.path.join(run_root, "graphs")
    plotter = DataPlotter(path_file_stats=output_path, folder_results=graphs_dir, group_by="flavor")

    plotter.plot_lines(
        x_column="uptime",
        y_columns=["energy_max"],
        title="Energy vs Uptime",
        annotate_variant=True,
        variant_column=variant_column,
    )
    plotter.plot_lines(
        x_column="uptime",
        y_columns=["cpu_usage"],
        title="CPU Usage vs Uptime",
        annotate_variant=True,
        variant_column=variant_column,
    )
    plotter.plot_lines(
        x_column="cpu_usage",
        y_columns=["energy_max"],
        title="Energy vs CPU Usage",
        annotate_variant=True,
        variant_column=variant_column,
    )

    if variant_column in plotter.stats_columns:
        plotter.plot_lines(x_column=variant_column, y_columns=["energy_max"], title="Energy vs Variant")
        plotter.plot_lines(x_column=variant_column, y_columns=["cpu_usage"], title="CPU Usage vs Variant")
        plotter.plot_lines(x_column=variant_column, y_columns=["vms"], title="VMS vs Variant")
        plotter.plot_lines(x_column=variant_column, y_columns=["ram"], title="RAM vs Variant")


def stage_collect(pattern: str) -> List[FileStats]:
    """
    Gather all preprocessed files that match the glob pattern.

    Args:
        pattern: Glob pattern to match preprocessed CSV files.

    Returns:
        List of FileStats objects for each matching file.
    """
    paths = sorted(glob.glob(pattern))
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
    run_id: Optional[str] = None,
) -> FileWriterCsv:
    """
    Aggregate metrics from each file into a single results CSV.

    Args:
        files_stats: Loaded FileStats objects.
        output_path: Path where the aggregated CSV will be written.
        task_label: Label used in tags (start_<label>, finish_<label>).
        variant_regex: Regex with a capture group to extract the variant from filenames.
        variant_column: Column name to store the extracted variant.

    Returns:
        FileWriterCsv with aggregated data.
    """
    if not files_stats:
        raise ValueError("No input files provided for aggregation.")

    start_label, finish_label = f"start_{task_label}", f"finish_{task_label}"

    run_root = _run_root_from_output_path(output_path)

    columns = [variant_column, "flavor", "run_id", *_AGG_METRIC_COLUMNS]
    rows = [
        _aggregate_file_row(
            file_stats=file_stats,
            task_label=task_label,
            start_label=start_label,
            finish_label=finish_label,
            variant_regex=variant_regex,
            run_id=run_id,
        )
        for file_stats in files_stats
    ]

    csv_writer = FileWriterCsv(file_path=output_path)
    csv_writer.set_columns(columns)
    csv_writer.append_rows(rows)
    csv_writer.order_by_columns(columns=["flavor", variant_column, "run_id"])
    csv_writer.write_to_csv()
    logger.info(f"Aggregated results written to {output_path}")

    # Normalize file
    _write_normalized(csv_writer.df_data, output_path, variant_column, norm_root=run_root)

    _generate_run_plots(output_path=output_path, run_root=run_root, variant_column=variant_column)

    return csv_writer


def _write_normalized(df: pd.DataFrame, output_path: str, variant_column: str, norm_root: Optional[str] = None) -> Optional[pd.DataFrame]:
    """
    Normalize metrics so the best (minimum) value per column becomes 1.0.

    Returns the normalized DataFrame (also written to disk) or None if nothing was produced.
    """
    if df.empty:
        logger.warning(f"No data to normalize for {output_path}.")
        return None
    if variant_column not in df.columns:
        logger.warning(f"Missing variant column '{variant_column}' in {output_path}; skipping normalization.")
        return None

    # Replace NaNs/zeros with 0.1 for normalization purposes only.
    df_norm = df.replace(0, 0.1).fillna(0.1)

    base_cols = [variant_column] + [col for col in ("flavor", "run_id") if col in df_norm.columns]
    metric_cols = [
        col for col in df_norm.columns if col not in base_cols and not col.endswith("_cv")
    ]
    if not metric_cols:
        logger.warning(f"No metric columns to normalize for {output_path}.")
        return None

    processed_root = (
        os.path.abspath(norm_root) if norm_root is not None else os.path.abspath(os.path.dirname(output_path))
    )
    norm_dir = os.path.join(processed_root, "normalized")
    os.makedirs(norm_dir, exist_ok=True)
    base_name = os.path.basename(output_path)
    energy_col = "energy_max"

    numeric_metrics = (
        df_norm[metric_cols].apply(pd.to_numeric, errors="coerce").fillna(0.1).replace(0, 0.1)
    )
    min_by_variant = numeric_metrics.groupby(df_norm[variant_column]).transform("min")
    normalized_metrics = numeric_metrics / min_by_variant

    # Compare across flavors but grouped by variant.
    norm_combined = pd.concat([df_norm[base_cols], normalized_metrics], axis=1)

    sort_cols = [variant_column] + ([energy_col] if energy_col in norm_combined.columns else [])
    norm_combined = norm_combined.sort_values(by=sort_cols)

    norm_path = os.path.join(norm_dir, base_name)
    norm_writer = FileWriterCsv(file_path=norm_path)
    norm_writer.set_data_frame(df=norm_combined)
    norm_writer.write_to_csv()
    logger.info(f"Normalized results written to {norm_path}")
    return norm_combined


def _write_flavor_deltas(norm_path: str, variant_column: str) -> None:
    """
    Using a normalized combined file that has both gil and nogil rows, compute
    average gil-vs-nogil differences across variants.
    """
    if not os.path.exists(norm_path):
        return
    df = pd.read_csv(norm_path)
    if "flavor" not in df.columns:
        return
    flavors = set(df["flavor"].dropna().unique().tolist())
    if not {"gil", "nogil"}.issubset(flavors):
        return

    metrics = [
        col
        for col in df.columns
        if col not in {variant_column, "flavor", "run_id"} and not col.endswith("_cv")
    ]

    delta_data = {m: [] for m in metrics}
    pct_data = {m: [] for m in metrics}
    gil_vals = {m: [] for m in metrics}
    nogil_vals = {m: [] for m in metrics}

    for _, sub in df.groupby(variant_column):
        if set(sub["flavor"]) < {"gil", "nogil"}:
            continue
        gil_row = sub[sub["flavor"] == "gil"].iloc[0]
        nogil_row = sub[sub["flavor"] == "nogil"].iloc[0]
        for m in metrics:
            gil_val = pd.to_numeric(gil_row[m], errors="coerce")
            nogil_val = pd.to_numeric(nogil_row[m], errors="coerce")
            if pd.isna(gil_val) or pd.isna(nogil_val):
                continue
            delta = gil_val - nogil_val
            delta_data[m].append(delta)
            if nogil_val:
                pct_data[m].append(delta / nogil_val)
            gil_vals[m].append(gil_val)
            nogil_vals[m].append(nogil_val)

    rows = []
    for m in metrics:
        if not delta_data[m]:
            continue
        rows.append(
            {
                "metric": m,
                "gil_mean": (sum(gil_vals[m]) / len(gil_vals[m])) if gil_vals[m] else None,
                "nogil_mean": (sum(nogil_vals[m]) / len(nogil_vals[m])) if nogil_vals[m] else None,
                "gil_minus_nogil_mean": sum(delta_data[m]) / len(delta_data[m]),
                "gil_minus_nogil_pct_mean": (sum(pct_data[m]) / len(pct_data[m])) if pct_data[m] else None,
            }
        )

    if not rows:
        return

    out_path = os.path.join(
        os.path.dirname(norm_path),
        f"{os.path.splitext(os.path.basename(norm_path))[0]}_gil_vs_nogil.csv",
    )
    writer = FileWriterCsv(file_path=out_path)
    writer.set_columns(
        [
            "metric",
            "gil_mean",
            "nogil_mean",
            "gil_minus_nogil_mean",
            "gil_minus_nogil_pct_mean",
        ]
    )
    for r in rows:
        writer.append_row(
            [
                r["metric"],
                r["gil_mean"],
                r["nogil_mean"],
                r["gil_minus_nogil_mean"],
                r["gil_minus_nogil_pct_mean"],
            ]
        )
    writer.write_to_csv()
    logger.info(f"Flavor delta summary written to {out_path}")


def _compute_per_run_ratios(df: pd.DataFrame, variant_column: str) -> pd.DataFrame:
    """
    Compute per-run nogil/gil ratios for key metrics and return them as a DataFrame.
    """
    if df.empty:
        logger.warning("No combined data available to compute per-run ratios.")
        return pd.DataFrame()

    required_columns = {"flavor", "run_id", variant_column}
    if not required_columns.issubset(df.columns):
        logger.warning("Missing required columns to compute per-run ratios; skipping.")
        return pd.DataFrame()

    metric_columns = [col for col in ["uptime", "cpu_usage", "energy_max", "vms", "ram", "cores_disparity"] if col in df.columns]
    if not metric_columns:
        logger.warning("No metric columns available to compute per-run ratios.")
        return pd.DataFrame()

    rows = []
    for (run_id, variant_value), group in df.groupby(["run_id", variant_column]):
        gil_row = group[group["flavor"] == "gil"]
        nogil_row = group[group["flavor"] == "nogil"]
        if gil_row.empty or nogil_row.empty:
            continue
        g = gil_row.iloc[0]
        n = nogil_row.iloc[0]
        row = {variant_column: variant_value, "run_id": run_id}
        for metric in metric_columns:
            denom = g[metric]
            ratio = (n[metric] / denom) if denom else None
            row[f"{metric}_ratio_nogil_over_gil"] = ratio
            row[f"{metric}_diff_nogil_minus_gil"] = abs(n[metric] - g[metric])
            row[f"{metric}_log_ratio_nogil_over_gil"] = math.log(ratio) if ratio and ratio > 0 else None
        rows.append(row)

    if not rows:
        logger.warning("No nogil/gil pairs found to compute per-run ratios.")
        return pd.DataFrame()

    return pd.DataFrame(rows).sort_values(by=["run_id", variant_column]).reset_index(drop=True)


def _compute_ratio_confidence(per_run_ratios: pd.DataFrame, variant_column: str, t_value: float = 4.303) -> pd.DataFrame:
    """
    Compute geometric mean ratios and 95% CIs (log space) per variant across runs.
    """
    if per_run_ratios.empty:
        return pd.DataFrame()

    metric_columns = [
        c for c in per_run_ratios.columns
        if c.endswith("_ratio_nogil_over_gil") and "_log_" not in c
    ]
    rows = []
    for variant_value, group in per_run_ratios.groupby(variant_column):
        n = len(group["run_id"].unique())
        for metric_col in metric_columns:
            logs = group[metric_col].apply(lambda x: math.log(x) if x and x > 0 else None).dropna()
            if logs.empty:
                continue
            mean_log = logs.mean()
            sd_log = logs.std(ddof=1) if len(logs) > 1 else 0.0
            se_log = sd_log / math.sqrt(len(logs)) if len(logs) else 0.0
            t = t_value if len(logs) > 1 else 0.0
            ci_low_log = mean_log - t * se_log
            ci_high_log = mean_log + t * se_log
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


def _infer_base_root(output_file: str) -> str:
    """
    Infer the directory where per-run folders should be created.

    If `output_file` is under a `summaries/` directory, the base root is the parent of
    that directory (so outputs become `<base_root>/runXXX/summaries/<file>.csv`).
    """
    output_dir = os.path.abspath(os.path.dirname(output_file))
    if os.path.basename(output_dir) == "summaries":
        return os.path.abspath(os.path.join(output_dir, os.pardir))
    return output_dir


def _group_files_by_run_id(stats_files: List[FileStats]) -> dict[Optional[str], List[FileStats]]:
    grouped: dict[Optional[str], List[FileStats]] = {}
    for file_stats in stats_files:
        run_id = _extract_run_id(file_stats._file_path)
        grouped.setdefault(run_id, []).append(file_stats)
    return grouped


def _run_summary_output_path(base_root: str, run_id: Optional[str], base_name: str) -> str:
    run_dir = os.path.join(base_root, f"run{run_id}") if run_id is not None else base_root
    summaries_dir = os.path.join(run_dir, "summaries")
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

    # Collect result files
    stats_files = stage_collect(pattern=args.pattern)

    # Group files by run_id in filename (if present)
    grouped = _group_files_by_run_id(stats_files)

    # Base root for per-run outputs
    base_root = _infer_base_root(args.output_file)
    os.makedirs(base_root, exist_ok=True)

    base_name = os.path.basename(args.output_file)
    run_results = []
    for run_id, files in grouped.items():
        out_path = _run_summary_output_path(base_root=base_root, run_id=run_id, base_name=base_name)
        csv_writer = stage_aggregate(
            files_stats=files,
            output_path=out_path,
            task_label=args.task_label,
            variant_regex=variant_regex,
            variant_column=args.variant_column,
            run_id=run_id,
        )
        run_results.append(
            {
                "run_id": run_id,
                "aggregated": csv_writer.df_data,
            }
        )

    # Build combined
    df_combined = pd.concat(
        [run["aggregated"].copy() for run in run_results],
        ignore_index=True,
    )

    global_root = os.path.join(base_root, "combined")
    summaries_dir = os.path.join(global_root, "summaries")
    os.makedirs(summaries_dir, exist_ok=True)
    base_name = os.path.basename(args.output_file)
    combined_summary_path = os.path.join(summaries_dir, base_name)
    combined_writer = FileWriterCsv(file_path=combined_summary_path)
    combined_writer.set_data_frame(
        df=df_combined.sort_values(by=["flavor", args.variant_column, "run_id"]).reset_index(drop=True)
    )
    combined_writer.write_to_csv()
    logger.info(f"Combined (all runs) summary written to {combined_summary_path}")

    run_ids = sorted(df_combined["run_id"].dropna().unique().tolist())
    num_runs = len(run_ids)

    # Per-run nogil/gil ratios
    per_run_ratios = _compute_per_run_ratios(df=df_combined, variant_column=args.variant_column)
    if not per_run_ratios.empty:
        ratios_dir = os.path.join(global_root, "ratios")
        os.makedirs(ratios_dir, exist_ok=True)
        ratios_path = os.path.join(
            ratios_dir,
            f"{os.path.splitext(base_name)[0]}_ratios_nogil_over_gil.csv",
        )
        ratio_cols = [
            col for col in per_run_ratios.columns
            if not col.endswith("_log_ratio_nogil_over_gil")
        ]
        ratios_clean = per_run_ratios[ratio_cols].sort_values(
            by=[args.variant_column, "run_id"]
        ).reset_index(drop=True)

        metric_names = ["uptime", "cpu_usage", "energy_max", "vms", "ram", "cores_disparity"]
        ordered_cols = [args.variant_column, "run_id"]
        for metric in metric_names:
            ratio_col = f"{metric}_ratio_nogil_over_gil"
            diff_col = f"{metric}_diff_nogil_minus_gil"
            if ratio_col in ratios_clean.columns:
                base_col = f"{metric}_ratio"
                pct_col = f"{metric}_pct"
                diff_out_col = f"{metric}_diff"
                ratios_clean[base_col] = ratios_clean[ratio_col]
                ratios_clean[pct_col] = ratios_clean[ratio_col] * 100
                if diff_col in ratios_clean.columns:
                    ratios_clean[diff_out_col] = ratios_clean[diff_col]
                    ordered_cols.extend([base_col, pct_col, diff_out_col])
                else:
                    ordered_cols.extend([base_col, pct_col])

        ratios_output = ratios_clean[ordered_cols]
        ratios_output.to_csv(ratios_path, index=False)

    # Confidence intervals over runs (geometric mean + 95% CI in ratio space)
    ratio_confidence = _compute_ratio_confidence(per_run_ratios=per_run_ratios, variant_column=args.variant_column)
    if not ratio_confidence.empty:
        ratios_dir = os.path.join(global_root, "ratios")
        os.makedirs(ratios_dir, exist_ok=True)
        ratio_conf_path = os.path.join(
            ratios_dir,
            f"{os.path.splitext(base_name)[0]}_ratio_confidence.csv",
        )
        metric_order = ["uptime", "cpu_usage", "energy_max", "vms", "ram", "cores_disparity"]
        ratio_confidence["metric"] = pd.Categorical(ratio_confidence["metric"], categories=metric_order, ordered=True)
        ordered_conf = ratio_confidence.sort_values(by=[args.variant_column, "metric"]).reset_index(drop=True)
        ordered_conf.to_csv(ratio_conf_path, index=False)
        logger.info(f"Ratio confidence intervals written to {ratio_conf_path}")

    # Combined graphs: one line per run per flavor using DataPlotter
    combined_graphs_dir = os.path.join(global_root, "graphs")
    plotter_combined = DataPlotter(
        path_file_stats=combined_summary_path,
        folder_results=combined_graphs_dir,
        group_by=["run_id", "flavor"],
    )
    plotter_combined.plot_lines(
        x_column="uptime",
        y_columns=["cpu_usage"],
        title="CPU Usage vs Uptime (runs)",
        annotate_variant=True,
        variant_column=args.variant_column,
    )
    plotter_combined.plot_lines(
        x_column=args.variant_column,
        y_columns=["cpu_usage"],
        title="CPU Usage vs Variant (runs)",
    )
    plotter_combined.plot_lines(
        x_column="cpu_usage",
        y_columns=["energy_max"],
        title="Energy vs CPU Usage (runs)",
        annotate_variant=True,
        variant_column=args.variant_column,
    )
    plotter_combined.plot_lines(
        x_column="uptime",
        y_columns=["energy_max"],
        title="Energy vs Uptime (runs)",
        annotate_variant=True,
        variant_column=args.variant_column,
    )
    plotter_combined.plot_lines(
        x_column=args.variant_column,
        y_columns=["energy_max"],
        title="Energy vs Variant (runs)",
    )
    plotter_combined.plot_lines(
        x_column=args.variant_column,
        y_columns=["vms"],
        title="VMS vs Variant (runs)",
    )
    plotter_combined.plot_lines(
        x_column=args.variant_column,
        y_columns=["ram"],
        title="RAM vs Variant (runs)",
    )
