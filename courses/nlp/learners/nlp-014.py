import numpy as np

VALUES = np.array([[1.0, 2.0], [3.0, 4.0], [100.0, 100.0]])
MASK = np.array([True, True, False])


def masked_mean(values, mask):
    raise NotImplementedError("Implement the valid-position denominator")


def main():
    print("Pooling and score fixtures are ready. Do not download or claim a pretrained encoder.")


if __name__ == "__main__":
    main()

# Exercise 1: Implement masked mean. Average the three-row fixture using only the two valid positions. Expected: [2,3]; all-padding input raises ValueError.
# Exercise 2: Normalize nonzero vectors. Pool and normalize the authored car/repair and automobile/repair sequences. Expected: Each result has unit norm and their similarity exceeds the dog/pet alternative.
# Exercise 3: Preserve the order counterexample. Compare dog bites person with person bites dog under static mean pooling. Expected: Exactly matching pooled vectors despite different role meaning.
# Exercise 4: Derive contrastive loss. Compute row-wise loss for scores[[3,1],[1,3]] at temperature1. Expected: Average log(1+exp(-2)), approximately .126928.
# Exercise 5: Change temperature and candidate semantics. Repeat at temperature.5 and explain a false-negative document case. Expected: Lower numeric loss on the fixed correctly ordered fixture; written warning that a valid alternative labeled negative changes the learning target.
# Exercise 6: Specify a retrieval handoff. Write a result record for a retrieved passage and reject an unknown-token query in the toy encoder. Expected: Record contains source identity/version/text span/score; unsupported token raises instead of inventing an embedding.
