"""Compare five ranking sources by their inversions against the combined rank."""

import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from algorithms import custom_sort, merge_sort, quick_sort

SOURCE_DIR = Path(__file__).resolve().parent / "sources"

SortAndCount = Callable[[list], tuple[list, int]]

ALGORITHMS: list[tuple[str, SortAndCount]] = [
    ("Merge sort", merge_sort.sort_and_count),
    ("Quick sort", quick_sort.sort_and_count),
    ("Binary insertion sort", custom_sort.sort_and_count),
]


@dataclass
class RankingData:
    """Ranks and sequences indexed by source, then by page line number."""

    names: list[str]
    ranks: list[list[int]]
    combined: list[int]
    sequences: list[list[int]]


def read_source(path: Path) -> list[int]:
    """Read ranks in page order, one rank per line."""
    source_ranks = []
    with open(path, encoding="utf-8") as source_file:
        for line in source_file:
            text = line.strip()
            if text:
                source_ranks.append(int(text))

    return source_ranks


def compute_combined(ranks: list[list[int]]) -> list[int]:
    """Add each page's ranks across the five sources."""
    page_count = len(ranks[0])
    combined = [0] * page_count
    for source_ranks in ranks:
        for page in range(page_count):
            combined[page] += source_ranks[page]

    return combined


def build_sequence(combined: list[int], source_ranks: list[int]) -> list[int]:
    """Put pages in combined-rank order, then take this source's ranks.

    A combined-rank tie is broken by this source's rank so it adds no
    inversion to this source's count.
    """
    page_order = sorted(
        range(len(combined)),
        key=lambda page: (combined[page], source_ranks[page]),
    )
    return [source_ranks[page] for page in page_order]


def load_rankings(source_dir: Path) -> RankingData:
    """Load source files and make one combined-order sequence per source."""
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


def count_inversions(
    data: RankingData, sort_and_count: SortAndCount
) -> dict[str, int]:
    """Count each source and check that the algorithm sorted its input."""
    counts = {}
    for source_name, sequence in zip(data.names, data.sequences):
        sorted_sequence, inversion_count = sort_and_count(sequence)

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
    """Stop if two algorithms disagree on a source's inversion count."""
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


def rank_sources(counts: dict[str, int]) -> list[tuple[str, int]]:
    """Put the source with the fewest inversions first."""
    return sorted(counts.items(), key=lambda name_and_count: name_and_count[1])


def print_report(
    results: dict[str, dict[str, int]], timings: dict[str, float]
) -> None:
    """Print inversion counts and times for each algorithm."""
    for algorithm_name, counts in results.items():
        ranked_sources = rank_sources(counts)

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
    data = load_rankings(SOURCE_DIR)

    results = {}
    timings = {}

    for algorithm_name, sort_and_count in ALGORITHMS:
        start_time = time.perf_counter()
        results[algorithm_name] = count_inversions(data, sort_and_count)
        timings[algorithm_name] = time.perf_counter() - start_time

    check_agreement(results)
    print_report(results, timings)
    print("All algorithms agree on every inversion count.")


if __name__ == "__main__":
    main()
