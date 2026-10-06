"""Merge sort, modified to count inversions while it sorts.

CS 3364 Project 1: find source reliability by counting inversions.

Definition
----------
An inversion is a pair of positions i < j with items[i] > items[j].
The comparison is strict, so two equal values never form an inversion.

How the count is obtained
-------------------------
Merge sort splits the list into a left half and a right half. Every inversion
in the list then belongs to exactly one of three groups:

1. both elements are in the left half   -> counted by the recursive call
2. both elements are in the right half  -> counted by the recursive call
3. one element is in each half          -> counted while the halves are merged

Group 3 is counted in `_merge_and_count`. Both halves are already sorted, so
when an element of the right half is merged ahead of the elements still waiting
in the left half, it is smaller than every one of those waiting elements.

Complexity
----------
Time:   Theta(n log n) in the best, average and worst case.
Memory: Theta(n) extra, for the merged lists.

Public interface (the same in every module of this package)
-----------------------------------------------------------
    sort_and_count(items) -> (sorted_items, inversion_count)
"""


def sort_and_count(items: list) -> tuple[list, int]:
    """Sort a list with merge sort and count its inversions.

    Args:
        items: Values that can be compared with each other (here, ranks).
            The list is not modified.

    Returns:
        A pair (sorted_items, inversion_count):
        sorted_items is a new list with the values in ascending order, and
        inversion_count is the number of pairs i < j with items[i] > items[j].
    """
    # Base case: zero or one element is already sorted and has no inversions.
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
    """Merge two sorted lists and count the inversions between them.

    A "split inversion" is a pair made of one element from each list in which
    the left element is strictly greater than the right element.

    Args:
        sorted_left: The sorted left half.
        sorted_right: The sorted right half.

    Returns:
        A pair (merged, split_inversions): the two lists merged into one sorted
        list, and the number of split inversions between them.
    """
    merged = []
    split_inversions = 0
    left_index = 0
    right_index = 0

    while left_index < len(sorted_left) and right_index < len(sorted_right):
        # "<=" and not "<": equal values are not an inversion, so on a tie the
        # left element goes first and nothing is counted.
        if sorted_left[left_index] <= sorted_right[right_index]:
            merged.append(sorted_left[left_index])
            left_index += 1
        else:
            # The right element is smaller than sorted_left[left_index] and,
            # because the left half is sorted, smaller than every element
            # after it too. Each of those elements forms one inversion with it.
            merged.append(sorted_right[right_index])
            right_index += 1
            split_inversions += len(sorted_left) - left_index

    # One list is used up. Whatever is left in the other is already in order
    # relative to everything merged so far, so it adds no inversions.
    merged.extend(sorted_left[left_index:])
    merged.extend(sorted_right[right_index:])

    return merged, split_inversions
