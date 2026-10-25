"""cuda-063: CPU reference only, not CUDA execution."""

from fractions import Fraction

filtered = [Fraction(2), Fraction(14, 3), Fraction(4)]
energy = sum(x * x for x in filtered)
assert energy == Fraction(376, 9)
print({"exact_filtered": [str(x) for x in filtered], "post_filter_energy": str(energy)})
