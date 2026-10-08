# search_engine_sorting

CS 3364 search engine sorting algorithm for web-pages based on ranking reliability.

This is Project 1 of CS 3364 (Algorithms): decide which of five ranking sources is the most reliable by counting inversions while sorting.

## The problem

Five sources each rank the same 10,000 web pages. A search engine combines them by adding up, for every page, the five ranks the page received. That sum is the page's **combined rank**.

A source is **more reliable the fewer inversions** its ranking has against the combined ranking.

An inversion in a list `A` is a pair of positions `i < j` with `A[i] > A[j]`. The project statement gives this example, with the pages listed in combined-rank order:

|               | Page8 | Page5 | Page6 | Page1 | Page3 |
| ------------- | ----- | ----- | ----- | ----- | ----- |
| Combined rank | 25    | 27    | 39    | 40    | 45    |
| Source A      | 4     | 5     | 8     | 9     | 6     |

Source A has 2 inversions: (8, 6) and (9, 6).

## What the program does

`main.py` runs five stages:

1. **Load.** Read every `sources/source*.txt` file. Each file holds one rank per line, and line *p* refers to page *p* in every file.
2. **Combine.** Add the sources up page by page to get the combined rank of each page.
3. **Arrange.** For each source, list that source's ranks with the pages placed in combined-rank order. This list is the source's *sequence*.
4. **Count.** Give every sequence to every sorting algorithm. Each algorithm sorts the sequence and counts the inversions it finds on the way.
5. **Report.** For each algorithm, print the sources from most to least reliable.

Two safety checks run along the way, and the program stops with an error if either fails:

- The list each algorithm returns must equal Python's built-in sort of the same sequence.
- All algorithms must report the same inversion count for every source. The count belongs to the sequence, not to the algorithm, so a difference means a bug.

## Requirements

- Python 3.9 or newer
- No third-party packages

## Submission files

- `main.py`, `algorithms/`, and `sources/` are the program and its input data.
- `Report_Project01/CS3364_Project1_Report.docx` is the team report.
- `tests/` contains the program's correctness checks.

## How to run

From the project folder:

```
python main.py
```

On systems where Python 3 is installed as `python3`, use `python3 main.py`. The program takes no arguments. It finds the `sources` folder next to `main.py`, so it can be started from any directory.

Expected output (the times depend on the machine):

```
Merge sort  (0.129 s)
  Rank  Source        Inversions
  1     source1       17,442,716
  2     source5       17,458,031
  3     source3       17,502,205
  4     source2       17,576,151
  5     source4       17,778,159
  Most reliable source: source1

Quick sort  (0.095 s)
  Rank  Source        Inversions
  1     source1       17,442,716
  2     source5       17,458,031
  3     source3       17,502,205
  4     source2       17,576,151
  5     source4       17,778,159
  Most reliable source: source1

Binary insertion sort  (0.085 s)
  Rank  Source        Inversions
  1     source1       17,442,716
  2     source5       17,458,031
  3     source3       17,502,205
  4     source2       17,576,151
  5     source4       17,778,159
  Most reliable source: source1

All algorithms agree on every inversion count.
```

Each time covers all five sources for that algorithm, including the built-in sort used by the first safety check.

## How to run the tests

From the project folder:

```
python -m unittest
```

The tests in `tests/test_algorithms.py` run every algorithm registered in `main.py` against hand-checked lists, random lists counted by brute force, and an input ordering that is hard for quick sort. They also check that an algorithm does not modify the list it is given.

## Project layout

```
search_engine_sorting/
├── main.py                  loading, summing, arranging, calling the algorithms, report
├── algorithms/
│   ├── __init__.py          marks the folder as a Python package
│   ├── merge_sort.py        merge sort that counts inversions
│   ├── quick_sort.py        quick sort that counts inversions
│   └── custom_sort.py       binary insertion sort that counts inversions (the team's choice)
├── tests/
│   ├── __init__.py          lets "python -m unittest" find the tests
│   └── test_algorithms.py   tests for every registered algorithm
├── sources/
│   └── source1.txt ... source5.txt    the five rankings, 10,000 lines each
├── Report_Project01/
│   └── CS3364_Project1_Report.docx    team report
└── README.md
```

## The algorithms

Every module in `algorithms/` exposes the same function, so `main.py` calls them all the same way:

```python
sort_and_count(items) -> (sorted_items, inversion_count)
```

The function returns a new sorted list and never modifies `items`.

| Module          | Where the inversions are counted | Time |
| --------------- | -------------------------------- | ---- |
| `merge_sort.py` | While merging two sorted halves: when an element of the right half is taken first, it forms one inversion with every element still waiting in the left half. | Θ(n log n) in every case |
| `quick_sort.py` | While partitioning around the pivot: each element forms one inversion with every earlier element already placed in a larger group. | Θ(n log n) expected |
| `custom_sort.py` | Binary insertion sort, the team's choice. While inserting each value into the list sorted so far: it forms one inversion with every value it is placed in front of. | Θ(n²) worst case |

Quick sort here is not the textbook in-place version. In-place partitioning swaps distant elements, which changes the order of pairs that have not been compared yet, so its swaps cannot be counted as inversions. This version partitions into three new lists (less than, equal to, greater than the pivot) and keeps the original order inside each. The pivot is chosen at random with a fixed seed, so no input ordering is systematically slow and every run is repeatable.

Binary insertion sort finds each insert position by binary search, so it needs only Θ(n log n) comparisons, but every insertion still moves the values behind that position. Those moves are made by Python's built-in `list.insert`, which runs in compiled code. That is why, for 10,000 values, it is about as fast as the other two even though its worst case is quadratic.

The docstring at the top of each module explains its method in full.

## Rules and assumptions

- **Strict inversions.** Equal values never count as an inversion.
- **Ties in the combined rank.** Pages with the same combined rank are ordered by the source's own rank, so a tie never adds an inversion to any source. Because of this, each source gets its own sequence.
- **Page identity.** Line *p* of every source file is assumed to be the same page.
- **Equal weights.** The combined rank is a plain sum of the five sources.
- **Built-in sort.** Python's `sorted` is used only to arrange the pages in stage 3 and in the safety check of stage 4. The inversion counts come from the algorithms in `algorithms/`.

## Adding an algorithm

1. Write `sort_and_count(items)` in a new module inside `algorithms/`, for example `algorithms/new_sort.py`. It must return `(sorted_items, inversion_count)` and leave `items` unchanged.
2. In `main.py`, add the module to the import line and add one line to the `ALGORITHMS` list:

   ```python
   from algorithms import custom_sort, merge_sort, new_sort, quick_sort

   ALGORITHMS = [
       ("Merge sort", merge_sort.sort_and_count),
       ("Quick sort", quick_sort.sort_and_count),
       ("Binary insertion sort", custom_sort.sort_and_count),
       ("New sort", new_sort.sort_and_count),
   ]
   ```

The report, both safety checks and the tests then cover the new algorithm automatically.
