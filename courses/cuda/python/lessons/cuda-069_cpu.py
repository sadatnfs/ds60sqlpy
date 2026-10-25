"""Editable CPU worked example. This does not execute or simulate a GPU.

Complete the six guide exercises separately; modify one bounded case at a time.
"""

import random

rng = random.Random(7)
state = rng.getstate()
first = [rng.random() for _ in range(4)]
second = [rng.random() for _ in range(4)]
rng.setstate(state)
assert first == [rng.random() for _ in range(4)]
assert first != second
print("CPU RNG reference: restored batch matches; continued batch differs")
