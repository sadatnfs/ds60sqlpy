"""mle-005: worked starting point; complete the guide's six changes."""

import numpy as np


def example_one():
    customers = np.arange(6)
    labels = np.array([0, 0, 0, 1, 1, 1])
    memory = dict(zip(customers, labels, strict=True))
    repeated_predictions = np.array([memory[int(c)] for c in customers])
    assert float(np.mean(repeated_predictions == labels)) == 1.0
    held_out = {1, 4}
    training = {int(c): int(y) for c, y in zip(customers, labels, strict=True) if c not in held_out}
    cold = np.array([training.get(c, 1) for c in sorted(held_out)])
    actual = labels[sorted(held_out)]
    assert float(np.mean(cold == actual)) == 0.5
    return {
        "repeated_entity_accuracy": 1.0,
        "unseen_entity_accuracy": 0.5,
        "target_population_changed": True,
    }


if __name__ == "__main__":
    print(example_one())

# TODO 1: State whether the target is known or unseen customers.
# TODO 2: Check both row identifiers and customer identifiers.
# TODO 3: Exclude labels that mature after the training cutoff.
# TODO 4: Describe where a decision threshold should be selected.
# TODO 5: Change the unseen-entity fallback and interpret the result.
# TODO 6: List the identities, clocks and selection decisions needed for reproduction.
