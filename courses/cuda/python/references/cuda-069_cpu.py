"""Independent CPU reference with deterministic contract assertions."""

import random

rng = random.Random(7)
state = rng.getstate()
first = [rng.random() for _ in range(4)]
second = [rng.random() for _ in range(4)]
rng.setstate(state)
assert first == [rng.random() for _ in range(4)]
assert first != second
print("CPU RNG reference: restored batch matches; continued batch differs")
