# java-020: explanatory solutions

Open after an attempt or an explicit solution reveal. The executable reference runs the six exercise checks together as `Main.java`. The guide contains independent worked examples, while this file explains the choices and failure cases in the complete answer.

## Mechanism review

Algorithms connect a problem contract to a sequence of operations and invariants. Binary search relies on sorted input and repeatedly narrows a half-open interval containing the possible answer. Stable sorting preserves relative order among equal keys,which matters when records already have a meaningful prior order. Recursion solves a problem through smaller instances and needs a base case;memoization avoids recomputing repeated subproblems. Dynamic programming makes those dependencies explicit in a table. The coin-change fixture shows why a locally greedy choice can fail even when a valid combination exists.

**Binary-search invariant:** The relationship preserved while narrowing a sorted search interval.

**Stable sort:** A sort preserving input order among equal sort keys.

**Dynamic programming:** Reusing solved subproblems according to explicit dependencies.

## Reading the reference

A lower-bound search returns the first index whose value is at least the target,orlength if none qualifies. The invariant keeps all earlier discarded positions below the target and all later discarded positions at least the target. A dynamic-programming tabledp[amount] stores the minimum coin count for that exact amount,withdp[0]=0 and an unreachable sentinel. Each transition considers a smaller amount and one added coin.

## Exercise 1: Find the first duplicate boundary

Task: RunlowerBound on1,2,2,5 withtarget2 andtarget6.

Returning the first qualifying position gives a precise duplicate policy. An arbitrary matching index would satisfy a different search contract.

```java
int[] sorted={1,2,2,5};assert lowerBound(sorted,2)==1 && lowerBound(sorted,6)==4;
```

**Expected:** indices1 and4.

**Verify:** Compare the program values or named exception with indices1 and4. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 2: Handle empty and outside searches

Task: Search an empty array and a target below the first element.

The half-open interval starts empty for an empty input. The result is an insertion position,not necessarily the index of an existing match.

```java
assert lowerBound(new int[0],7)==0;
assert lowerBound(sorted,0)==0;
```

**Expected:** both return0.

**Verify:** Compare the program values or named exception with both return0. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 3: Preserve stable ties

Task: Sort recordsa2,b1,c2 by key only and inspect the equal-key order.

The two key2 records retain their originala-before-c order. Adding an explicit secondary comparator would intentionally define a different tie rule.

```java
List<Item> items=new ArrayList<>(List.of(new Item("a",2),new Item("b",1),new Item("c",2)));
items.sort(Comparator.comparingInt(Item::key));
assert items.stream().map(Item::id).toList().equals(List.of("b","a","c"));
```

**Expected:** IDs b,a,c.

**Verify:** Compare the program values or named exception with IDs b,a,c. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 4: Solve a greedy counterexample

Task: Find minimum coins foramount6 usingcoins1,3,4.

The best first coin does not necessarily belong to the globally best solution. The table compares all valid smaller-amount transitions.

```java
assert minimumCoins(6,new int[]{1,3,4})==2;
```

**Expected:** 2 coins,using3+3 rather than4+1+1.

**Verify:** Compare the program values or named exception with 2 coins,using3+3 rather than4+1+1. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 5: Represent an unreachable amount

Task: Solveamount3 withonlycoin2 andamount0 withanypositivecoins.

Zero is the base case,while-1 is an explicit unreachable result. Confusing them would make an impossible amount look solvable with no coins.

```java
assert minimumCoins(3,new int[]{2})==-1;
assert minimumCoins(0,new int[]{2,5})==0;
```

**Expected:** -1 forunreachable3;0 foramount0.

**Verify:** Compare the program values or named exception with -1 forunreachable3;0 foramount0. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 6: Reject invalid recurrence inputs

Task: Pass a negative amount or a zero-valued coin.

A zero coin would not reduce the subproblem and violates the intended recurrence. Validation prevents an ill-defined algorithm rather than relying on an accidental loop bound.

```java
boolean negative=false,zeroCoin=false;
try{minimumCoins(-1,new int[]{1});}catch(IllegalArgumentException expected){negative=true;}
try{minimumCoins(3,new int[]{0,1});}catch(IllegalArgumentException expected){zeroCoin=true;}
assert negative&&zeroCoin;
```

**Expected:** IllegalArgumentException forboth.

**Verify:** Compare the program values or named exception with IllegalArgumentException forboth. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## After comparing the answer

Run the complete reference with assertions enabled, then return to your own implementation. Recreate one check with different values and explain its expected result before execution. A compiler error, an expected domain exception and an assertion failure represent different stages and should be reported separately. Preserve ownership boundaries when adapting file, network or concurrency examples. The reference never authorizes access to a shared service or deletion of learner state. Use a fresh tiny fixture when you need to distinguish two interpretations of an API contract.
