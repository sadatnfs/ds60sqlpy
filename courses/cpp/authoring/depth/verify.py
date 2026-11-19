"""Exercise-specific Verify lines for the 38 depth guides and their explanations.

Each line says how to check that exercise's Expected result with its own data, so
it never repeats the Expected sentence. Keys are lesson.exercise; build_depth.py
writes the same line into the guide and the explanatory solution.
"""

_TABLE = r"""
004.1 Add a temporary print of `x` and `total` inside the loop of Worked example 1: it must print exactly four lines, and the last total must equal the asserted 10.
004.2 Assert both counts (3 and 2) and both sums (10) in one program; only the element 0 changes classification between the two predicates.
004.3 Keep a separate iteration counter and assert `counter == 4 && sum == 10`, then confirm the condition is `i <= 4` when `i` starts at 1.
004.4 Run the broken scratch copy and confirm it returns 6, the last element alone; after moving `total = 0` back above the loop, assert the result is 10 again.
004.5 Assert `nonnegative_sum({}) == 0` and `nonnegative_sum({-1, -5}) == 0` in one program; the empty case must not index the vector.
004.6 Assert the kept values equal `std::vector<int>{0, 4, 5}` and their total is 9; both boundary values 0 and 5 stay while -1 and 6 are dropped.
005.1 Assert `clamp_reading(-3, 0, 10) == 0`, `clamp_reading(5, 0, 10) == 5` and `clamp_reading(12, 0, 10) == 10`: one call below, inside and above the interval.
005.2 Store the result in a second variable and assert `result == 10 && x == 12`; the by-value parameter cannot change the caller's `x`.
005.3 Assert `inside(0, 0, 10)`, `inside(10, 0, 10)` and `!inside(11, 0, 10)` so both inclusive edges and one outside value are covered.
005.4 Without the check, `clamp_reading(5, 10, 0)` silently returns 10; after restoring it, Worked example 2 must catch `std::invalid_argument` again.
005.5 Assert that `clamp_reading(2, 3, 3)`, `clamp_reading(3, 3, 3)` and `clamp_reading(4, 3, 3)` all equal 3; equal bounds form a one-value interval, not a reversed one.
005.6 Assert `clamp_reading(1250, 0, 1000) == 1000` with `int` arguments only, and compile with `-Wconversion` to confirm no floating conversion appears.
006.1 Print `ptr - s.data()` for both inputs (2 and 2) next to `s.size()` (2 and 3); only the input whose distance equals its size may be accepted.
006.2 Assert `parse_int("0") == 0` and `parse_int("-7") == -7`; checking `has_value()` alone would not catch a wrong value.
006.3 Collect accepted values into a vector and count rejections, then assert the vector equals `{12, 0}` and the rejected count is 2, with the empty string among the rejected.
006.4 In the scratch copy, Worked example 2's `assert(!parse_int("12x"))` must abort; restoring the `ptr` comparison must make it pass again.
006.5 Assert `!parse_int(std::string(21, '9'))`, and in a scratch copy check that `ec == std::errc::result_out_of_range` to confirm the reason.
006.6 Assert `!parse_int(" 42 ")` and `parse_int(trimmed) == 42`, where `trimmed` is produced by your trim step rather than typed by hand.
007.1 Compare your paper result with the `sorted:` line printed by Worked example 1, element by element, and confirm the duplicate 3 appears twice.
007.2 Assert `original == std::vector<int>{3, 1, 3, 0}` after sorting the copy, and assert `std::ranges::is_sorted(copy)`.
007.3 Assert the `std::count_if` result with the predicate `x >= 3` is 2 on `{3, 1, 3, 0}`; changing the predicate to `x > 3` must give 0.
007.4 Run the scratch copy and confirm it prints `sum=17`, exactly 10 more than the data; after restoring `0LL` the `sum=7` line must return.
007.5 Assert `xs.size() == 0`, a count of 0 and `std::accumulate(xs.begin(), xs.end(), 0LL) == 0` in one program, with no `front()` or `[0]` call.
007.6 Assert `xs == std::vector<int>{0, 1, 3}` after `xs.erase(std::unique(xs.begin(), xs.end()), xs.end())`; run `std::unique` once without sorting to see the non-adjacent 3 survive.
008.1 Check the drawing against Worked example 1: the temporary `{2, 4}` and `out` are the two owners, and `xs` inside `doubled` is only another name for the temporary.
008.2 Keep the input in a named vector, then assert `input[0] == 2 && output[0] == 99` after the write, as Worked example 2 does for `xs` and `ys`.
008.3 Assert `size_of({2, 4}) == 2` and `size_of({}) == 0`, and confirm the function also accepts a `const std::vector<int>` variable.
008.4 Compile the scratch file with the lesson flags and keep the error that points at the `xs[0] = 9` line; after deleting that write the file must compile without warnings.
008.5 Trace where the local result is destroyed and confirm the reviewed return type is `const std::vector<int>&`; the repaired signature returns `std::vector<int>` and compiles without warnings.
008.6 Store `auto kept = doubled(std::vector<int>{5});` and assert `kept == std::vector<int>{10}` on a later line, after the temporary argument is gone.
010.1 Check each part of your description against the declaration: `id` holds 7, `cents` holds 200 cents rather than dollars, and `status` is the enumerator `Status::paid`, not a string.
010.2 Sum `settled()` over both records and assert the total is 200 while the input vector's size is 2; the pending record is still counted as input.
010.3 Add `Status::refunded`, make `settled()` return 0 for it, and assert that a paid 200 record plus a refunded 200 record sum to 200.
010.4 Wrap `settled(Payment{9, -1, Status::paid})` in `try`/`catch`, assert that `std::invalid_argument` was caught, and confirm no total was updated.
010.5 Assert `settled(Payment{10, 0, Status::paid}) == 0` without an exception; 0 passes the `cents < 0` guard.
010.6 Assert the settled sum is 400 and that the two records' `id` fields differ; equal amounts must not merge two payments.
011.1 Assert `read_lines` on the fixture returns exactly `{"10", "20"}`; the final newline must not create a third, empty record.
011.2 Assert `read_lines(input).empty()` for an empty `std::istringstream` and that no `std::runtime_error` is thrown, because end of input without `bad()` is not a read failure.
011.3 After closing the `std::ofstream`, read the file back through `read_lines` and assert the result is `{"10", "20"}`; any other size means the write was not flushed or was appended twice.
011.4 Run both loops on the 10-newline-20-newline fixture: the eof-first loop records a third, empty line, while the `getline` loop must produce exactly two records.
011.5 Assert `!std::ifstream("missing-file.txt").is_open()`, and check that your error message names `missing-file.txt` and that no record is processed afterward.
011.6 Print `std::filesystem::absolute("input.txt")` from each working directory and confirm the two paths differ, then pass one absolute path explicitly and confirm both runs read the same file.
012.1 Confirm `math.hpp` holds only the declaration, `math.cpp` the single definition and `main.cpp` the caller, then run the executable and check that `add(2, 3)` produced 5.
012.2 Run `g++ -std=c++20 -c main.cpp`, then list the directory and confirm `main.o` exists and no executable has been produced yet.
012.3 Link with `g++ main.o math.o -o app`, run `./app`, and check both the printed value 5 and a status of 0 from `echo $?`.
012.4 Link `main.o` alone and keep the undefined reference to `add(int, int)` message and the nonzero status; no new executable may appear.
012.5 Compile both files and link them; the linker must report a multiple definition of `add(int, int)`, and the error must disappear once the body moves back to `math.cpp`.
012.6 Assert `subtract(5, 3) == 2` in `main.cpp`, and check that the declaration in `math.hpp` and the definition in `math.cpp` have the same parameter types.
013.1 Check that your explanation assigns `-std=c++20` to choosing the language standard and gives `-Wall`, `-Wextra` and `-Wpedantic` three different roles; `-Wall` does not enable every warning.
013.2 Read the ctest summary line and record the number of tests run and passed; a summary of zero tests means nothing was registered, not that the code is correct.
013.3 Build the scratch copy, run it, and confirm `echo $?` prints 1 and the `always-active check passed` line is missing; ctest must also mark the test as failed.
013.4 Build the scratch file with `-DNDEBUG` and confirm the wrong `assert` no longer stops the program while the `if`-based check still returns 1; without `-DNDEBUG` the `assert` aborts first.
013.5 Add `if (twice(0) != 0) return 1;` next to the existing check, build with `-DNDEBUG`, and confirm the exit status is still 0.
013.6 With `x + x + 1`, confirm `twice(3)` gives 7 and `twice(0)` gives 1 so both checks return 1; after restoring `x * 2`, both must pass again.
014.1 Apply your written grammar to each of the five rows by hand and confirm it accepts exactly 10, 0 and 25 and gives a reason for rejecting `bad` and `-2`.
014.2 Assert the ledger has 5 entries, 3 holding a value and 2 holding a reason, and confirm each entry keeps its original raw text.
014.3 Compare your printed line with Worked example 1's assertion `accepted == 3 && rejected == 2 && total == 35`; the total is a `long long` and includes the accepted 0.
014.4 Change only the last row to `25x`: the original assertion now aborts, and with it updated to 2, 3 and 10 the program prints `accepted=2 rejected=3 total=10`.
014.5 Use an empty `rows` vector and assert `accepted == 0`, `rejected == 0` and `total == 0` without adding a special case for empty input.
014.6 Have someone follow only your package in a fresh directory and confirm they see `accepted=3 rejected=2 total=35` and, for the `25x` case, `accepted=2 rejected=3 total=10`.
015.1 Check the drawing against Worked example 1's assertion `!p && q && *q == 7`: after the move `p` is null, `q` owns the single int 7, and no second allocation appears.
015.2 Print `live` inside the inner scope and after it closes, and confirm the two lines show 1 and 0, matching Worked example 2's assertions.
015.3 Create a `std::unique_ptr<Tracked>` inside `try`, throw `std::runtime_error`, and assert `live == 0` in the `catch` block, which shows the destructor ran during unwinding.
015.4 Compile the scratch line and keep the error about the deleted copy constructor of `std::unique_ptr`; `auto q = std::move(p);` must compile instead.
015.5 Assert `!std::unique_ptr<int>{}` and confirm the program never applies `*` to the empty pointer.
015.6 Put three `std::unique_ptr<Tracked>` values in a vector inside a scope and assert `live == 3` inside and `live == 0` afterward; the code must contain no `delete`.
016.1 After `b.values[0] = 9`, assert `a.values == std::vector<int>{1, 2}` and `b.values == std::vector<int>{9, 2}`, as Worked example 1 does.
016.2 Assert `receiver.values == std::vector<int>{1, 2, 3}` after `std::move`, and make no assertion about the source's contents.
016.3 After the move, assign `a = Batch{{4}, "new"}` and assert `a.values == std::vector<int>{4}`, as Worked example 2 does with `a.values[0] == 4`.
016.4 Confirm no remaining assertion reads a moved-from vector's size or elements; the tests may only check the receiver's values and that the source can be assigned or destroyed.
016.5 Check that your list adds no destructor, copy or move member, then confirm Worked examples 1 and 2 still compile and pass with the struct unchanged.
016.6 Write a function returning `Batch{{5, 6}, "made"}`, store the result, and assert its values and label on a later line, after the factory has returned.
017.1 Assert `std::get<int>(positive(0)) == 0`, `std::get<int>(positive(5)) == 5` and `std::holds_alternative<ParseError>(positive(-1))`; zero is a success, not an error.
017.2 Run 0, 5 and -1 through one `std::get_if` branch each and confirm three printed lines, with -1 showing `negative` and no exception escaping.
017.3 Assert `std::optional<int>{0}.has_value()` and `!std::optional<int>{}.has_value()`; comparing contained values alone would hide the difference.
017.4 Wrap `std::get<int>(positive(-1))` in `try`/`catch` and assert `std::bad_variant_access` is caught; after switching to `std::get_if` or `std::visit`, no exception is possible.
017.5 Check that your explanation stops the whole run with a nonzero status for the missing file but records the bad row and continues with the next one.
017.6 Assert the reasons for 101 and -1 are `too_large` and `negative`, and that `std::get<int>(positive(100)) == 100`; 100 is the inclusive boundary.
018.1 Check that the drawing shows `xs` owning the three ints and the span holding only a pointer and a length into that same buffer, with no second copy of the values.
018.2 Assert `sum_view(std::span<const int>(xs).subspan(1, 2)) == 10` and `xs == std::vector<int>{2, 4, 6}`; Worked example 1 checks the sum.
018.3 Check `offset <= size && count <= size - offset` before calling `subspan`, and assert the check is false for offset 2, count 2 and size 3 but true for count 1.
018.4 Compare `xs.data()` before and after the growth, and confirm the reviewed code builds a new span from `xs` after any `push_back` that may reallocate.
018.5 Assert `sum_view(std::span<const int>{}) == 0`; `std::accumulate` over an empty range returns its initial value without reading an element.
018.6 Trace the local `std::string` to the function's closing brace, and confirm the repaired version returns `std::string` or takes the text from a caller whose owner outlives the result.
019.1 Collect the filtered and doubled view into a vector and assert it equals `std::vector<int>{0, 6}`.
019.2 Swap the two adaptors, change the predicate to `x > 0`, and assert the collected vector is `std::vector<int>{6}`; -1 doubles to -2 and 0 stays 0, so both drop out.
019.3 After collecting, set `xs[2] = 100` and assert the stored vector is still `std::vector<int>{0, 6}`, while iterating the view again yields 0 and 200.
019.4 Trace where the local vector is destroyed and confirm the reviewed function returns a view over it; the repair returns `std::vector<int>` or takes the owner by reference from the caller.
019.5 Assert `scores[0].id == 2 && scores[1].id == 1` after `std::ranges::sort(scores, {}, &Score::points)`, as Worked example 2 does.
019.6 Sort with a comparator on `std::tie(a.points, a.id) < std::tie(b.points, b.id)` and assert the ids are 2, 3, 1; the tie at 4 points is broken by the smaller id.
020.1 Add `static_assert(std::is_same_v<decltype(identity_sum(2, 3)), int>)` and the same check with `2LL` and `3LL` against `long long`.
020.2 Compile the call with two `std::string` arguments and confirm the error names the unsatisfied `std::integral` constraint rather than a failure inside the function body.
020.3 Add `static_assert(std::signed_integral<int>)` and `static_assert(!std::signed_integral<unsigned>)`, then confirm a call with `3u` fails to compile.
020.4 Keep the deduction error for `identity_sum(2, 3LL)`, where `T` would be both `int` and `long long`, then assert `identity_sum(2LL, 3LL) == 5LL`.
020.5 Show that `identity_sum(std::numeric_limits<int>::max(), 1)` compiles because `int` satisfies `std::integral`; with `-fsanitize=undefined`, running it reports the signed overflow.
020.6 Assert `identity_sum(7, 0) == 7` and `identity_sum(7LL, 0LL) == 7LL`; both arguments must have the same type for deduction to succeed.
021.1 Confirm `Cents{125}.value == 125` compiles while `Cents{125} == 125` does not; equal numbers do not make the two domains comparable.
021.2 Assert `(Cents{125} + Cents{0}) == Cents{125}`, as Worked example 2 does, with the zero written as `Cents{0}` rather than a raw integer.
021.3 Write `Cents{1} + ItemCount{1}` in a scratch file and confirm the compiler finds no matching `operator+`, while `Cents + Cents` still compiles.
021.4 In a scratch copy, add a non-explicit `Cents(long long)` constructor and show that `Cents total = 125;` compiles; marking it `explicit` must make that line fail.
021.5 Assert `a == a`, `a == b`, `b == a`, `b == c` and `a == c` for the three `Cents{125}` values, all through the defaulted `operator==`.
021.6 Test your guard with `LLONG_MAX` plus 1 and confirm it rejects before computing the sum, while `LLONG_MAX - 1` plus 1 is accepted.
022.1 Check your document against `encode(7, 125) == "v1,7,125"`: the version comes first, the ID second and the cents third, and the unit is named.
022.2 Assert `encode(0, 0) == "v1,0,0"`; zero values must still produce all three fields.
022.3 Assert your decoder rejects `"v2,7,125"` and `"v1,7,125,junk"` but accepts `"v1,7,125"` as ID 7 and 125 cents.
022.4 Check that your explanation ties each hazard to a concrete case, for example `sizeof(long)` being 4 on 64-bit Windows but 8 on 64-bit Linux.
022.5 Print `std::filesystem::current_path()` and `std::filesystem::absolute("records/batch.csv")`, and confirm the second path starts with the first.
022.6 Feed `"v2,7,125,paid"` to the v1 reader and confirm it is rejected rather than decoded as ID 7 and 125 cents; only the v2 reader may accept it.
023.1 Check that your list puts the `int` parameters, the `out` pointer and statuses 0, 1 and 2 under the source contract, and `extern "C"` linkage, compiler and platform under binary assumptions.
023.2 Initialize `out` to another value first, then assert `add_checked(2, 3, &out) == 0 && out == 5`, as Worked example 1 does.
023.3 Assert `add_checked(2, 3, nullptr) == 1`, as Worked example 2 does; the null check must come before any write through `out`.
023.4 Confirm the repaired wrapper catches inside the `extern "C"` function and returns a documented status; `noexcept` alone would call `std::terminate` instead.
023.5 Assert `add_checked(std::numeric_limits<int>::max(), 1, &out) == 2` and that `out` still holds its previous value.
023.6 Record `g++ --version` and `uname -m` next to the successful link and test run, and confirm the header declaration matches the definition's `extern "C"` signature.
024.1 Assert `reversed({1, 2, 3}) == std::vector<int>{3, 2, 1}`, as Worked example 1 does; the expected vector is typed by hand, not computed with `std::reverse`.
024.2 Loop over every pair `a, b` from -2 to 2, count the pairs whose double reversal returns `{a, b}`, and assert the count is 25.
024.3 Assert that double reversal returns `{}`, `{7}` and `{2, 2}` unchanged, and also that `reversed({7}) == std::vector<int>{7}` directly.
024.4 Run both tests against the identity version: the double-reversal assertion still passes while the `{3, 2, 1}` golden assertion fails, so the property alone is too weak.
024.5 Record the smallest input that fails, such as the singleton `{7}` coming back empty, together with the exact assertion that fired.
024.6 Assert that decoding an encoded record returns the same ID and cents for several valid pairs, and separately that hand-written `"v1,7,125x"` and `"v2,7,125"` are rejected.
025.1 Check your explanation against `xs.size() == 2`: the last valid index is `size() - 1`, and `checked_at({2, 4}, 1) == 4` in Worked example 1 is the boundary that works.
025.2 Confirm Worked example 2 catches `std::out_of_range` from `at(2)`, and do not run `xs[2]`; your answer must call it undefined behavior rather than predict its output.
025.3 Build with `-fsanitize=address,undefined -g`, run the program, and record the compiler version plus separate compile, link and run statuses.
025.4 Confirm the AddressSanitizer report says `heap-buffer-overflow`, points at your scratch file and line, and that the exit status is nonzero.
025.5 Rebuild the same scratch program with the same sanitizer flags and confirm it exits 0 with no report and asserts the correct value.
025.6 Check that the guard compares `a > std::numeric_limits<int>::max() - b` before adding, and assert it rejects `INT_MAX` plus 1 while accepting `INT_MAX - 1` plus 1.
026.1 Write 12 down before running anything, then compare it with Worked example 1's assertion `total({2, 4, 6}) == 12`.
026.2 At the breakpoint, print the backtrace and confirm `total` appears above `main`, then print `xs.size()` and check that it is 3.
026.3 Assert `checksum == 12000`, as Worked example 2 does, and print the duration through `std::chrono::duration_cast<std::chrono::microseconds>` so the unit appears with the number.
026.4 Check that your explanation names the build flags (`-O0` versus `-O2`), the fixed workload of 1000 totals, the number of repeated runs and the spread between them.
026.5 Assert `total({}) == 0`, or step through it in the debugger and confirm `std::accumulate` returns its initial 0 without reading an element.
026.6 First assert that both versions return the same answer for every query, then compare operation counts and repeated timings at the same input size and build flags.
027.1 Check that each of the four entries is a value you can re-read later, such as the `g++ --version` output, `-std=c++20`, a `sha256sum` of the dependency archive and Ninja.
027.2 Run configure, build and ctest with networking disabled, for example inside `docker run --network none`, and confirm all three steps succeed.
027.3 Link a consumer target to the interface target without setting its own standard, then confirm its compile command, shown by `ninja -v`, contains `-std=c++20` or `-std=gnu++20`.
027.4 Confirm the repaired script uses a local archive or directory and checks a recorded hash, and that configure still succeeds with networking disabled.
027.5 List the delivery tree and confirm the license file exists at exactly the path your inventory names.
027.6 Check that your record lists the architecture you actually built and ran, from `uname -m`, separately from planned ones marked unqualified until executed.
028.1 Check your grammar against `parse_record("7,125")` succeeding and `parse_record("7,125x")` failing, and state that the returned `Record` holds copied ints, not views into the input.
028.2 Assert `parse_record` succeeds for `"7,125"` and `"0,0"` and returns an empty optional for `"7,125x"` and `"7,-1"`.
028.3 Confirm `CMakeLists.txt` declares a library target for the parser and an executable target that links it, then build both and run the executable.
028.4 Run Worked example 2's `assert(!parse_record("7,125x"))` against the scratch version and confirm it aborts; restoring the full-consumption check makes it pass.
028.5 Parse from a `std::string` declared in an inner scope, keep only the `std::optional<Record>`, and assert `id == 7` and `cents == 125` after the scope ends.
028.6 Build a separate consumer that includes only the public header and links the built library, and keep its test output beside the compiler version and architecture.
029.1 Check the drawing against Worked example 1: `answer` is declared before the thread, the write of 42 happens before `t.join()`, and the read and scope exit come after it.
029.2 Assert `answer == 42` on the line after `t.join()`, as Worked example 1 does; moving the assertion above the join creates a data race.
029.3 Confirm Worked example 2 contains no sleep, that `started.get()` returns before `stop.store(true)`, and that `worker.join()` returns.
029.4 Trace the captured local to the end of its scope and confirm a detached thread could still use it afterward; the repaired code joins before the scope ends.
029.5 Write a `std::jthread` loop that checks `stop_token::stop_requested()`, call `request_stop()`, let the jthread leave scope, and record the compiler and library version that built it.
029.6 Take the early-return path in a test and confirm the program does not call `std::terminate`, which happens when a joinable `std::thread` is destroyed.
030.1 Check that every read or write of `q` and `closed` in Worked example 1 happens while a lock on `m` is held, including inside the wait predicate.
030.2 Assert `total == 5` after `consumer.join()` and that `q.empty()` is true, so both items were consumed before the loop ended.
030.3 Record `q.size()` right after every push while holding the lock, and assert it is never greater than 2.
030.4 Confirm the repaired call passes the predicate `!q.empty() || closed` to `cv.wait`, so `front()` is reached only after the queue was seen to be non-empty.
030.5 Set `closed = true` under the lock before any push, notify, and assert `total == 0` after `consumer.join()`; Worked example 2 shows the wait returning at once.
030.6 Count accepted, processed and discarded items and assert `accepted == processed + discarded` after every worker has been joined.
031.1 Assert `count.load() == 2000` only after both `a.join()` and `b.join()`, as Worked example 1 does.
031.2 Check that your statement notes that no other variable is read based on `count`, and that the final read happens after `join()`, which already synchronizes.
031.3 Check that the drawing has `payload = 7` before the release store, the acquire load that sees `true` before the payload read, and an arrow from the store to that load.
031.4 If your host supports `-fsanitize=thread`, build the reviewed code in a scratch copy and confirm ThreadSanitizer reports a data race even when the printed total happens to be correct.
031.5 Set both loop bounds to 0 and assert `count.load() == 0` after both joins; no other data depends on this value.
031.6 Write both fields before `ready.store(true, std::memory_order_release)` and assert both values after the acquire loop exits, as Worked example 2 does for `payload == 7`.
032.1 Check that your document gives two separate numbers, 2 running and 4 waiting, and says what happens to a fifth waiting task.
032.2 Assert `checked_square(3) + checked_square(4) == 25`, and that the sum of `get()` on two `std::async` futures is also 25.
032.3 Assert that `get()` on the future for -1 throws `std::invalid_argument` in the calling thread, as Worked example 2 does with its `rejected` flag.
032.4 Confirm every `std::async` future is stored and `get()` is called on each, then check that results plus caught exceptions equal the number of submitted tasks.
032.5 Run an empty task list and assert the results are empty and the total is 0 without starting any future.
032.6 Check that the sketch blocks the producer when the queue holds 4 tasks, so running plus queued tasks never exceed 6 of the 10.
033.1 Check your answer against Worked example 1: `started.get()` returns only after `ready.set_value()`, and `worker.join()` is still needed before the program ends.
033.2 Confirm Worked example 2 runs 20 trials, asserts `count == 200` in every trial and never sleeps.
033.3 Run a deliberately deadlocked scratch copy under `timeout 10` (or `ctest --timeout 10`) and confirm a timeout result, status 124 from `timeout`, instead of a hang.
033.4 Confirm the repaired test calls `set_value()` in the worker and `get()` on the matching future before the main thread continues, and that no `sleep_for` remains.
033.5 Record the exact compile command, its status and the run status, or write unavailable with the compiler's error message if it rejects `-fsanitize=thread`.
033.6 Confirm the ThreadSanitizer report names a data race on the plain counter in the scratch file, then rebuild Worked example 2 with the same flags and confirm it reports nothing.
034.1 Check that both sketches contain the pairs (1, 10), (2, 20) and (3, 30), with the first interleaving ID and value and the second storing all IDs, then all values.
034.2 Assert both sums equal 60, as Worked examples 1 and 2 do, using the same three values in each layout.
034.3 Assert `v.size() == 0` and `v.capacity() >= 100` after `v.reserve(100)`; do not assert an exact capacity.
034.4 Print each candidate's checksum before timing and assert both equal 60; the candidate without 30 produces 30, which must stop the comparison.
034.5 Record the row cap, build flags, number of repetitions and each duration with its unit, and assert the checksum is identical in every repetition.
034.6 Measure combined ID and value access in both layouts with the same row cap and repetitions, and state whether your earlier one-field result still holds.
035.1 Increment a comparison counter inside the loop over `{2, 3, 2, 4}` and assert it ends at 4 with a match count of 2.
035.2 Assert `counts.size() == 3`, `counts.at(2) == 2`, `counts.at(3) == 1` and `counts.at(4) == 1`, extending Worked example 1's assertion.
035.3 Assert both approaches return the same count for each of the 100 queries, then report the index-building work separately from the lookup work.
035.4 Assert `counts.size()` grows by one after `counts[9]` but not after `counts.find(9) == counts.end()`, as Worked example 2 does.
035.5 Assert `counts.empty()`, `counts.find(2) == counts.end()` and `counts.count(2) == 0` for an index built from no rows.
035.6 Use `std::equal_range` on the sorted vector and assert its length for key 2 equals `counts.at(2)`, then record the one-time sort cost next to the per-query cost.
036.1 Change 16 to 17 in a scratch copy and confirm the build fails at the `static_assert`, while `square(runtime) == 25` is only checked when the program runs.
036.2 Fill a `constexpr std::array<int, 5>` with `square(i)` and add `static_assert(table[0] == 0 && table[4] == 16)` so the build itself checks the table.
036.3 Use your `consteval` function's result with a literal argument inside a `static_assert` and confirm the build succeeds; the call is evaluated during compilation.
036.4 Compile the scratch call and keep the error saying the argument is not a constant expression; changing `consteval` to `constexpr` must let it compile and run.
036.5 Check that your bound is at most 46340, the largest `int` whose square fits in 32 bits, and add `static_assert(square(bound) > 0)`, which fails to compile if the square overflows.
036.6 Time each build with the same flags, list the two object file sizes, and record both pairs of numbers without claiming they scale the same way elsewhere.
037.1 Check your explanation against the function body: one `for` loop reads each element once, and nothing calls `std::ranges::size` or traverses `xs` again.
037.2 Assert `keep_positive(std::vector<int>{-1, 0, 2, 2}) == std::vector<int>{2, 2}`, as Worked example 1 does; the duplicate 2 must appear twice.
037.3 Store `auto out = keep_positive(std::vector<int>{3, -1});` and assert `out == std::vector<int>{3}` on a later line, after the temporary is destroyed.
037.4 Run the reviewed function on a single-pass source such as `std::views::istream<int>` over a `std::istringstream`, and confirm the second traversal sees no elements.
037.5 Assert `keep_positive(std::vector<int>{}).empty()` and `keep_positive(std::span<const int>{}).empty()`.
037.6 Use input with two qualifying records that have equal points, and assert the output keeps both with every field unchanged.
038.1 Assert `safe_add(100, 25) == 125` with `int` values and no `double` anywhere in the calculation.
038.2 Assert `!safe_add(std::numeric_limits<int>::max(), 1)`, as Worked example 1 does, and confirm the guard compares before adding.
038.3 Print with `std::setprecision(17)` and record `0.30000000000000004`, then assert `std::abs((0.1 + 0.2) - 0.3) < 1e-12`, as Worked example 2 does.
038.4 Test your policy on 1e-9 versus 2e-9, which an absolute 0.1 calls equal, and on 1e20 versus 1e20 + 1e5, which it calls different although they differ by about 1e-15 relatively.
038.5 Assert `safe_add(0, 0) == 0` and `!safe_add(-1, 2)`; the second call is rejected by the `a < 0` check even though the true sum, 1, fits.
038.6 Assert `(1e16 + -1e16) + 1 == 1`, and print `(1e16 + 1) + -1e16`, which gives 0 because `1e16 + 1` rounds back to 1e16.
039.1 Check your answer against Worked example 1: the `unique_ptr` owner calls `analyzer_destroy` once at scope exit, and no other line deletes `raw`.
039.2 Use a scratch deleter that increments a counter and then calls `analyzer_destroy`, and assert the counter is 0 inside the scope and 1 after it ends.
039.3 Assert `analyzer_read(nullptr, &out) == 1` and `analyzer_read(handle, nullptr) == 1` as two separate assertions, and that `out` keeps its old value -1.
039.4 Confirm the repaired function wraps `new` in `try`/`catch` inside its `extern "C"` body, as `analyzer_create` does, and that callers check for `nullptr` before use.
039.5 Assert the query returns 1, then make the caller accept only version 2 in a scratch copy and confirm it stops before calling `analyzer_create`.
039.6 Run `nm -D` on the shared library and confirm `analyzer_create`, `analyzer_destroy` and `analyzer_read` appear unmangled, then keep that list with `uname -m`, the compiler version and the create/destroy test result.
040.1 Check your specification against `safe_id`: it rejects an empty string, accepts at most 16 characters and allows only `a-z`, `0-9` and `_`, so no uppercase letter, dot or slash.
040.2 Assert `safe_id("batch_7")` and `safe_id("0")`; a single digit is a valid identifier under this grammar.
040.3 Assert `!safe_id("../secret")`, `!safe_id("a/b")` and `!safe_id("a\\b")`, and confirm the program makes no `std::filesystem` call for a rejected name.
040.4 Check that your explanation says `safe_id` only validates a name, and names a case it cannot cover, such as a symbolic link inside the data directory that points elsewhere.
040.5 Assert `!safe_id("")`, `safe_id(std::string(16, 'a'))` and `!safe_id(std::string(17, 'a'))`.
040.6 Feed 101 short rows, then a single 257-byte row, and confirm each run reports the limit and count it hit and writes no output file.
041.1 Check that the record contains a git commit or `sha256sum` values, `g++ --version` and `uname -m` output, and no absolute path from your own machine.
041.2 Build once with `-O0` and once with `-O2 -DNDEBUG`, confirm both print `schema=1 rows=3 total=6`, and record how many tests ctest ran in each.
041.3 Write the row count, repetitions and expected checksum before running, then compare every run's checksum with that value and keep each duration with its unit.
041.4 Check that the corrected packet lists arm64 Linux as tested and Windows as unqualified, with no Windows test output claimed.
041.5 Rebuild from a clean directory with networking disabled and confirm the tests print the same `rows=3 total=6` result as the original build.
041.6 Have a reviewer locate the previous binary from your notes alone, run the acceptance test with it and get the documented result.
042.1 Check that each of the three limits appears with its number and with what happens when it is exceeded, for example a 17-character field being rejected.
042.2 Assert `first == 6`, `second == 15` and `first + second == serial_total(rows)`, which is 21, as Worked example 2 does.
042.3 Assert 6 accepted, 2 rejected and an accepted total of 21 for the eight inputs; the rejected strings must not change the sum.
042.4 Force one worker to report an error and confirm the program prints no combined total, exits nonzero, and reports which partition failed and what happened to the other.
042.5 Assert the two-worker total is 0 for no rows and 15 for five rows, where the uneven split of 2 and 3 rows must still count the last row.
042.6 Have a second person follow only your package and confirm they reproduce total 21, total 0, the two rejected strings and the failed-partition case.
"""

VERIFY: dict[int, list[str]] = {}
for _line in _TABLE.strip().splitlines():
    _key, _text = _line.split(" ", 1)
    _lesson, _exercise = (int(part) for part in _key.split("."))
    VERIFY.setdefault(_lesson, [""] * 6)[_exercise - 1] = _text
