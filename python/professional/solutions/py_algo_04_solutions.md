# python-algo-04: Explained reference solutions

These answers implement the contracts in [Dynamic Programming, State Design, and Reconstructable Decisions](../companion-guides/py_algo_04.md). Compare after an attempt. The [executable reference](py_algo_04_solution.py) contains the complete implementations and assertions. Each answer explains the mechanism, not just the final value.

## Exercises and reasoning

### Exercise 1: Define the empty-state identity

Count ordered ways to reach steps using moves of one or two. Require a nonnegative non-Boolean integer. Use an iterative recurrence with constant retained state, returning one for zero steps.

**Expected:** Steps 0,1,2,5 return 1,1,2,8. Negative, True or a noninteger raises ValueError.

```python
def stair_paths(steps: int) -> int:
    if isinstance(steps,bool) or not isinstance(steps,int) or steps<0:
        raise ValueError("Expected a nonnegative integer step count")
    previous,current=1,1
    for _ in range(steps):
        previous,current=current,previous+current
    return previous
```

Every nonempty route ends with a one-step or two-step move, partitioning routes into the two predecessor states. The empty route counts once so a move directly reaching the target is included. Only two consecutive counts are needed, making retained state constant even though Python integers grow with the result magnitude. The recurrence check across many small states tests the mathematical structure independently of a few memorized values.

```python
assert [stair_paths(n) for n in [0,1,2,5]]==[1,1,2,8]
for n in range(2,20):
    assert stair_paths(n)==stair_paths(n-1)+stair_paths(n-2)
expect_value_error(lambda:stair_paths(-1))
expect_value_error(lambda:stair_paths(True))
```

### Exercise 2: Distinguish impossible from zero cost

Find the fewest unlimited positive-integer coins needed for a nonnegative integer amount. Reject Boolean/noninteger/zero/negative coins and invalid amounts. Return None if impossible and zero for amount 0, including with no denominations.

**Expected:** Coins[1,3,4], amount 6 returns 2; [2,4], amount 3 returns None; [], amount 0 returns 0. A zero denomination raises ValueError.

```python
def minimum_coins(coins: list[int], amount: int) -> int | None:
    if isinstance(amount,bool) or not isinstance(amount,int) or amount<0 or any(isinstance(c,bool) or not isinstance(c,int) or c<=0 for c in coins):
        raise ValueError("Expected positive integer coins and nonnegative amount")
    best=[0]+[math.inf]*amount
    for total in range(1,amount+1):
        best[total]=min((1+best[total-coin] for coin in coins if coin<=total),default=math.inf)
    return None if math.isinf(best[amount]) else int(best[amount])
```

Infinity represents an amount not yet reachable and remains infinite when an impossible predecessor is extended. Zero is reserved for the valid empty payment. Iterating amounts upward is correct here because coins are unlimited and each predecessor amount is smaller. Duplicate denominations do not change the optimum, though removing them can reduce redundant work. The returned None preserves impossibility rather than pretending an empty coin list pays a positive amount.

```python
assert minimum_coins([1,3,4],6)==2 and minimum_coins([2,4],3) is None
assert minimum_coins([],0)==0 and minimum_coins([],2) is None
expect_value_error(lambda:minimum_coins([0,1],2))
expect_value_error(lambda:minimum_coins([True],2))
```

### Exercise 3: Reconstruct an optimal payment

Return a sorted list of coins achieving the minimum count, or None if impossible. Use the same input rules as minimum_coins. Record improving choices, with ascending denominations considered first and no replacement on equal count.

**Expected:** [1,3,4], amount 6 returns [3,3], whose sum is 6 and length equals minimum_coins. Amount 0 returns [] and an unreachable odd amount with only even coins returns None.

```python
def coin_plan(coins: list[int], amount: int) -> list[int] | None:
    minimum_coins(coins,amount)
    denominations=sorted(set(coins));best=[0]+[math.inf]*amount;choice=[None]*(amount+1)
    for total in range(1,amount+1):
        for coin in denominations:
            if coin<=total and 1+best[total-coin]<best[total]:
                best[total]=1+best[total-coin];choice[total]=coin
    if math.isinf(best[amount]):
        return None
    result=[];remaining=amount
    while remaining:
        coin=choice[remaining]
        assert coin is not None
        result.append(coin);remaining-=coin
    return sorted(result)
```

The score table alone cannot identify which coins produced the optimum, so a choice is stored whenever a strictly better count is found. Following choices decreases the remaining amount until the base state. Sorting the reconstructed multiset is a presentation policy because payment order is irrelevant to this objective. The assertions verify feasibility, optimal count and impossible-state behavior separately rather than trusting only the printed plan.

```python
plan=coin_plan([4,1,3],6)
assert plan==[3,3] and sum(plan)==6 and len(plan)==minimum_coins([1,3,4],6)
assert coin_plan([],0)==[] and coin_plan([2,4],3) is None
expect_value_error(lambda:coin_plan([-1,2],3))
```

### Exercise 4: Design a prefix recurrence

Compute unit-cost insertion, deletion and substitution edit distance for Python strings using only two rows of dynamic-programming state. Empty strings are valid. Treat Unicode code points as units and do not include a one-step transposition operation.

**Expected:** kitten to sitting costs 3; empty to abc costs 3; identical strings cost 0; ab to ba costs 2, not 1. Swapping arguments preserves the distance.

```python
def edit_distance(left: str, right: str) -> int:
    if len(right)>len(left):
        left,right=right,left
    previous=list(range(len(right)+1))
    for i,a in enumerate(left,1):
        current=[i]
        for j,b in enumerate(right,1):
            current.append(min(current[j-1]+1,previous[j]+1,previous[j-1]+(a!=b)))
        previous=current
    return previous[-1]
```

Each state concerns prefixes, and the three candidate transitions correspond to insertion, deletion and substitution or match. The first row and column encode conversion to or from an empty prefix. Only the preceding row is needed for the score, so placing the shorter string on the column axis bounds retained memory by its length. Code-point distance differs from user-perceived grapheme distance; normalization and linguistic tokenization are separate domain decisions.

```python
assert edit_distance("kitten","sitting")==3 and edit_distance("","abc")==3
assert edit_distance("same","same")==0 and edit_distance("ab","ba")==2
assert edit_distance("abc","ax")==edit_distance("ax","abc")
```

### Exercise 5: Preserve the at-most-once constraint

Compute maximum total nonnegative integer value for 0/1 items with positive integer weights and a nonnegative integer capacity. Require matching lengths and reject Boolean or invalid numbers. Use a one-dimensional table updated downward so each item is used at most once.

**Expected:** Weights[2,3,4], values[4,5,7], capacity 5 gives 9. One item weight 2, value 3 with capacity 4 gives 3, not 6. Empty items or zero capacity give 0.

```python
def knapsack_value(weights: list[int], values: list[int], capacity: int) -> int:
    if isinstance(capacity,bool) or not isinstance(capacity,int) or capacity<0 or len(weights)!=len(values) or any(isinstance(w,bool) or not isinstance(w,int) or w<=0 for w in weights) or any(isinstance(v,bool) or not isinstance(v,int) or v<0 for v in values):
        raise ValueError("Expected valid 0/1 items and capacity")
    best=[0]*(capacity+1)
    for weight,value in zip(weights,values):
        for available in range(capacity,weight-1,-1):
            best[available]=max(best[available],value+best[available-weight])
    return best[capacity]
```

The state means best value using the items processed so far within an available capacity. Descending capacity order ensures each transition reads the state before the current item was added. Ascending updates would solve a different unlimited-reuse problem. The algorithm takes O(number_of_items*capacity) time and O(capacity) memory, so a very large numeric capacity can be impractical despite a short input representation.

```python
assert knapsack_value([2,3,4],[4,5,7],5)==9
assert knapsack_value([2],[3],4)==3 and knapsack_value([],[],4)==0
assert knapsack_value([2],[3],0)==0
expect_value_error(lambda:knapsack_value([0],[3],4))
expect_value_error(lambda:knapsack_value([2],[3,4],4))
```

### Exercise 6: Combine binary search, recurrence and backpointers

Choose nonoverlapping half-open jobs(start, end, value, id) maximizing nonnegative integer value. Require integer times with start<end, unique string IDs and nonnegative integer values. Sort by end, start, id, use compatible-prefix binary search, and skip on exact-value ties. Return value plus chosen IDs in time order.

**Expected:** Jobs(0,2,4, a),(2,4,4, b),(1,4,7, c) choose[a, b] with value 8. End==next start is compatible; an overlapping lower-value combination is excluded. Empty input gives (0,[]).

```python
def weighted_schedule(jobs: list[tuple[int, int, int, str]]) -> tuple[int, list[str]]:
    seen=set()
    for start,end,value,ident in jobs:
        if any(isinstance(x,bool) or not isinstance(x,int) for x in [start,end,value]) or start>=end or value<0 or not isinstance(ident,str) or ident in seen:
            raise ValueError("Expected positive intervals, nonnegative values and unique string IDs")
        seen.add(ident)
    ordered=sorted(jobs,key=lambda job:(job[1],job[0],job[3]));ends=[job[1] for job in ordered]
    best=[0]*(len(ordered)+1);take=[False]*(len(ordered)+1);previous=[0]*(len(ordered)+1)
    for i,(start,end,value,ident) in enumerate(ordered,1):
        compatible=bisect_right(ends,start,0,i-1)
        previous[i]=compatible;candidate=value+best[compatible]
        if candidate>best[i-1]:
            best[i]=candidate;take[i]=True
        else:
            best[i]=best[i-1]
    chosen=[];i=len(ordered)
    while i:
        if take[i]:
            chosen.append(ordered[i-1][3]);i=previous[i]
        else:
            i-=1
    return best[-1],list(reversed(chosen))
```

Sorting by end time makes all jobs compatible with a candidate form a prefix of earlier jobs. bisect_right includes jobs ending exactly at the candidate start, matching half-open semantics. The recurrence compares taking the candidate plus that optimal prefix against skipping it. Backpointers recover actual IDs, and separate checks prove their intervals do not overlap and their values sum to the reported optimum. The explicit skip-on-tie policy makes equally valuable schedules deterministic.

```python
jobs=[(0,2,4,"a"),(2,4,4,"b"),(1,4,7,"c")]
value,chosen=weighted_schedule(jobs)
assert (value,chosen)==(8,["a","b"])
selected=[next(job for job in jobs if job[3]==ident) for ident in chosen]
assert sum(job[2] for job in selected)==value and all(a[1]<=b[0] for a,b in zip(selected,selected[1:]))
assert weighted_schedule([])==(0,[])
expect_value_error(lambda:weighted_schedule([(0,0,1,"a")]))
expect_value_error(lambda:weighted_schedule([(0,1,1,"a"),(2,3,1,"a")]))
```

## Verification and interpretation

Run `python python/professional/solutions/py_algo_04_solution.py` from the repository root with the prepared interpreter. The code checks normal inputs and explicit edge cases before printing its success line. Assertions are the evidence; the printed sentence alone is not. The helper `expect_value_error` requires an actual `ValueError` and fails if a function silently accepts an invalid input. Inspect each function's mutation and ordering behavior as part of its contract.
