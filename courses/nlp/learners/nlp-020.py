LABELS = [[1, 1, -1], [0, -1, 0], [1, 0, -1], [-1, -1, -1]]
PROBABILITIES = [0.5, 0.6, 0.95, 0.1]
FAMILIES = ["a", "a", "b", "c"]


def weak_summary(labels):
    raise NotImplementedError("Keep coverage, conflict and aggregate votes separate")


def main():
    print("Weak-label and query-pool fixtures loaded. Preserve a separate gold evaluation set.")


if __name__ == "__main__":
    main()

# Exercise 1: Compute weak-label diagnostics. Calculate covered and conflicting rows in the supplied matrix. Expected: Coverage.75,overall conflict.25 and conflict among covered1/3.
# Exercise 2: Implement tie-aware voting. Aggregate the four rows without treating -1 as a class vote. Expected: Outputs[1,0,-1,-1].
# Exercise 3: Inspect source correlation. Compare votes[1,1,0] with collapsed source-family votes[1,0]. Expected: Majority1 becomes abstain, with a written explanation of duplicated evidence.
# Exercise 4: Rank uncertainty. Compute binary entropy for probabilities[.5,.6,.95,.1]. Expected: Top two uncertainty indices[0,1]; p=.5 has maximum entropy.
# Exercise 5: Enforce diversity and budget. Select two examples with families[a,a,b,c], at most one per family. Expected: Selected indices[0,3]; budget0 returns an empty batch.
# Exercise 6: Protect independent evaluation. Design a weak-label/active-review experiment with disjoint query and gold IDs. Expected: A written split and provenance ledger prevent reviewed pool cases from silently becoming the final acceptance set.
