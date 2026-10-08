"""Quicksort with an inversion count.

The three partitions keep their input order. Cross-partition inversions are
counted during partitioning, and recursion counts the remaining ones.
Random pivots give expected O(n log n) time; the worst case is O(n^2).
"""

import random

PIVOT_SEED = 3364


def sort_and_count(items: list) -> tuple[list, int]:
    """Return a sorted copy and its number of inversions."""
    pivot_rng = random.Random(PIVOT_SEED)
    return _quick_sort_and_count(items, pivot_rng)


def _quick_sort_and_count(
    items: list, pivot_rng: random.Random
) -> tuple[list, int]:
    if len(items) <= 1:
        return list(items), 0

    pivot = pivot_rng.choice(items)
    less_than_pivot = []
    equal_to_pivot = []
    greater_than_pivot = []
    split_inversions = 0

    for item in items:
        if item < pivot:
            # Earlier values in the equal and greater groups are larger.
            split_inversions += len(equal_to_pivot) + len(greater_than_pivot)
            less_than_pivot.append(item)
        elif item > pivot:
            greater_than_pivot.append(item)
        else:
            split_inversions += len(greater_than_pivot)
            equal_to_pivot.append(item)

    sorted_less, less_inversions = _quick_sort_and_count(
        less_than_pivot, pivot_rng
    )
    sorted_greater, greater_inversions = _quick_sort_and_count(
        greater_than_pivot, pivot_rng
    )

    sorted_items = sorted_less + equal_to_pivot + sorted_greater
    inversion_count = split_inversions + less_inversions + greater_inversions
    return sorted_items, inversion_count
