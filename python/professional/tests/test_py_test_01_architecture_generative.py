"""Deterministic and generative tests for python-test-01."""

from __future__ import annotations

import importlib.util
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from python.professional.solutions.py_test_01_architecture_generative_solution import (
    CacheSettings,
    ExpiringCache,
    FixedClock,
    JsonFileStore,
    MemoryStore,
    SessionService,
    choose_double,
    load_cache_settings,
    merge_intervals,
    verify_store_contract,
)


class ArchitectureTests(unittest.TestCase):
    def test_fake_and_real_local_store_share_a_contract(self) -> None:
        verify_store_contract(MemoryStore.empty)
        with tempfile.TemporaryDirectory(prefix="ds60-store-contract-") as directory:
            path = Path(directory) / "store.json"
            verify_store_contract(lambda: JsonFileStore(path))

    def test_fake_clock_controls_expiry_without_sleep(self) -> None:
        clock = FixedClock(10.0)
        cache = ExpiringCache(
            MemoryStore.empty(),
            clock,
            CacheSettings(ttl_seconds=2.0, namespace="test"),
        )
        cache.put("u1", "s1")
        self.assertEqual(cache.get("u1"), "s1")
        clock.advance(2.0)
        self.assertIsNone(cache.get("u1"))

    def test_environment_patch_is_scoped_and_restored(self) -> None:
        original = os.environ.get("DS60_CACHE_TTL_SECONDS")
        with patch.dict(
            os.environ,
            {
                "DS60_CACHE_TTL_SECONDS": "7.5",
                "DS60_CACHE_NAMESPACE": "patched",
            },
            clear=False,
        ):
            settings = load_cache_settings()
            self.assertEqual(settings, CacheSettings(7.5, "patched"))
        self.assertEqual(os.environ.get("DS60_CACHE_TTL_SECONDS"), original)

    def test_mock_is_narrowly_used_for_one_audit_interaction(self) -> None:
        audit = Mock(spec=["record"])
        service = SessionService(
            ExpiringCache(
                MemoryStore.empty(),
                FixedClock(1.0),
                CacheSettings(10.0, "sessions"),
            ),
            audit,
        )
        service.issue("user-1", "session-1")
        audit.record.assert_called_once_with("session_issued", "user-1")

    def test_double_choice_makes_tradeoff_visible(self) -> None:
        self.assertEqual(choose_double("stateful-collaborator"), "fake")
        self.assertEqual(choose_double("single-interaction"), "mock")
        self.assertEqual(choose_double("file-format-contract"), "real-local")


@unittest.skipUnless(
    importlib.util.find_spec("hypothesis") is not None,
    "Hypothesis is not installed; install the professional dependency group",
)
class HypothesisProperties(unittest.TestCase):
    """Defined dynamically in setUpClass so import remains an explained skip."""

    def test_interval_properties_and_shrinking_target(self) -> None:
        from hypothesis import given, settings
        from hypothesis import strategies as st

        @settings(max_examples=100, derandomize=True, database=None, deadline=None)
        @given(
            st.lists(
                st.tuples(
                    st.integers(min_value=-50, max_value=50),
                    st.integers(min_value=-50, max_value=50),
                ),
                max_size=30,
            )
        )
        def property_check(intervals: list[tuple[int, int]]) -> None:
            merged = merge_intervals(intervals)
            self.assertEqual(merged, sorted(merged))
            self.assertTrue(
                all(merged[index][1] + 1 < merged[index + 1][0] for index in range(len(merged) - 1))
            )
            original_points = {
                point
                for left, right in intervals
                for point in range(min(left, right), max(left, right) + 1)
            }
            merged_points = {point for left, right in merged for point in range(left, right + 1)}
            self.assertEqual(merged_points, original_points)

        property_check()


if __name__ == "__main__":
    unittest.main()
