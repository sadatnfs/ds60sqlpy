"""Per-task solution reasoning for thin C explanatory solutions.

Each entry gives, for every one of the six cases in order, the approach, why it
holds for this lesson's data, one plausible wrong approach and why it fails here,
and how to verify it. The transfer text replaces the generic closing paragraph.
"""

LABELS = ("Approach", "Why it holds here", "A plausible wrong approach", "Verify")

REASONING = {
    "c-001": dict(
        cases=[
            (
                "Evaluate the edited initializer before reading the CHECK: `3 + 3` stores 6 in `total`, and the CHECK still compares with 5.",
                "The expected 5 was fixed before the program ran, so 6 makes `total == 5` false. `lesson_check` writes `Check failed at main.c:` plus the line number to stderr and calls `abort()`, so the success line never prints.",
                "Predicting that the run still succeeds because CHECK behaves like `assert`, which a release build can remove with `NDEBUG`. This CHECK is always compiled in, so the wrong total always reaches the comparison.",
                "Run the edited pad and see the `Check failed` line with a nonzero exit status (134 in a shell after `abort`); restore `2 + 3` and see `Worked example checks passed.`",
            ),
            (
                "Read the two CHECKs separately: `snprintf` still writes seven characters, `total=6`, so `n == 7` passes and the string comparison is the CHECK that stops the run.",
                'The length check cannot tell one digit from another, because `total=5` and `total=6` are both seven characters. Only `strcmp(out, "total=5") == 0` sees the wrong digit, so restoring the argument 5 repairs it.',
                "Concluding from the passing `n == 7` that formatting is fine and enlarging `out` or changing the format string. The buffer has 16 bytes and nothing was truncated; the defect is the value 6 passed to `snprintf`.",
                'Add `printf("%d %s\\n", n, out);` before the CHECKs and see `7 total=6` with the regression and `7 total=5` after the repair.',
            ),
            (
                "Apply the statements in source order: `count` starts at 1, `+= 1` makes it 2 and `*= 3` makes it 6.",
                "Each compound assignment reads the value left by the previous statement, so the multiplication sees 2, not the initial 1, and the CHECK on 6 holds.",
                "Collapsing the steps into one expression as `count = count * 3 + 1;`. Multiplying first gives 4 from the starting value 1, so the CHECK on 6 fails; order matters because both operations change the same object.",
                "Print `count` after each statement and see 2 and then 6.",
            ),
            (
                "Evaluate each comparison to a `bool`: `4 == 4` is true and `4 != 5` is true, so `same && different` is true.",
                "Both relational expressions compare values without changing anything, and `&&` needs both to be true, which they are for these literals.",
                "Writing the equality with `=`, for example `int a = 4; bool same = (a = 4);`. That assigns 4 to `a` and converts 4 to true, so it passes for the wrong reason; `(a = 5)` would also be true and would change `a`. With two literals, `4 = 4` does not even compile because a literal is not assignable.",
                "Print `same`, `different` and `(4 == 5)` with `%d` and see `1 1 0`.",
            ),
            (
                "Call the helper `seven()`, which is defined above `main` with the prototype `int seven(void)`, and compare its result with 7.",
                "Because the definition is visible before the call, the compiler checks the call against an `int` return and an empty parameter list, and the call yields 7.",
                "Moving the helper below `main` without a prototype. C99 removed implicit declarations, so current GCC and Clang reject the call to an undeclared function under `-std=c17`; old compilers guessed an `int` return, which happens to match here but would silently break a helper returning `double`.",
                "Temporarily move the helper below `main`, compile with the lesson flags and read the undeclared-function diagnostic; restore it, or add `int seven(void);` above `main`, and the program prints its success line.",
            ),
            (
                "Multiply `items` by `unit` in `int`: 4 times 6 is 24, which is far inside the range of `int`.",
                "No intermediate value comes near `INT_MAX`, so the product is exact and the CHECK on 24 holds.",
                "Reusing the same line for large receipts, such as 100000 items at a unit of 30000. The true product, 3000000000, exceeds `INT_MAX` on the worker, and signed overflow is undefined behavior, so that input must be rejected before multiplying rather than run to see what happens.",
                "Keep the CHECK on 24, then add `CHECK(4 <= INT_MAX / 6);` and `CHECK(100000 > INT_MAX / 30000);`. The quotient `INT_MAX / 30000` is 71582, so the second CHECK proves the large receipt would overflow without performing it.",
            ),
        ],
        transfer="Write `bool format_total(char *out, size_t cap, int total)` that calls `snprintf` and returns true only when the result is nonnegative and less than `cap`. Check that capacity 16 and total 5 give `total=5`, capacity 8 also succeeds because seven characters plus the null byte fit exactly, capacity 7 is rejected with `out` truncated to `total=`, and capacity 8 with total 123 is rejected. Explain which of these a test written as `n > cap` would wrongly accept.",
    ),
    "c-002": dict(
        cases=[
            (
                "Evaluate the edited line with integer operands: `8 / 2` is exact and stores 4 in `whole`, while `fraction` is still `7 / 2.0`, which is 3.5.",
                "The CHECK needs `whole == 3`, so the first operand of `&&` is false and the run stops even though `fraction` is unchanged.",
                "Assuming the original `7 / 2` rounds to 4, so that the edit looks harmless. Integer division in C truncates toward zero, so 7 / 2 is 3 and the edit really changes the value from 3 to 4.",
                "Print `whole` and `fraction` with `%d %.1f` and see `4 3.5` for the edit and `3 3.5` for the original.",
            ),
            (
                "Trace the regressed line from `UINT_MAX`: subtracting 1 gives `UINT_MAX - 1`, which on the worker's 32-bit `unsigned int` is 4294967294.",
                "Unsigned arithmetic is defined modulo 2 to the number of value bits, so only `n += 1U` wraps `UINT_MAX` to 0. With `-=` nothing wraps and `n == 0U` fails; restoring `+=` repairs it.",
                "Deciding that unsigned wraparound is unreliable and rewriting the experiment with `int n = INT_MAX; n += 1;`. That is signed overflow, which is undefined behavior, so it trades a defined result for one that must never be executed.",
                "Print `n` with `%u` and see 4294967294 for the regression and 0 after the repair.",
            ),
            (
                "Check only facts the standard guarantees: `sizeof(char)` is 1 by definition and `CHAR_BIT` is at least 8.",
                "`sizeof` counts in units of `char`, so the first CHECK holds on every implementation, and `<limits.h>` must define `CHAR_BIT` as 8 or more.",
                "Adding `CHECK(sizeof(int) == 4)` as another representation fact. It passes on the Linux worker, but C only requires `int` to hold at least 16 bits, so it records a platform assumption rather than a language rule.",
                "Print `sizeof(char)`, `CHAR_BIT` and `sizeof(int)` with `%zu %d %zu` and see `1 8 4` on the worker; only the first two values are guaranteed, and POSIX additionally fixes `CHAR_BIT` at 8.",
            ),
            (
                "Declare both operands as `int64_t` so the multiplication itself happens in a 64-bit type and produces 2500000000.",
                "The usual arithmetic conversions use the operand types, and 2500000000 fits easily in `int64_t`, so the product compares equal to `INT64_C(2500000000)`.",
                "Keeping the operands as `int` and assigning the result to a wider variable, as in `int a = 50000, b = 50000; int64_t p = a * b;`. The product is computed in `int` first and 2500000000 exceeds `INT_MAX`, so the overflow is undefined before the conversion can help; describe it, do not run it.",
                "Print `(long long)(a * b)` with `%lld` and see 2500000000. Then print `INT_MAX / 50000`, which is 42949: since 50000 is larger, the `int` product would overflow.",
            ),
            (
                "Compare the computed sum with 0.3 through an absolute tolerance, `fabs((a + b) - 0.3) < 1e-15`.",
                "Neither 0.1 nor 0.2 is exactly representable in binary floating point, and their sum is 0.30000000000000004. The error is about 5.55e-17, comfortably below 1e-15.",
                "Writing `CHECK(a + b == 0.3)`. The nearest doubles do not add up to the double nearest 0.3, so the exact comparison is false and the CHECK fails on a correct calculation.",
                "Print `a + b` with `%.17g` and the error with `%.3g`, and see `0.30000000000000004 5.55e-17`; `a + b == 0.3` prints as 0.",
            ),
            (
                "Use C's truncating division: -7 / 2 is -3, and the remainder is defined so that `q * 2 + r` equals -7, which makes it -1.",
                "Since C99 the quotient truncates toward zero, and the remainder takes the sign of the dividend, so all three conditions in the CHECK hold.",
                "Expecting floor division as in Python, a quotient of -4 and a remainder of 1. Those values also satisfy the reconstruction identity, but they are not what C computes, so the CHECK on -3 and -1 fails.",
                "Print `-7 / 2`, `-7 % 2` and `floor(-7 / 2.0)` and see `-3 -1 -4`.",
            ),
        ],
        transfer="Write `bool mul_nonneg(int a, int b, int *out)` for nonnegative operands that returns false when `b != 0 && a > INT_MAX / b` and otherwise stores `a * b`. Check that 4 and 6 store 24, 50000 and 50000 is rejected with `*out` unchanged, 0 and `INT_MAX` store 0, and `INT_MAX` and 1 store `INT_MAX`. Explain why testing `a * b < 0` after multiplying is not a valid overflow check in C.",
    ),
    "c-005": dict(
        cases=[
            (
                "Evaluate the edited call: `twice(1)` returns 2, and the edited CHECK still expects 0.",
                "`twice` has no hidden state, so its result depends only on the argument. Changing the input from 0 to 1 changes the correct result to 2, and `2 == 0` is false, so the run stops at that CHECK.",
                "Predicting that the CHECK still holds because only the argument changed and the expected value was kept. An expected value belongs to one input; a CHECK whose input changes needs a new expected value, here 2.",
                "Print `twice(1)` and see 2; restore `twice(0)` and the program prints its success line.",
            ),
            (
                "Follow the edited call: `try_area(4, 4, &out)` is a valid request, so it returns true, the edited CHECK passes and `out` becomes 16.",
                "The status CHECK only states that the call succeeded, which it did. The failure appears one statement later, where `out == 12` reads 16, so the reported line number points at the value CHECK, not the edited one.",
                "Expecting the edited CHECK line itself to report the failure. `try_area` accepts every positive pair whose product fits in `int`, so a valid but different request changes the output, not the status.",
                "Print `out` after the edited call and see 16; restore `3, 4` and see 12.",
            ),
            (
                "Call `try_area(0, 4, &out)` with `out` preset to -1 and check both the false status and the untouched output.",
                "The helper tests `w <= 0` before it writes, so it returns false and never assigns `*out`, leaving -1 in place.",
                "Computing the product before validating, as in `*out = w * h; return w > 0 && h > 0;`. The status is still false, but `out` now holds 0, so `out == -1` fails and the caller cannot tell a rejected call from a real result.",
                "Print `out` after the call and see -1, and the program reaches its success line.",
            ),
            (
                "Pass `value` to `reassign`, which overwrites its own parameter with 99, and check that the caller still sees 5.",
                "C passes a scalar argument by value: `reassign` receives a separate `int` initialized from 5, so assigning 99 to it never touches the caller's object.",
                "Expecting `value` to be 99 after the call, as if the parameter were a reference. A CHECK written as `value == 99` fails; changing the caller requires an `int *` parameter and an explicit `&value` at the call site.",
                "Print `value` after the call and see 5.",
            ),
            (
                "Pass `NULL` as the output pointer and expect `try_area` to reject the call before any access.",
                "The first test in the helper is `out == NULL`, and `||` stops at the first true operand, so the function returns false without evaluating anything that dereferences `out`.",
                "Validating only the sizes and then writing `*out = w * h;`. With a null `out` that write is undefined behavior, typically a crash, so it must be described rather than executed; the null test has to come before the first dereference.",
                "Build with `-fsanitize=address,undefined` and run: the CHECK passes with no sanitizer report and the success line prints.",
            ),
            (
                "Ask whether `INT_MAX` times 2 fits before multiplying, by comparing `w` with `INT_MAX / h`.",
                "`INT_MAX / 2` is 1073741823 and `w` is `INT_MAX`, so `w > INT_MAX / h` is true, the helper returns false and `out` keeps 9.",
                "Multiplying first and testing the result, for example `int area = w * h; if (area < 0) return false;`. The product overflows, which is undefined behavior, so an optimizer may delete the test entirely; the decision has to be made before the multiplication.",
                "Call `try_area(1073741823, 2, &out)` and see true with `out` equal to 2147483646, the largest accepted product; then call it with 1073741824 and see false with `out` unchanged. Print in separate statements, because argument evaluation order in one `printf` call is unspecified.",
            ),
        ],
        transfer="Write `bool try_perimeter(int w, int h, int *out)` that rejects a null `out`, nonpositive sides and any pair whose `2 * (w + h)` exceeds `INT_MAX`, testing `w > INT_MAX / 2 - h` before adding, and that leaves `*out` unchanged on rejection. Check 3 and 4 store 14, 0 and 4 is rejected, 1073741822 and 1 store 2147483646, and 1073741823 and 1 are rejected. Explain why computing `w + h` first is unsafe when `w` is `INT_MAX`.",
    ),
    "c-008": dict(
        cases=[
            (
                "Trace the edited input: `n` starts at 5, `increment(&n)` adds 1 through the pointer, so `n` becomes 6 and the CHECK on 5 fails.",
                "The helper receives a copy of the address, and that copy designates the caller's `n`, so `*p += 1` changes the caller's object.",
                "Predicting that the CHECK still passes because C passes arguments by value, so `n` would stay 5. The value that is copied is the pointer, not the integer it points to.",
                "Print `n` after the call and see 6; restore 4 and see 5.",
            ),
            (
                "Trace the regressed line: `copy` is initialized from `*p` while `n` is 4, so `copy` is 4; then `*p = 9` changes only `n`.",
                "`copy` is a separate `int` holding the value read at that moment. The CHECK needs `copy == 3`, which fails because the starting value is wrong, not because the later write reached `copy`.",
                "Suspecting that `*p = 9` also changed `copy` and rewriting the write. `copy` holds no pointer to `n`, so no later store through `p` can change it; the defect is the initializer 4.",
                "Print `copy` and `n` and see `4 9` with the regression and `3 9` after restoring `int n = 3;`.",
            ),
            (
                "Call `set_if_present(NULL, 8)` and expect false, because the helper tests for null before it writes.",
                "`p == NULL` is true, so the function returns false and the store `*p = value` is never reached.",
                "Writing the helper as `*p = value; return p != NULL;`, testing after the store. Storing through a null pointer is undefined behavior, typically a crash, so the order of the test matters; describe it instead of running it.",
                "Build with `-fsanitize=address,undefined` and run: the CHECK passes with no report.",
            ),
            (
                "Call `set_if_present(&n, 8)` first and read `n` only after it returns, which is the order `&&` guarantees.",
                "`&&` evaluates its left operand completely, including the store, before the right operand, so `n == 8` sees the new value.",
                "Writing the CHECK as `n == 8 && set_if_present(&n, 8)`. `n` is still 1 when the left operand is evaluated, so `&&` short-circuits, the helper never runs and the CHECK fails with `n` still 1.",
                "Evaluate the reordered expression into a `bool`, print it and `n`, and see `0 1`.",
            ),
            (
                "Reassign `p` from `&a` to `&b` and check that both integers keep their values while `*p` now reads 7.",
                "Assigning to `p` changes which object it designates. Nothing is stored into `a` or `b`, so they remain 2 and 7.",
                "Writing `*p = b;` instead of `p = &b;`. That stores 7 into `a` through the old pointer, so `a == 2` fails even though `*p` is 7.",
                "Print `a`, `b` and `*p` and see `2 7 7`; the `*p = b` version prints `7 7 7`.",
            ),
            (
                "Save `*a` in a temporary, copy `*b` into `*a`, then store the saved value into `*b`.",
                "The temporary keeps the original 2 after `*a` is overwritten with 7, so `*b` receives 2 and the CHECK on `7 2` holds. Calling `swap_ints(&a, &a)` also leaves `a` unchanged.",
                "Swapping without a temporary, `*a = *b; *b = *a;`. The first store destroys 2, so both integers end as 7 and `b == 2` fails.",
                "Print `a` and `b` and see `7 2`; the version without the temporary prints `7 7`.",
            ),
        ],
        transfer="Write `bool min_max(const int *values, size_t count, int *lo, int *hi)` that rejects null pointers and a count of 0, leaves both outputs unchanged on rejection, and starts both running values at `values[0]`. Check that `{4, -2, 9}` gives -2 and 9, a single element `{5}` gives 5 for both, count 0 is rejected and a null `hi` is rejected. Explain which result a version that starts the running minimum at 0 gets wrong for `{4, 9}`.",
    ),
    "c-010": dict(
        cases=[
            (
                "Evaluate the edited initializer: `.x = 3` and `.y = 3` give a field sum of 6, so the CHECK on 5 fails.",
                "Designated initializers bind each value to the named field, so the edit changes exactly `p.x`, and the sum changes from 5 to 6.",
                "Treating the sum CHECK as proof that the fields were assigned correctly. `{.x = 3, .y = 2}` also sums to 5 and passes, so a swapped pair goes unnoticed; when field identity matters, check `p.x == 2 && p.y == 3`.",
                "Print `p.x` and `p.y` and see `3 3` for the edit and `2 3` for the original.",
            ),
            (
                "Trace the regressed initializer: `a` starts as `{3, 3}`, `b = a` copies both fields, and `b.x = 9` changes only `b`.",
                "Struct assignment copies every member into `b`'s own storage, so `a.x` stays at its initial 3, and `a.x == 2` fails because of the initializer, not because of the later write.",
                "Suspecting that `b.x = 9` wrote through to `a`, as with a reference type in other languages, and changing the assignment. C struct assignment copies values; only pointer members would still share a target.",
                "Print `a.x` and `b.x` and see `3 9` with the regression and `2 9` after restoring `{2, 3}`.",
            ),
            (
                "Store the integer alternative with `.tag = VALUE_INT` and `.data.integer = 7`, and read the payload only after checking the tag.",
                "The tag records which union member was last written, and the CHECK reads that same member, so the payload is 7.",
                'Reading the other member, for example `strcmp(v.data.text, "ready")`, on this integer-tagged value. The union\'s 8 bytes then hold the integer 7 plus whatever was left in the rest, treated as an address, so passing it to `strcmp` is undefined behavior; the tag exists to prevent exactly that read.',
                "Print `v.tag == VALUE_INT` and `v.data.integer` and see `1 7`; `sizeof v.data` is 8 on the worker because the pointer member is the largest.",
            ),
            (
                'Store a pointer to the string literal `"ready"` under `VALUE_TEXT` and compare the text with `strcmp`.',
                "A string literal has static storage duration, so the borrowed pointer remains valid for the whole program and `strcmp` returns 0.",
                'Borrowing a local array instead, `{ char buf[] = "ready"; v.data.text = buf; }`, and comparing after the block. `buf` no longer exists, so the read through the dangling pointer is undefined; describe it rather than run it.',
                "Print `v.data.text` with `%s` and see `ready`; under AddressSanitizer the defined version runs with no report.",
            ),
            (
                "Compare the meaningful fields one by one: `a.x == b.x && a.y == b.y`.",
                "Both points were initialized with 2 and 3, so each field comparison is true and the conjunction holds.",
                "Writing `CHECK(a == b)`. C has no built-in equality for structs, so the compiler rejects the expression as invalid operands of type `struct Point`. `memcmp` would compile, but it also compares padding bytes, which this two-`int` struct lacks but a struct such as `{char c; int n;}` has.",
                "Compile the `a == b` version to read the invalid-operands diagnostic, then print `sizeof(struct Point)` and see 8, exactly two `int`s, which confirms there is no padding here.",
            ),
            (
                "Convert 99 to `enum ValueTag` and pass it to `valid_tag`, which accepts only the two named enumerators.",
                "An enum type is an integer type; the conversion keeps 99 because the worker's enum is 4 bytes, so `valid_tag` sees a value equal to neither enumerator and returns false.",
                "Trusting the type alone, for example a `switch` with cases for `VALUE_INT` and `VALUE_TEXT` and no `default`, on the assumption that an `enum ValueTag` cannot hold anything else. 99 matches no case and falls through unhandled.",
                "Print `(int)(enum ValueTag)99` and `valid_tag(VALUE_TEXT)` and see `99 1`.",
            ),
        ],
        transfer="Write `bool value_equal(const struct Value *a, const struct Value *b)` that returns false when either tag is invalid or the tags differ, compares integers with `==` and text with `strcmp`. Check that two `VALUE_INT` 7 values are equal, 7 and 8 are not, two `VALUE_TEXT` values pointing at different arrays that both hold `ready` are equal, and an integer 7 against tag 99 is unequal. Explain which case comparing `a->data.text == b->data.text` gets wrong.",
    ),
    "c-011": dict(
        cases=[
            (
                "Trace both objects: the outer `value` now starts at 4, the inner block declares a new `value` set to 7, and after the block the name refers to the outer object again.",
                "The inner CHECK reads the inner object and passes with 7. The outer object was never touched, so it still holds 4 and the CHECK on 3 fails.",
                "Predicting the inner CHECK fails because the inner `value` starts from the outer 4. The inner declaration creates a separate object with its own initializer, 7, so only the outer CHECK sees the edit.",
                "Print `value` inside the block and after it, and see 7 and then 4.",
            ),
            (
                "Count the calls: the first CHECK consumes the first call, which returns 1, and the edited CHECK makes the second call, which returns 2.",
                "`count` has static storage duration: it is initialized once and keeps its value between calls, so the second call returns 2 and `2 != 2` is false.",
                "Predicting the edited CHECK passes because `count` is reset to 0 on every call, so the second call would return 1. The initializer of a static local runs once, before the first call, not on each entry.",
                "Call `next_count()` three times in separate statements and print each result: 1, 2, 3.",
            ),
            (
                "Return the address of a `static const` object and read it through the returned pointer.",
                "A static object lives for the entire program, so the pointer stays valid after `static_value` returns and `*p` is 7.",
                "Returning the address of an ordinary local, `int value = 7; return &value;`. The object ends when the function returns, so any later read is undefined; Clang reports `address of stack memory associated with local variable returned` and GCC reports `-Wreturn-local-addr`.",
                "Compile a helper with the local version and read the warning without calling it; run the static version and see 7.",
            ),
            (
                "Call `local_count` twice: each call creates a fresh `count` initialized to 0, increments it and returns 1.",
                "Automatic objects are created on every entry and destroyed on return, so the second call cannot see the first call's 1, and both operands of `&&` are true.",
                "Adding `static` to the local, `static int count = 0;`. That turns the function into `next_count`: the second call returns 2, so `local_count() == 1` fails on the right side of `&&`.",
                "Call `local_count()` twice in separate statements and see 1 and 1, while `next_count()` keeps counting upward.",
            ),
            (
                "Copy the inner block's value into `copy`, declared in the outer scope, before the block ends.",
                "The assignment copies the integer 9 into `copy`, which lives until the end of `main`, so ending `local`'s lifetime does not affect it.",
                "Keeping the address instead, `int *keep; { int local = 9; keep = &local; } CHECK(*keep == 9);`. After the block `local` no longer exists, so the read is undefined even if it happens to print 9; AddressSanitizer reports it as stack use after scope. Describe it rather than run it.",
                "Print `copy` after the block and see 9.",
            ),
            (
                "Initialize `total` to 0 before the loop, so an empty range leaves the identity value.",
                "With `count` 0 the condition `i < count` is false at once, the body never runs, and `total` keeps the 0 it was given.",
                "Declaring `int total;` without an initializer and relying on the loop to set it. With an empty range the loop never assigns it, so the CHECK reads an indeterminate value, which is undefined. Clang warns that `total` is uninitialized when used, and GCC may not warn without optimization.",
                "Compile the uninitialized version with `-Wall` to see the warning without running it; run the initialized version and see the success line.",
            ),
        ],
        transfer="Write `int next_id(void)` and `void reset_ids(void)` that share a file-scope `static int next = 100;`. Check that two calls give 100 and 101, a reset followed by a call gives 100 again, and `local_count` still returns 1 throughout. Explain why moving the counter into `next_id` as an automatic local returns 100 every time, and why a `static` local inside `next_id` would leave `reset_ids` unable to reach it.",
    ),
    "c-012": dict(
        cases=[
            (
                "Follow the pointer to its target: `view` holds the address of `value`, so `*view` reads whatever `value` holds, now 5.",
                "`const int *` limits writes through `view`; it does not copy the integer. Changing the initializer to 5 therefore changes the read, and `*view == 4` fails.",
                "Predicting the CHECK passes because a const view somehow pins the value it first saw. `view` is only an address with a read-only access path, so it observes the new initializer.",
                "Print `*view` and see 5 with the edit and 4 after restoring the line.",
            ),
            (
                "Locate the write that feeds the failing read: `value = 8;` replaced the expected `value = 7;`, and the view reads 8.",
                "`value` itself is not const, so the direct assignment is legal and the view sees it immediately; restoring 7 makes `*view == 7` true without touching the CHECK.",
                "Repairing through the view, for example `*(int *)view = 7;` after the bad write. That cast hides a design error and does not remove the regression; the correct edit is the one assignment that changed.",
                "Print `value` and `*view` in separate statements and see 8 and 8 before the repair, 7 and 7 after it.",
            ),
            (
                "Put `const` after the `*`: `int *const fixed` makes the pointer object read-only while `*fixed` stays a writable `int`.",
                "The assignment `*fixed = 8` writes the target, which is allowed, so `value` becomes 8.",
                "Swapping the qualifier position to `const int *fixed`. Then `*fixed = 8` is the forbidden operation and Clang rejects it with `read-only variable is not assignable`; with the correct declaration, it is `fixed = &other;` that is rejected.",
                "Compile both mistakes to read the two diagnostics, then run the original and print `value` to see 8.",
            ),
            (
                "Read the const object through a `const int *`, which matches its qualification exactly.",
                "Nothing writes `value`, so `*p` is 9; the compiler may even keep 9 in a register or fold it into code, because it may assume a const object never changes.",
                "Casting the qualifier away to change it, `*(int *)p = 10;`. The object was defined const, so the write is undefined behavior, and Clang accepts it silently under `-Wall -Wextra -Wpedantic`; only `-Wcast-qual` reports `cast ... drops const qualifier`. Describe it rather than run it.",
                "Add `-Wcast-qual` to a compile-only build of the bad line to see the warning; run the original and see 9.",
            ),
            (
                "Declare the parameter as `const int *values`, so `read_sum` promises to read elements only.",
                "Both `const int[3]` and plain `int[3]` arrays convert to `const int *` without a cast, and the loop adds 1, 2 and 3 to get 6.",
                "Declaring the parameter as `int *values`. Passing this const array then draws `passing 'const int[3]' to parameter of type 'int *' discards qualifiers`, and any write inside the function would modify a const object.",
                "Compile a variant with `int *values` to see the warning, then print `read_sum(values, 3)` and see 6.",
            ),
            (
                "Copy the integer: `int snapshot = *view;` stores 2 in a separate object before `value` changes.",
                "Later assignments to `value` cannot reach `snapshot`, while `view` still points at `value`, so the two reads are 2 and 5.",
                "Keeping the snapshot as a pointer, `const int *snapshot = view;`. That copies the address, not the integer, so after `value = 5` both reads return 5 and the CHECK on 2 fails.",
                "Print `snapshot` and `*view` in separate statements and see 2 and 5; the pointer variant prints 5 and 5.",
            ),
        ],
        transfer="Write `void scale_into(const int *in, int *out, size_t n, int factor)` that writes `in[i] * factor` to `out[i]`. Check that a const input `{1, 2, 3}` scaled by 2 gives `{2, 4, 6}`, that `in` is unchanged, and that `n` 0 writes nothing. Then explain what happens when a caller passes the same array as both `in` and `out`, and why the `const` on `in` does not forbid that aliasing.",
    ),
    "c-013": dict(
        cases=[
            (
                "Expand the macro by hand: `SQUARE(3 + 3)` becomes `((3 + 3)*(3 + 3))`, which is 36.",
                "The parentheses around each `x` and the whole body keep the argument grouped, so the edit gives a true square, and 36 is not 25.",
                "Expanding without the parentheses, `3 + 3*3 + 3`, and predicting 15. That is what an unparenthesized `#define SQUARE(x) x*x` would produce, and it still fails, for the wrong reason.",
                "Run `cc -E` on the file and read the expanded line, then print `SQUARE(3 + 3)` and see 36.",
            ),
            (
                "Find the changed initializer: with `int value = 4;` the call passes 4, the helper returns 16, and `value` ends at 5.",
                "`&&` evaluates the left side first and `result == 9` is already false, so the CHECK fails without ever comparing 5 to 4; restoring 3 makes both sides true.",
                "Repairing by switching the call to `SQUARE(value++)`. The macro expands the argument twice, so `value` is modified twice without sequencing, which is undefined behavior; Clang warns `multiple unsequenced modifications to 'value'`. Describe it rather than run it.",
                "Print `result` and `value` in separate statements and see 16 and 5 before the repair, 9 and 4 after it.",
            ),
            (
                "Assert a fact the compiler can evaluate: `sizeof(char) == 1` is an integer constant expression the standard guarantees.",
                "`_Static_assert` evaluates the expression during translation, so a true fact produces no code and no runtime cost, and the runtime CHECK repeats the same truth.",
                'Using it for a runtime value, `int n = 2; _Static_assert(n > 0, "positive");`. Clang rejects it with `static assertion expression is not an integral constant expression`; data that arrives at run time needs an ordinary check.',
                "Compile `_Static_assert(sizeof(int) == 2, ...)` and read `expression evaluates to '4 == 2'`, which proves a false assertion stops the build before the program exists.",
            ),
            (
                "Size the array with `LESSON_CAPACITY` and compute the element count with `sizeof values / sizeof values[0]` in the same scope.",
                "`values` is still an array object here, so `sizeof values` is 32 bytes and each `int` is 4, giving 8.",
                "Moving the count into a helper, `size_t count_of(int values[LESSON_CAPACITY])`. The parameter is really an `int *`, so the division gives 8 / 4 = 2 on the worker, and Clang warns `sizeof on array function parameter will return size of 'int *'`.",
                "Print the count in `main` and from the helper and see 8 and 2; pass the capacity explicitly instead.",
            ),
            (
                "Let `_Generic` select a string literal from the controlling expression's type: `3` is `int` and `3.0` is `double`.",
                "Selection happens at compile time from the type alone, and both types have an association, so `strcmp` returns 0 for both labels.",
                "Expecting `TYPE_LABEL('a')` to be `other` or `TYPE_LABEL(3.0f)` to be `floating`. In C a character constant has type `int`, so it selects `integer`, and `float` has no association here, so it falls to `default` and prints `other`.",
                "Print the labels for `'a'`, `3.0f` and `3L` and see `integer other other`.",
            ),
            (
                "Call the typed helper with 0 and -3; each argument is evaluated once and converted to `int` at the call.",
                "Zero times zero is 0 and -3 times -3 is 9, both well inside `int`, so the conjunction holds.",
                "Assuming every `int` input is safe. `square_int(46341)` would need 2147488281, which exceeds `INT_MAX` 2147483647, so signed overflow is undefined; 46340 gives 2147395600 and is the largest safe magnitude.",
                "Print `square_int(46340)` and see 2147395600, and compute `46341LL * 46341LL` in `long long` to see the overflow without triggering it.",
            ),
        ],
        transfer="Write `bool checked_square(int value, int *out)` that returns false when `value` is outside -46340..46340 and otherwise stores the square. Check 0, -3, 46340 and 46341, and confirm that `*out` is unchanged on rejection. Then add `#define MAX_ITEMS 4` with `_Static_assert(MAX_ITEMS <= LESSON_CAPACITY, ...)`, and explain why raising `MAX_ITEMS` to 9 fails the build, not the run.",
    ),
    "c-014": dict(
        cases=[
            (
                'Split the edited CHECK into its two operands: `parse_int("43", &out)` succeeds and stores 43, then `out == 42` compares 43 with 42.',
                '`"43"` is a complete decimal integer in range, so every rejection test passes and the parser writes 43; the CHECK fails on the comparison, not on parsing.',
                "Predicting the failure comes from the parser rejecting the input. Printing only the CHECK result hides which operand failed, so a learner may start changing a parser that is working correctly.",
                "Print the return value and `out` in separate statements and see `1 43`.",
            ),
            (
                'Read the CHECK as two facts: the call must fail on `"42x"`, and `out` must still equal its starting value. The regression changed the start to 8.',
                "`strtol` stops at `x`, so `*end != '\\0'` rejects the input before any assignment; `out` keeps 8, and the comparison with 7 fails until the initializer is 7 again.",
                'Assigning `*out = (int)value;` before the validation checks. Then `"42x"` still returns false, but `out` becomes 42, which breaks the preserve-on-rejection contract this CHECK tests even with the correct initializer.',
                "Print `out` after the call and see 8 before the repair and 7 after it.",
            ),
            (
                "Detect that no digits were consumed with `end == text`.",
                'For `""`, `strtol` performs no conversion and sets `end` to the start, so the parser returns false and leaves `out` at 7.',
                'Using `atoi(text)`. It returns 0 for `""`, the same as for `"0"`, so the caller cannot tell an empty field from a real zero, and `atoi` also reports no range errors.',
                'Print `atoi("")` and see 0, then confirm `parse_int("", &out)` returns 0 with `out` still 7.',
            ),
            (
                "Reset `errno` to 0, call `strtol` and reject when `errno == ERANGE`, before the `int` range test.",
                "The 30-digit input exceeds `long`, so `strtol` returns `LONG_MAX` 9223372036854775807 and sets `ERANGE`; the parser returns false without writing `out`.",
                "Relying only on `value > INT_MAX`. That happens to work here because the worker's `long` is 64 bits, but where `long` is 32 bits, as on 64-bit Windows, `LONG_MAX` equals `INT_MAX` and the clamped value would be accepted as 2147483647.",
                "Call `strtol` directly on the fixture and print the value and `errno == ERANGE`, and see `9223372036854775807 1`.",
            ),
            (
                "Let `strtol` accept the optional sign and range-check the resulting `long` against `INT_MIN`.",
                "`-7` converts to the `long` -7, which lies inside `int`, so the parser stores -7.",
                'Parsing with `strtoul` to reuse an unsigned helper. `strtoul("-7", ...)` negates the converted value in unsigned arithmetic and returns 18446744073709551609 with no error, so a negative input silently becomes a huge positive one.',
                'Print `strtoul("-7", &end, 10)` and see 18446744073709551609 with `errno` 0, then confirm `parse_int` yields -7.',
            ),
            (
                "Keep the grammar asymmetric: `strtol` skips leading whitespace, and the `*end != '\\0'` test rejects anything left over.",
                '`" 3"` converts to 3 with `end` at the terminator, while `"3 "` leaves `end` at the space, so the second call returns false and `out` keeps 3.',
                'Checking only `end != text` to detect digits. That accepts `"3 "`, and also `"3x"`, so the second CHECK fails and the grammar quietly changes to accept any valid prefix.',
                "Call both inputs in separate statements and print the returns and `out`: `1`, `0`, then 3.",
            ),
        ],
        transfer='Write `bool parse_port(const char *text, int *out)` that reuses `parse_int` and then requires 1..65535. Check `"80"`, `"0"`, `"65536"`, `"-1"`, `"8080 "` and `""`, and confirm that `*out` is unchanged after every rejection. Explain which check rejects `"65536"` (the domain check, not `ERANGE`) and why `" 80"` passes under the inherited whitespace policy.',
    ),
    "c-020": dict(
        cases=[
            (
                "Follow the call through the pointer: `transform(5)` calls `double_value(5)`, which returns 10.",
                "A function pointer stores which function to call, not a result, so each call evaluates its argument afresh; 10 is not 8 and the CHECK fails.",
                "Declaring the pointer with a different parameter type, such as `int (*transform)(long) = double_value;`, to make it accept more inputs. Clang rejects it with `incompatible function pointer types`, and forcing it with a cast would make every call undefined.",
                "Print `transform(4)` and `transform(5)` and see 8 and 10.",
            ),
            (
                "Run the sort and read the result: `{4, 1, 2}` becomes `1, 2, 4`, so the first two operands pass and `values[2] == 3` fails.",
                "`compare_ints` orders the elements correctly; the regression is in the data, and restoring `{3, 1, 2}` gives 1, 2, 3.",
                "Suspecting the `qsort` call and rewriting it as `qsort(values, sizeof values, sizeof values[0], compare_ints)`. That passes 12 as the element count for a 3-element array, so `qsort` reads and writes past the end, which is undefined; the count is `sizeof values / sizeof values[0]`.",
                "Print the three elements after sorting and see `1 2 4` before the repair and `1 2 3` after it.",
            ),
            (
                "Return `(a > b) - (a < b)`, which yields -1, 0 or 1 from two comparisons that cannot overflow.",
                "For `INT_MIN` and `INT_MAX`, `a > b` is 0 and `a < b` is 1, so the result is -1, and `< 0` holds.",
                "Returning `a - b`. The true difference is -4294967295, which does not fit in `int`, so the subtraction is signed overflow and undefined; on two's complement hardware it typically wraps to 1 and reports `INT_MIN` as the larger value. UBSan reports it as a signed integer overflow.",
                "Compute the difference in `long long` and see -4294967295, and print `compare_ints(&a, &b)` and see -1.",
            ),
            (
                "Return 0 for equal keys, so both 2s compare equal and stay in the array.",
                "`qsort` permutes elements and never removes them, and a comparator that returns 0 for equal keys is consistent, so the result is 1, 2, 2.",
                "Writing a comparator that never returns 0, such as `return a < b ? -1 : 1;`. It reports each 2 as greater than the other, which violates the consistency `qsort` requires, so the behavior is undefined even if one run looks sorted. Describe it rather than rely on it.",
                "Print the sorted array and see `1 2 2`, and check that `compare_ints` on two equal `int`s returns 0.",
            ),
            (
                "Pass the function name `is_even` as the predicate; `count_if` calls it once per element.",
                "2 and 4 satisfy `value % 2 == 0` and 1 and 3 do not, so the count is 2.",
                "Writing the opposite predicate as `value % 2 == 1` and reusing it on negative data. In C, `-3 % 2` is -1, so that predicate misses every negative odd number; `value % 2 != 0` is the correct test.",
                "Print `-3 % 2` and see -1, then print `count_if(values, 4, is_even)` and see 2.",
            ),
            (
                "Let the loop condition `i < n` guard every element read and every callback.",
                "With `n` 0 the condition is false at once, so neither `values[i]` nor `predicate` is evaluated, and passing `NULL` is safe.",
                "Rewriting the loop as `do { ... } while (++i < n);`. The body runs once before the test, so it reads `values[0]` through the null pointer, which is undefined and usually crashes.",
                "Run the original and see the success line; put a counter in a test predicate and confirm it was called 0 times.",
            ),
        ],
        transfer="Write `size_t count_if_ctx(const int *values, size_t n, bool (*pred)(int, void *), void *ctx)` and a predicate `bool above(int value, void *ctx)` that compares with `*(const int *)ctx`. Check that `{1, 5, 9}` with threshold 4 gives 2, threshold 9 gives 0 and `n` 0 with `NULL` gives 0. Explain why the context pointer replaces a global threshold, and what goes wrong if `ctx` points at a local that has gone out of scope.",
    ),
    "c-022": dict(
        cases=[
            (
                "Trace the queue state through the edited insertion: `enqueue(&q, 6)` stores 6 at index `(head + count) % 4`, which is 1, so the queue holds 2 and then 6.",
                "FIFO removal returns values in insertion order. The first `dequeue` still yields 2 and passes, but the second yields 6, so `out == 5` is false and the run stops at that third CHECK, not at the edited one.",
                "Predicting that the edited CHECK itself fails because the stored value changed. `enqueue` returns true whenever there is spare capacity, and the queue is empty, so the edited line passes; only the later comparison with 5 sees the different value.",
                "Run the edited pad and see `Check failed` reported on the line with `out == 5`; restore 5 and see `Worked example checks passed.`",
            ),
            (
                "Read the empty-queue contract: `dequeue` on `count == 0` returns false and must not write `*out`, so `out` keeps its initial value.",
                "With `int out = 10;` the rejected read leaves 10 in `out`, so `out == 9` is false even though `!dequeue(&q, &out)` and `q.count == 0` both hold. Restoring the initializer 9 repairs the run without touching the helper.",
                "Changing `dequeue` to store a sentinel such as 0 or 9 on failure so the CHECK passes. That hides a real item of the same value and breaks the rule that a rejected operation leaves its output unchanged.",
                "Print `out` and `q.count` after the failed call and see `10 0` with the regression and `9 0` after the repair.",
            ),
            (
                "Fill all four slots, then call `enqueue(&q, 99)` and check that it returns false with `count` still 4.",
                "`enqueue` tests `q->count == QUEUE_CAPACITY` (4) before computing the write index, so the fifth call rejects without writing `q->data[(q->head + q->count) % QUEUE_CAPACITY]`, which would overwrite the oldest value 0.",
                "Testing `head == tail` with a separate tail index to detect full. When the ring is full the tail wraps back to `head`, the same state as empty, so the queue cannot tell the two apart; storing `count` avoids that ambiguity.",
                "After the rejected write, dequeue four times and see 0, 1, 2 and 3, proving nothing was overwritten.",
            ),
            (
                "Fill the ring, dequeue twice so `head` is 2, then enqueue 4 and 5, which land at physical indices 0 and 1 because `(2 + 2) % 4` is 0.",
                "Logical order follows `head` and `count`, not physical index, so the four dequeues read indices 2, 3, 0 and 1 and yield 2, 3, 4 and 5.",
                "Writing new values at `head + count` without the modulo. With `head` 2 and `count` 2 the index 4 is one past the end of `data`, an out-of-bounds write that the sanitizer reports and that a plain run may silently survive.",
                "Print `q.head` and the physical index of each write and see indices 0 and 1 for values 4 and 5.",
            ),
            (
                "Enqueue 0, dequeue it into `out` initialized to 9, and check both the returned status and the value 0.",
                "The `bool` return reports success separately from the payload written through `out`, so a legitimate 0 replaces 9 and the status is still true.",
                "Making `dequeue` return the item and using 0 to mean empty. This queue can hold 0, so the caller could not distinguish an empty read from a stored zero.",
                "Change the enqueued value to -1 and to 0 in turn; both reads succeed and store exactly the enqueued value.",
            ),
            (
                "Push 2 and 5 by writing `stack[length++]`, check `length > 0`, then pop with `stack[--length]`.",
                "A stack removes the newest value: after two pushes `length` is 2, so the pop reads index 1 and yields 5, leaving `length` 1. The nonempty check runs before the decrement, so the unsigned `length` cannot wrap.",
                "Popping with `stack[length--]`. The postfix form reads index 2, one past the last occupied slot, which holds an indeterminate value, so the pop returns garbage rather than 5.",
                "Pop a second time and see 2 with `length` 0; a third pop must fail at `CHECK(length > 0)` instead of reading `stack[SIZE_MAX]`.",
            ),
        ],
        transfer="Write `bool push(int *stack, size_t cap, size_t *length, int value)` and `bool pop(int *stack, size_t *length, int *out)` that reject a full push and an empty pop without writing. Check that capacity 2 accepts 2 and 5, rejects 9, pops 5 then 2, and rejects a third pop with `*out` unchanged. Explain why the queue needs `count` to separate full from empty while the stack can use `length` alone.",
    ),
    "c-024": dict(
        cases=[
            (
                "Find the first element that is not less than 5: in `{2, 5, 6, 8}` that is the 5 at index 1.",
                "Lower bound returns the first position whose value is `>=` the target, so a matching element is found at its own index, and 1 is not 2.",
                'Predicting 2 because 5 "goes after 4". That is the upper-bound answer, the position after all elements `<=` the target; lower bound stops at the first equal element.',
                "Print `lower_bound(values, 4, 5)` and see 1 with the edit and 2 after restoring `{2, 4, 6, 8}`.",
            ),
            (
                "Search for 4 in `{1, 3, 3, 5}`: no element equals 4, and the first element `>= 4` is the 5 at index 3.",
                "The array is unchanged; only the target changed, so the edited CHECK compares 3 with 1 and fails. With target 3, the `high = middle` branch keeps the earlier 3 and returns 1.",
                "Using `<=` in the comparison, `if (values[middle] <= target)`. That computes the upper bound and returns 3 for target 3, past both duplicates, so the original CHECK fails too.",
                "Print `lower_bound(values, 4, 4)` and see 3; the `<=` variant prints 3 for target 3.",
            ),
            (
                "Return `n` when every element is smaller than the target, here 3 for `{2, 4, 6}` and 9.",
                "Each probe finds a value below 9 and moves `low` past it until `low` reaches `high`, which started at `n`, so the result is one past the end.",
                "Reading `values[i]` right after the call to see what was found. With `i` 3 that reads past the 3-element array, which is undefined; every caller must test `i < n` first.",
                "Print the result and see 3, and confirm it equals `sizeof values / sizeof values[0]`.",
            ),
            (
                "Start with `low` 0 and `high` equal to `n`, so an empty range never enters the loop.",
                "With `n` 0, `low < high` is false at once, no element is read, and the insertion index 0 is returned without touching the null pointer.",
                "Adding a fast path such as `if (target <= values[0]) return 0;` before the loop. It reads the first element through `NULL` when the view is empty, which is undefined and usually crashes.",
                "Run the CHECK and see the success line; the fast-path variant should only be compiled, never run, with `NULL`.",
            ),
            (
                "Use the half-open interval `[low, high)` so the answer 0 is reached by shrinking `high`, never by subtracting below 0.",
                "Every element is at least 1, so each probe sets `high = middle` until `high` reaches 0, and `low` 0 is returned.",
                "Using a closed interval with `size_t` and `high = middle - 1`. When `middle` is 0 that wraps to 18446744073709551615, `low <= high` stays true and the next probe reads far out of bounds.",
                "Print `(size_t)0 - 1` and see 18446744073709551615, then print `lower_bound(values, 3, 1)` and see 0.",
            ),
            (
                "Combine both tests: `i < 3` proves the index is in range, and `values[i] == 4` proves the element matches.",
                "4 is present at index 1, the lower bound returns 1, and both operands are true; `&&` evaluates the bounds test first, so the read is always safe.",
                "Testing only `i < 3`. For a missing target such as 5 the lower bound is 2, which is in range, so the code would report 5 present even though `values[2]` is 6.",
                "Print `lower_bound(values, 3, 5)` and see 2, then confirm that `values[2] == 5` is false.",
            ),
        ],
        transfer="Write `bool count_equal(const int *values, size_t n, int target, size_t *count)` that uses `lower_bound` and an upper bound with `<=` to count matching elements in a sorted array. Check `{1, 3, 3, 5}` for 3 (2), 4 (0) and 5 (1), and an empty `NULL` view (0). Explain why the count is the difference of the two bounds, and why that takes about 2 log2 n comparisons instead of one pass over every element.",
    ),
    "c-025": dict(
        cases=[
            (
                "Add the three node values after the edit: root 2, left 2 and right 3 give 7.",
                "`root` stores the addresses `&left` and `&right`, so `tree_sum` reads the edited `left` through its pointer, and 7 is not 6.",
                "Predicting 6 because `root` was built from copies of its children. The initializer stores pointers, not copies, so any change to `left` is visible through `root`.",
                "Print `tree_sum(&root)` and see 7 with the edit and 6 after restoring `left` to 1.",
            ),
            (
                "Evaluate the base case: `tree_sum(NULL)` returns 0 immediately, so `!= 0` is false.",
                "An empty tree has no values, and 0 is the identity for addition, so returning 0 lets every leaf combine its two empty children without special cases.",
                "Writing the base case at the leaves, `if (node->left == NULL && node->right == NULL) return node->value;`, without a null test. `tree_sum(NULL)` then dereferences a null pointer, and so does any node with exactly one child.",
                "Run the restored CHECK and see the success line; print `tree_sum(NULL)` and see 0.",
            ),
            (
                "Return 1 plus the larger child depth, with 0 for an empty subtree.",
                "Each leaf has depth 1 + 0, and the root takes 1 + max(1, 1), so the depth is 2 even though there are three nodes.",
                "Adding the child depths instead of taking the maximum, `1 + a + b`. That counts nodes, so it returns 3 for this tree and grows with width rather than with nesting.",
                "Print `tree_depth(&root)` and see 2; the summing variant prints 3.",
            ),
            (
                "Give a budget of 2: the root uses 1 and the call on the right child receives 1, enough to compare the leaf.",
                "The leaf's value is 3, so it returns true before the budget reaches 0, and `||` passes that result up through the root.",
                "Treating the budget as a count of edges and passing 1. The budget counts nodes on the path including the root, so a budget of 1 stops before the child and reports false.",
                "Print `tree_contains(&root, 3, 2)` and `tree_contains(&root, 3, 1)` in separate statements and see 1 and 0.",
            ),
            (
                "Check the budget before examining a node, so a budget of 1 examines only the root.",
                "The root holds 2, so it recurses with budget 0, and the child call returns false at once without reading the leaf.",
                "Testing `node->value == target` before `budget == 0`. The child is then examined with budget 0 and returns true, so a search limited to one level descends anyway and this CHECK fails.",
                "Compile that reordered variant and print it with budget 1 to see 1, while the lesson's helper prints 0.",
            ),
            (
                "Run both functions on one node: its two empty children supply depth 0 and sum 0.",
                "Depth is 1 + max(0, 0) = 1 and the sum is 7 + 0 + 0 = 7, so both base cases are exercised in a single call.",
                "Treating the singleton as complete evidence. A leaf-only base case without a null check also returns 1 and 7 here, yet crashes on `{2, NULL, &leaf}`, so add a one-child tree to the tests.",
                "Print `tree_depth` for `{2, NULL, &leaf}` and see 2 alongside the singleton's 1 and 7.",
            ),
        ],
        transfer="Write `bool tree_max(const struct Tree *node, int *out)` that returns false for an empty tree and otherwise stores the largest value. Check the singleton 7, the three-node tree (3), a tree with only negative values such as -5 over -9, and `NULL`, with `*out` unchanged on false. Explain why starting the search from 0 instead of from the root's value gives the wrong answer for the negative tree.",
    ),
    "c-028": dict(
        cases=[
            (
                "Add the edited elements: 3 + 4 + 6 is 13, so the CHECK on 12 fails.",
                "The prototype makes the compiler check the argument types and count, but values are a run-time matter; the call is still valid and simply returns 13.",
                "Assuming a prototype in a header keeps every caller and the definition in agreement. If `stats.h` declares `int stats_sum(const int *values, int length);` and `stats.c` does not include it, each file compiles alone and the mismatch with the `size_t` definition is undefined at link time. Including the header in `stats.c` makes Clang report `conflicting types for 'stats_sum'`.",
                "Print `stats_sum(values, 3)` and see 13 with the edit and 12 after restoring `{2, 4, 6}`.",
            ),
            (
                "Evaluate the empty call: with `length` 0 the loop never runs, so the sum stays at its initial 0 and `!= 0` is false.",
                "The contract permits `NULL` when the length is 0, and the implementation reads only inside `i < length`, so no pointer is dereferenced.",
                "Changing the implementation to `if (values == NULL) return -1;` as an error signal. That breaks the documented empty case, and -1 is also a legitimate sum such as `{-1}`, so callers cannot tell an error from data.",
                "Print `stats_sum(NULL, 0)` and see 0.",
            ),
            (
                "Call the helper on `a` and then on `b`; each call starts a fresh local `sum` at 0.",
                "The result depends only on the pointer and length passed, so the calls give 1 + 2 = 3 and 3 + 4 = 7 independently.",
                "Keeping the accumulator as `static int sum = 0;` to avoid re-initializing it. The second call then starts from 3 and returns 10, so the result depends on call history rather than on the input.",
                "Call the two arrays in separate statements and print 3 and 7; the static variant prints 3 and 10.",
            ),
            (
                "Pass the array through the `const int *` parameter and read it back afterward.",
                "The function can only read through `values`, so `values[0]` and `values[1]` are still 2 and 4 after the call.",
                "Reusing the input as scratch space, for example a running prefix sum with `values[i] += values[i - 1];`. The `const` parameter rejects that with `read-only variable is not assignable`, which is the point of putting it in the API.",
                "Print both elements after the call and see `2 4`.",
            ),
            (
                "Run the loop once for `length` 1, adding -3 to 0.",
                "`i < length` admits exactly index 0, so the sum is -3; a signed `int` accumulator holds the negative value without conversion.",
                "Stopping at `i < length - 1`, an off-by-one that skips the last element. For one element the loop never runs and the result is 0, and for `length` 0 the subtraction wraps to `SIZE_MAX` and the loop reads out of bounds.",
                "Print `stats_sum(values, 1)` and see -3; the off-by-one variant prints 0.",
            ),
            (
                "Call the pure helper twice on the same unchanged array and compare both results with 6.",
                "The function reads only its parameters and writes no shared state, so both calls compute 1 + 2 + 3 = 6.",
                "Taking identical output as proof that builds are reproducible. A file that prints `__TIME__` behaves the same way each run, yet two builds a second apart produce different binaries, because the build time is embedded.",
                "Build the same source twice to the same output name and compare with `cmp`; then repeat with a `__TIME__` line and see `cmp` report a difference.",
            ),
        ],
        transfer="Split `stats_sum` into `stats.h` and `stats.c`, add `int stats_max(const int *values, size_t length, int *out)` that returns 0 for an empty view and 1 otherwise, and include the header in both `stats.c` and `main.c`. Check `{2, 4, 6}`, `{-3}` and `NULL` with length 0. Then change the header's length type to `int`, rebuild and read the diagnostic, and explain why it only appears because `stats.c` includes its own header.",
    ),
    "c-031": dict(
        cases=[
            (
                "Evaluate both operands: `add_checked(8, 5, &out)` passes both guards and stores 13, then `out == 12` is false.",
                "8 + 5 is far from either limit, so the function takes the normal path and returns true; the CHECK fails on the comparison, not on overflow.",
                'Inspecting the call with `printf("%d %d", add_checked(8, 5, &out), out);`. The order in which arguments are evaluated is unspecified, so `out` may be read before the call stores 13 and print the old 0.',
                "Print the return value and `out` in separate statements and see 1 and then 13.",
            ),
            (
                "Read the guard: for `b` 1, `a > INT_MAX - b` is `INT_MAX > INT_MAX - 1`, which is true, so the function returns false before any addition and leaves `out` alone.",
                "The function is correct; the regression changed the initial value to 10, so `out == 9` fails until the initializer is 9 again.",
                "Checking after the fact: `int sum = a + b; if (b > 0 && sum < a) return false;`. The addition has already overflowed, which is undefined, so the compiler may assume it did not; Clang at `-O2` compiles that function to an unconditional store and `return true`.",
                "Compile that variant with `-O2 -S` and see that the comparison is gone; run the lesson's version and print `out` as 9.",
            ),
            (
                "Use the negative branch: for `b` -1, reject when `a < INT_MIN - b`, which is `INT_MIN < INT_MIN + 1`.",
                "`INT_MIN - b` is `INT_MIN + 1`, which is representable, so the guard itself cannot overflow and the call returns false with `out` still 9.",
                "Reusing the positive test for every `b`, `if (a > INT_MAX - b)`. With `b` -1 the expression `INT_MAX - (-1)` overflows during the check itself, which is undefined, so the guard is not a guard.",
                "Print `add_checked(INT_MIN, -1, &out)` and see 0, then print `out` and see 9.",
            ),
            (
                "Let `b` 0 skip both inequalities, because adding 0 can never overflow.",
                "`b > 0` and `b < 0` are both false, so the function stores `INT_MAX` and then `INT_MIN` and returns true each time.",
                "Writing the positive test with `>=`, `a >= INT_MAX - b`. For `INT_MAX` plus 0 that is `INT_MAX >= INT_MAX`, so a valid sum at the exact boundary is rejected.",
                "Print `add_checked(INT_MAX, 0, &out)` and see 1, then confirm `out == INT_MAX`.",
            ),
            (
                "Compare `a` with `SIZE_MAX / b` before multiplying: `SIZE_MAX` is greater than `SIZE_MAX / 2`, so the product would not fit.",
                "Division cannot overflow, and the inequality is exact for unsigned values, so the helper returns false before computing `a * b` and leaves `out` at 7.",
                "Multiplying first and testing `product < a`. Unsigned multiplication wraps without undefined behavior, but the test misses many wraps: `3 * 2^63` wraps to 9223372036854775808, which is not less than 3. A wrapped size passed to `malloc` allocates far too little.",
                "Print `(size_t)3 * ((size_t)1 << 63)` and see 9223372036854775808, then confirm `size_product(SIZE_MAX, 2, &out)` returns 0.",
            ),
            (
                "Test `b != 0` before dividing, so a zero factor skips the division and the product 0 is stored.",
                "Any count times 0 is 0, which fits, so the helper returns true with `out` 0.",
                "Dropping the `b != 0` guard, `if (a > SIZE_MAX / b)`. With `b` 0 that divides by zero, which is undefined; on x86-64 it traps with a floating-point exception signal, while on ARM64 it silently yields 0.",
                "Print `size_product(SIZE_MAX, 0, &out)` and `out` in separate statements and see 1 and 0.",
            ),
        ],
        transfer="Write `void *checked_array_alloc(size_t count, size_t size)` that uses `size_product` and returns `NULL` when it fails or when the product is 0, otherwise `malloc(product)`. Check `count` 4 with `sizeof(int)`, `count` `SIZE_MAX` with size 2, and `count` 0, freeing every non-null pointer. Explain why calling `malloc(count * size)` directly with the second input could return a small block that later writes overrun.",
    ),
    "c-037": dict(
        cases=[
            (
                "Multiply workers by iterations: 5 workers each adding 100 under the mutex give exactly 500.",
                "5 is still within the `workers <= 5` guard for the `threads[5]` array, and each increment is a locked read-modify-write, so none are lost and 500 is not 400.",
                "Predicting a count that varies from run to run near 400 or 500, as with an unprotected counter. The mutex serializes every `s->count++`, so the total is exact on every run; only the interleaving changes.",
                "Print `locked_total(5, 100)` several times and see 500 each time.",
            ),
            (
                "Note that `iterations` is per worker: with 2 workers each running 7 increments the total is 14.",
                "Each thread runs the full `for` loop over `s->iterations`, so adding a worker adds another 7, and the edited CHECK compares 14 with 7.",
                "Reading the second argument as a total split among the workers and predicting 7. Nothing in `increment_worker` divides the work, so the count scales with the number of threads.",
                "Print `locked_total(2, 7)` and see 14, and `locked_total(1, 7)` and see 7.",
            ),
            (
                "Create and join both workers even though each loop body runs zero times.",
                "Each worker reads `s->iterations` as 0, never locks the mutex and returns, so `count` stays 0; joining before the mutex is destroyed keeps the cleanup order valid.",
                "Skipping `pthread_join` when there is no work to wait for. The workers still read `s->iterations` through a pointer to `locked_total`'s local `s`, so returning first leaves them reading a dead object, which is undefined.",
                "Run the CHECK under AddressSanitizer and UndefinedBehaviorSanitizer and see a clean run with 0.",
            ),
            (
                "Hold the mutex and wait in `while (!s.ready)`, then read `s.value` while still holding the lock.",
                "The worker sets `value` and `ready` under the same mutex before signaling, so when the loop exits the predicate is true and `value` is the published 42, whether the signal came before or after the wait began.",
                "Writing `if (!s.ready)` instead of `while`. `pthread_cond_wait` may return without a signal (a spurious wakeup), and with `if` the parent then reads `value` while `ready` is still false and can return 0.",
                "Print `wait_for_value()` and see 42; the loop re-tests `ready` after every return from `pthread_cond_wait`.",
            ),
            (
                "Call the fixture twice; each call initializes its own mutex, condition variable and `ready` flag and destroys them after joining.",
                "Nothing survives between calls, so the second wait depends only on its own worker's publication and returns 42.",
                "Making `struct ReadyState s` static to avoid reinitializing it. Its initializer runs once, so the second call sees `ready` already true, skips the wait and returns the first run's value. The CHECK still passes because both values are 42, so publish a different value per run to expose it.",
                "Print both calls in separate statements and see 42 and 42; give each run a distinct value to make stale state visible.",
            ),
            (
                "Run 2 workers of 5 increments and 5 workers of 2, each under the same locked increment.",
                "Every protected increment is counted exactly once, so both totals equal the product, 10, regardless of how the threads are scheduled.",
                "Dropping the lock because the counts are small, `s->count++;` alone. Unsynchronized concurrent writes are a data race and undefined behavior; a small test may still print 10 by luck, so a passing run proves nothing, and ThreadSanitizer is the tool that reports it. Describe it rather than run it.",
                "Print `locked_total(2, 5)` and `locked_total(5, 2)` in separate statements and see 10 and 10.",
            ),
        ],
        transfer="Write `int wait_for_count(int target)` that starts 3 workers, each adding 1 to a shared count under a mutex and broadcasting with `pthread_cond_broadcast`, while the parent waits in a `while (count < target)` loop. Check targets 0, 1 and 3, joining every worker before destroying the objects. Explain why waiting with `while (count != target)` can block forever when several increments land before the parent wakes, while `count < target` cannot.",
    ),
}
