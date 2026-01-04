import argparse
import csv
import glob
import os
from typing import List, Dict

import matplotlib.pyplot as plt
import pandas as pd

from ....util import FileWriterCsv, logger


def detect_flavor(filename: str) -> str:
    """Extract gil/nogil flavor from the filename."""
    return "nogil" if "nogil" in filename else "gil"


def scenario_from_filename(filename: str) -> str:
    """
    Derive scenario name from a summary filename like bubble_sort_summary_gil.csv.
    """
    base = os.path.basename(filename)
    parts = base.replace(".csv", "").split("_summary_")
    return parts[0] if parts else base


def collect_rows(pattern: str) -> List[Dict]:
    rows: List[Dict] = []

    def process_paths(paths: List[str]) -> None:
        for path in paths:
            # Skip helper artifacts
            parts = path.split(os.sep)
            if any(part in {"normalized", "cvs", "graphs", "graphs_all"} for part in parts):
                continue
            base = os.path.basename(path)
            if path.endswith("_cv.csv") or "_summary_gil" in base or "_summary_nogil" in base:
                continue
            with open(path, newline="") as f:
                reader = csv.DictReader(f)
                if not reader.fieldnames:
                    continue
                variant_col = reader.fieldnames[0]
                for row in reader:
                    try:
                        rows.append(
                            {
                                "scenario": scenario_from_filename(path),
                                "flavor": row.get("flavor", detect_flavor(path)),
                                "variant_type": variant_col,
                                "variant_value": row.get(variant_col, ""),
                                "uptime": row.get("uptime", ""),
                                "cpu_usage": row.get("cpu_usage", ""),
                                "energy_delta": row.get("energy_delta", ""),
                                "power_avg": row.get("power_avg", ""),
                                "vms": row.get("vms", ""),
                                "ram": row.get("ram", ""),
                                "cores_disparity": row.get("cores_disparity", ""),
                            }
                        )
                    except Exception as excep:
                        logger.warning(f"Skipping row in {path}: {excep}")
                        continue

    paths = glob.glob(pattern, recursive=True)
    process_paths(paths)

    # Fallbacks if nothing useful was collected (e.g., pattern matched only skipped files)
    if not rows:
        fallback_patterns = []
        if "summary_*" in pattern:
            fallback_patterns.append(pattern.replace("summary_*", "summary"))
            fallback_patterns.append(pattern.replace("summary_*", "summary*.csv"))
        # Prefer combined summaries if present
        fallback_patterns.append("results/processed/combined/summaries/*summary*.csv")
        # Then any run summaries
        fallback_patterns.append("results/processed/*/summaries/*summary*.csv")
        fallback_patterns.append("results/processed/*summary.csv")
        fallback_patterns.append("results/processed/*summary*.csv")
        fallback_patterns.append("results/processed/aggregate/*summary*.csv")
        fallback_patterns.append("results/processed/**/*.csv")

        for fb in fallback_patterns:
            process_paths(glob.glob(fb, recursive=True))
            if rows:
                logger.info(f"Using fallback pattern '{fb}'")
                break

    return rows


def write_output(rows: List[Dict], output_path: str) -> None:
    if not rows:
        logger.warning("No rows to write for aggregated metrics.")
        return
    df = pd.DataFrame(rows)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    writer = FileWriterCsv(file_path=output_path)
    writer.set_columns(
        [
            "scenario",
            "flavor",
            "variant_type",
            "variant_value",
            "uptime",
            "cpu_usage",
            "energy_delta",
            "power_avg",
            "vms",
            "ram",
            "cores_disparity",
        ]
    )
    for row in rows:
        writer.append_row(
            [
                row["scenario"],
                row["flavor"],
                row["variant_type"],
                row["variant_value"],
                row["uptime"],
                row["cpu_usage"],
                row["energy_delta"],
                row["power_avg"],
                row["vms"],
                row["ram"],
                row["cores_disparity"],
            ]
        )
    writer.write_to_csv()
    logger.info(f"Aggregated metrics written to {output_path}")
    _generate_plots(df, output_path)


def _generate_plots(df: pd.DataFrame, output_path: str) -> None:
    if df.empty:
        logger.warning("No data available for correlation plots.")
        return

    def fmt_variant(val) -> str:
        """Format variant values as int when possible to keep labels tidy."""
        try:
            fval = float(val)
            if fval.is_integer():
                return str(int(fval))
        except (TypeError, ValueError):
            return str(val)
        return str(val)

    # Ensure numeric types where needed
    for col in ["uptime", "cpu_usage", "energy_delta", "power_avg", "vms", "ram", "cores_disparity", "variant_value"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=["uptime", "cpu_usage", "energy_delta", "vms", "ram", "cores_disparity"])

    output_dir = os.path.join(os.path.dirname(output_path), "graphs_all")
    os.makedirs(output_dir, exist_ok=True)

    def save(fig_name: str):
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, fig_name), format="png")
        plt.close()

    def scatter_all(x, y, title, filename):
        plt.figure(figsize=(10, 7))
        plt.scatter(df[x], df[y], alpha=0.7)
        plt.xlabel(x)
        plt.ylabel(y)
        plt.title(title)
        plt.grid(True)
        save(filename)

    # Global (scenario-agnostic) scatter plots
    scatter_all("uptime", "energy_delta", "Energy vs Uptime (All)", "energy_vs_uptime_all.png")
    scatter_all("cpu_usage", "cores_disparity", "CPU Usage vs Cores Disparity (All)", "cpu_usage_vs_cores_disparity_all.png")
    scatter_all("cpu_usage", "uptime", "CPU Usage vs Uptime (All)", "cpu_usage_vs_uptime_all.png")
    scatter_all("cpu_usage", "energy_delta", "Energy vs CPU Usage (All)", "energy_vs_cpu_usage_all.png")
    if "power_avg" in df.columns and df["power_avg"].notna().any():
        df_power = df.dropna(subset=["power_avg"])
        plt.figure(figsize=(10, 7))
        plt.scatter(df_power["cpu_usage"], df_power["power_avg"], alpha=0.7)
        plt.xlabel("cpu_usage")
        plt.ylabel("power_avg")
        plt.title("Power vs CPU Usage (All)")
        plt.grid(True)
        save("power_vs_cpu_usage_all.png")

        plt.figure(figsize=(10, 7))
        plt.scatter(df_power["uptime"], df_power["power_avg"], alpha=0.7)
        plt.xlabel("uptime")
        plt.ylabel("power_avg")
        plt.title("Power vs Uptime (All)")
        plt.grid(True)
        save("power_vs_uptime_all.png")
    scatter_all("vms", "ram", "VMS vs RAM (All)", "vms_vs_ram_all.png")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Aggregate processed summaries into a single metrics file.")
    parser.add_argument("--pattern", default="results/processed/*summary*.csv", help="Glob pattern to match summary CSV files.")
    parser.add_argument("--output_file", default="results/processed/aggregate/all_metrics.csv", help="Path to write the aggregated metrics CSV.")
    args = parser.parse_args()

    aggregated_rows = collect_rows(pattern=args.pattern)
    write_output(rows=aggregated_rows, output_path=args.output_file)
