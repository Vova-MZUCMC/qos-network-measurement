import argparse
import os
import pandas as pd
import numpy as np


def main():
    parser = argparse.ArgumentParser(description="Stats for Spruce-like results")
    parser.add_argument("--input", default="results/raw/spruce_results.csv")
    parser.add_argument("--output", default="results/raw/spruce_stats.csv")
    args = parser.parse_args()

    df = pd.read_csv(args.input)

    if df.empty:
        print("No Spruce results found.")
        return

    abw = df["abw_estimate_mbps"].dropna()

    if abw.empty:
        print("No valid bandwidth estimates found.")
        return

    stats = {
        "abw_mean_mbps": float(abw.mean()),
        "abw_median_mbps": float(abw.median()),
        "abw_p95_mbps": float(np.percentile(abw, 95)),
        "abw_min_mbps": float(abw.min()),
        "abw_max_mbps": float(abw.max()),
        "abw_std_mbps": float(abw.std()) if len(abw) > 1 else 0.0,
    }

    out_df = pd.DataFrame([stats])
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    out_df.to_csv(args.output, index=False)

    print(out_df)


if __name__ == "__main__":
    main()