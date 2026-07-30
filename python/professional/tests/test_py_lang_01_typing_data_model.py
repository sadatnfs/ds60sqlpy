"""Tests for python-lang-01."""

from __future__ import annotations

import unittest

from python.professional.solutions.py_lang_01_typing_data_model_solution import (
    ApiRecord,
    Batches,
    Customer,
    Handler,
    Named,
    SequenceReader,
    Transaction,
    UpperHandler,
    UserCreated,
    describe_event,
    parse_scalar,
)


class TypingDataModelTests(unittest.TestCase):
    def test_overloads_match_runtime_behavior(self) -> None:
        self.assertEqual(parse_scalar("12", "int"), 12)
        self.assertIs(parse_scalar("true", "bool"), True)
        self.assertEqual(parse_scalar("  keep  ", "text"), "  keep  ")
        with self.assertRaises(ValueError):
            parse_scalar("yes", "bool")

    def test_typed_event_uses_discriminant(self) -> None:
        event = UserCreated(
            kind="user_created",
            user_id="u1",
            email_verified=False,
        )
        self.assertEqual(describe_event(event), "user u1 created (unverified)")

    def test_generic_iterator_obeys_protocol(self) -> None:
        batches = Batches(["a", "b", "c"], 2)
        self.assertIs(iter(batches), batches)
        self.assertEqual(next(batches), ("a", "b"))
        self.assertEqual(next(batches), ("c",))
        with self.assertRaises(StopIteration):
            next(batches)

    def test_context_manager_commits_or_rolls_back(self) -> None:
        committed = ["a"]
        with Transaction(committed) as transaction:
            transaction.append("b")
        self.assertEqual(committed, ["a", "b"])

        rolled_back = ["a"]
        with self.assertRaises(RuntimeError), Transaction(rolled_back) as transaction:
            transaction.append("never")
            raise RuntimeError("abort")
        self.assertEqual(rolled_back, ["a"])

    def test_descriptor_supports_class_and_instance_access(self) -> None:
        customer = Customer("  Ada  ")
        self.assertEqual(customer.name, "Ada")
        self.assertIsInstance(customer, Named)
        self.assertEqual(Customer.name.__class__.__name__, "NonBlankText")
        with self.assertRaises(ValueError):
            customer.name = " "

    def test_mro_and_registration_are_visible(self) -> None:
        self.assertEqual(ApiRecord().label(), "json:audit:record")
        self.assertIs(Handler.registry["upper"], UpperHandler)
        self.assertEqual(UpperHandler().handle("mixed"), "MIXED")

    def test_covariant_reader_returns_more_specific_value(self) -> None:
        reader = SequenceReader(["alpha"])
        self.assertEqual(reader.get(0), "alpha")


if __name__ == "__main__":
    unittest.main()
