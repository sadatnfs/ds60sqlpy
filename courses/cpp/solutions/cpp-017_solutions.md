# cpp-017: explanations and reference observations

Attempt the learner tasks before opening this document. The executable reference checks the bounded normal and boundary examples; the six explanations below cover the deliberate changes and manual checks.

## Mechanism

optional represents either one value or absence. variant represents one of several named alternatives, useful for distinguishing error reasons. An exception transfers control to a matching catch boundary. Choose errors-as-values for expected input rejection and exceptions for exceptional failures that callers cannot usefully ignore.

## Detailed reasoning

Treat the result as a tagged choice. For 0, the active alternative is int and the numeric value happens to be zero. For -1, the active alternative is ParseError with a reason string. Asking get<int> of the second value is a programmer error, not expected input rejection. A checked visitor or get_if branch handles both alternatives. Exceptions are useful at a file or process boundary only when that boundary can preserve context and decide whether to stop or recover.

## Worked example 1

```cpp
auto result=positive(0); assert(std::holds_alternative<int>(result));
```

Expected: Zero is a present successful integer.

## Worked example 2

```cpp
auto result=positive(-1); assert(std::get<ParseError>(result).reason=="negative");
```

Expected: The error alternative carries an inspectable reason.

## Exercise 1: Classify alternatives

Evaluate positive for 0,5,-1.

**Expected:** Two success values 0,5 and one negative error.

**Reasoning:** Error state is encoded independently of numeric value.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 2: Write an observer

Use get_if to print value or reason without throwing.

**Expected:** All three inputs produce a classified outcome.

**Reasoning:** Check the active variant before accessing it.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 3: Preserve a missing value

Distinguish optional<int>{0} from nullopt.

**Expected:** First present, second absent.

**Reasoning:** get_or_else-style defaults can erase missingness.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 4: Repair bad access

Call get<int> on the error in a scratch copy.

**Expected:** bad_variant_access; replace with checked dispatch.

**Reasoning:** A wrong alternative is a program logic error.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 5: Choose a boundary

Explain why a missing required file is fatal while one bad row can be recorded.

**Expected:** Separate process-level error from row-level rejection.

**Reasoning:** The caller needs enough context to choose recovery.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 6: Transfer richer reasons

Add too_large for values above 100.

**Expected:** 101 maps to too_large, -1 to negative, 100 succeeds.

**Reasoning:** Named reasons preserve the failure taxonomy.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.
