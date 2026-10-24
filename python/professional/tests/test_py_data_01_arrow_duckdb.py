"""Tests for the python-data-01 reference implementation."""

from __future__ import annotations

import importlib.util
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

from python.professional.solutions.py_data_01_arrow_duckdb_solution import (
    FIXTURE,
    load_sales,
    parse_nullable_text,
    partition_directory,
    query_parquet_with_duckdb,
    summarize_stdlib,
    summarize_with_csv_fallback,
    write_parquet_round_trip,
    write_partitioned_csv,
)


class CsvFallbackTests(unittest.TestCase):
    def test_explicit_csv_schema_preserves_values_and_nulls(self) -> None:
        sales = load_sales()
        summary = summarize_stdlib()

        self.assertEqual(len(sales), 6)
        self.assertEqual(summary.row_count, 6)
        self.assertEqual(summary.total_revenue, Decimal("114.60"))
        self.assertEqual(summary.null_note_count, 3)
        self.assertEqual(summary.regions, ("north", "south", "west"))
        self.assertIsNone(parse_nullable_text("  "))

    def test_csv_fallback_has_the_same_aggregate_contract(self) -> None:
        summary = summarize_with_csv_fallback()

        self.assertIn(summary.engine, {"stdlib-csv", "pandas-csv"})
        self.assertEqual(summary.total_revenue, Decimal("114.60"))
        self.assertEqual(summary.null_note_count, 3)

    def test_partition_paths_are_bounded_and_deterministic(self) -> None:
        self.assertEqual(partition_directory("north-2"), "region=north-2")
        for unsafe in ("", "../north", "North", "north/west"):
            with self.subTest(unsafe=unsafe), self.assertRaises(ValueError):
                partition_directory(unsafe)

        with tempfile.TemporaryDirectory(prefix="ds60-partition-test-") as directory:
            root = Path(directory)
            paths = write_partitioned_csv(load_sales(FIXTURE), root)
            self.assertEqual(
                [path.parent.name for path in paths],
                ["region=north", "region=south", "region=west"],
            )
            self.assertTrue(all(path.is_file() for path in paths))


@unittest.skipUnless(
    all(importlib.util.find_spec(name) is not None for name in ("pyarrow", "duckdb")),
    "optional PyArrow and DuckDB packages are not installed",
)
class ColumnarIntegrationTests(unittest.TestCase):
    def test_parquet_schema_and_duckdb_plan_are_observed(self) -> None:
        with tempfile.TemporaryDirectory(prefix="ds60-parquet-test-") as directory:
            path = Path(directory) / "sales.parquet"
            proof = write_parquet_round_trip(load_sales(), path)
            observation = query_parquet_with_duckdb(path, minimum_units=2)

            self.assertEqual(proof.row_count, 6)
            self.assertEqual(proof.null_note_count, 3)
            self.assertEqual(proof.schema_before, proof.schema_after)
            self.assertEqual(
                observation.rows,
                (
                    ("north", Decimal("28.600")),
                    ("south", Decimal("56.000")),
                    ("west", Decimal("12.000")),
                ),
            )
            self.assertTrue(observation.filter_visible, observation.plan)
            self.assertTrue(observation.projections_visible, observation.plan)


if __name__ == "__main__":
    unittest.main()
