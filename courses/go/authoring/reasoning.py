"""Per-case solution reasoning for the explained Go solutions.

Each entry holds one (approach, why it holds, plausible wrong approach, verify)
tuple per case, in case order, plus a lesson-specific transfer paragraph that
replaces the generic one. Every sentence refers to its own lesson's code,
values and failure modes; do not paste a shared paragraph across lessons.
"""

LABELS = ("Approach", "Why it holds here", "A plausible wrong approach", "Verify")

REASONING = {
    "go-002": dict(
        cases=[
            (
                "Evaluate the edited line before the check: both operands of `8 / 2` are integers, so Go performs integer division and `a` becomes 4. Line `b := float64(7) / 2` is untouched and still holds 3.5.",
                "The check is a conjunction whose first operand is `a == 3`. With 4 in `a` that operand is false, so `check` panics with `division` no matter what `b` holds.",
                "Expecting the original `7 / 2` to round to 4 and therefore predicting that the edit changes nothing. Go integer division truncates toward zero, so the original `a` is 3 and the edited `a` is 4, which is exactly why the check now fails.",
                "Add `fmt.Println(a, b)` above the check. The edited run prints `4 3.5` and panics with `division`; after restoring `7 / 2` it prints `3 3.5` and then `Worked example checks passed.`",
            ),
            (
                "Narrow by hand before running: a `uint8` keeps only the low eight bits, which is the value modulo 256. For 260 that is 4, and for the regressed 261 it is 5.",
                "Because `n` is a variable rather than a constant, `uint8(n)` is a legal run-time conversion that wraps instead of failing, so the check sees 5 and panics with `narrowing`. Restoring 260 restores 4.",
                "Repairing the program by writing `small := uint8(260)` or by changing the check to 5. The first is rejected at compile time because the constant 260 overflows `uint8`, and the second hides the regression by rewriting the claim to match the bug.",
                "Print `small` with each input: 261 shows 5 and 260 shows 4. As an extra control, `n := 516` also yields 4 because 516 is 2 times 256 plus 4, which confirms that only the low byte survives.",
            ),
            (
                "Give both operands the type `int64` before multiplying, so the multiplication itself runs in 64 bits and `a*b` is 2500000000.",
                "The product exceeds the `int32` maximum of 2147483647 but is far below the `int64` maximum of about 9.22e18, so no wraparound happens and the equality holds exactly.",
                "Multiplying two `int32` variables and converting the result: `x, y := int32(50000), int32(50000)` followed by `int64(x*y)` gives -1794967296, because the product wrapped modulo 2 to the 32nd before the conversion. Writing the same thing with constants does not even compile, since the constant product overflows `int32`.",
                "Run the case and confirm the success line. Then print `int64(x*y)` for the `int32` variables beside `a*b`; seeing -1794967296 next to 2500000000 shows why the width must be chosen before the operation.",
            ),
            (
                "Store 0.1 and 0.2 in `float64` variables, add them, and compare the absolute difference from 0.3 with the tolerance `1e-15` instead of testing equality.",
                "Neither 0.1 nor 0.2 is exactly representable in binary, so `a+b` is 0.30000000000000004. Its distance from the stored 0.3 is about 5.55e-17, far below `1e-15`, so the check passes for this one addition.",
                "Testing `a+b == 0.3`, which is false for the variables. A subtler mistake is checking `0.1+0.2 == 0.3` written as literals: Go evaluates untyped constant expressions exactly, so that line is true and hides the `float64` rounding the variables expose.",
                "Print `a+b` and `math.Abs((a+b)-0.3)`: the output is `0.30000000000000004` and `5.551115123125783e-17`. The `rounding` check then passes and the success line appears.",
            ),
            (
                'Call `strconv.ParseInt("12x", 10, 64)` and treat the returned `err` as the result that matters; the numeric value is discarded with `_`.',
                "`ParseInt` must consume the whole string as a base-ten integer. The trailing `x` is not a digit, so it returns 0 and a `*strconv.NumError` wrapping `strconv.ErrSyntax`, and `err != nil` holds.",
                'Reading the text with `fmt.Sscanf("12x", "%d", &n)`. It scans the leading `12`, stops at `x` and reports no error for the unread tail, so the program would silently accept 12 from malformed input.',
                'Print `err`: it reads `strconv.ParseInt: parsing "12x": invalid syntax`, and `errors.Is(err, strconv.ErrSyntax)` is true. Changing the text to `12` makes `err` nil, which shows the check distinguishes valid from invalid input.',
            ),
            (
                "Compute `-7/2` and `-7%2` with Go's rule that integer division truncates toward zero, giving -3 and -1, and confirm the reconstruction `q*2+r == -7`.",
                "Truncating -3.5 toward zero gives -3, and the remainder must satisfy `q*2 + r == -7`, so it is -1 and takes the sign of the dividend. All three conjuncts hold.",
                "Expecting floor division as in Python, which gives -4 and remainder 1. The reconstruction identity still holds for that pair, but `q == -3` fails, so a port of Python code that relies on floor semantics would compute different buckets for negative inputs.",
                "Print `q, r`: the output is `-3 -1`. For a floor-style result you would need `math.Floor(float64(-7) / 2)`, which prints -4 and makes the difference visible.",
            ),
        ],
        transfer="Repeat the lesson with new numbers in your own pad. Predict `9 / 4` as 2 and `float64(9) / 4` as 2.25, narrow a variable holding 300 to `uint8` and predict 44, and divide -9 by 4 to predict -2 with remainder -1. Write one check per claim, then explain which check a rounding, floor-division or constant-narrowing implementation would fail.",
    ),
    "go-004": dict(
        cases=[
            (
                "Evaluate the edited check with the helper's definition: `twice(8)` returns 16, so the first operand `twice(8) == 14` is false before `twice(0) == 0` is even considered.",
                "`twice` is a pure function of its argument, so nothing else can change its answer. The edited claim pairs input 8 with the output for 7, which is simply false, and `check` panics with `twice`.",
                "Predicting that the check still passes because `twice` is correct. A correct helper cannot rescue a wrong claim; the check states a specific input and output pair, and that pair is what changed.",
                "Run the edited check and read the `twice` panic, then print `twice(8)` to see 16. Restore 7 and the program prints `Worked example checks passed.`",
            ),
            (
                "Read the guard in `positiveArea`: it returns an error only when `w <= 0 || h <= 0`. With the regressed call `positiveArea(1, 4)` both dimensions are positive, so it returns 4 and a nil error.",
                "The second check asserts `err != nil`, so a valid rectangle makes it panic with `invalid area`. Restoring width 0 brings back the rejected input the check was written for.",
                "Repairing the panic by tightening the guard to `w <= 1`. That makes this line pass but also rejects a genuine 1 by 4 rectangle, so it changes the domain policy instead of fixing the test input.",
                "Print `err` for both calls: width 1 shows `<nil>` and width 0 shows `positive dimensions required`. After the repair both checks pass and the success line appears.",
            ),
            (
                "Call `reassign(n)` with `n` holding 5 and inspect `n` afterward. The parameter `x` inside `reassign` is a separate copy of the argument.",
                "Go passes an `int` by value, so `x = 99` writes only to the helper's local copy, which disappears when the function returns. The caller's `n` is still 5 and `check(n == 5, ...)` passes.",
                "Expecting 99 because the helper assigns to its parameter, as a pass-by-reference language would. To really change the caller you would need `func reassign(x *int) { *x = 99 }` and the call `reassign(&n)`.",
                "Print `n` after the call and see 5. Then write the pointer version in a scratch pad: `n` becomes 99, which confirms that only an explicit pointer shares the caller's variable.",
            ),
            (
                "Implement `bounds` with one comparison: when `a < b` return `a, b`, otherwise return `b, a`. Both values come back as separate results.",
                "For 9 and 2 the test `9 < 2` is false, so the function returns 2 then 9, which is exactly the order the check expects.",
                "Writing the condition backward as `if a > b { return a, b }`. For 9 and 2 it returns 9 then 2, so `low == 2` fails and the `bounds` panic points straight at the comparison.",
                "Check three inputs: `bounds(9, 2)` and `bounds(2, 9)` both give `2 9`, and `bounds(4, 4)` gives `4 4`. The equal case shows the else branch is harmless when the values match.",
            ),
            (
                "Start the accumulator at 0 and range over the variadic slice `values`, adding each element.",
                "When `total()` receives no arguments, `values` is a nil slice and the loop runs zero times, so the result is the additive identity 0. For 1, 2 and 3 the loop adds to 6.",
                "Seeding the accumulator with `values[0]` and looping from index 1. That works for `total(1, 2, 3)` but `total()` panics with an index out of range, because a call with no arguments is a normal input here.",
                "Print `total()` and `total(1, 2, 3)` to see 0 and 6. Also try `total([]int{4, 5}...)`, which passes an existing slice and returns 9.",
            ),
            (
                "Call `positiveArea(3, -1)` and keep both results, checking that `err` is non-nil and that `value` is the reserved 0.",
                "The guard uses `||`, so a negative height alone is enough to take the error path, which returns 0 together with the error.",
                "Writing the guard as `w <= 0 && h <= 0`. It rejects only rectangles where both sides are invalid, so `positiveArea(3, -1)` returns -3 with a nil error and the `negative dimension` check panics.",
                "Print `value, err` and see `0 positive dimensions required`. Swapping to `positiveArea(-3, 1)` must give the same result, which confirms either dimension alone triggers the policy.",
            ),
        ],
        transfer="Write a `perimeter(w, h int) (int, error)` helper with the same policy as `positiveArea`. Check that 3 by 4 returns 14, that 0 by 4 and 3 by -1 return errors, and pass a `Rect{W: 3, H: 4}` struct to a helper that changes `W` to show the caller's struct keeps 3. Explain which check an `&&` guard or a pointer-free mutation would fail.",
    ),
    "go-007": dict(
        cases=[
            (
                "Count the edited string in two units. `A` and `!` are one byte each and U+1F642 needs four bytes in UTF-8, so `len(text)` becomes 6 while `utf8.RuneCountInString(text)` becomes 3.",
                "`len` on a string always reports bytes, so the first operand `len(text) == 5` is false as soon as one more ASCII byte is appended, and `check` panics with `text units`.",
                'Assuming the emoji counts as two units, as `"🙂".length` does in JavaScript\'s UTF-16 strings, and predicting lengths of 3 and 4 for the original and edited strings. Go strings hold UTF-8 bytes, so the lengths really are 5 and 6.',
                "Print `len(text), utf8.RuneCountInString(text)`: the edited run shows `6 3` before the `text units` panic, and the restored line shows `5 2` and the success line.",
            ),
            (
                "Trace the copy and the edit separately. `[]byte(original)` allocates new storage holding `c a t`, and the regressed `data[1] = 'b'` overwrites the `a`, producing `cbt`.",
                '`original` is untouched in both versions because strings are immutable and the conversion copied its bytes, so the failing operand is `string(data) == "bat"`. Writing index 0 replaces the `c` and restores `bat`.',
                "Trying to edit the string directly with `original[0] = 'b'`. The compiler rejects it because string bytes cannot be assigned, which is exactly why the lesson converts to a byte slice first.",
                "Print `original, string(data)`: the regression shows `cat cbt` and the repair shows `cat bat`, and only the repaired run reaches the success line.",
            ),
            (
                "Build a one-byte string from 0xff and ask `utf8.ValidString` about it, expecting false.",
                "No UTF-8 sequence can start with 0xff, and the conversion `string([]byte{0xff})` copies bytes without checking them, so the string exists but fails validation.",
                "Testing validity with `utf8.RuneCountInString(text) == 0`. It returns 1 because each invalid byte is counted as one `utf8.RuneError`, so the malformed input would look like a normal one-rune string.",
                "Print `len(text)`, `utf8.ValidString(text)` and `[]rune(text)`: the output is `1`, `false` and `[65533]`, where 65533 is the replacement character produced by decoding.",
            ),
            (
                'Convert `"A🙂"` to `[]rune`, which yields two code points, and slice from index 1 so the emoji stays whole.',
                "Rune indexes count code points rather than bytes, so `r[1:]` holds exactly U+1F642 and converting it back encodes the same four bytes.",
                'Byte-slicing the original string as `"A🙂"[1:2]` to get the second character. That yields the single lead byte 0xf0, which is invalid UTF-8 and prints as a replacement character instead of the emoji.',
                "Print `len(r)` and `len(string(r[1:]))` to see 2 and 4, and confirm `utf8.ValidString(string(r[1:]))` is true while the byte slice `[1:2]` is not valid.",
            ),
            (
                'Count runes in `"e\\u0301"`: the letter `e` plus U+0301 COMBINING ACUTE ACCENT, which is two code points even though it can display as one character.',
                "`RuneCountInString` counts code points, so the result is 2. The string is three bytes because the combining mark needs two bytes in UTF-8.",
                'Expecting 1 because the output looks like `é`, or comparing it with the precomposed `"\\u00e9"`. That form is one rune, and `"e\\u0301" == "\\u00e9"` is false because Go compares bytes and the standard library does not normalize.',
                'Print `utf8.RuneCountInString` and `len` for both spellings: `"e\\u0301"` gives 2 runes and 3 bytes, while `"\\u00e9"` gives 1 rune and 2 bytes.',
            ),
            (
                'Apply `strings.TrimSpace` to `" \\tblue sky\\n"`, which removes leading and trailing Unicode whitespace and leaves interior characters alone.',
                "The leading space and tab and the trailing newline are all whitespace, while the space between `blue` and `sky` is interior, so the result is exactly `blue sky`.",
                'Using `strings.Trim(raw, " ")` or `strings.ReplaceAll(raw, " ", "")` on the raw input. The first trims only spaces, leaving the tab and newline, and the second also deletes the interior space and returns `\\tbluesky\\n`.',
                'Print with `fmt.Printf("%q\\n", label)` so invisible characters show: it prints `"blue sky"`, while the `Trim` version prints `"\\tblue sky\\n"`.',
            ),
        ],
        transfer='Repeat the measurements with `"naïve"` written with the precomposed U+00EF. Predict 6 bytes and 5 runes, take the first three runes as `naï` with a rune slice, show that the byte slice `[:3]` gives `na` plus a broken lead byte, and trim `"\\n naïve \\t"` to `naïve`. Explain which check byte indexing or a space-only trim would fail.',
    ),
    "go-010": dict(
        cases=[
            (
                "Follow the call through the interface: `v` stores a copy of `Counter{N: 4}`, and `v.Value()` dispatches to `Counter.Value`, which returns the stored field, 4.",
                "The check compares the dispatched result with 3, so it fails and panics with `interface dispatch`. Nothing else in the example changes.",
                "Predicting a compile error because `Counter` never declares that it implements `Valuer`. Go satisfies interfaces implicitly: having a `Value() int` method in the method set is enough, so the program compiles and fails only at the check.",
                'Print `v.Value()` and `fmt.Sprintf("%T", v)`: the edited run shows `4` and `main.Counter` before the panic, and restoring 3 brings back the success line.',
            ),
            (
                "Trace `c.Add(2)`: Go takes `&c` for the pointer-receiver call, so `c.N += 2` updates the caller's variable. Starting from the regressed 4 gives 6.",
                "The check expects 3 plus 2, so 6 makes it panic with `pointer receiver`. Restoring `Counter{N: 3}` restores 5 without touching the method or the check.",
                "Compensating with `c.Add(1)` so the result is 5 again. The check passes, but the starting state is still wrong and the example no longer demonstrates the intended mutation. Changing `Add` to a value receiver is worse: `c.N` would stay at its start value.",
                "Print `c.N` after the call: 6 with the regression and 5 after the repair. As a control, temporarily give `Add` a value receiver and observe that `c.N` stays at 3.",
            ),
            (
                "Call the value-receiver method `Incremented` and inspect both its return value and the caller's field.",
                "The method receives a copy of `c`, increments the copy's `N` to 4 and returns it, while the caller's `c.N` stays 3, so `got == 4 && c.N == 3` holds.",
                'Expecting `c.N` to become 4 by analogy with `Add`, or switching `Incremented` to a pointer receiver to "fix" it. With a pointer receiver the caller\'s field becomes 4 and the `receiver copy` check panics.',
                "Print `got, c.N` and see `4 3`. Call `c.Incremented()` twice and both calls return 4, which shows each call starts from the same unchanged original.",
            ),
            (
                "Store a nil `*Counter` in a variable of type `any` and compare the interface itself with nil.",
                "An interface value is nil only when both its dynamic type and value are absent. Here the dynamic type is `*Counter`, so `item != nil` is true even though the pointer inside is nil.",
                "Guarding with `if item == nil { return }` and then calling `item.(*Counter).Add(1)`. The guard does not trigger, and the call dereferences a nil pointer, which panics with an invalid memory address error.",
                'Print `fmt.Printf("%T %v\\n", item, item)` to see `*main.Counter <nil>`, and check that `item.(*Counter) == nil` is true while `item == nil` is false.',
            ),
            (
                "Use the two-result assertion `_, ok := item.(int)` on an interface that holds the string `three`.",
                "The dynamic type is `string`, not `int`, so the comma-ok form returns the zero value 0 and `ok == false` instead of panicking, and the check passes.",
                "Writing the single-result form `n := item.(int)`. With a string inside, it panics with `interface conversion: interface {} is string, not int`, turning an expected mismatch into a crash.",
                "Print the zero value and `ok` to see `0 false`, then assert `item.(string)` with comma-ok and see `three true`.",
            ),
            (
                "Give the named type `Fixed` its own `Value() int` method with a value receiver and pass both `Counter{N: 2}` and `Fixed(8)` to the unchanged `readValue`.",
                "`readValue` depends only on the `Valuer` method set, and both value types have `Value` in their method sets, so the calls return 2 and 8.",
                "Declaring the method as `func (f *Fixed) Value() int`. Then only `*Fixed` implements `Valuer`, and `readValue(Fixed(8))` fails to compile with a message that `Value` has a pointer receiver.",
                "Run the case and read the success line, then print `%T` for each argument to see `main.Counter` and `main.Fixed` handled by the same helper.",
            ),
        ],
        transfer="Add a `Doubled struct{ Base int }` whose value-receiver `Value` returns twice `Base`, and a pointer-receiver `Reset` that sets `Base` to 0. Check that `readValue(Doubled{Base: 4})` is 8, that `Reset` changes an addressable variable, and that `var d *Doubled` stored in a `Valuer` is not nil. Explain why calling `Value` through that nil pointer would panic.",
    ),
    "go-012": dict(
        cases=[
            (
                "Trace the three deferred calls in `deferOrder` in reverse registration order: the `second` append runs first, then the `first` append, then the join that writes `result`.",
                "Deferred calls run after the bare `return` and may still assign the named result, so the function returns `second,first`. The edited literal adds `!`, so the comparison is false and the check panics with `defer order`.",
                "Predicting an empty string because the bare `return` already returned. A named result can be changed by deferred functions after the return statement, which is how the join reaches the caller.",
                "Print `deferOrder()` to see `second,first`. Swapping the two append lines in the helper flips it to `first,second`, which confirms the order follows registration in reverse.",
            ),
            (
                "Evaluate when the deferred argument is captured: `defer func(v int){ result = v }(x)` copies `x` into `v` at the `defer` statement, when `x` is still 1.",
                "Changing `x` to 2 afterward cannot change the already evaluated argument, so `deferArgument()` returns 1. The edited check `!= 1` therefore rejects the same state the original accepts and panics with `argument evaluation`.",
                "Assuming the deferred call reads `x` when it finally runs and returns 2. That is the closure behavior of case 3, not the behavior of an argument passed at registration.",
                "Print `deferArgument()` and `deferClosure()` together: the output is `1 2`, and the restored check passes.",
            ),
            (
                "Defer a closure with no parameters that reads `x`, then assign 2 before returning.",
                "The closure refers to the variable `x` itself, not a snapshot, so when it runs after `x = 2` it stores 2 in `result`.",
                "Expecting 1 by analogy with case 2. Only an explicit call argument is evaluated at the `defer` statement; a captured variable is read at execution time.",
                "Print `deferClosure()` and see 2. Rewriting it to pass `x` as an argument changes the output to 1, which isolates evaluation time as the only difference.",
            ),
            (
                'Install a deferred function that calls `recover()` and converts any recovered value to text with `fmt.Sprint`, then call `panic("broken")`.',
                "`recover` returns the panic value only when it is called directly by a deferred function during panicking. Here it receives `broken`, stores it in the named `result`, and the helper returns normally.",
                "Calling `recover()` in the ordinary body before `panic`, or from a helper that the deferred function calls. In both places it returns nil, the panic continues, and the program exits with `panic: broken` instead of returning a value.",
                "Print `recoverKnown()` and see `broken`. Remove the `defer` keyword in a scratch copy and the run terminates with a nonzero status and the `panic: broken` message.",
            ),
            (
                "Register a recovery defer and then a cleanup defer that sets `cleaned` to true, and panic afterward.",
                "During panicking, deferred calls still run in reverse order: the cleanup sets `cleaned = true`, then the recovery stops the panic, so the helper returns true.",
                'Writing `cleaned = true` as an ordinary statement after `panic("fixture")`. It is unreachable, so the function returns the zero value false and the check panics with `cleanup on panic`.',
                "Print `cleanedAfterPanic()` and see `true`. Replace the cleanup defer with a plain `cleaned = true` after the `panic` call and the value becomes false, which shows the cleanup depends on deferral, not on line order.",
            ),
            (
                "Put the defer inside a helper, `scopedCleanup`, and call it once per loop iteration so each call's deferred increment runs when that call returns.",
                "Each of the three calls returns before the next starts, so the three increments happen inside the loop and `count` is 3 at the check.",
                "Writing `defer func(){ count++ }()` directly inside the loop in `main`. All three increments wait until `main` returns, so at the check `count` is still 0 and the `iteration cleanup` check panics. With real files this pattern keeps every handle open until the outer function ends.",
                "Print `count` after the loop and see 3. In the in-loop defer version the same print shows 0.",
            ),
        ],
        transfer="Write `releaseOrder() (log string)` that acquires `db`, `cache` and `file` in that order and defers appending each name to a slice that a first-registered defer joins into `log`. Predict `file,cache,db`, then add a deferred call that passes a counter as an argument and one that captures it, and explain which result each would report after the counter changes.",
    ),
    "go-015": dict(
        cases=[
            (
                "Instantiate `first` with the edited slice `[]int{5, 5}`. The function returns `items[0]`, so `a` becomes 5 and `okA` stays true.",
                'Only `a == 4` changes: `okA`, `okB` and `b == "red"` still hold, so the conjunction fails on the integer value and panics with `generic first`.',
                "Predicting that the duplicate makes `okA` false or that type inference changes. `first` neither inspects duplicates nor depends on the values, and `T` is still inferred as `int` from the slice type.",
                "Print `a, okA` and see `5 true` before the panic. Restoring `4` restores the success line.",
            ),
            (
                "For an empty slice, `first` declares `var zero T` and returns it with `false`, so for `[]int{}` the results are 0 and false.",
                "The original check accepts exactly that state. The edited `v != 0` is false because 0 is the zero value of `int`, so the same program state now panics with `empty generic`.",
                "Returning `items[0]` without the length test, which panics with an index out of range on the empty slice, or returning a sentinel such as -1, which does not compile because -1 is not a valid value for every `T`.",
                "Print `v, ok` for `first([]int{})` and `first([]int{0})`: they show `0 false` and `0 true`, which is why the boolean, not the value, reports presence.",
            ),
            (
                "Walk the input once, record each value in the `seen` map and append it to `out` only the first time it appears.",
                "For 2, 1, 2 the first 2 and the 1 are appended and the second 2 is skipped, so `out` is `[2 1]` and its order follows first occurrence.",
                "Building the result by ranging over the `seen` map. Go randomizes map iteration order, so `v[0] == 2` fails on some runs, which makes the test flaky rather than reliably wrong.",
                "Print `unique([]int{2, 1, 2})` and see `[2 1]`, and `unique([]int{3, 3, 3})` to see `[3]`. Run several times to confirm the order is stable.",
            ),
            (
                "Call `sumInts` with `[]Count{3, 4}`. `T` is inferred as `Count`, which `Integer` admits through `~int`.",
                "The tilde admits any type whose underlying type is `int`, and `out += x` works on that representation, so the result is `Count(7)` with the named type preserved.",
                "Writing the constraint as `int | int64` without tildes. Then `Count` does not satisfy `Integer`, and the call fails to compile with a hint about a missing `~`.",
                'Print `fmt.Printf("%T %v\\n", sumInts([]Count{3, 4}), sumInts([]Count{3, 4}))` and see `main.Count 7`.',
            ),
            (
                "Call `sumInts` on an empty `[]int64`. The accumulator `var out T` starts at the zero value and the loop body never runs.",
                "Zero is the additive identity for every type in `Integer`, so returning the untouched accumulator gives `int64(0)` and the check passes.",
                "Seeding the accumulator with `items[0]` and summing `items[1:]`. It works for `[]Count{3, 4}` but panics with an index out of range here, because empty input is a defined case.",
                'Print `fmt.Printf("%T %v\\n", sumInts([]int64{}), sumInts([]int64{}))` and see `int64 0`.',
            ),
            (
                "Deduplicate `Red`, `red`, `Red` with the same `unique`, which compares strings with `==` through `comparable`.",
                "`Red` and `red` differ in their first byte, so they are distinct keys; only the second `Red` is dropped and the result has length 2.",
                "Lowercasing inside the generic helper to merge them. `strings.ToLower` needs a `string`, not an arbitrary `T`, so it cannot compile there, and a string-only version would silently change the policy and make the length 1.",
                "Print the result and see `[Red red]`. To fold case, map the input through `strings.ToLower` before calling `unique` and expect `[red]`.",
            ),
        ],
        transfer='Write `last[T any](items []T) (T, bool)` and `count[T comparable](items []T, x T) int`. Check `last([]string{"a", "b"})` returns `b` and true, `last([]float64{})` returns 0 and false, and `count([]Count{2, 2, 3}, 2)` returns 2. Explain which check a sentinel return or a constraint without `~` would break.',
    ),
    "go-021": dict(
        cases=[
            (
                "Run the edited slice through `parseArgs`. The flag set parses `-count=4` into `n`, finds no positional arguments and passes the range check, so it returns 4, an empty slice and nil.",
                "Only `n == 3` changes: `err == nil` and `len(args) == 0` still hold, so the conjunction fails on the count and panics with `flag`.",
                'Writing the argument as one element `"-count 4"` because that is how it looks in a shell. No shell splits a synthetic slice, so the flag package reads the name `count 4` and returns `flag provided but not defined: -count 4`. The space form needs two elements, `"-count", "4"`.',
                "Print `n, args, err` and see `4 [] <nil>` before the panic. Restoring `-count=3` restores the success line.",
            ),
            (
                "Call `parseArgs(nil)`. `IntVar` stores the default 1 in `n`, `Parse` succeeds with no arguments and 1 passes the range check, so the results are 1 and nil.",
                "The edited `err != nil` is false for that same state, so the check panics with `default`. The parse and the count are unchanged; only the expectation about the error was inverted.",
                'Changing the `IntVar` default to 0 so that "unset" is visible. The domain check then rejects 0, and the bare command returns `positive count required`, so every existing invocation without `-count` breaks.',
                "Print `n, err` for `parseArgs(nil)` and see `1 <nil>`, then restore the original check and read the success line.",
            ),
            (
                "Parse `-mystery=2` with a flag set built using `flag.ContinueOnError` and output sent to `io.Discard`, so `Parse` returns an error instead of exiting or printing usage.",
                "No flag named `mystery` is defined, so `Parse` returns `flag provided but not defined: -mystery` and `parseArgs` passes it through, making `err != nil` true.",
                "Building the set with `flag.ExitOnError`. On the unknown flag the package calls `os.Exit(2)`, so the program ends before `check` runs and nothing in the example can observe the error.",
                "Print `err` and see `flag provided but not defined: -mystery`. A defined flag such as `-count=2` returns nil.",
            ),
            (
                "Parse `-count=2` followed by `input.csv`. Flag parsing stops at the first argument that is not a flag, and `f.Args()` returns the rest.",
                "`-count=2` sets `n`, then `input.csv` ends flag parsing, so `args` is `[input.csv]` and the count of 2 passes the range check.",
                'Putting the filename first: `[]string{"input.csv", "-count=2"}`. Parsing stops at `input.csv`, so `-count=2` stays in `args` as a second positional and `n` keeps the default 1. `len(args) == 1` fails and the check panics with `positionals`.',
                "Print `n, args` and see `2 [input.csv]`; the reversed order prints `1 [input.csv -count=2]`.",
            ),
            (
                "Parse `-count=-1`. `IntVar` accepts any signed integer, so parsing succeeds, and the separate check `n < 1` rejects the value.",
                "-1 is a well-formed `int`, so the flag package reports no error; only the domain check returns `positive count required`, which makes `err != nil` true.",
                "Switching to `flag.UintVar` so the parser rejects negatives. That does reject `-1`, but `-count=0` parses as a valid `uint` and slips through, even though zero items is outside the domain.",
                "Print `err` for `-count=-1` and for `-count=0` and see `positive count required` both times, while `-count=1` returns nil.",
            ),
            (
                "Parse `-count=4`. The flag set started with the default 1, and the explicit flag overwrites it during `Parse`.",
                "An explicit value is applied after the default, so `n` is 4 with no error. If the flag repeats, the last occurrence wins: `-count=4 -count=2` gives 2.",
                "Deciding whether the user set the flag by comparing `n` with the default 1. An explicit `-count=1` looks identical to no flag, so a lower-priority environment value would wrongly win. `f.Visit` reports only the flags actually set.",
                "Print `n` for `-count=4` and for `-count=4 -count=2` and see `4` and `2`.",
            ),
        ],
        transfer='Write `resolveCount(args []string, env map[string]string) (int, error)` with precedence flag, then `env["COUNT"]`, then the default 1, using `f.Visit` to learn whether `-count` was set. Check no flag and no env gives 1, env 3 gives 3, env 3 with `-count=1` gives 1 and `-count=0` returns an error. Explain why comparing with the default would get the third case wrong.',
    ),
    "go-025": dict(
        cases=[
            (
                "Trace the edited sends: the buffer of capacity 2 now holds 3 and 3, `close` marks the channel finished, and `range` receives both values before it stops.",
                "Both sends complete without a receiver because the buffer has room for two, and close keeps buffered values, so the sum is 6 and the check `sum == 5` panics with `drain`.",
                "Predicting a deadlock because nothing receives during the sends, or a zero sum because close discards the buffer. Capacity 2 lets both sends finish, and `range` drains buffered values before it observes the close.",
                "Print `sum` and see 6 before the panic. As a separate experiment, delete `close(ch)`: the loop drains both values and then the runtime stops with `fatal error: all goroutines are asleep - deadlock!`.",
            ),
            (
                "Use the two-result receive to read the regressed state: the first receive yields 1 with `okA` true and the second yields the zero value with `okB` false.",
                "The check requires the delivered value to be 0, so 1 fails `a == 0` and panics with `closed presence`. Sending 0 again makes both received values zero while `ok` still separates them.",
                "Testing completion with `b == 0` instead of `okB`. With the original program both `a` and `b` are 0, so value comparison cannot tell a delivered zero from the closed channel's zero.",
                "Print `a, okA, b, okB`: the regression shows `1 true 0 false` and the repair shows `0 true 0 false`.",
            ),
            (
                "Let `produce` own the channel: it sends 1 and 2 on the unbuffered channel and its deferred `close` runs after the last send, which ends the consumer's `range`.",
                "Each unbuffered send waits for the receive, so both values arrive in order, and the close happens only after the producer has finished sending, so `count` is exactly 2.",
                "Leaving out the `defer close(out)` in `produce`. The consumer receives two values and then waits forever on an open channel with no sender, and the runtime reports `fatal error: all goroutines are asleep - deadlock!`.",
                "Collect the values into a slice and print it to see `[1 2]` with `count` 2. Closing from `main` before the producer finishes instead produces `panic: send on closed channel`.",
            ),
            (
                "Send 4 and 5 into a channel of capacity 2 with no receiver, then read `len` and `cap` before draining.",
                "Two sends fit the buffer, so neither blocks; `len(ch)` reports the two queued values and `cap(ch)` the fixed capacity 2.",
                "Adding a third send `ch <- 6` before the receives. The buffer is full and no goroutine receives, so `main` blocks forever and the run ends with the all goroutines are asleep deadlock error.",
                "Print `len(ch), cap(ch)` before and after the two receives and see `2 2`, then `0 2`.",
            ),
            (
                "Use a nil receive channel as the disabled arm and a closed `ready` channel as the live one.",
                "A receive from a nil channel never proceeds, so `select` can only choose `<-ready`, which is immediately ready because the channel is closed. `selected` becomes true every run.",
                "Disabling the arm with a closed channel instead of nil. A closed channel is always ready, `select` picks uniformly at random among ready arms, and about half the runs panic with `nil selected`.",
                "Run the case several times and it always passes. In the closed-channel version, repeated runs may succeed or panic with `nil selected` unpredictably.",
            ),
            (
                "Copy the slice with `append([]int(nil), original...)` before sending it, then mutate `original`.",
                "The copy has its own backing array, so `original[0] = 9` changes only the original, and the received slice still holds 1.",
                "Sending `original` directly. The channel copies only the slice header, which points at the same backing array, so the later write makes `received[0]` 9 and the check panics with `copy`.",
                "Print `received, original` and see `[1] [9]`; with the direct send the output is `[9] [9]`.",
            ),
        ],
        transfer="Write `squares(n int, out chan<- int)` that sends 1, 4, up to n*n and closes `out`, and sum its output with `range`. Check `squares(3)` totals 14, `squares(0)` totals 0 because the range ends at once, and a channel of capacity 3 holds all three values before the consumer starts. Explain which run deadlocks if the producer forgets to close.",
    ),
    "go-026": dict(
        cases=[
            (
                "Cancel a fresh `WithCancel` context and read `ctx.Err()` immediately; it is `context.Canceled`, which makes the edited `!=` comparison false.",
                "`cancel` closes `Done` and records the error before it returns, so no receive or delay is needed. The edited check rejects that state and panics with `cancel`.",
                "Predicting that `Err` stays nil until something receives from `ctx.Done()`, so the edited check would pass. Cancellation is recorded synchronously by `cancel`, not by observers.",
                "Print `ctx.Err()` and see `context canceled`, and call `cancel()` a second time to confirm nothing changes and nothing panics.",
            ),
            (
                "Cancel the parent of a derived child and read both errors; both are `context.Canceled` because cancellation flows from parent to children.",
                "The edited check requires `parent.Err()` to differ from `context.Canceled`, which is false right after `cancel()`, so it panics with `tree` while the child condition still holds.",
                "Deriving the child from `context.Background()` instead of `parent`. The child is then unrelated, its `Err` stays nil after the parent is canceled, and the original check panics with `tree`.",
                "Print `parent.Err(), child.Err()` and see `context canceled context canceled`. Keep `defer stop()`: `go vet` reports a lost cancel function when a derived context's cancel is discarded.",
            ),
            (
                "Cancel a child derived from `context.Background()` and compare the two errors.",
                "Cancellation propagates only downward, so the child records `context.Canceled` while the parent is unaffected; `Background` can never be canceled and its `Err` is always nil.",
                "Assuming cancellation travels upward and checking `parent.Err() != nil`. That is never true for `Background`, so the check would panic every run.",
                "Print `child.Err(), parent.Err()` and see `context canceled <nil>`.",
            ),
            (
                "Create the context with a deadline at `time.Unix(0, 0)`, which is already in the past, so it is done when `WithDeadline` returns.",
                "A context whose deadline has passed is created already expired with `context.DeadlineExceeded`, which is a different error from `context.Canceled`, so the check passes without sleeping.",
                "Using `context.WithTimeout(ctx, time.Millisecond)` and checking at once. `Err` is still nil at that moment and the check panics with `deadline`; adding a sleep makes it pass only when the scheduler cooperates.",
                "Print `ctx.Err()` and see `context deadline exceeded`, and print `ctx.Deadline()` to see the 1970 time with `true`.",
            ),
            (
                "Have `contextValue` check `ctx.Err()` before doing any work and return 0 with that error when the context is already done.",
                "The context was canceled before the call, so the preflight returns `0, context.Canceled` and the calculation never runs.",
                "Computing first and reporting afterward, as in `return 2 * x, ctx.Err()`. The error is correct, but `v` is 8, so the check panics with `refusal` and a caller may use a result from canceled work.",
                "Print `v, err` and see `0 context canceled`.",
            ),
            (
                "Call the same helper with `context.Background()`, which is never canceled, so the preflight passes and the helper returns `2 * 4`.",
                "`ctx.Err()` is nil for a live context, so the helper reaches `return 2*x, nil` and the check sees 8 with no error.",
                "Passing `nil` because no cancellation is wanted. The helper calls `ctx.Err()` on a nil interface and panics with a nil pointer dereference; use `context.Background()` or `context.TODO()`.",
                "Print `v, err` and see `8 <nil>`.",
            ),
        ],
        transfer="Write `sumUntil(ctx context.Context, xs []int) (int, error)` that checks `ctx.Err()` before each element. Check it returns 6 and nil for 1, 2, 3 under `Background`, 0 and `context.Canceled` for a canceled context, and 0 and `context.DeadlineExceeded` for a deadline at `time.Unix(0, 0)`. Explain why checking only after the loop would return the full sum together with an error.",
    ),
    "go-027": dict(
        cases=[
            (
                "Count goroutines in the edited loop: starting at 1 and stopping before 4 launches three workers, each calling `Inc` 100 times.",
                "Every increment holds the mutex and `wg.Wait` joins all workers before `Value` reads, so the result is exactly 300 on every run and `c.Value() == 400` panics with `count`.",
                "Predicting a different total on each run because goroutines interleave. The lock makes each increment indivisible and the join waits for all of them, so the value is deterministic; only an unlocked `c.n++` would lose updates.",
                "Print `c.Value()` and see 300 before the panic. `go run -race` on the restored program reports no data race and prints the success line.",
            ),
            (
                "Add the two deltas: with the regression both calls add 4, so `Load` returns 8 instead of 7.",
                "Atomic adds compose exactly, so 8 is the true sum of the regressed deltas and the check panics with `atomic`. Restoring the first delta to 3 gives 7.",
                "Moving the adds into a helper `func add(c atomic.Int64, d int64)` that takes the counter by value. The helper increments a copy, so `n` misses that delta and the check still panics; `go vet` reports that the helper passes a lock by value because `atomic.Int64` contains a no-copy guard.",
                "Print `n.Load()` and see 8 with the regression and 7 after the repair.",
            ),
            (
                "Move 3 from `A` to `B` inside one locked method, then read both fields with `Snapshot` under the same lock.",
                "Both fields change while the mutex is held, so no reader can see one update without the other: the snapshot is 2 and 8 and the sum stays 10.",
                "Declaring `Transfer` with a value receiver. It locks and edits a copy of the `Pair`, the caller's fields stay 5 and 5 and the check panics with `pair`; `go vet` also reports that the method passes a lock by value.",
                "Print `a, b` and see `2 8`, and run `go vet` to confirm no copylocks warning.",
            ),
            (
                "Call `once.Do` three times with the same `sync.Once`; only the first call runs the function.",
                "`Once` records that its function has run, so the second and third calls return immediately and `n` is 1.",
                "Declaring `var once sync.Once` inside the loop. Each iteration gets a fresh `Once`, so the body runs three times, `n` is 3 and the check panics with `once`.",
                "Print `n` and see 1; the in-loop declaration prints 3.",
            ),
            (
                "Store 2, swap it for 3 with `CompareAndSwap(2, 3)`, then try `CompareAndSwap(2, 4)` with the now stale expectation.",
                "The first swap finds 2 and succeeds. The second finds 3, which does not match 2, so it returns false and leaves the value at 3.",
                "Retrying the stale swap in a loop, `for !n.CompareAndSwap(2, 4) {}`. The value is 3 and nothing changes it back, so the loop spins forever. A correct retry reloads the expected value each time, as in `old := n.Load()` then `CompareAndSwap(old, old+1)`.",
                "Print the first result, the second result and `n.Load()` and see `true false 3`.",
            ),
            (
                "Read the same `Pair{A: 4, B: 6}` twice through `Snapshot`, which locks, copies both fields and unlocks.",
                "Nothing modifies the pair between the reads and each read is consistent, so both totals are 10.",
                "Adding a locked `Total` method and calling it from inside `Snapshot` while `p.mu` is held. `sync.Mutex` is not reentrant, so the second `Lock` waits forever and the runtime reports that all goroutines are asleep.",
                "Print `a, b, c, d` and see `4 6 4 6`. Run a concurrent `Transfer` between the snapshots under `go run -race` and both totals are still 10.",
            ),
        ],
        transfer="Start four goroutines that each call `Transfer(1)` 25 times on `Pair{A: 100, B: 0}`, join them and check the snapshot is 0 and 100. Add a locked `Swap` that exchanges the fields and check it gives 100 and 0. Explain which result a value receiver or a missing `wg.Wait` would produce.",
    ),
    "go-028": dict(
        cases=[
            (
                "Follow each task's `Index` through the pool: whichever worker squares the edited first value 4 returns `squareTask{0, 16}`, and the collector writes it to `out[0]`.",
                "Results are placed by index, not by arrival, so the output is `[16 1 4]` on every run. Only `v[0] == 9` fails, and the check panics with `order`.",
                "Collecting with `out = append(out, result.Value)` in arrival order. With two workers the order of sends on `results` depends on scheduling, so the output is sometimes `[1 9 4]` and the original check fails on some runs only.",
                "Print `v` and see `[16 1 4]` before the panic. Print `v` in the restored program across repeated runs, including under `go run -race`, and it is always `[9 1 4]`.",
            ),
            (
                "Trace the empty call: the feeder ranges over no items and closes `jobs`, both workers' loops end, `wg.Wait` returns and the closer goroutine closes `results`, so the collector returns `make([]int, 0)` with nil.",
                "The function produced an empty slice and no error, so the edited `err != nil` is false and the check panics with `empty`, even though every goroutine finished.",
                "Having each worker call `close(results)` when its range loop ends. With two workers and no jobs, both exit at once and the second close panics with `close of closed channel`. One goroutine, after `wg.Wait`, must own that close.",
                "Print `len(v), err` and see `0 <nil>`. The restored check passes and the program exits instead of hanging, which shows every channel reached its close.",
            ),
            (
                "Validate `workers` before creating any channel or goroutine and return `workers must be 1 through 8` for 0.",
                "The guard runs first, so the call returns nil and the error without starting the pool, and `err != nil` holds.",
                "Removing the guard and trusting the pool. With zero workers `wg.Wait` returns at once, `results` closes and the call returns `[0]` with a nil error, while the feeder goroutine stays blocked forever on `jobs <-`. The check panics with `zero workers` and the leak goes unnoticed.",
                "Print `err` for 0 and for 9 workers and see `workers must be 1 through 8` both times; 1 and 8 workers return nil.",
            ),
            (
                "Run the same input with one worker and with three, then compare the slices element by element with `slices.Equal`.",
                "Indexes fix each result's position, so both calls return `[1 4 9]` no matter how the workers interleave, and `slices.Equal` reports true.",
                "Comparing with `a == b`. Go slices are not comparable, so the program does not compile: `invalid operation: a == b (slice can only be compared to nil)`.",
                "Print `a, b` and see `[1 4 9] [1 4 9]`. Measure timing separately with a benchmark rather than inferring it from this check.",
            ),
            (
                "Treat each position as its own task: indexes 0, 1 and 2 each carry the value 2 and each write 4 into their own slot.",
                "Equal values do not merge because identity is the index, so the output has three entries and `v[2]` is 4.",
                'Collecting into `map[int]int` keyed by input value to "remove redundant work". All three tasks share the key 2, the map has one entry, the returned slice has length 1 and the check panics with `duplicates`.',
                "Print `v` and see `[4 4 4]`.",
            ),
            (
                "Start four workers for one item: one worker receives the task, the feeder closes `jobs`, and all four range loops end.",
                "After `close(jobs)` every idle worker's `range jobs` stops, so `wg.Wait` returns, `results` closes and the collector returns `[25]`.",
                "Forgetting `close(jobs)` in the feeder. The idle workers block on `range jobs` forever, `wg.Wait` never returns, `results` is never closed and the runtime reports `fatal error: all goroutines are asleep - deadlock!`.",
                "Print `v` and see `[25]`; the program exits normally, which shows no goroutine is left blocking the collector.",
            ),
        ],
        transfer='Adapt the pool to compute `len(word)` for `[]string{"go", "", "worker"}` with two workers, keeping an index on every task. Check the result is 2, 0, 6 in input order, that 9 workers are rejected before any goroutine starts and that empty input returns an empty slice. Explain what a per-worker close of `results` or a missing close of `jobs` would do.',
    ),
    "go-030": dict(
        cases=[
            (
                "Evaluate the predicate `items[i] >= 5` over the edited sorted slice `2, 5, 6, 8`: it is false at index 0 and true from index 1, so `sort.Search` returns 1.",
                "`sort.Search` returns the smallest index where a monotone predicate becomes true. The new 5 itself satisfies `>= 5`, so the boundary moves left and `i == 2` panics with `boundary`.",
                'Reading the predicate as "greater than 5" and predicting 2 again. With `>=` the element equal to the target counts, which is exactly what makes this a lower bound.',
                "Print `i` and see 1 before the panic; the restored input prints 2.",
            ),
            (
                "Search the regressed slice `2, 4, 6, 9` for the first value at least 9. The predicate is true at index 3, so the result is 3, not the not-found position 4.",
                "The check encodes that 9 is absent from the original data, so the expected answer is `len(items)`. The regression placed a 9 in the slice, and restoring 8 makes the predicate false everywhere and returns 4.",
                "Using the result as an element index without checking it, as in `found := items[i] == 9`. With the repaired data `i` is 4 and that line panics with `index out of range [4] with length 4`.",
                "Print `i, len(items)` and see `3 4` for the regression and `4 4` after the repair.",
            ),
            (
                "Allocate with `make([]int, 0, 4)` so the slice starts empty with room for four, then append 7 into the first slot.",
                "Append writes into existing capacity without reallocating, so length becomes 1, capacity stays 4 and `items[0]` is 7.",
                "Writing `make([]int, 4)` and then appending. The slice already holds four zeros, so the append produces `[0 0 0 0 7]` with length 5 and a reallocated capacity of 8, and the check panics with `capacity`.",
                "Print `len(items), cap(items), items` and see `1 4 [7]`; the wrong version prints `5 8 [0 0 0 0 7]`.",
            ),
            (
                "Count one visit per element while summing, so the work count is measured, not assumed.",
                "The loop body runs once for each of the five values, giving 5 visits and a sum of 1 through 5, which is 15.",
                "Recording work as the last index, `for i, v := range ... { visits = i }`. Indexes run 0 through 4, so `visits` ends at 4, an off-by-one that makes the `work` check panic.",
                "Print `visits, sum` and see `5 15`. For timing, put the loop in a `BenchmarkSum` in a `_test.go` file and run `go test -bench=. -benchmem` rather than asserting a clock threshold.",
            ),
            (
                "Call `sort.Search(0, f)` and count how often `f` runs.",
                "With an empty interval the search range is already closed, so `Search` returns 0 without calling the predicate, and `calls` stays 0.",
                "Adding a fast path that inspects `items[0]` before searching. On an empty slice that read panics with `index out of range [0] with length 0`, while `sort.Search` handles the empty case without touching any element.",
                "Print `i, calls` and see `0 0`.",
            ),
            (
                "Search `1, 3, 3, 5` with `items[i] >= 3`, which is false only at index 0, so the lower bound is 1.",
                "`sort.Search` always returns the first index where the predicate turns true, so with duplicates it lands on the leftmost 3.",
                "A classic binary search that returns as soon as `items[mid] == 3`. Starting from `lo = 0` and `hi = 4`, its first probe is index 2, which holds a 3, so it returns 2 and the check panics with `duplicates`.",
                "Print `i` and see 1. Searching with `> 3` returns 3, and 3 minus 1 gives the two copies of 3.",
            ),
        ],
        transfer="Write `countInRange(items []int, lo, hi int) int` for a sorted slice as the difference of two `sort.Search` lower bounds. For `1, 3, 3, 5, 8` check that [3, 4) gives 2, [6, 8) gives 0 and [0, 9) gives 5, and that an empty slice gives 0. Explain which answer an any-match binary search or a `>` predicate would get wrong.",
    ),
    "go-031": dict(
        cases=[
            (
                "Follow the edited value through the JSON handler: `count` is written as the number 4, and `json.Unmarshal` into `map[string]any` decodes it as `float64(4)`.",
                '`msg` is still `processed`, so only `v["count"] == float64(3)` fails and the check panics with `fields`.',
                'Writing the comparison as `v["count"] == 3`. The constant 3 becomes `int(3)` when compared with an `any`, and an interface holding `float64` never equals one holding `int`, so even the original record would fail.',
                "Print `v` and see `map[count:4 level:INFO msg:processed]` before the panic.",
            ),
            (
                'Inspect the decoded record from the regression: the attribute key is `request_id!`, so the map has that key and `v["request_id"]` is nil.',
                "The check looks up the exact key `request_id`, and nil never equals `lesson-7`, so it panics with `correlation`. Restoring the key name restores the lookup without touching the value.",
                'Passing the pair as one string, `logRecord("read", "request_id=lesson-7")`. A lone string argument with no value becomes an attribute under the key `!BADKEY`, so `request_id` is still missing and the check panics.',
                "Print `v` and see `request_id!:lesson-7` for the regression and `request_id:lesson-7` after the repair.",
            ),
            (
                "Rely on the handler's `ReplaceAttr`, which returns an empty `slog.Attr` for `slog.TimeKey`; the handler omits empty attributes.",
                "The time attribute is dropped before encoding, so the decoded map has no `time` key and `present` is false.",
                "Creating the handler with `slog.NewJSONHandler(&b, nil)`. The record then includes the current time, `present` is true and the check panics with `time`; asserting the exact time instead would be flaky.",
                "Print `v` and see `map[level:INFO msg:stable]` with no time field.",
            ),
            (
                "Pass `status` as its own key and value instead of placing it in the message text.",
                "The handler writes `status` as a separate JSON field, so the decoded map has `status` equal to `failed` while `msg` stays `read finished`.",
                'Folding it into the message with `fmt.Sprintf("read finished: status=%s", "failed")` and no attributes. The map then has no `status` key, `v["status"]` is nil and the check panics with `status`.',
                'Print `v["msg"], v["status"]` and see `read finished failed`.',
            ),
            (
                "Replace the credential with the fixed marker before calling the logger, so the secret never reaches the handler or the buffer.",
                "The handler only ever sees `[redacted]`, so the decoded `credential` field equals the marker.",
                "Logging the real value and relying on a `ReplaceAttr` rule that redacts a key named `password`. This call uses the key `credential`, so the rule never fires and the secret is written into the buffer.",
                "Print `v` and see `map[credential:[redacted] level:INFO msg:configuration]`, and confirm `strings.Contains(fmt.Sprint(v), secret)` is false for the real value.",
            ),
            (
                "Log the byte count as the integer 12 so the handler writes a JSON number.",
                'A JSON number decoded into `any` becomes `float64`, so `v["bytes"]` is `float64(12)` and the comparison holds.',
                'Logging `strconv.Itoa(12)`. The field becomes the JSON string `"12"`, the decoded value is a `string`, the check panics with `numeric`, and a log query that sums bytes would skip it.',
                'Print `fmt.Printf("%T %v\\n", v["bytes"], v["bytes"])` and see `float64 12`.',
            ),
        ],
        transfer='Log `upload` with `request_id` `lesson-9`, `bytes` 2048 and `status` `ok`, decode the buffer with a `json.Decoder` that calls `UseNumber`, and check `bytes` is `json.Number("2048")`, `status` is `ok`, `msg` is `upload` and `time` is absent. Explain which checks a message like `upload ok 2048 bytes` with no attributes would fail.',
    ),
    "go-032": dict(
        cases=[
            (
                "Execute the template with the script text as data; `html/template` escapes it for the HTML text context and returns nil.",
                "Escaping is how the package handles dangerous data; it does not refuse it. `Execute` therefore returns nil, the edited `!= nil` is false and the check panics with `render`.",
                "Predicting that `Execute` rejects the script with an error, so the edited check would pass. The package never treats data as an error; it renders it as inert text.",
                "Print `b.String()` and see `<p>&lt;script&gt;alert(1)&lt;/script&gt;</p>`. Changing the import to `text/template` prints the raw tags and fails the `escape` check.",
            ),
            (
                "Encode `a&role=admin` with `url.QueryEscape`, giving `a%26role%3Dadmin`, then decode it with `url.QueryUnescape`.",
                "Escaping and unescaping round-trip, so `decoded` equals the original with a nil error and the encoded form differs. The edited `err != nil` is false and the check panics with `query`.",
                'Building the URL as `"?q=" + original`. Parsing that query yields `q=a` and a separate `role=admin` parameter, so the input added a field it was never allowed to set.',
                'Print `encoded` and see `a%26role%3Dadmin`, and `url.Values{"q": {original}}.Encode()` prints `q=a%26role%3Dadmin`.',
            ),
            (
                "Ask `filepath.IsLocal` about each path; it rejects empty, absolute and parent-escaping paths after lexical cleaning.",
                "`../outside` starts by leaving the base directory, so it is not local, while `reports/item.txt` stays inside it, so only the second returns true.",
                "Rejecting only paths that start with `..`. That allows `reports/../../outside`, which cleans to `../outside`, and absolute paths such as `/etc/passwd`; `IsLocal` returns false for both.",
                "Print `filepath.IsLocal` for `reports/../../outside`, `/etc/passwd` and the empty string and see `false` three times.",
            ),
            (
                "Measure each value in bytes, the unit storage and network budgets are charged in, and compare with the inclusive limit 4.",
                "`abc` is 3 bytes and fits, `abcde` is 5 and does not, so both sides of the check hold.",
                "Counting runes with `utf8.RuneCountInString`. For ASCII the answers match, but `ééé` is 3 runes and 6 bytes, so a rune budget of 4 accepts it while it exceeds the byte limit.",
                'Print `len("abc"), len("abcde"), len("ééé")` and see `3 5 6`; `len` of a string already counts bytes, without the conversion.',
            ),
            (
                "Compare the equal and the unequal four-byte values with `subtle.ConstantTimeCompare`, which returns an `int`.",
                "For equal-length inputs it inspects every byte before answering, returning 1 for `abcd` and `abcd` and 0 for `abcd` and `abce`.",
                'Writing `check(subtle.ConstantTimeCompare(a, b), "equal")` as if the result were a `bool`. Go does not convert `int` to `bool`, so it fails to compile with a message that an `int` value cannot be used as `bool`.',
                "Print both results and see `1 0`. Comparing `abc` with `abcd` also returns 0, immediately, because differing lengths are reported without a byte scan.",
            ),
            (
                "Accept an action only when it is a key in the reviewed `allowed` map; a missing key reads as false.",
                "`read` was reviewed and maps to true, while `exec` was never listed, so the lookup returns false and the check holds.",
                'Keeping a denylist such as `blocked := map[string]bool{"exec": true}` and accepting anything not blocked. `Exec`, `shell` or any new name passes because missing keys read as false, so unreviewed actions are accepted.',
                'Print `allowed["read"], allowed["exec"], allowed["Read"]` and see `true false false`.',
            ),
        ],
        transfer="Write `searchURL(base, q string) (string, error)` that accepts only `/search` and `/docs` as `base` and appends `?q=` plus `url.QueryEscape(q)`. Check `a&b` gives `/search?q=a%26b`, `/admin` is refused and a 300-byte `q` is rejected by a 256-byte budget. Explain which check plain concatenation or a denylist of bases would fail.",
    ),
    "go-037": dict(
        cases=[
            (
                "Walk `plan(3, true, 0)` through the branches in order: 3 is not negative, the child exists, and 3 differs from 0, so the planner returns `update`.",
                "The edit only flipped `exists`, and an existing child is never created again, so the result is `update` rather than `create` and the check panics with `missing child`.",
                'Predicting `create` because a current count of 0 looks like "nothing there". The planner decides absence from `exists`, not from the count, which is what lets an existing child legitimately sit at 0.',
                "Print `plan(3, true, 0)` and `plan(3, false, 0)` and see `update create`.",
            ),
            (
                "Evaluate the edited call `plan(3, true, 3)`: the child exists and its observed count already equals the desired 3, so the planner returns `none`.",
                "The edited check expects `update` for a converged child, which the planner never returns when nothing differs, so it panics with `changed child`. The original call with current 2 has a real difference and returns `update`.",
                "Expecting `update` because an earlier event announced a change to 3. The planner compares desired with observed state each time, so a change that has already been applied produces no further write.",
                "Print `plan(3, true, 2)` and `plan(3, true, 3)` and see `update none`.",
            ),
            (
                "Call `plan(3, true, 3)`, where desired and observed state agree, and expect the planner's no-op result.",
                'None of the earlier branches apply, invalid, create or update, so the function reaches `return "none"` and the adapter writes nothing.',
                "Returning `update` whenever the planner runs so that every event re-applies the spec. For this converged input the check panics with `converged`, and every periodic resync would send a write that changes nothing.",
                "Print `plan(3, true, 3)` three times and see `none` each time, which shows repeated events are harmless.",
            ),
            (
                "Validate desired state first: any negative `wanted` returns `invalid` before existence or counts are considered.",
                "-1 hits the first branch, so the planner reports `invalid` even though the child exists and its count differs.",
                "Placing the validation after the existence and difference checks. Then `plan(-1, true, 2)` returns `update`, the adapter would try to set a negative count, and the check panics with `invalid intent`.",
                "Print `plan(-1, true, 2)` and `plan(-1, false, 0)` and see `invalid invalid`.",
            ),
            (
                "Plan from current 1, apply the action by setting `current` to the desired 3, and plan again from the new observation.",
                "The first plan sees a difference and returns `update`; after the update the observed count equals the desired count, so the second plan returns `none`, which is convergence.",
                "Modeling the update as one step closer, `current++`. After one step the count is 2, the second plan returns `update` again and the check panics with `second plan`; the action means set to the desired count.",
                "Print both plans and see `update none`, then plan a third time with `current` still 3 and see `none` again.",
            ),
            (
                "Treat 0 as a real desired count: `plan(0, true, 2)` differs from the observed 2 and returns `update`, and `plan(0, true, 0)` returns `none`.",
                "0 passes the `wanted < 0` validation, the child exists, and the comparison with current drives the result, so the planner scales down and then converges.",
                "Validating with `wanted <= 0`. Zero then becomes `invalid`, the first call returns `invalid` instead of `update` and the check panics with `zero scale`; a legitimate scale-to-zero is refused.",
                "Print `plan(0, true, 2)`, `plan(0, true, 0)` and `plan(0, false, 0)` and see `update none create`.",
            ),
        ],
        transfer="Add a `deleting bool` parameter, checked after validation, that returns `delete` for an existing child and `none` for a missing one. Check `plan(3, true, 3, true)` gives `delete`, `plan(3, false, 0, true)` gives `none`, `plan(0, true, 0, false)` still gives `none`, and replanning after each applied action converges to `none`. Explain which result a planner that treats a count of zero as absent would get wrong.",
    ),
    "go-043": dict(
        cases=[
            (
                "Evaluate the edited call `finalAction(true, false, false, true)` in branch order: the object is owned, it is deleting, and it has no finalizer, so the result is `done`.",
                "Registration happens only while the object is not deleting. With deletion already started and no finalizer to wait for, the function returns `done`, and the check expecting `add-finalizer` panics with `register`.",
                "Predicting `add-finalizer` because the finalizer is missing. A Kubernetes API server refuses to add new finalizers to an object that is already being deleted, so the controller must register before deletion begins.",
                "Print `finalAction(true, false, false, true)` and `finalAction(false, false, false, true)` and see `done add-finalizer`.",
            ),
            (
                "Evaluate the edited call `finalAction(true, true, false, true)`: owned, deleting, finalizer present and cleanup not done, so the result is `cleanup`.",
                "The deleting flag is tested before ordinary reconciliation, so a deleting object never returns `reconcile`. The edited check therefore panics with `normal`, while the original non-deleting call returns `reconcile`.",
                "Expecting `reconcile` because the finalizer is present and the object is owned, as if the finalizer itself meant normal operation. Once deletion starts, the finalizer is a gate for cleanup, not a sign of health.",
                "Print `finalAction(false, true, false, true)` and `finalAction(true, true, false, true)` and see `reconcile cleanup`.",
            ),
            (
                "Call `finalAction(true, true, false, true)` for a deleting object whose external cleanup has not succeeded yet.",
                "With deletion in progress, the finalizer present and `cleaned` false, the function returns `cleanup`, so the finalizer keeps the object until the external resource is gone.",
                "Removing the finalizer first and cleaning up afterward. The function would return `remove-own-finalizer`, the check panics with `cleanup`, and in a cluster the object could disappear before cleanup ran, leaving no record of the external resource.",
                "Print the action for `cleaned` false and true and see `cleanup` then `remove-own-finalizer`.",
            ),
            (
                "Call `finalAction(true, true, true, true)` for a deleting object whose cleanup is confirmed.",
                "The only remaining duty is releasing this controller's own gate, so the function returns `remove-own-finalizer`. On the next observation the finalizer is gone and the action becomes `done`.",
                "Returning `done` after cleanup without removing the finalizer. The check panics with `release`, and in a cluster the object would stay in Terminating because deletion waits for every finalizer to be removed.",
                "Print `finalAction(true, true, true, true)` and then `finalAction(true, false, true, true)` and see `remove-own-finalizer done`.",
            ),
            (
                "Check ownership before anything else: when the observed UID does not match the owned UID, return `ownership-error` regardless of the other flags.",
                "`owned` is false, so the first branch returns `ownership-error` and the controller neither cleans up nor removes finalizers on an object it does not own.",
                "Placing the ownership test after the deleting branch. For this input the function returns `cleanup` before it reads `owned`, the check panics with `UID mismatch`, and a real controller would delete external resources of a replacement that reused the name.",
                "Print `finalAction(false, false, false, false)` and `finalAction(true, true, true, false)` and see `ownership-error` both times.",
            ),
            (
                "Build a new slice that keeps every finalizer except the exact string `lesson.example/cleanup`.",
                "Only the entry equal to this controller's name is skipped, so `other.example/retain` is copied to `out` and remains the single element.",
                "Removing by position with `values[:len(values)-1]`, assuming this controller's entry is last. Here it is first, so the slice keeps `lesson.example/cleanup`, drops the other controller's entry and the check panics with `preserve others`.",
                "Print `out` and see `[other.example/retain]`; the positional version prints `[lesson.example/cleanup]`.",
            ),
        ],
        transfer="Write `removeFinalizer(list []string, name string) []string` that returns a new slice without `name` and leaves the input unchanged. Check `[other.example/a lesson.example/cleanup other.example/b]` gives the two others in order, a list without the name comes back equal, and an empty list stays empty. Explain which case removal by position or replacing the list with nil would break.",
    ),
    "go-045": dict(
        cases=[
            (
                'Trace the edited call `acquire(&l, "a", 11, 5)` on an empty lease: the candidate and duration are valid and nobody holds the lease, so `a` takes it with `Expires` set to 11 plus 5.',
                "Expiry is computed from the acquisition time, so it becomes 16. `acquire` returns true and the holder is `a`, but `l.Expires == 15` fails and the check panics with `acquire`.",
                "Predicting that expiry stays 15 because the lease window is fixed, or that a later `now` is refused. An empty lease is always granted, and the window always starts at the moment of acquisition.",
                "Print `l` after the edited call and see `{a 16}`; the original call gives `{a 15}`.",
            ),
            (
                "Run the regressed fixture: the lease is held by `a!` until 15, and `b` asks at 12. The holder differs from the candidate and 12 is before expiry, so `acquire` refuses.",
                'The refusal is correct, so `!acquire(...)` holds; the failing operand is `l.Holder == "a"`, because the fixture names `a!`. Restoring `a` repairs the data without changing `acquire`.',
                "Assuming the contender won and debugging the time comparison in `acquire`. The result is false and the lease is unchanged, so the defect is in the fixture's holder name, not in the policy.",
                "Print the result and `l` and see `false {a! 15}` for the regression and `false {a 15}` after the repair.",
            ),
            (
                "Let the current holder `a` call `acquire` at 13. The holder equals the candidate, so the lease is renewed with `Expires` set to 13 plus 5.",
                "Renewal uses the same rule as acquisition, the window starts now, so expiry moves from 15 to 18 and `acquire` returns true.",
                "Renewing by adding the duration to the old expiry, `l.Expires += duration`. That gives 20 instead of 18, the check panics with `renew`, and repeated early renewals would stretch leadership far beyond the configured window.",
                "Print `l` after renewal and see `{a 18}`.",
            ),
            (
                "Ask for the lease as `b` at exactly 15, the stored expiry. The refusal requires `now < l.Expires`, and 15 is not less than 15.",
                "At the boundary the lease counts as expired, so `b` takes over with `Expires` 20 and `l.Holder` is `b`.",
                "Writing the comparison as `now <= l.Expires`. Then `b` is refused at 15, the holder stays `a` and the check panics with `takeover`: a one-tick off-by-one at the boundary.",
                "Print the result and `l` and see `true {b 20}`; repeating at 14 on a fresh lease gives `false {a 15}`.",
            ),
            (
                "Let the destination accept a write only when its token equals the current fencing token 5.",
                "Token 4 was issued to an earlier leader, so `accept(4)` is false, while the current holder's token 5 is accepted.",
                "Accepting any token the system has issued, `token <= current`. The stale leader's token 4 passes, the check panics with `fencing`, and a paused former leader could overwrite newer data.",
                "Print `accept(3), accept(4), accept(5)` and see `false false true`.",
            ),
            (
                "Reject a nonpositive duration before looking at the lease, so a zero duration returns false and leaves the lease empty.",
                "`duration <= 0` is true for 0, so `acquire` returns false without assigning the holder, and `l.Holder` stays empty.",
                "Validating with `duration < 0`. Zero then passes, `a` becomes holder with `Expires` 10, a lease that is already expired, and the check panics with `duration`; any contender could take it the same instant.",
                "Print the result and `l` and see `false { 0}`.",
            ),
        ],
        transfer="Add a `Token int` field that `acquire` increments only when the holder changes. Check that `a` taking an empty lease at 10 gets token 1, renewing at 13 keeps 1, `b` taking over at 15 gets 2, and a destination that rejects tokens below the highest seen refuses a late write from `a` with token 1. Explain which check a token incremented on every renewal would change.",
    ),
}
