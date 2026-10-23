REFERENCE="service is not ready".split()
CANDIDATE="service is ready".split()

def clipped_precision(candidate,reference,n=1):
    raise NotImplementedError("Implement clipped counts and a declared empty policy")

def main():
    print("Overlap and contradiction fixtures loaded. Do not treat a high score as factual support.")

if __name__ == "__main__":
    main()

# Exercise 1: Implement clipped precision. Count unigram overlap for the repeated-the candidate. Expected: Precision .25, not1.
# Exercise 2: Derive the brevity penalty. Score the cat against the cat sat with maximum order2 and no smoothing. Expected: Both precisions1; BP and score exp(-.5).
# Exercise 3: Implement longest common subsequence. Compute LCS and P/R/F1 for the readiness minimal pair. Expected: LCS3, precision1, recall.75, F1=6/7.
# Exercise 4: Document semantic failure. Write a source-support judgment for the same minimal pair. Expected: The candidate contradicts readiness; a high overlap score is retained alongside the failure label.
# Exercise 5: Aggregate at the right unit. Use family a outcomes[true,false] and family b outcome[false]. Expected: Family rates[.5,0] and equal-family mean.25; explain why row mean1/3 answers a different weighting question.
# Exercise 6: Specify an evaluation packet. Design a rubric and record for a source-grounded generated summary. Expected: Record includes task/source/version/output/atomic support labels/metric config/rater or judge identity and an abstention case.
