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
    rows = []
    for path in glob.glob(pattern):
        if path.endswith("_cv.csv"):
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
                            "flavor": detect_flavor(path),
                            "variant_type": variant_col,
                            "variant_value": row.get(variant_col, ""),
                            "uptime": row.get("uptime", ""),
                            "cpu_usage": row.get("cpu_usage", ""),
                            "energy_max": row.get("energy_max", ""),
                            "vms": row.get("vms", ""),
                            "ram": row.get("ram", ""),
                            "cores_disparity": row.get("cores_disparity", ""),
                        }
                    )
                except Exception as excep:
                    logger.warning(f"Skipping row in {path}: {excep}")
                    continue
    return rows


def write_output(rows: List[Dict], output_path: str) -> None:
    if not rows:
        logger.warning("No rows to write for aggregated metrics.")
        return
    df = pd.DataFrame(rows)
    writer = FileWriterCsv(file_path=output_path)
    writer.set_columns(
        [
            "scenario",
            "flavor",
            "variant_type",
            "variant_value",
            "uptime",
            "cpu_usage",
            "energy_max",
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
                row["energy_max"],
                row["vms"],
                row["ram"],
                row["cores_disparity"],
            ]
        )
    writer.write_to_csv()
    logger.info(f"Aggregated metrics written to {output_path}")
    _write_global_cvs(df, output_path)
    _generate_plots(df, output_path)


def _write_global_cvs(df: pd.DataFrame, output_path: str) -> None:
    def _cv(series: pd.Series) -> float:
        series = pd.to_numeric(series, errors="coerce").dropna()
        if series.empty:
            return 0.0
        mean_val = series.mean()
        return series.std() / mean_val if mean_val else 0.0

    cv_path = os.path.join(os.path.dirname(output_path), "cvs", f"{os.path.splitext(os.path.basename(output_path))[0]}_cv.csv")
    cv_writer = FileWriterCsv(file_path=cv_path)
    cv_writer.set_columns(["metric", "cv"])
    for metric in ["cpu_usage", "vms", "ram"]:
        if metric in df.columns:
            cv_writer.append_row([metric, _cv(df[metric])])
    cv_writer.write_to_csv()
    logger.info(f"Aggregated global CVs written to {cv_path}")


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
    for col in ["uptime", "cpu_usage", "energy_max", "vms", "ram", "cores_disparity", "variant_value"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=["uptime", "cpu_usage", "energy_max", "vms", "ram", "cores_disparity"])

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

    # Thread scaling per scenario: uptime and energy_max vs variant_value
    for scenario, group in df.groupby("scenario"):
        if group["variant_value"].isna().all():
            continue
        group = group.sort_values(by="variant_value")
        plt.figure(figsize=(10, 7))
        for flavor, sub in group.groupby("flavor"):
            plt.plot(sub["variant_value"], sub["uptime"], marker="o", linestyle="-", label=f"{flavor} uptime")
            plt.plot(sub["variant_value"], sub["energy_max"], marker="o", linestyle="--", label=f"{flavor} energy_max")
            for _, row in sub.iterrows():
                label_val = fmt_variant(row.get("variant_value", ""))
                plt.annotate(label_val, (row["variant_value"], row["uptime"]), textcoords="offset points", xytext=(4, 4), fontsize=6)
                plt.annotate(label_val, (row["variant_value"], row["energy_max"]), textcoords="offset points", xytext=(4, 4), fontsize=6)
        plt.xlabel("variant_value")
        plt.ylabel("value")
        plt.title(f"Scaling for {scenario}")
        plt.legend(loc="best", fontsize=8)
        plt.grid(True)
        save(f"scaling_{scenario}.png")

        # Memory scaling (vms and ram) per scenario
        plt.figure(figsize=(10, 7))
        for flavor, sub in group.groupby("flavor"):
            plt.plot(sub["variant_value"], sub["vms"], marker="o", linestyle="-", label=f"{flavor} vms")
            plt.plot(sub["variant_value"], sub["ram"], marker="o", linestyle="--", label=f"{flavor} ram")
            for _, row in sub.iterrows():
                label_val = fmt_variant(row.get("variant_value", ""))
                plt.annotate(label_val, (row["variant_value"], row["vms"]), textcoords="offset points", xytext=(4, 4), fontsize=6)
                plt.annotate(label_val, (row["variant_value"], row["ram"]), textcoords="offset points", xytext=(4, 4), fontsize=6)
        plt.xlabel("variant_value")
        plt.ylabel("value")
        plt.title(f"Memory Scaling for {scenario}")
        plt.legend(loc="best", fontsize=8)
        plt.grid(True)
        save(f"scaling_memory_{scenario}.png")

    # Global (scenario-agnostic) scatter plots
    scatter_all("uptime", "energy_max", "Energy vs Uptime (All)", "energy_vs_uptime_all.png")
    scatter_all("cpu_usage", "cores_disparity", "CPU Usage vs Cores Disparity (All)", "cpu_usage_vs_cores_disparity_all.png")
    scatter_all("cpu_usage", "uptime", "CPU Usage vs Uptime (All)", "cpu_usage_vs_uptime_all.png")
    scatter_all("cpu_usage", "energy_max", "Energy vs CPU Usage (All)", "energy_vs_cpu_usage_all.png")
    scatter_all("vms", "ram", "VMS vs RAM (All)", "vms_vs_ram_all.png")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Aggregate processed summaries into a single metrics file.")
    parser.add_argument("--pattern", default="results/processed/*summary_*.csv", help="Glob pattern to match summary CSV files.")
    parser.add_argument("--output_file", default="results/processed/all_metrics.csv", help="Path to write the aggregated metrics CSV.")
    args = parser.parse_args()

    aggregated_rows = collect_rows(pattern=args.pattern)
    write_output(rows=aggregated_rows, output_path=args.output_file)
