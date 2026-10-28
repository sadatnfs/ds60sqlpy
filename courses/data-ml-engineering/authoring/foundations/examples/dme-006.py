"""Tests compare independent expected behavior and challenge incomplete invariants."""

import unittest


def package_total(records):
    total = 0
    for _, packages in records:
        if type(packages) is not int or packages < 1:
            raise ValueError("Expected a positive integer package count")
        total += packages
    return total


def example_one():
    class ContractChecks(unittest.TestCase):
        def test_known_rows(self):
            self.assertEqual(package_total([("A", 2), ("B", 3), ("C", 1)]), 6)

        def test_empty(self):
            self.assertEqual(package_total([]), 0)

        def test_invalid(self):
            with self.assertRaises(ValueError):
                package_total([("A", -1)])

    suite = unittest.defaultTestLoader.loadTestsFromTestCase(ContractChecks)
    result = unittest.TestResult()
    suite.run(result)
    assert result.testsRun == 3 and result.wasSuccessful()
    return {
        "actual_unittest_cases": result.testsRun,
        "failures": len(result.failures),
        "errors": len(result.errors),
    }


def example_two():
    def wrong_total(records):
        return len(records) * 2

    baseline = [("A", 2), ("B", 3), ("C", 1)]
    changed = [("A", 2), ("B", 3), ("C", 4)]
    assert wrong_total(baseline) == package_total(baseline) == 6
    assert wrong_total(changed) >= 0  # This weak invariant still passes.
    expected = 2 + 3 + 4
    assert expected == 9 and wrong_total(changed) == 6
    assert package_total(changed) == expected

    class ChangedInputCheck(unittest.TestCase):
        def test_changed_input(self):
            self.assertEqual(wrong_total(changed), 9)

    suite = unittest.defaultTestLoader.loadTestsFromTestCase(ChangedInputCheck)
    result = unittest.TestResult()
    suite.run(result)
    assert result.testsRun == 1 and len(result.failures) == 1 and not result.errors
    return {
        "coincidental_baseline_match": 6,
        "changed_expected": expected,
        "wrong_changed_result": wrong_total(changed),
        "nonnegative_invariant_could_not_detect_error": True,
        "expected_unittest_failures": len(result.failures),
    }


def main():
    print("Run actual contract tests:", example_one())
    print("Falsify a plausible implementation:", example_two())


if __name__ == "__main__":
    main()
