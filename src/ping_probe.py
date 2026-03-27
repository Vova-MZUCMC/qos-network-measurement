import platform
import re
import subprocess
from dataclasses import dataclass
from typing import Optional


@dataclass
class PingResult:
    timestamp: float
    seq: int
    target: str
    success: bool
    latency_ms: Optional[float]
    packet_loss_percent: float


def run_ping_once(target: str, seq: int, timestamp: float) -> PingResult:
    system = platform.system().lower()

    try:
        if system == "windows":
            cmd = ["ping", "-n", "1", target]
            completed = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding="cp866",
                errors="replace",
                timeout=5
            )
        else:
            cmd = ["ping", "-c", "1", target]
            completed = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=5
            )

        output = completed.stdout + completed.stderr

        latency_ms = parse_latency_ms(output)
        success = latency_ms is not None
        packet_loss_percent = 0.0 if success else 100.0

        return PingResult(
            timestamp=timestamp,
            seq=seq,
            target=target,
            success=success,
            latency_ms=latency_ms,
            packet_loss_percent=packet_loss_percent,
        )

    except subprocess.TimeoutExpired:
        return PingResult(
            timestamp=timestamp,
            seq=seq,
            target=target,
            success=False,
            latency_ms=None,
            packet_loss_percent=100.0,
        )


def parse_latency_ms(output: str) -> Optional[float]:
    patterns = [
        r"time[=<]\s*([\d.]+)\s*ms",
        r"time[=<]\s*([\d.]+)ms",
        r"время[=<]\s*([\d.]+)\s*мс",
        r"время[=<]\s*([\d.]+)мс",
    ]

    for pattern in patterns:
        match = re.search(pattern, output, re.IGNORECASE)
        if match:
            return float(match.group(1))

    return None