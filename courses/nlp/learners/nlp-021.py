ROWS = [
    {"id": "a1", "family": "a", "time": 1},
    {"id": "a2", "family": "a", "time": 2},
    {"id": "b1", "family": "b", "time": 1},
    {"id": "b2", "family": "b", "time": 3},
    {"id": "c1", "family": "c", "time": 3},
]


def split_rows(rows, cutoff):
    raise NotImplementedError("Return train, future-new-family test and exclusion ledger")


def main():
    print("Family/time fixtures loaded. State the generalization target before splitting.")


if __name__ == "__main__":
    main()

# Exercise 1: Define normalized identity. Hash the two router variants after the declared normalization. Expected: Equal normalized hashes while original strings remain unchanged.
# Exercise 2: Expose a near-duplicate trap. Compute token-set Jaccard for ready versus not ready. Expected: Similarity.75 despite a contradictory status claim.
# Exercise 3: Build the combined split. Apply cutoff2 and exclude future families already seen in training. Expected: Train[a1,a2,b1],test[c1],excluded[b2].
# Exercise 4: Assert pipeline boundaries. Check temporal ordering and family disjointness, then list train-only learned transforms. Expected: Both invariants hold; vocabulary/IDF/calibration/tuning are explicitly inside training/development.
# Exercise 5: Compute paired family differences. Average the supplied differences by family and compare with flattened rows. Expected: Equal-family2/15 versus row-weighted.2.
# Exercise 6: Bootstrap and qualify uncertainty. Run the seeded family bootstrap twice and explain the small-family limit. Expected: Identical quantiles under the same seed; support within[-.1,.3]; no strong population claim from three families.
