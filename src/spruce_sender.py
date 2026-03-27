import argparse
import csv
import os
import socket
import time
from datetime import datetime

import pandas as pd


def ensure_output_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def write_csv_header_if_needed(csv_path: str) -> None:
    if not os.path.exists(csv_path):
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "run_id",
                "pair_id",
                "send_ts_pkt1",
                "send_ts_pkt2",
                "delta_in_us",
                "packet_size_bytes",
                "delta_out_us",
                "capacity_mbps",
                "abw_estimate_mbps",
            ])


def append_row(csv_path: str, row: list) -> None:
    with open(csv_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(row)


def estimate_abw_mbps(capacity_mbps: float, delta_in_us: float, delta_out_us: float) -> float:
    if delta_in_us <= 0:
        return 0.0

    estimate = capacity_mbps * (1.0 - ((delta_out_us - delta_in_us) / delta_in_us))
    return max(0.0, estimate)


def load_receiver_results(receiver_csv: str) -> pd.DataFrame:
    if not os.path.exists(receiver_csv):
        return pd.DataFrame()

    df = pd.read_csv(receiver_csv)
    return df


def compute_delta_out_us(receiver_df: pd.DataFrame, pair_id: int):
    pair_df = receiver_df[receiver_df["pair_id"] == pair_id].sort_values("packet_index")
    if len(pair_df) < 2:
        return None

    recv_times = pair_df["recv_ts"].tolist()
    delta_out_us = (recv_times[1] - recv_times[0]) * 1_000_000
    return delta_out_us


def main():
    parser = argparse.ArgumentParser(description="Spruce-like UDP sender")
    parser.add_argument("--target", required=True, help="Receiver IP")
    parser.add_argument("--port", type=int, default=9999)
    parser.add_argument("--pairs", type=int, default=20, help="Number of packet pairs")
    parser.add_argument("--interval", type=float, default=1.0, help="Seconds between pair probes")
    parser.add_argument("--packet-size", type=int, default=200, help="Probe packet size in bytes")
    parser.add_argument("--delta-in-us", type=float, default=2000.0, help="Gap between packet 1 and 2 in microseconds")
    parser.add_argument("--capacity-mbps", type=float, default=10.0, help="Known link capacity")
    parser.add_argument("--receiver-csv", default="results/raw/spruce_receiver_raw.csv")
    parser.add_argument("--output", default="results/raw/spruce_results.csv")
    args = parser.parse_args()

    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    ensure_output_dir(os.path.dirname(args.output))
    write_csv_header_if_needed(args.output)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    print(f"Starting Spruce-like sender -> {args.target}:{args.port}")
    print(f"Pairs={args.pairs}, packet_size={args.packet_size}, delta_in_us={args.delta_in_us}, capacity={args.capacity_mbps} Mbps")

    for pair_id in range(1, args.pairs + 1):
        payload1 = f"{pair_id},1,{time.time()},{args.delta_in_us},{args.packet_size}".encode("utf-8")
        if len(payload1) < args.packet_size:
            payload1 += b"x" * (args.packet_size - len(payload1))

        send_ts_pkt1 = time.time()
        sock.sendto(payload1, (args.target, args.port))

        time.sleep(args.delta_in_us / 1_000_000)

        payload2 = f"{pair_id},2,{time.time()},{args.delta_in_us},{args.packet_size}".encode("utf-8")
        if len(payload2) < args.packet_size:
            payload2 += b"x" * (args.packet_size - len(payload2))

        send_ts_pkt2 = time.time()
        sock.sendto(payload2, (args.target, args.port))

        time.sleep(0.2)
        receiver_df = load_receiver_results(args.receiver_csv)
        delta_out_us = compute_delta_out_us(receiver_df, pair_id)

        if delta_out_us is None:
            print(f"[pair {pair_id}] incomplete pair at receiver")
            continue

        abw_estimate_mbps = estimate_abw_mbps(
            capacity_mbps=args.capacity_mbps,
            delta_in_us=args.delta_in_us,
            delta_out_us=delta_out_us
        )

        append_row(args.output, [
            run_id,
            pair_id,
            send_ts_pkt1,
            send_ts_pkt2,
            args.delta_in_us,
            args.packet_size,
            delta_out_us,
            args.capacity_mbps,
            abw_estimate_mbps,
        ])

        print(
            f"[pair {pair_id}] "
            f"delta_in={args.delta_in_us:.1f} us, "
            f"delta_out={delta_out_us:.1f} us, "
            f"abw={abw_estimate_mbps:.3f} Mbps"
        )

        time.sleep(args.interval)

    print("Spruce-like sender finished.")


if __name__ == "__main__":
    main()