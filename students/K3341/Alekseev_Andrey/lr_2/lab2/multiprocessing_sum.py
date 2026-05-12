from __future__ import annotations

import argparse
import multiprocessing as mp
import time

from lab2.sum_utils import DEFAULT_LIMIT, DEFAULT_WORKERS, calculate_range_sum, expected_sum, split_range


def calculate_sum(start: int, end: int) -> int:
    return calculate_range_sum(start, end)


def main() -> None:
    parser = argparse.ArgumentParser(description="Multiprocessing sum benchmark")
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT)
    parser.add_argument("--workers", type=int, default=DEFAULT_WORKERS)
    args = parser.parse_args()

    ranges = split_range(args.limit, args.workers)

    started_at = time.perf_counter()
    with mp.Pool(processes=args.workers) as pool:
        partial_sums = pool.starmap(calculate_sum, ranges)

    total = sum(partial_sums)
    elapsed = time.perf_counter() - started_at

    print(f"multiprocessing total={total}")
    print(f"expected={expected_sum(args.limit)}")
    print(f"workers={args.workers}")
    print(f"elapsed={elapsed:.6f}s")


if __name__ == "__main__":
    main()
