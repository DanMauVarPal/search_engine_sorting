"""Binary insertion sort with an inversion count.

Binary search finds the insert position, but moving list items still takes
O(n^2) time in the worst case.
"""


def sort_and_count(items: list) -> tuple[list, int]:
    """Return a sorted copy and its number of inversions."""
    sorted_items = []
    inversion_count = 0

    for item in items:
        insert_position = _find_insert_position(sorted_items, item)
        # Values after this position are larger and came before item.
        inversion_count += len(sorted_items) - insert_position
        sorted_items.insert(insert_position, item)

    return sorted_items, inversion_count


def _find_insert_position(sorted_items: list, new_item) -> int:
    """Find the position after equals, so equal values add no inversions."""
    low = 0
    high = len(sorted_items)

    while low < high:
        middle = (low + high) // 2
        if sorted_items[middle] <= new_item:
            low = middle + 1
        else:
            high = middle

    return low
