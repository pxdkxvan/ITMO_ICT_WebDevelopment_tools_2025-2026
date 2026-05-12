from __future__ import annotations

import argparse
import re
import subprocess
import sys


def extract_elapsed(output: str) -> float:
    match = re.search(r"elapsed=([0-9.]+)s", output)
    if not match:
        raise RuntimeError(f"Cannot find elapsed time in output:\n{output}")
    return float(match.group(1))


def run_module(module_name: str, *args: str) -> tuple[float, str]:
    command = [sys.executable, "-m", module_name, *args]
    completed = subprocess.run(command, check=True, capture_output=True, text=True)
    return extract_elapsed(completed.stdout), completed.stdout


def main() -> None:
    parser = argparse.ArgumentParser(description="Benchmark all lab2 scripts")
    parser.add_argument("--sum-limit", type=int, default=10_000_000_000_000)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--skip-parse", action="store_true")
    args = parser.parse_args()

    sum_modules = [
        "lab2.threading_sum",
        "lab2.multiprocessing_sum",
        "lab2.async_sum",
    ]
    parse_modules = [
        "lab2.threading_parse",
        "lab2.multiprocessing_parse",
        "lab2.async_parse",
    ]

    print("Sum benchmarks")
    for module_name in sum_modules:
        elapsed, _ = run_module(module_name, "--limit", str(args.sum_limit), "--workers", str(args.workers))
        print(f"{module_name}: {elapsed:.6f}s")

    if args.skip_parse:
        return

    print("\nParse benchmarks")
    for module_name in parse_modules:
        elapsed, _ = run_module(module_name, "--workers", str(args.workers))
        print(f"{module_name}: {elapsed:.6f}s")


if __name__ == "__main__":
    main()
