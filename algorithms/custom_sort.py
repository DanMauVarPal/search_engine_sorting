"""Binary insertion sort, modified to count inversions while it sorts.

CS 3364 Project 1: find source reliability by counting inversions.
This is the team's third algorithm, next to merge sort and quick sort.

Algorithm
---------
Binary insertion sort builds the sorted list one value at a time. For each new
value it finds the position where the value belongs in the list sorted so far,
and inserts it there. Plain insertion sort finds that position by walking left
one element at a time; this version finds it by binary search, which is the
only difference between the two.

Definition
----------
An inversion is a pair of positions i < j with items[i] > items[j].
The comparison is strict, so two equal values never form an inversion.

How the count is obtained
-------------------------
When a value is about to be inserted, the sorted list holds exactly the values
that came before it in the input. The value is inserted in front of every one
of them that is strictly greater, and each of those forms one inversion with
it: it came earlier and it is larger. Their number is

    len(sorted_items) - insert_position

Every inversion is counted exactly once, at the moment its later (smaller)
value is inserted. A new value is placed after any values equal to it, so
equal values are never counted.

Complexity
----------
Time:   Theta(n^2) in the worst case (input in descending order).
        The binary searches need about log2(n) comparisons per value, which
        is Theta(n log n) in total. The insertions are what cost more: each
        one moves every value behind the insert position one place to the
        right, up to n moves per insertion.
        Best case: Theta(n log n), for input that is already sorted, because
        every value is then inserted at the end and nothing is moved.
Memory: Theta(n) extra, for the sorted list.

Note on measured times: the moves are made by Python's built-in list.insert,
which runs in compiled code. For 10,000 values this makes the algorithm about
as fast as merge sort in practice, although its growth rate is quadratic.

Public interface (the same in every module of this package)
-----------------------------------------------------------
    sort_and_count(items) -> (sorted_items, inversion_count)
"""


def sort_and_count(items: list) -> tuple[list, int]:
    """Sort a list with binary insertion sort and count its inversions.

    Args:
        items: Values that can be compared with each other (here, ranks).
            The list is not modified.

    Returns:
        A pair (sorted_items, inversion_count):
        sorted_items is a new list with the values in ascending order, and
        inversion_count is the number of pairs i < j with items[i] > items[j].
    """
    sorted_items = []  # the values read so far, always kept in order
    inversion_count = 0

    for item in items:
        insert_position = _find_insert_position(sorted_items, item)

        # Every value from insert_position to the end of sorted_items is
        # strictly greater than `item` and came before it in `items`, so each
        # one forms an inversion with it.
        inversion_count += len(sorted_items) - insert_position

        # list.insert moves those larger values one place to the right and
        # puts `item` in the gap, which keeps sorted_items in order.
        sorted_items.insert(insert_position, item)

    return sorted_items, inversion_count


def _find_insert_position(sorted_items: list, new_item) -> int:
    """Find by binary search where a new value belongs in a sorted list.

    The position returned is the one of the first value strictly greater than
    `new_item`. Inserting there keeps the list sorted and places `new_item`
    after any values equal to it, which is what keeps equal values from being
    counted as inversions.

    Args:
        sorted_items: A list in ascending order. It is not modified.
        new_item: The value about to be inserted.

    Returns:
        A position from 0 to len(sorted_items). It equals len(sorted_items)
        when no value in the list is greater than `new_item`.
    """
    # The answer always lies in the range low..high. While the loop runs:
    #   every value before position `low` is less than or equal to new_item
    #   every value from position `high` onward is strictly greater
    low = 0
    high = len(sorted_items)

    while low < high:
        middle = (low + high) // 2
        # "<=" and not "<": a value equal to new_item belongs before it, so
        # the search continues to the right of `middle`.
        if sorted_items[middle] <= new_item:
            low = middle + 1
        else:
            high = middle

    return low
