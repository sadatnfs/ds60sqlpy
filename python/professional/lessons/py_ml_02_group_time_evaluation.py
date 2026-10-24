"""python-ml-02: Leakage-Resistant Evaluation Across Groups and Time.

Read ../companion-guides/py_ml_02_group_time_evaluation.md before attempting the exercises.
The example runs; unfinished exercise functions raise NotImplementedError.
Keep solutions separate until you have attempted and checked the contract.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass(frozen=True)
class Observation:
    event_id: str
    entity_id: str
    observed_at: datetime
    feature_available_at: datetime
    label_available_at: datetime
    feature: float
    target: float


def validate_observations(rows: list[Observation]) -> None:
    """TODO: validate identities, awareness, availability, and finite numeric values."""
    raise NotImplementedError("complete validate_observations")


def group_split(
    rows: list[Observation], held_out: set[str]
) -> tuple[list[Observation], list[Observation]]:
    """TODO: hold out entire entities and reject empty train/test selections."""
    raise NotImplementedError("complete group_split")


def time_split(
    rows: list[Observation],
    cutoff: datetime,
    gap: timedelta = timedelta(0),
    end: datetime | None = None,
) -> tuple[list[Observation], list[Observation], int]:
    """TODO: permitted past training, half-open future validation, excluded count."""
    raise NotImplementedError("complete time_split")


def fit_mean(values: list[float]) -> float:
    """TODO: fit a finite mean from nonempty permitted values."""
    raise NotImplementedError("complete fit_mean")


def mae(actual: list[float], predicted: list[float]) -> float:
    """TODO: validate dimensions/domain and compute mean absolute error."""
    raise NotImplementedError("complete mae")


def evaluate_baseline(
    training: list[Observation], validation: list[Observation]
) -> dict[str, object]:
    """TODO: fit only training targets, audit ids, and score validation targets."""
    raise NotImplementedError("complete evaluate_baseline")


if __name__ == "__main__":
    print("Worked train-only mean:", (2 + 4) / 2)
    print("Worked held-out centered value:", 100 - (2 + 4) / 2)
    print("TODO: complete six boundaries and eight exercises")

# Exercise 1. Validate availability before splitting
# Prompt: Implement `validate_observations` to reject duplicate ids, naive timestamps,
# nonfinite numbers, features available after observation, and labels available before
# observation.
# Verify: Each rule has a named test that captures ValueError. Equality at feature availability
# and equality at label availability both complete validation without exceptions.

# Exercise 2. Hold out whole entities
# Prompt: Implement `group_split(rows, held_out)` using explicit entity ids. Preserve source
# order and require nonempty training and validation sets.
# Verify: Assert validation ids [A1, A2], training ids [B1, C1], and an empty entity-set
# intersection when A is held out; unknown or all-inclusive holdouts raise ValueError.

# Exercise 3. Enforce delayed-label time policy
# Prompt: Implement `time_split` with aware cutoff, nonnegative gap, optional end, and strict
# label availability before cutoff minus gap.
# Verify: A label exactly at cutoff minus gap is excluded; a label one second earlier is
# eligible when observation is also earlier than cutoff.

# Exercise 4. Fit a transformation only on training
# Prompt: Implement `fit_mean` and use it to center feature values. Train on [2, 4] and
# transform validation value 100 with the fitted mean.
# Verify: Training mean is 3, centered train values are -1 and 1, and centered validation is 97.
# Adding validation before fitting would change the mean and fails the test.

# Exercise 5. Calculate a transparent baseline
# Prompt: Implement `mae` and `evaluate_baseline` with the permitted training target mean. Use
# train targets [0, 0] and validation target [100].
# Verify: The fitted prediction is 0 and MAE is 100; empty sets, unequal metric input lengths,
# and nonfinite values raise ValueError.

# Exercise 6. Rehearse walk-forward windows
# Prompt: Create two consecutive one-day validation windows over a tiny aware-timestamp
# fixture. Refit the baseline using only each fold eligible past.
# Verify: An observation at the shared boundary appears in the second validation window only;
# fold reports retain ids and counts for independent inspection.

# Exercise 7. Demonstrate a misleading improvement
# Prompt: Intentionally fit the baseline mean on train plus validation in a scratch
# experiment. Compare its score with the valid [0,0] versus [100] case.
# Verify: The leaked mean is about 33.333 and test error about 66.667, lower than 100; your note
# identifies target leakage rather than model progress.

# Exercise 8. Transfer to the deployment question
# Prompt: Write policies for returning-customer next-day predictions and new-customer next-day
# predictions. Explain which group/time constraints each needs and what a final test set
# protects.
# Verify: The second policy explicitly checks both entity disjointness and future availability.
# Both report excluded coverage and reserve evaluation data outside policy selection.
