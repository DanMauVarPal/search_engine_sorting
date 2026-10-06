"""Third sorting algorithm (the team's choice), modified to count inversions.

CS 3364 Project 1: find source reliability by counting inversions.

TEMPLATE: this module is not implemented yet. Replace every TODO, including
the ones in this docstring, then register the algorithm in main.py (see "When
the algorithm is ready" below).

Algorithm
---------
TODO: name the algorithm and describe it in two or three sentences.

Definition
----------
An inversion is a pair of positions i < j with items[i] > items[j].
The comparison is strict, so two equal values never form an inversion.

How the count is obtained
-------------------------
TODO: explain which step of the algorithm counts inversions, and why every
inversion is counted exactly once.

Not every sorting algorithm can do this. The count is easy to obtain when each
step removes a known number of inversions: swapping two neighbouring elements
that are out of order, for example, removes exactly one. It is not the number
of swaps when elements jump over others, as in selection sort or heap sort.

Complexity
----------
Time:   TODO
Memory: TODO

Public interface (the same in every module of this package)
-----------------------------------------------------------
    sort_and_count(items) -> (sorted_items, inversion_count)

When the algorithm is ready
---------------------------
1. In main.py, add `custom_sort` to the import of the algorithm modules:
       from algorithms import custom_sort, merge_sort, quick_sort
2. In main.py, add one line to the ALGORITHMS list:
       ("<algorithm name>", custom_sort.sort_and_count),
3. Run `python -m unittest`, then `python main.py`. The tests, the
   sorted-output check and the agreement check then cover this module too.
"""


def sort_and_count(items: list) -> tuple[list, int]:
    """Sort a list with <TODO: algorithm name> and count its inversions.

    Rules that every algorithm module follows:
      * Do not modify `items`. Work on a copy, for example list(items).
      * Return a new list with the values in ascending order.
      * Count strictly: equal values are not an inversion.
      * Do not print, read files or keep anything between calls.

    Args:
        items: Values that can be compared with each other (here, ranks).
            The list is not modified.

    Returns:
        A pair (sorted_items, inversion_count):
        sorted_items is a new list with the values in ascending order, and
        inversion_count is the number of pairs i < j with items[i] > items[j].
    """
    # TODO: write the algorithm here, then delete the line below.
    raise NotImplementedError("custom_sort.sort_and_count is not written yet")


def _helper_and_count(items: list) -> tuple[list, int]:
    """TODO: optional helper. Rename it, or delete it if it is not needed.

    A helper does one step of the algorithm and is private to this module, so
    its name starts with an underscore. See merge_sort._merge_and_count and
    quick_sort._choose_pivot for examples. Change the parameters and the
    return value to whatever the step needs.

    Args:
        items: TODO: describe what the helper receives.

    Returns:
        TODO: describe what the helper returns.
    """
    # TODO: write the helper here, then delete the line below.
    raise NotImplementedError(
        "custom_sort._helper_and_count is not written yet"
    )
