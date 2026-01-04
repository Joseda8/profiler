import os
import pandas as pd

def main():
    # Use the current aggregate location, with a fallback for older runs.
    candidates = [
        "results/processed/aggregate/all_metrics.csv",
        "results/processed/all_metrics.csv",
    ]
    csv_path = next((p for p in candidates if os.path.exists(p)), None)
    if not csv_path:
        raise FileNotFoundError(f"None of the aggregate files found: {candidates}")

    df = pd.read_csv(csv_path)

    # Select numeric columns for correlation
    numeric_cols = ["uptime", "cpu_usage", "energy_delta", "power_avg", "vms", "ram", "cores_disparity"]
    df_numeric = df[numeric_cols].apply(pd.to_numeric, errors="coerce")

    corr_pearson = df_numeric.corr(method="pearson")
    corr_spearman = df_numeric.corr(method="spearman")

    print("Pearson correlation matrix:")
    print(corr_pearson)
    print("\nSpearman correlation matrix:")
    print(corr_spearman)

if __name__ == "__main__":
    main()
