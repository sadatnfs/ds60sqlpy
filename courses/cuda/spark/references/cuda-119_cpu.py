"""Independent CPU reference with deterministic contract assertions."""

from fractions import Fraction

gpu = Fraction(1)
request = Fraction(1, 4)
slots = int(gpu / request)
plugin_limit = 2
active = min(slots, plugin_limit)
assert slots == 4 and active == 2
print("CPU resource model:", slots, "scheduled shares;", active, "GPU-active bound")
