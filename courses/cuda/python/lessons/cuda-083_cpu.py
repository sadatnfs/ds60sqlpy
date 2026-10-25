"""Editable CPU worked example. This does not execute or simulate a GPU.

Complete the six guide exercises separately; modify one bounded case at a time.
"""


def validate_contract(count, itemsize, allocated):
    if count < 0 or itemsize <= 0 or allocated < count * itemsize:
        raise ValueError("invalid buffer contract")


validate_contract(5, 4, 20)
try:
    validate_contract(5, 8, 20)
except ValueError:
    print("CPU ABI model: insufficient float64 storage rejected")
else:
    raise AssertionError("expected rejection")
