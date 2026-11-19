"""llm-044: RoPE, relative positions, ALiBi and long-context limits.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Rotate a two-dimensional vector
# Rotate [1, 0] by pi/2 and check length preservation.
# Expected: approximately [0, 1]; norm 1.

# Exercise 2: Verify the relative dot-product identity
# Use q = [1, 2], k = [3, -1] and angles m = 0.3, n = 1.1.
# Expected: dot(Rm q, Rn k)=dot(q, R(n-m)k) within1e-12.

# Exercise 3: Inspect an ALiBi causal row
# Use zero content scores for query position 2, keys 0, 1, 2 and slope \(\log 2\).
# Expected: normalized weights [1/7, 2/7, 4/7].

# Exercise 4: Apply multi-frequency RoPE
# Use width 4, base 10000 and positions 0, 1 on two fixed vectors; inspect pair norms.
# Expected: frequencies 1 and 0.01; each pair norm preserved.

# Exercise 5: Catch a cache offset reset
# Encode the third key at position 2 and compare with mistakenly encoding it at position
# 0.
# Expected: correct incremental encoding matches full encoding; the reset differs.

# Exercise 6: Separate computability from extrapolation evidence
# Compute a finite encoding at position 1000000, then record that no trained-model quality
# was measured.
# Expected: finite vector; long_context_quality_verified=False; odd width rejected.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
