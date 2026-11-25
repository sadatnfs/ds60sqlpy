# cpp-017: explanations and reference observations

The [executable reference](cpp-017_solution.cpp) adds `bounded`, which accepts 100 and reports `too_large` for 101, alongside the pad's negative case. The explanations show how each error keeps its own reason inside the variant. How to compare: [study guide](../STUDY-GUIDE.md#compare-with-the-solutions).

## Mechanism

optional represents either one value or absence. variant represents one of several named alternatives, useful for distinguishing error reasons. An exception transfers control to a matching catch boundary. Choose errors-as-values for expected input rejection and exceptions for exceptional failures that callers cannot usefully ignore.

## Detailed reasoning

Treat the result as a tagged choice. For 0, the active alternative is int and the numeric value happens to be zero. For -1, the active alternative is ParseError with a reason string. Asking get<int> of the second value is a programmer error, not expected input rejection. A checked visitor or get_if branch handles both alternatives. Exceptions are useful at a file or process boundary only when that boundary can preserve context and decide whether to stop or recover.

<!-- depth:start -->
## Representing failure as data or control flow

An operation can fail without producing a valid result. The interface must make that distinction visible. optional<T> represents either a value or absence, but carries no detailed error by itself. variant<int, ParseError> can represent a successful integer or a structured reason. An exception transfers control to a matching handler and can unwind intermediate scopes. These choices express different contracts rather than one universally best error style.

The positive function accepts zero because nonnegative includes the boundary. Its success alternative contains int 0. The failure alternative for -1 contains ParseError with reason negative. holds_alternative checks which type is active before the caller extracts a value. Treating the variant as though it always held int would lose the error path; using get on the wrong alternative can itself throw bad_variant_access.

Error context should explain the input boundary without exposing unnecessary data. A parser might retain row number and a reason code while avoiding a complete sensitive record. A small structured error also supports exact tests and programmatic handling more reliably than matching a long free-form sentence. The teaching reason string is deliberately simple, not a complete production diagnostic schema.

Choose a consistent handling boundary. If a lower-level parser returns a variant, the caller should deliberately decide whether to count a rejected row, abort the operation or translate the error into an exception. Silently substituting zero for every failure makes invalid input indistinguishable from legitimate zero. Conversely, aborting an entire batch for one malformed row may violate a declared partial-acceptance policy.

Exceptions and RAII work together when a failure crosses several calls. Returned error values can make expected local alternatives explicit. In both designs, test that success and failure have different observable results and that required cleanup/accounting still happens. A function that prints an error but returns an apparently valid value leaves callers unable to enforce the contract.

## Debugging the contract

When a bad input contributes zero to a total, inspect whether rejection was collapsed into a default value. When variant access throws unexpectedly, inspect the active alternative before extraction. When an exception is swallowed, verify that the caller still records failure and does not publish a normal result. Test zero, negative input and the largest supported valid value separately because they exercise different parts of the domain boundary.
<!-- depth:end -->

## Worked example 1

```cpp
auto result = positive(0);
assert(std::holds_alternative<int>(result));
```

Expected: Zero is a present successful integer.

## Worked example 2

```cpp
auto result = positive(-1);
assert(std::get<ParseError>(result).reason == "negative");
```

Expected: The error alternative carries an inspectable reason.

## Exercise 1: Classify alternatives

Evaluate positive for 0, 5, -1.

**Expected:** Two success values 0, 5 and one negative error.

**Reasoning:** Error state is encoded independently of numeric value.

**Verify:** Assert `std::get<int>(positive(0)) == 0`, `std::get<int>(positive(5)) == 5` and `std::holds_alternative<ParseError>(positive(-1))`; zero is a success, not an error.

## Exercise 2: Write an observer

Use get_if to print value or reason without throwing.

**Expected:** All three inputs produce a classified outcome.

**Reasoning:** Check the active variant before accessing it.

**Verify:** Run 0, 5 and -1 through one `std::get_if` branch each and confirm three printed lines, with -1 showing `negative` and no exception escaping.

## Exercise 3: Preserve a missing value

Distinguish optional<int>{0} from nullopt.

**Expected:** First present, second absent.

**Reasoning:** get_or_else-style defaults can erase missingness.

**Verify:** Assert `std::optional<int>{0}.has_value()` and `!std::optional<int>{}.has_value()`; comparing contained values alone would hide the difference.

## Exercise 4: Repair bad access

Call get<int> on the error in a scratch copy.

**Expected:** bad_variant_access; replace with checked dispatch.

**Reasoning:** A wrong alternative is a program logic error.

**Verify:** Wrap `std::get<int>(positive(-1))` in `try`/`catch` and assert `std::bad_variant_access` is caught; after switching to `std::get_if` or `std::visit`, no exception is possible.

## Exercise 5: Choose a boundary

Explain why a missing required file is fatal while one bad row can be recorded.

**Expected:** Separate process-level error from row-level rejection.

**Reasoning:** The caller needs enough context to choose recovery.

**Verify:** Check that your explanation stops the whole run with a nonzero status for the missing file but records the bad row and continues with the next one.

## Exercise 6: Transfer richer reasons

Add too_large for values above 100.

**Expected:** 101 maps to too_large, -1 to negative, 100 succeeds.

**Reasoning:** Named reasons preserve the failure taxonomy.

**Verify:** Assert the reasons for 101 and -1 are `too_large` and `negative`, and that `std::get<int>(positive(100)) == 100`; 100 is the inclusive boundary.
