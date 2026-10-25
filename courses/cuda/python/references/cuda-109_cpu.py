"""Independent CPU reference with deterministic contract assertions."""


def accepted(batch, sequence):
    return 1 <= batch <= 8 and 1 <= sequence <= 32


assert accepted(1, 32)
assert not accepted(9, 16)
assert not accepted(2, 0)
print("CPU deployment contract: supported shapes accepted; invalid shapes rejected")
