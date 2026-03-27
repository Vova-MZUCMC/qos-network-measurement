import argparse
import csv
import os
import socket
import time
from collections import defaultdict


def ensure_output_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def write_csv_header_if_needed(csv_path: str) -> None:
    if not os.path.exists(csv_path):
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "pair_id",
                "packet_index",
                "recv_ts",
                "send_ts",
                "delta_in_us",
                "packet_size_bytes",
            ])


def append_row(csv_path: str, row: list) -> None:
    with open(csv_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(row)


def main():
    parser = argparse.ArgumentParser(description="Spruce-like UDP receiver")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=9999)
    parser.add_argument("--output", default="results/raw/spruce_receiver_raw.csv")
    args = parser.parse_args()

    ensure_output_dir(os.path.dirname(args.output))
    write_csv_header_if_needed(args.output)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((args.host, args.port))

    print(f"Receiver listening on {args.host}:{args.port}")
    print(f"Raw receive data -> {args.output}")

    while True:
        data, addr = sock.recvfrom(65535)
        recv_ts = time.time()

        try:
            payload = data.decode("utf-8")
            parts = payload.split(",")
            pair_id = int(parts[0])
            packet_index = int(parts[1])
            send_ts = float(parts[2])
            delta_in_us = float(parts[3])
            packet_size_bytes = int(parts[4])
        except Exception:
            continue

        append_row(args.output, [
            pair_id,
            packet_index,
            recv_ts,
            send_ts,
            delta_in_us,
            packet_size_bytes,
        ])

        print(f"Received pair={pair_id}, pkt={packet_index} from {addr[0]}")
        

if __name__ == "__main__":
    main()