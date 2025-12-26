import pandas as pd

def main():
    df = pd.read_csv("results/processed/all_metrics.csv")

    # Select numeric columns for correlation
    numeric_cols = ["uptime", "cpu_usage", "energy_max", "vms", "ram", "cores_disparity"]
    df_numeric = df[numeric_cols].apply(pd.to_numeric, errors="coerce")

    corr_pearson = df_numeric.corr(method="pearson")
    corr_spearman = df_numeric.corr(method="spearman")

    print("Pearson correlation matrix:")
    print(corr_pearson)
    print("\nSpearman correlation matrix:")
    print(corr_spearman)

if __name__ == "__main__":
    main()
