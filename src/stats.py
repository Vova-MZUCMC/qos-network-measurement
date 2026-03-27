import os
import pandas as pd
import numpy as np


def append_stats(input_csv: str, output_csv: str, run_id: str, target: str, duration: int, interval: float) -> None:
    df = pd.read_csv(input_csv)

    total_packets = len(df)
    if total_packets == 0:
        print("No rows in input CSV. Stats will not be written.")
        return

    df_clean = df.dropna(subset=["latency_ms"])

    successful_packets = len(df_clean)
    lost_packets = total_packets - successful_packets
    loss_percent = (lost_packets / total_packets) * 100

    if successful_packets == 0:
        stats = {
            "run_id": run_id,
            "target": target,
            "duration_sec": duration,
            "interval_sec": interval,
            "total_packets": total_packets,
            "successful_packets": successful_packets,
            "lost_packets": lost_packets,
            "packet_loss_percent": loss_percent,
            "latency_mean": None,
            "latency_median": None,
            "latency_p95": None,
            "latency_min": None,
            "latency_max": None,
            "latency_std": None,
        }
    else:
        latency = df_clean["latency_ms"]

        stats = {
            "run_id": run_id,
            "target": target,
            "duration_sec": duration,
            "interval_sec": interval,
            "total_packets": total_packets,
            "successful_packets": successful_packets,
            "lost_packets": lost_packets,
            "packet_loss_percent": loss_percent,
            "latency_mean": float(latency.mean()),
            "latency_median": float(latency.median()),
            "latency_p95": float(np.percentile(latency, 95)),
            "latency_min": float(latency.min()),
            "latency_max": float(latency.max()),
            "latency_std": float(latency.std()) if len(latency) > 1 else 0.0,
        }

    stats_df = pd.DataFrame([stats])

    os.makedirs(os.path.dirname(output_csv), exist_ok=True)

    file_exists = os.path.exists(output_csv)
    stats_df.to_csv(
        output_csv,
        mode="a",
        header=not file_exists,
        index=False
    )

    print(f"Stats appended to: {output_csv}")
    print(stats_df)