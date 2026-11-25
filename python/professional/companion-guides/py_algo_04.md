# Dynamic Programming, State Design, and Reconstructable Decisions

**Stable ID:** `python-algo-04`

**Estimated time:** 150 minutes; split the reading and implementation across sessions when useful.

## Level and prerequisites

Intermediate. Direct catalog prerequisites: `python-algo-03`. This lesson deepens the named mechanism after the introductory track; it does not require a cloud account or download data.

## Learning objectives

By the end, you can name the state each dynamic program stores, write its recurrence, and choose a table update order that matches the problem: downward for 0/1 items, upward when reuse is allowed. You will rebuild an optimal plan from recorded choices and keep two edge cases apart: no solution, which returns `None`, and a zero target, which costs nothing.

## How to run this lesson

The [learner script](../lessons/py_algo_04.py) needs only the standard library. Its worked examples find that 6 needs two coins from `[1, 3, 4]` (3 + 3), where taking the largest coin first would use three, and show that a capacity-4 table updated upward lets a single weight-2 item of value 3 count twice, reporting 6 instead of 3.

The [Python study guide](../../STUDY-GUIDE.md) covers the browser classroom and this prepared-checkout run:

```sh
uv run --no-sync python python/professional/lessons/py_algo_04.py
```

After your attempt, compare the update direction in `knapsack_value` and the backpointer walk in `weighted_schedule` against the [runnable reference](../solutions/py_algo_04_solution.py). Use the [explanatory solutions](../solutions/py_algo_04_solutions.md) to check how `coin_plan` keeps the earlier denomination when two choices tie on coin count.

## Vocabulary and mental model

- **Dynamic programming:** Solving overlapping subproblems once and reusing their results according to a justified recurrence.

- **State:** The information needed to identify a subproblem without retaining irrelevant details of the path that reached it.

- **Recurrence:** A relationship expressing a state result through smaller or previously solved states.

- **Backpointer:** A recorded choice that permits reconstructing an actual optimal solution rather than reporting only its numerical score.

Dynamic programming begins with a question about information. What must be remembered so that future choices depend only on the current state? For a coin total, the remaining amount can be enough when coins are unlimited and order does not affect cost. For a 0/1 knapsack, which items remain available matters as well. Choosing too small a state loses constraints; choosing an unnecessarily large state creates wasted work.

A recurrence needs base cases and a valid evaluation order. The number of ways to climb zero steps is one: the empty sequence. That identity lets the recurrence for one-step and two-step moves work naturally. An impossible optimization state should be represented distinctly from a valid zero-cost solution, for example with infinity internally and None at the public boundary.

Minimum-coin change illustrates why a greedy rule is not always correct. For denominations 1,3,4 and amount 6, choosing the largest coin first gives 4+1+1, while 3+3 uses fewer coins. The dynamic program examines each possible final coin and reuses the optimal count for the remaining amount. Once the recurrence is justified, a backpointer records which coin produced an improvement.

Edit distance defines states for prefixes of two strings. Insertion, deletion and substitution connect each cell to three smaller prefix problems. Only the previous row is needed to compute the next row's score, reducing storage when the actual edit script is not required. If reconstruction is required, additional choices or a divide-and-conquer reconstruction strategy are necessary. Memory optimization changes which evidence remains available.

The 0/1 knapsack recurrence permits each item at most once. A one-dimensional capacity table must be updated from high capacity downward; otherwise the current item's newly updated state can be reused repeatedly, turning the algorithm into an unbounded-knapsack solver. This is a semantic bug hidden inside a loop direction.

Weighted interval scheduling combines ordering, binary search and dynamic programming. Sort jobs by end time, find each job's last compatible predecessor, then compare skipping the job with taking its value plus the optimal compatible prefix. Half-open intervals permit a job ending at another's start. The result includes selected job identities so compatibility and total value can be verified independently.

Complexity claims should identify the state space. Coin change and knapsack tables scale with the numeric amount or capacity, which can be enormous relative to its encoded bit length; this is called pseudopolynomial behavior. A correct recurrence can still be an impractical algorithm for a large state domain.

## Worked examples and syntax anatomy

### Example 1

```python
import math

coins = [1, 3, 4]
amount = 6
best = [0] + [math.inf] * amount
for total in range(1, amount + 1):
    best[total] = min((1 + best[total - coin] for coin in coins if coin <= total), default=math.inf)
assert best[6] == 2
assert best[6] < 1 + 1 + 1
print("Minimum coins for6:", best[6])
```

Each state asks about one amount, and choosing the final coin leaves a smaller amount whose optimal count is already known. The comparison with the three-coin greedy result demonstrates why looking only at the largest available denomination is insufficient.

### Example 2

```python
capacity = 4
weight = 2
value = 3
correct = [0] * (capacity + 1)
for available in range(capacity, weight - 1, -1):
    correct[available] = max(correct[available], value + correct[available - weight])
wrong = [0] * (capacity + 1)
for available in range(weight, capacity + 1):
    wrong[available] = max(wrong[available], value + wrong[available - weight])
assert correct[4] == 3 and wrong[4] == 6
print("One item used once:", correct[4], "ascending-loop reuse:", wrong[4])
```

Descending updates read the previous-item state for lower capacities. Ascending updates read a value already improved by the same item and use it twice. Both loops terminate and produce plausible numbers, so an explicit single-item capacity test is necessary.

## Exercises

1. **Define the empty-state identity.** Count ordered ways to reach steps using moves of one or two. Require a nonnegative non-Boolean integer. Use an iterative recurrence with constant retained state, returning one for zero steps.

**Expected:** Steps 0,1,2,5 return 1,1,2,8. Negative, True or a noninteger raises ValueError.

2. **Distinguish impossible from zero cost.** Find the fewest unlimited positive-integer coins needed for a nonnegative integer amount. Reject Boolean/noninteger/zero/negative coins and invalid amounts. Return None if impossible and zero for amount 0, including with no denominations.

**Expected:** Coins[1,3,4], amount 6 returns 2; [2,4], amount 3 returns None; [], amount 0 returns 0. A zero denomination raises ValueError.

3. **Reconstruct an optimal payment.** Return a sorted list of coins achieving the minimum count, or None if impossible. Use the same input rules as minimum_coins. Record improving choices, with ascending denominations considered first and no replacement on equal count.

**Expected:** [1,3,4], amount 6 returns [3,3], whose sum is 6 and length equals minimum_coins. Amount 0 returns [] and an unreachable odd amount with only even coins returns None.

4. **Design a prefix recurrence.** Compute unit-cost insertion, deletion and substitution edit distance for Python strings using only two rows of dynamic-programming state. Empty strings are valid. Treat Unicode code points as units and do not include a one-step transposition operation.

**Expected:** kitten to sitting costs 3; empty to abc costs 3; identical strings cost 0; ab to ba costs 2, not 1. Swapping arguments preserves the distance.

5. **Preserve the at-most-once constraint.** Compute maximum total nonnegative integer value for 0/1 items with positive integer weights and a nonnegative integer capacity. Require matching lengths and reject Boolean or invalid numbers. Use a one-dimensional table updated downward so each item is used at most once.

**Expected:** Weights[2,3,4], values[4,5,7], capacity 5 gives 9. One item weight 2, value 3 with capacity 4 gives 3, not 6. Empty items or zero capacity give 0.

6. **Combine binary search, recurrence and backpointers.** Choose nonoverlapping half-open jobs(start, end, value, id) maximizing nonnegative integer value. Require integer times with start<end, unique string IDs and nonnegative integer values. Sort by end, start, id, use compatible-prefix binary search, and skip on exact-value ties. Return value plus chosen IDs in time order.

**Expected:** Jobs(0,2,4, a),(2,4,4, b),(1,4,7, c) choose[a, b] with value 8. End==next start is compatible; an overlapping lower-value combination is excluded. Empty input gives (0,[]).

## Common mistakes and diagnosis

If an impossible coin amount returns an empty plan, distinguish unreachable infinity from the valid zero-amount base case. If knapsack value is too large for one item, inspect capacity-loop direction. If edit distance treats a swap as one operation, verify that the implementation has not silently changed to a transposition-aware metric. If a reconstructed schedule overlaps, inspect compatible-prefix endpoint ownership and backpointer indices. If a dynamic program is slow, count reachable states and transition choices before adding memoization to an incorrectly designed state.

## Self-check and retrieval

Trace `minimum_coins([1, 3, 4], 6)` through its table by hand and confirm `coin_plan` returns `[3, 3]`. Then check the edges: `minimum_coins([], 0)` is 0, `minimum_coins([2], 3)` is `None`, and `stair_paths(0)` is 1 because standing still is one way. For `weighted_schedule`, jobs `(1, 3)` and `(3, 5)` do not overlap, since intervals are half-open.

## Next steps

Next, [binary trees, tries, and structural invariants](py_algo_05.md) moves from tables indexed by amount or capacity to linked structures, where each node must keep an ordering or prefix property. The [professional track](../README.md) lists the other modules.

## Primary sources and official APIs

- [Python bisect for compatible-prefix boundaries](https://docs.python.org/3/library/bisect.html).

- [MIT OpenCourseWare, dynamic programming lectures](https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-fall-2011/pages/lecture-notes/).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning to coach me through python-algo-04: Dynamic Programming, State Design, and Reconstructable Decisions.
Read python/professional/companion-guides/py_algo_04.md and python/professional/lessons/py_algo_04.py. Direct prerequisites: python-algo-03.
Explain the vocabulary and mechanism at a beginner-friendly pace, then ask me to predict a concrete result before my attempt. Give one hint at a time, review my numerical or exception evidence, and ask retrieval questions in my own words. Do not read solutions/ until I request it or have made an honest attempt. Use only the prepared local Python environment and tiny offline inputs; preserve my saved work.
Done when all six contracts and their boundary cases have inspected evidence and I can explain why a tempting incorrect implementation fails.
```
