"""Merge sort with an inversion count, O(n log n) time."""


def sort_and_count(items: list) -> tuple[list, int]:
    """Return a sorted copy and its number of inversions."""
    if len(items) <= 1:
        return list(items), 0

    middle = len(items) // 2
    sorted_left, left_inversions = sort_and_count(items[:middle])
    sorted_right, right_inversions = sort_and_count(items[middle:])

    merged, split_inversions = _merge_and_count(sorted_left, sorted_right)

    return merged, left_inversions + right_inversions + split_inversions


def _merge_and_count(
    sorted_left: list, sorted_right: list
) -> tuple[list, int]:
    """Count pairs split across the two sorted halves."""
    merged = []
    split_inversions = 0
    left_index = 0
    right_index = 0

    while left_index < len(sorted_left) and right_index < len(sorted_right):
        if sorted_left[left_index] <= sorted_right[right_index]:
            merged.append(sorted_left[left_index])
            left_index += 1
        else:
            # Every remaining left value is bigger than this right value.
            merged.append(sorted_right[right_index])
            right_index += 1
            split_inversions += len(sorted_left) - left_index

    merged.extend(sorted_left[left_index:])
    merged.extend(sorted_right[right_index:])

    return merged, split_inversions
