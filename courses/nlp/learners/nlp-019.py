A = [1, 1, 0, 0, 1, 0]
B = [1, 0, 0, 0, 1, 1]


def agreement(a, b):
    raise NotImplementedError(
        "Compute observed and marginal-expected agreement with an undefined policy"
    )


def main():
    print("Independent ratings loaded. Preserve them when adding adjudication.")


if __name__ == "__main__":
    main()

# Exercise 1: Define the annotation unit. Write a binary urgency rubric with a source-context boundary and one ambiguous case. Expected: A concrete unit, two label definitions, abstention/review rule and a counterexample.
# Exercise 2: Calculate agreement manually. Compute raw agreement, marginal expected agreement and kappa for the six-item arrays. Expected: 2/3,1/2,1/3 respectively, matching the library.
# Exercise 3: Explain the imbalanced case. Calculate the hundred-item prevalence counterexample. Expected: Raw agreement.98 but kappa slightly below zero.
# Exercise 4: Retain soft labels. Compute proportions and entropy for the three three-rater rows. Expected: Soft labels[2/3,1,0]; positive entropy only for the disputed row.
# Exercise 5: Preserve adjudication evidence. Create a final-label record without changing the independent ratings. Expected: Original(1,1,0),final label1,rationale and item identity retained.
# Exercise 6: Handle undefined agreement. Evaluate two identical all-positive arrays and design a follow-up annotation sample. Expected: Raw agreement1,kappa undefined/None; follow-up includes rare and ambiguous categories.
