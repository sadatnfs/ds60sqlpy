"""llm-046: MHA, MQA, GQA and blockwise exact attention.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Count cache andprojection dimensions
# Usebatch1, time5, queryheads4, headwidth2, float32, andcompareKVheads4, 2, 1.
# Expected: rawKVbytes320, 160, 80; projection weights256, 192, 160 for modelwidth8 withoutbiases.

# Exercise 2: Verify grouped heads against an equivalent repeated-head oracle
# Use4queryheads and2KVheads; repeat eachKVhead twice only in the dense oracle.
# Expected: outputs agree within1e-12; shape(4, 3, 2).

# Exercise 3: Trace online softmax at extreme scores
# Combine scores1000, 999, 998 andvalues1, 3, 5 in blocks of 2.
# Expected: finite output equals a maximum-shifted dense calculation.

# Exercise 4: Compare several block sizes under causal masking
# Use five nonuniform query/key rows andcompareblock sizes1, 2, 3, 5 withdense attention.
# Expected: all outputs agree within1e-12; largest temporary score block does not exceed the chosen size.

# Exercise 5: Preserve a causal prefix under future changes
# Change only value rows3and4 andcomparethefirstthree online outputs.
# Expected: firstthree rows unchanged.

# Exercise 6: Reject invalid grouping andempty support
# Try4queryheads with 3KVheads, and anall-false attention row.
# Expected: both raiseValueError; no outputNaNs are accepted.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
