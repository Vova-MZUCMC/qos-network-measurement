import argparse
import csv
import os
import time
from datetime import datetime

from ping_probe import run_ping_once
from stats import append_stats
from plots import plot_latency_histogram


def ensure_output_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def write_csv_header_if_needed(csv_path: str) -> None:
    if not os.path.exists(csv_path):
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "run_id",
                "timestamp",
                "seq",
                "target",
                "success",
                "latency_ms",
                "packet_loss_percent",
            ])


def append_ping_result(csv_path: str, run_id: str, result) -> None:
    with open(csv_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            run_id,
            result.timestamp,
            result.seq,
            result.target,
            result.success,
            result.latency_ms,
            result.packet_loss_percent,
        ])


def copy_run_results_to_aggregate(run_csv_path: str, aggregate_csv_path: str) -> None:
    import pandas as pd

    run_df = pd.read_csv(run_csv_path)

    if run_df.empty:
        print("Run CSV is empty, nothing to append to aggregate results.")
        return

    ensure_output_dir(os.path.dirname(aggregate_csv_path))

    file_exists = os.path.exists(aggregate_csv_path)
    run_df.to_csv(
        aggregate_csv_path,
        mode="a",
        header=not file_exists,
        index=False
    )

    print(f"Raw results appended to: {aggregate_csv_path}")


def main():
    parser = argparse.ArgumentParser(description="QoS measurement: ping part")
    parser.add_argument("--target", required=True, help="IP or hostname to ping")
    parser.add_argument("--duration", type=int, default=60, help="Measurement duration in seconds")
    parser.add_argument("--interval", type=float, default=1.0, help="Seconds between measurements")
    args = parser.parse_args()

    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    run_results_csv = f"results/raw/ping_results_{run_id}.csv"
    aggregate_results_csv = "results/raw/ping_results.csv"
    aggregate_stats_csv = "results/raw/ping_stats.csv"
    histogram_png = f"results/plots/latency_histogram_{run_id}.png"

    ensure_output_dir("results/raw")
    ensure_output_dir("results/plots")

    write_csv_header_if_needed(run_results_csv)

    print(f"Starting ping measurements for target={args.target}")
    print(f"Duration: {args.duration} sec, interval: {args.interval} sec")
    print(f"Run ID: {run_id}")
    print(f"Per-run raw results: {run_results_csv}")

    start_time = time.time()
    seq = 1

    while time.time() - start_time < args.duration:
        current_ts = time.time()

        result = run_ping_once(
            target=args.target,
            seq=seq,
            timestamp=current_ts,
        )

        append_ping_result(run_results_csv, run_id, result)

        if result.success:
            print(f"[{seq}] latency={result.latency_ms:.3f} ms, loss={result.packet_loss_percent}%")
        else:
            print(f"[{seq}] timeout/loss, loss={result.packet_loss_percent}%")

        seq += 1
        time.sleep(args.interval)

    print("Ping measurement finished.")

    copy_run_results_to_aggregate(run_results_csv, aggregate_results_csv)

    append_stats(
        input_csv=run_results_csv,
        output_csv=aggregate_stats_csv,
        run_id=run_id,
        target=args.target,
        duration=args.duration,
        interval=args.interval,
    )

    plot_latency_histogram(
        input_csv=run_results_csv,
        output_png=histogram_png
    )


if __name__ == "__main__":
    main()