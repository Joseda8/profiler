import argparse
import csv
import glob
import os
from typing import List, Dict

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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Aggregate processed summaries into a single metrics file.")
    parser.add_argument("--pattern", default="results/processed/*summary_*.csv", help="Glob pattern to match summary CSV files.")
    parser.add_argument("--output_file", default="results/processed/all_metrics.csv", help="Path to write the aggregated metrics CSV.")
    args = parser.parse_args()

    aggregated_rows = collect_rows(pattern=args.pattern)
    write_output(rows=aggregated_rows, output_path=args.output_file)
