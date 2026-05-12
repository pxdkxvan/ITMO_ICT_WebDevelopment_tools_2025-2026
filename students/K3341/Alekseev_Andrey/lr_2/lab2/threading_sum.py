from __future__ import annotations

import argparse
import threading
import time

from lab2.sum_utils import DEFAULT_LIMIT, DEFAULT_WORKERS, calculate_range_sum, expected_sum, split_range


def calculate_sum(start: int, end: int) -> int:
    return calculate_range_sum(start, end)


def main() -> None:
    parser = argparse.ArgumentParser(description="Threading sum benchmark")
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT)
    parser.add_argument("--workers", type=int, default=DEFAULT_WORKERS)
    args = parser.parse_args()

    ranges = split_range(args.limit, args.workers)
    partial_sums = [0] * len(ranges)
    threads: list[threading.Thread] = []

    def worker(index: int, start: int, end: int) -> None:
        partial_sums[index] = calculate_sum(start, end)

    started_at = time.perf_counter()
    for index, (start, end) in enumerate(ranges):
        thread = threading.Thread(target=worker, args=(index, start, end))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    total = sum(partial_sums)
    elapsed = time.perf_counter() - started_at

    print(f"threading total={total}")
    print(f"expected={expected_sum(args.limit)}")
    print(f"workers={args.workers}")
    print(f"elapsed={elapsed:.6f}s")


if __name__ == "__main__":
    main()
