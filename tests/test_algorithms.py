"""Check every sorting algorithm registered in main.ALGORITHMS."""

import random
import unittest

from main import ALGORITHMS

KNOWN_CASES = [
    ([4, 5, 8, 9, 6], 2),  # the example in the project statement
    ([], 0),
    ([7], 0),
    ([1, 2, 3, 4], 0),  # already sorted
    ([4, 3, 2, 1], 6),  # reversed: every pair is an inversion
    ([5, 5, 5], 0),  # equal values are not inversions
    ([2, 1, 2, 1], 3),  # repeated values mixed with real inversions
]


def count_inversions_by_brute_force(items: list) -> int:
    """Count inversions by checking every pair."""
    inversion_count = 0
    for earlier in range(len(items)):
        for later in range(earlier + 1, len(items)):
            if items[earlier] > items[later]:
                inversion_count += 1
    return inversion_count


class SortAndCountTests(unittest.TestCase):
    def test_known_cases(self):
        for algorithm_name, sort_and_count in ALGORITHMS:
            for items, expected_count in KNOWN_CASES:
                with self.subTest(algorithm=algorithm_name, items=items):
                    sorted_items, inversion_count = sort_and_count(items)
                    self.assertEqual(sorted_items, sorted(items))
                    self.assertEqual(inversion_count, expected_count)

    def test_random_lists_match_brute_force(self):
        random_generator = random.Random(3364)
        for _ in range(300):
            length = random_generator.randint(0, 60)
            items = [random_generator.randint(0, 15) for _ in range(length)]
            expected_count = count_inversions_by_brute_force(items)

            for algorithm_name, sort_and_count in ALGORITHMS:
                with self.subTest(algorithm=algorithm_name, items=items):
                    sorted_items, inversion_count = sort_and_count(items)
                    self.assertEqual(sorted_items, sorted(items))
                    self.assertEqual(inversion_count, expected_count)

    def test_input_is_not_modified(self):
        original_items = [3, 1, 2, 3, 0]
        for algorithm_name, sort_and_count in ALGORITHMS:
            with self.subTest(algorithm=algorithm_name):
                items = list(original_items)
                sorted_items, _ = sort_and_count(items)
                self.assertEqual(items, original_items)
                self.assertIsNot(sorted_items, items)

    def test_rise_then_fall_list(self):
        run_length = 1500
        rising_run = list(range(run_length))
        falling_run = list(range(run_length, 0, -1))
        items = rising_run + falling_run
        expected_count = count_inversions_by_brute_force(items)

        for algorithm_name, sort_and_count in ALGORITHMS:
            with self.subTest(algorithm=algorithm_name):
                sorted_items, inversion_count = sort_and_count(items)
                self.assertEqual(sorted_items, sorted(items))
                self.assertEqual(inversion_count, expected_count)
