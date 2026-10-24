import numpy as np

TRAIN = [
    "urgent outage",
    "urgent incident",
    "outage incident",
    "thanks resolved",
    "thanks update",
    "resolved update",
]
LABELS = np.array([1, 1, 1, 0, 0, 0])


def stable_sigmoid(score):
    raise NotImplementedError("Exercise 1: implement and explain the stable calculation")


def main():
    print("Six local training messages are ready. Implement the six guide tasks in this pad.")


if __name__ == "__main__":
    main()

# Exercise 1: Trace log odds. Implement a stable sigmoid and evaluate the stated two-feature score. Expected: Logit 2.5 and probability approximately 0.92414182; finite outputs at logits +/-1000.
# Exercise 2: Freeze the vocabulary. Fit the six-message classifier and transform escalation urgent without refitting. Expected: Exactly six learned vocabulary terms; escalation absent; two stated probes predicted [1,0].
# Exercise 3: Compare regularization. Fit the same corpus with C=0.1 and C=10 using the same solver/settings. Expected: The C=0.1 coefficient norm is smaller; record both norms and do not call either universally best.
# Exercise 4: Separate a threshold. Apply thresholds 0.5 and 0.3 to [0.2,0.4,0.8] with >= semantics. Expected: Actions [false,false,true] and [false,true,true].
# Exercise 5: Inspect probability quality. Compute both Brier scores for the four labels and reject probabilities outside [0,1]. Expected: Scores 0.41 and 0.26; invalid 1.2 raises ValueError.
# Exercise 6: Expose negation loss. Compare frozen unigram features for urgent and not urgent, then inspect an isolated bigram representation. Expected: The frozen unigram rows match; a separately fitted demonstration contains the not urgent bigram.
