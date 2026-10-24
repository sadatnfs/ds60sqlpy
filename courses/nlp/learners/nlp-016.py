TARGET = ["repair"]
SENTENCES = ["The service is unavailable.", "A repair is scheduled."]


def shifted_targets(tokens):
    raise NotImplementedError("Separate decoder input from prediction targets")


def main():
    print(
        "Sequence and source fixtures loaded. Label the search table and extraction baseline honestly."
    )


if __name__ == "__main__":
    main()

# Exercise 1: Build teacher-forced inputs. Implement target shifting for [repair] and empty raw output. Expected: [BOS,repair] versus[repair,EOS]; empty becomes[BOS] versus[EOS].
# Exercise 2: Trace cross-attention dimensions. Compute the one-query, two-source weighted output. Expected: Weights sum to one; output[10p,20(1-p)] with p=sigmoid(1/sqrt2).
# Exercise 3: Mask source padding. Mark the second source invalid and repeat the calculation. Expected: Output exactly[10,0]; an all-invalid source raises.
# Exercise 4: Expose greedy search failure. Run width-one and width-two bounded search on the authored table. Expected: Greedy tea,EOS probability.3; beam coffee,EOS probability.4.
# Exercise 5: Preserve extractive provenance. Select a sentence for service and test an unsupported refund query. Expected: Return index0 and the unchanged unavailable sentence; refund returns None.
# Exercise 6: Explain generation error propagation. Describe what changes after an incorrect first generated token and how a summary can reverse a qualification. Expected: A concrete account separates teacher-forced loss, autoregressive rollout, search score and factual support.
