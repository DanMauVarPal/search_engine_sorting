"""Quick sort, modified to count inversions while it sorts.

CS 3364 Project 1: find source reliability by counting inversions.

Definition
----------
An inversion is a pair of positions i < j with items[i] > items[j].
The comparison is strict, so two equal values never form an inversion.

Why this is not the textbook in-place quick sort
------------------------------------------------
The usual in-place partitions (Lomuto, Hoare) swap elements that are far apart.
A swap changes the relative order of pairs that have not been compared yet, so
the number of swaps is not the number of inversions.

To count correctly, the partition has to keep the elements in their original
relative order. This module therefore partitions into three new lists in a
single left-to-right pass:

    less_than_pivot | equal_to_pivot | greater_than_pivot

How the count is obtained
-------------------------
After the partition, every inversion belongs to exactly one of two groups:

1. its two elements are in different lists  -> counted during the pass
2. its two elements are in the same list    -> counted by the recursive call
   (equal_to_pivot holds equal values only, so it contains no inversions)

Group 1 is counted as each element arrives. The earlier elements that are
larger than it are exactly the ones already sitting in a "larger" list:

    arriving element     added to the count
    ------------------   ---------------------------------------------
    less than pivot      len(equal_to_pivot) + len(greater_than_pivot)
    equal to pivot       len(greater_than_pivot)
    greater than pivot   0

Pivot choice
------------
The pivot is the value at a randomly chosen position (randomized quick sort).
Because the choice ignores how the input is ordered, no ordering is
systematically bad: sorted, reversed and "rise then fall" lists behave like any
other list, with a recursion depth proportional to log n.

A fixed rule does not have this property. Median-of-three, for example, is
defeated by an ascending run followed by a descending run (0, 1, ..., k, k,
..., 1): its recursion depth reaches half the length of the list and Python
raises RecursionError from about 2,000 elements.

The random generator is created from the fixed seed PIVOT_SEED at the start of
every call to `sort_and_count`. The same input therefore always gets the same
pivots, which keeps runs, recursion depth and timings repeatable. The pivots
never affect the result: the sorted list and the inversion count are the same
for any pivot choice.

Complexity
----------
Time:   Theta(n log n) expected for every input order. Theta(n^2) is still
        possible in theory, but only through a long streak of unlucky pivots,
        not through the order of the input.
Memory: Theta(n) extra on average. Keeping the original order costs quick sort
        its usual in-place memory advantage.

Public interface (the same in every module of this package)
-----------------------------------------------------------
    sort_and_count(items) -> (sorted_items, inversion_count)
"""

import random

# Seed of the pivot generator. A fixed value makes every run pick the same
# pivots, so results, recursion depth and timings can be reproduced.
PIVOT_SEED = 3364


def sort_and_count(items: list) -> tuple[list, int]:
    """Sort a list with quick sort and count its inversions.

    Args:
        items: Values that can be compared with each other (here, ranks).
            The list is not modified.

    Returns:
        A pair (sorted_items, inversion_count):
        sorted_items is a new list with the values in ascending order, and
        inversion_count is the number of pairs i < j with items[i] > items[j].
    """
    # A new generator for every call: what was sorted before has no effect
    # on the pivots chosen now.
    pivot_rng = random.Random(PIVOT_SEED)
    return _quick_sort_and_count(items, pivot_rng)


def _quick_sort_and_count(
    items: list, pivot_rng: random.Random
) -> tuple[list, int]:
    """Recursive part of `sort_and_count`.

    Args:
        items: The values to sort. The list is not modified.
        pivot_rng: Random generator shared by the whole recursion, used to
            pick the pivots.

    Returns:
        The pair (sorted_items, inversion_count) for `items`.
    """
    # Base case: zero or one element is already sorted and has no inversions.
    if len(items) <= 1:
        return list(items), 0

    pivot = _choose_pivot(items, pivot_rng)

    less_than_pivot = []
    equal_to_pivot = []
    greater_than_pivot = []
    split_inversions = 0  # inversions between elements of different lists

    # Order-preserving partition. Appending keeps each list in the same
    # relative order as in `items`, which the recursive calls rely on.
    for item in items:
        if item < pivot:
            # Everything already in the two larger lists came before `item`
            # and is greater than it: one inversion each.
            split_inversions += len(equal_to_pivot) + len(greater_than_pivot)
            less_than_pivot.append(item)
        elif item > pivot:
            # Earlier elements in the other lists are smaller: no inversions.
            greater_than_pivot.append(item)
        else:
            # Only the elements already in greater_than_pivot are larger.
            split_inversions += len(greater_than_pivot)
            equal_to_pivot.append(item)

    # equal_to_pivot always holds at least the pivot, so both recursive calls
    # receive strictly shorter lists and the recursion always ends.
    sorted_less, less_inversions = _quick_sort_and_count(
        less_than_pivot, pivot_rng
    )
    sorted_greater, greater_inversions = _quick_sort_and_count(
        greater_than_pivot, pivot_rng
    )

    sorted_items = sorted_less + equal_to_pivot + sorted_greater
    inversion_count = split_inversions + less_inversions + greater_inversions

    return sorted_items, inversion_count


def _choose_pivot(items: list, pivot_rng: random.Random):
    """Return the value at a randomly chosen position of the list.

    See "Pivot choice" at the top of this module for why the pivot is random.

    Args:
        items: A list with at least one element.
        pivot_rng: The random generator to draw the position from.

    Returns:
        The pivot value (one of the values in the list).
    """
    return pivot_rng.choice(items)
