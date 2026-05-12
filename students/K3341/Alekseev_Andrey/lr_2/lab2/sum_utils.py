from __future__ import annotations

DEFAULT_LIMIT = 10_000_000_000_000
DEFAULT_WORKERS = 4


def split_range(limit: int, parts: int) -> list[tuple[int, int]]:
    if limit < 1:
        raise ValueError("limit must be positive")
    if parts < 1:
        raise ValueError("parts must be positive")

    chunk_size, remainder = divmod(limit, parts)
    ranges: list[tuple[int, int]] = []
    start = 1

    for index in range(parts):
        extra = 1 if index < remainder else 0
        end = start + chunk_size + extra - 1
        if start <= end:
            ranges.append((start, end))
        start = end + 1

    return ranges


def calculate_range_sum(start: int, end: int) -> int:
    if start > end:
        return 0
    count = end - start + 1
    return count * (start + end) // 2


def expected_sum(limit: int) -> int:
    return calculate_range_sum(1, limit)
