import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def plot_latency_histogram(input_csv: str, output_png: str) -> None:
    df = pd.read_csv(input_csv)
    df_clean = df.dropna(subset=["latency_ms"])

    if df_clean.empty:
        print("No valid latency values found. Histogram will not be created.")
        return

    latency = df_clean["latency_ms"]

    min_val = int(np.floor(latency.min()))
    max_val = int(np.ceil(latency.max()))

    bins = np.arange(min_val - 0.5, max_val + 1.5, 1)

    os.makedirs(os.path.dirname(output_png), exist_ok=True)

    plt.figure(figsize=(8, 5))
    plt.hist(latency, bins=bins, edgecolor="black")
    plt.xticks(range(min_val, max_val + 1))
    plt.title("Latency Histogram")
    plt.xlabel("Latency (ms)")
    plt.ylabel("Frequency")
    plt.tight_layout()
    plt.savefig(output_png)
    plt.close()

    print(f"Latency histogram saved to: {output_png}")