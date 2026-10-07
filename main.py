"""CS 3364 Project 1: find the most reliable ranking source.

Five sources each rank the same 10,000 web pages. The combined rank of a page
is the sum of its five source ranks. A source is more reliable the fewer
inversions its ranking has against the combined ranking.

What this program does
----------------------
1. Load     read every sources/source*.txt file into a list of ranks
2. Combine  add the sources up page by page to get the combined rank
3. Arrange  for each source, list its ranks with the pages put in
            combined-rank order (this list is the source's "sequence")
4. Count    give every sequence to every sorting algorithm; each algorithm
            returns the number of inversions it found while sorting, and the
            sorted list it returns is checked against Python's built-in sort
5. Report   rank the sources from fewest to most inversions, after checking
            that all algorithms reported the same counts

Assumptions
-----------
* Line p of every source file refers to the same web page p.
* An inversion is a pair i < j with sequence[i] > sequence[j] (strict).
* Pages with the same combined rank are ordered by the source's own rank, so
  a tie in the combined rank never adds an inversion to any source.

Usage
-----
    python main.py

Adding an algorithm
-------------------
Create algorithms/<name>.py containing a function

    sort_and_count(items) -> (sorted_items, inversion_count)

that does not modify `items`, then add one line to ALGORITHMS below.
"""

import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from algorithms import custom_sort, merge_sort, quick_sort

# Folder holding the source files. It is built from the location of this file
# so the program can be started from any working directory.
SOURCE_DIR = Path(__file__).resolve().parent / "sources"

# Signature shared by every algorithm module: it receives a list and returns
# (that list sorted ascending, the number of inversions in that list).
SortAndCount = Callable[[list], tuple[list, int]]

# Algorithms to run, as (name shown in the report, function to call).
# To add another algorithm, import its module above and add one line here.
ALGORITHMS: list[tuple[str, SortAndCount]] = [
    ("Merge sort", merge_sort.sort_and_count),
    ("Quick sort", quick_sort.sort_and_count),
    ("Binary insertion sort", custom_sort.sort_and_count),
]


@dataclass
class RankingData:
    """Everything read or derived from the source files.

    Built once by `load_rankings` and only read afterwards.

    Index conventions used by every field:
        source index: 0 .. number of sources - 1, in file-name order
        page:         0 .. number of pages - 1, the zero-based line number
                      of the page in the source files

    Attributes:
        names: Name of each source, taken from its file name ("source1", ...).
        ranks: ranks[source_index][page] is the rank that source gives that
            page.
        combined: combined[page] is the sum of the ranks every source gives
            that page.
        sequences: sequences[source_index] holds that source's ranks with the
            pages arranged in combined-rank order. These lists are the input
            of the sorting algorithms.
    """

    names: list[str]
    ranks: list[list[int]]
    combined: list[int]
    sequences: list[list[int]]


# ---------------------------------------------------------------------------
# Stages 1 to 3: load the files, sum them, arrange each source's ranks
# ---------------------------------------------------------------------------


def read_source(path: Path) -> list[int]:
    """Read one source file into a list of ranks.

    The file holds one integer per line. Position `page` of the returned list
    is the rank this source gives to page number `page`.

    Args:
        path: Location of the source file.

    Returns:
        The ranks in file order.
    """
    source_ranks = []
    with open(path, encoding="utf-8") as source_file:
        for line in source_file:
            # strip() also removes the Windows line endings (CRLF) the
            # provided files use.
            text = line.strip()
            if text:
                source_ranks.append(int(text))
    return source_ranks


def compute_combined(ranks: list[list[int]]) -> list[int]:
    """Sum the ranks of all sources page by page.

    All sources are weighted equally, as the project statement requires.

    Args:
        ranks: ranks[source_index][page], one inner list per source, all of
            the same length.

    Returns:
        A list where position `page` is the combined rank of that page.
    """
    page_count = len(ranks[0])
    combined = [0] * page_count
    for source_ranks in ranks:
        for page in range(page_count):
            combined[page] += source_ranks[page]
    return combined


def build_sequence(combined: list[int], source_ranks: list[int]) -> list[int]:
    """Arrange one source's ranks in combined-rank order.

    The pages are ordered by combined rank, lowest first. Pages that share a
    combined rank are ordered by this source's own rank (the tie rule), so a
    tie can never count as an inversion against the source.

    The number of inversions in the returned list is the number of page pairs
    that the combined ranking and this source put in opposite orders.

    Python's built-in `sorted` is used here on purpose: this step only
    prepares the input, and keeping it independent of the algorithms under
    test means a bug in one of them cannot corrupt what all of them count.

    Args:
        combined: combined[page] is the combined rank of that page.
        source_ranks: source_ranks[page] is this source's rank of that page.

    Returns:
        This source's ranks, listed in combined-rank order of the pages.
    """
    page_order = sorted(
        range(len(combined)),
        key=lambda page: (combined[page], source_ranks[page]),
    )
    return [source_ranks[page] for page in page_order]


def load_rankings(source_dir: Path) -> RankingData:
    """Read every source file and build the data the algorithms need.

    Args:
        source_dir: Folder containing the files named "source*.txt".

    Returns:
        A RankingData with the names, ranks, combined ranks and sequences.

    Raises:
        ValueError: If the source files do not all hold the same number of
            ranks, since they would then not describe the same pages.
    """
    source_paths = sorted(source_dir.glob("source*.txt"))
    names = [source_path.stem for source_path in source_paths]
    ranks = [read_source(source_path) for source_path in source_paths]

    expected_page_count = len(ranks[0])
    for source_path, source_ranks in zip(source_paths, ranks):
        if len(source_ranks) != expected_page_count:
            raise ValueError(
                f"{source_path.name} has {len(source_ranks)} ranks but "
                f"{source_paths[0].name} has {expected_page_count}. "
                "Every source must rank the same pages."
            )

    combined = compute_combined(ranks)
    sequences = [
        build_sequence(combined, source_ranks) for source_ranks in ranks
    ]
    return RankingData(names, ranks, combined, sequences)


# ---------------------------------------------------------------------------
# Stage 4: count inversions with each algorithm
# ---------------------------------------------------------------------------


def count_inversions(
    data: RankingData, sort_and_count: SortAndCount
) -> dict[str, int]:
    """Count the inversions of every source with one sorting algorithm.

    Args:
        data: The loaded rankings.
        sort_and_count: The algorithm to use, for example
            merge_sort.sort_and_count.

    Returns:
        A dictionary mapping each source name to its inversion count.

    Raises:
        RuntimeError: If the list the algorithm returns for a source is not
            that source's sequence in sorted order.
    """
    counts = {}
    for source_name, sequence in zip(data.names, data.sequences):
        sorted_sequence, inversion_count = sort_and_count(sequence)

        # Safety check: a count is only trustworthy if the algorithm really
        # sorted the sequence. Python's built-in sort is the reference.
        if sorted_sequence != sorted(sequence):
            algorithm_function = (
                f"{sort_and_count.__module__}.{sort_and_count.__name__}"
            )
            raise RuntimeError(
                f"{algorithm_function} did not return the sequence of "
                f"{source_name} in sorted order."
            )

        counts[source_name] = inversion_count
    return counts


def check_agreement(results: dict[str, dict[str, int]]) -> None:
    """Confirm that every algorithm reported the same inversion counts.

    The number of inversions is a property of the sequence, not of the
    algorithm that counts it. Any difference between two algorithms therefore
    means one of them has a bug, and the program stops instead of reporting
    two different answers.

    Args:
        results: results[algorithm_name][source_name] is an inversion count.

    Raises:
        RuntimeError: If two algorithms disagree on the count of a source.
    """
    algorithm_names = list(results)
    reference_algorithm = algorithm_names[0]
    reference_counts = results[reference_algorithm]

    for algorithm_name in algorithm_names[1:]:
        for source_name, inversion_count in results[algorithm_name].items():
            reference_count = reference_counts[source_name]
            if inversion_count != reference_count:
                raise RuntimeError(
                    f"{algorithm_name} counted {inversion_count} inversions "
                    f"for {source_name}, but {reference_algorithm} counted "
                    f"{reference_count}."
                )


# ---------------------------------------------------------------------------
# Stage 5: report
# ---------------------------------------------------------------------------


def rank_sources(counts: dict[str, int]) -> list[tuple[str, int]]:
    """Order the sources from most reliable to least reliable.

    Fewer inversions means more reliable.

    Args:
        counts: Maps each source name to its inversion count.

    Returns:
        (source_name, inversion_count) pairs, fewest inversions first.
    """
    return sorted(counts.items(), key=lambda name_and_count: name_and_count[1])


def print_report(
    results: dict[str, dict[str, int]], timings: dict[str, float]
) -> None:
    """Print, for each algorithm, the sources ranked by reliability.

    Args:
        results: results[algorithm_name][source_name] is an inversion count.
        timings: timings[algorithm_name] is the time in seconds the algorithm
            took to process all sources, including the sorted-output check
            made by `count_inversions`.
    """
    for algorithm_name, counts in results.items():
        ranked_sources = rank_sources(counts)

        # Several sources can share the lowest count; all of them are then
        # reported as most reliable.
        fewest_inversions = ranked_sources[0][1]
        most_reliable = [
            source_name
            for source_name, inversion_count in ranked_sources
            if inversion_count == fewest_inversions
        ]

        print(f"{algorithm_name}  ({timings[algorithm_name]:.3f} s)")
        print(f"  {'Rank':<6}{'Source':<12}{'Inversions':>12}")
        for rank, (source_name, inversion_count) in enumerate(
            ranked_sources, start=1
        ):
            print(f"  {rank:<6}{source_name:<12}{inversion_count:>12,}")

        if len(most_reliable) == 1:
            print(f"  Most reliable source: {most_reliable[0]}")
        else:
            tied_sources = ", ".join(most_reliable)
            print(f"  Most reliable sources (tied): {tied_sources}")
        print()


def main() -> None:
    """Run every algorithm on every source and print the reliability report."""
    data = load_rankings(SOURCE_DIR)

    results = {}  # results[algorithm_name][source_name] = inversion count
    timings = {}  # timings[algorithm_name] = seconds for all sources

    for algorithm_name, sort_and_count in ALGORITHMS:
        # The measured time includes the sorted-output check that
        # count_inversions makes (a few milliseconds per algorithm).
        start_time = time.perf_counter()
        results[algorithm_name] = count_inversions(data, sort_and_count)
        timings[algorithm_name] = time.perf_counter() - start_time

    check_agreement(results)
    print_report(results, timings)
    print("All algorithms agree on every inversion count.")


if __name__ == "__main__":
    main()
