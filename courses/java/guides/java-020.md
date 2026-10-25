# java-020: Search, sorting and dynamic programming

## Level and prerequisites

Intermediate, approximately 90 minutes. Direct prerequisites: `java-019`

## Learning objectives

Explain binary-search invariant, stable sort, dynamic programming using a concrete program. Trace the normal execution, identify its boundary assumptions and make a failure case observable. The first investigation is Run lowerBound on 1,2,2,5 with target 2 and target 6. The final exercise transfers the mechanism to reject invalid recurrence inputs.

## Purpose and mental model

Algorithms connect a problem contract to a sequence of operations and invariants. Binary search relies on sorted input and repeatedly narrows a half-open interval containing the possible answer. Stable sorting preserves relative order among equal keys,which matters when records already have a meaningful prior order. Recursion solves a problem through smaller instances and needs a base case;memoization avoids recomputing repeated subproblems. Dynamic programming makes those dependencies explicit in a table. The coin-change fixture shows why a locally greedy choice can fail even when a valid combination exists.

## Vocabulary and concepts

**Binary-search invariant:** The relationship preserved while narrowing a sorted search interval.

**Stable sort:** A sort preserving input order among equal sort keys.

**Dynamic programming:** Reusing solved subproblems according to explicit dependencies.

## How to run this lesson

Open the Docker classroom, choose the prepared Java 21 profile and save a learner pad. The pad is compiled as `Main.java` with `javac --release 21` and executed with `java -ea Main`. Assertions are enabled deliberately. A successful assertion has no output; a failed assertion throws `AssertionError` and the process should fail. Do not remove assertions to obtain a green result.

For a prepared native JDK, copy a worked example into your own `Main.java` under ignored `.learning/expansion/java-020/`. From that directory run the same two commands on PowerShell, macOS or Linux:

```text
javac --release 21 Main.java
java -ea Main
```

The public class name and source filename must agree. Each worked example below is a complete file. Example B includes the setup it needs from Example A, so it can be compiled by itself. The six exercise reference blocks form one complete program in the separate solution. Keep your original prediction, source and diagnostic text together. Most examples use prepared JDK libraries and tiny local fixtures; any additional dependency is specified in the lesson notes below. Any lesson-specific library or additional file is named explicitly; do not download packages from inside a learner program. Resource examples close their owned files, executors or loopback servers.



## Syntax anatomy and execution trace

A lower-bound search returns the first index whose value is at least the target,or length if none qualifies. The invariant keeps all earlier discarded positions below the target and all later discarded positions at least the target. A dynamic-programming tabledp[amount] stores the minimum coin count for that exact amount,withdp[0]=0 and an unreachable sentinel. Each transition considers a smaller amount and one added coin.

## Worked example / walkthrough

### Example A: Find the first duplicate boundary

Returning the first qualifying position gives a precise duplicate policy. An arbitrary matching index would satisfy a different search contract.

```java
import java.util.*;

public class Main {
    record Item(String id,int key){}
    static int lowerBound(int[] values,int target){int low=0,high=values.length;while(low<high){int mid=low+(high-low)/2;if(values[mid]<target)low=mid+1;else high=mid;}return low;}
    static int minimumCoins(int amount,int[] coins){
        if(amount<0||amount>1000)throw new IllegalArgumentException("amount0..1000 required");
        for(int coin:coins)if(coin<=0)throw new IllegalArgumentException("positive coins required");
        int[] dp=new int[amount+1];Arrays.fill(dp,amount+1);dp[0]=0;
        for(int current=1;current<=amount;current++)for(int coin:coins)if(coin<=current)dp[current]=Math.min(dp[current],dp[current-coin]+1);
        return dp[amount]>amount?-1:dp[amount];
    }
    public static void main(String[] args) throws Exception {
        int[] sorted={1,2,2,5};assert lowerBound(sorted,2)==1 && lowerBound(sorted,6)==4;
    }
}

```

**Expected:** indices 1 and 4.

### Example B: Handle empty and outside searches

The half-open interval starts empty for an empty input. The result is an insertion position,not necessarily the index of an existing match.

```java
import java.util.*;

public class Main {
    record Item(String id,int key){}
    static int lowerBound(int[] values,int target){int low=0,high=values.length;while(low<high){int mid=low+(high-low)/2;if(values[mid]<target)low=mid+1;else high=mid;}return low;}
    static int minimumCoins(int amount,int[] coins){
        if(amount<0||amount>1000)throw new IllegalArgumentException("amount0..1000 required");
        for(int coin:coins)if(coin<=0)throw new IllegalArgumentException("positive coins required");
        int[] dp=new int[amount+1];Arrays.fill(dp,amount+1);dp[0]=0;
        for(int current=1;current<=amount;current++)for(int coin:coins)if(coin<=current)dp[current]=Math.min(dp[current],dp[current-coin]+1);
        return dp[amount]>amount?-1:dp[amount];
    }
    public static void main(String[] args) throws Exception {
        int[] sorted={1,2,2,5};assert lowerBound(sorted,2)==1 && lowerBound(sorted,6)==4;

        assert lowerBound(new int[0],7)==0;
        assert lowerBound(sorted,0)==0;
    }
}

```

**Expected:** both return0.

## Prediction before your attempt

Read the source from the entry point and name each value before executing it. Identify which operations create new values, which mutate existing state and which can fail. Predict the first observable output or assertion result. For a compile-time failure, explain which source rule is violated before discussing runtime state: a program that did not compile never reached its main method. Keep normal, boundary and invalid inputs separate so each check has a clear purpose.

## Exercises

1. **Find the first duplicate boundary.** Run lowerBound on 1,2,2,5 with target 2 and target 6.
   **Expected:** indices 1 and 4.
   **Verify:** Compare your assertion values or captured diagnostic with indices 1 and 4.

2. **Handle empty and outside searches.** Search an empty array and a target below the first element.
   **Expected:** both return0.
   **Verify:** Compare your assertion values or captured diagnostic with both return0.

3. **Preserve stable ties.** Sort recordsa2,b1,c2 by key only and inspect the equal-key order.
   **Expected:** IDs b,a,c.
   **Verify:** Compare your assertion values or captured diagnostic with IDs b,a,c.

4. **Solve a greedy counterexample.** Find minimum coins foramount6 usingcoins1,3,4.
   **Expected:** 2 coins,using3+3 rather than4+1+1.
   **Verify:** Compare your assertion values or captured diagnostic with 2 coins,using3+3 rather than4+1+1.

5. **Represent an unreachable amount.** Solveamount3 withonlycoin2 andamount0 withanypositivecoins.
   **Expected:** -1 forunreachable3;0 foramount0.
   **Verify:** Compare your assertion values or captured diagnostic with -1 forunreachable3;0 foramount0.

6. **Reject invalid recurrence inputs.** Pass a negative amount or a zero-valued coin.
   **Expected:** IllegalArgumentException for both.
   **Verify:** Compare your assertion values or captured diagnostic with IllegalArgumentException for both.

## Common pitfalls and diagnosis

When a check fails, keep the smallest source file that still demonstrates the failure. Read the first relevant compiler diagnostic before editing several lines; later diagnostics can be consequences of the same missing delimiter or wrong type. For a runtime exception, identify the first frame belonging to your code and compare its input with the method contract. For an assertion failure, inspect the actual value and the independent expected value. A passing process exit is weaker than a checked invariant, and a checked invariant applies only under its stated assumptions.

Do not replace a precise exception with a catch-all that returns a plausible default. That can hide an invalid input or an unfinished operation. If an example owns a resource, verify its lifetime on both the success and failure paths. If an operation is concurrent, use ordering primitives to establish the relationship you need; an observed timing coincidence is not a synchronization guarantee. The solution explanations identify the specific alternative that would break each exercise.

## Progressive hints

First reconstruct the values and identities in the worked example. Next isolate the line that changes the result when one input is altered. Finally compare the normal and failure paths with the stated contract. Use a small table of input, expected value, actual value and exception type. Ask for one hint about the first incorrect assumption before requesting the entire reference implementation.

## Self-check and retrieval

Close the solution and explain Binary-search invariant, Stable sort, Dynamic programming in your own words. Reconstruct one example from a blank `Main.java`, then add a new boundary input. Explain why the new case should pass or fail before compiling it. Identify a situation where this technique is appropriate and one where a different data structure, lifetime policy or abstraction would be clearer. This is a reasoning check, not a memorization test for an API spelling.

## Next step

Preserve the saved pad and the six exercise observations. Continue to the next lesson only when you can explain the invariants without reading the answer. Later chapters reuse these contracts in larger programs, so keep a failing counterexample as well as a repaired result. A reference implementation demonstrates one valid design under the stated assumptions; it is not a universal design rule.

## Sources and verification status

[Official Java21 API or language reference](https://docs.oracle.com/en/java/javase/21/docs/api/index.html), reviewed2026-10-22. Examples and exercise fixtures are original course material. Use the [validation guide](../../../docs/validation.md) and CI artifacts for the exact revision and platform to inspect actual compile/run results. Authoring, parsing, compilation, execution and learner mastery are separate forms of evidence.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for java-020: Search, sorting and dynamic programming.
Read courses/java/guides/java-020.md and courses/java/lessons/java-020.java. Direct prerequisites: `java-019`.
Explain the mechanism, ask for a prediction, review my attempt, give one hint,
request compiler/runtime evidence, and ask a fresh retrieval question.
Keep courses/java/solutions/ closed until I request comparison or show an attempt.
Use Java21 and the declared offline fixture. Done when I can explain the state
transitions, pass all six exercise contracts, diagnose one failure and solve a
new boundary case without copying the solution.
```
