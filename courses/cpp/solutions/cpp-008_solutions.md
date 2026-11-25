# cpp-008: explanations and reference observations

The [executable reference](cpp-008_solution.cpp) adds an observer lambda that takes a vector by const reference and reports sizes 2 and 0, and checks that `doubled({5})` returns `{10}` from a temporary. The explanations contrast returning by value with returning a view into the argument. How to compare: [study guide](../STUDY-GUIDE.md#compare-with-the-solutions).

## Mechanism

A value copy has its own state. A reference is another name for an existing object and does not own its lifetime. `const` blocks mutation through that access path. A const reference can avoid copying a large vector, but it does not keep the vector alive after its owner is destroyed.

## Detailed reasoning

The copy operation duplicates values into another owning vector. The const reference parameter creates no second vector and must not escape the call beyond its owner. The returned vector is different: it owns the doubled elements, so the caller may keep it after a temporary argument is destroyed. Const describes permitted access through an expression, while lifetime describes whether the object still exists. Neither concept substitutes for the other.

<!-- depth:start -->
## Copies, aliases and lifetime responsibility

Ownership answers who is responsible for keeping an object alive. A vector owns its element storage. A reference names an existing object without becoming another owner. A const reference prevents mutation through that particular access path, but it does not freeze every alias to the object or extend every lifetime automatically. Keeping those questions separate prevents many plausible but unsafe interfaces.

In doubled, the const vector reference borrows the caller input for the call. `auto out=xs` then creates an independent vector copy. The loop uses int& so each assignment changes an element of out rather than a temporary integer copy. Returning out by value produces an owning result. Copy elision or movement can make that return efficient without changing the basic correctness argument: the caller receives a value that owns its elements.

The first complete program passes a temporary vector. That temporary remains alive through the function call, so the borrowed parameter is valid while doubled reads it. The returned vector owns different storage and survives after the temporary argument is destroyed. A function returning a reference to its local out would instead leave the caller with a reference to an object whose lifetime ended at return.

The second program copies a const input and edits the copy. Constness of the source does not make the copied vector const. The two objects have separate state, so changing `ys[0]` does not change `xs[0]`. This is different from `const auto& ys=xs`, which would create another read-only alias to the same vector and prohibit the assignment through ys.

Choose parameter passing based on the interface. Small integers are commonly copied. A read-only large vector can be borrowed by const reference. A function that needs to retain an owned copy may accept by value and move into its storage. A mutation function can take a nonconst reference, but then the caller must understand the side effect. Avoid using references simply because they look faster: lifetime and aliasing are part of the cost.

## Debugging the contract

A compiler error assigning through const is useful evidence of the access contract. A dangling reference may compile and fail unpredictably later, so successful compilation cannot prove lifetime safety. Draw the owner scope and the last use of each borrow. If a helper returns a reference or view, identify the surviving owner explicitly. If no owner survives, return an owning value instead of adding const or relying on an observed address.
<!-- depth:end -->

## Worked example 1

```cpp
auto out = doubled(std::vector<int>{2, 4});
```

Expected: An owned result [4, 8] survives the temporary argument.

## Worked example 2

```cpp
const std::vector<int> xs{2, 4};
auto ys = xs;
ys[0] = 99;
```

Expected: xs stays [2, 4]; ys becomes [99, 4].

## Exercise 1: Draw owners

Draw input, copied output and borrowed parameter.

**Expected:** Two owners and one temporary borrow, no extra owner for the reference.

**Reasoning:** References alias; vectors own storage.

**Verify:** Check the drawing against Worked example 1: the temporary `{2, 4}` and `out` are the two owners, and `xs` inside `doubled` is only another name for the temporary.

## Exercise 2: Predict mutation

Change `output[0]` to 99 after `doubled({2, 4})`.

**Expected:** Input first value 2; output first value 99.

**Reasoning:** The result owns independent elements.

**Verify:** Keep the input in a named vector, then assert `input[0] == 2 && output[0] == 99` after the write, as Worked example 2 does for `xs` and `ys`.

## Exercise 3: Write a const observer

Write size_of(const vector<int>&) without mutation.

**Expected:** [2, 4] gives 2; empty gives 0.

**Reasoning:** A read-only observer does not need a value copy.

**Verify:** Assert `size_of({2, 4}) == 2` and `size_of({}) == 0`, and confirm the function also accepts a `const std::vector<int>` variable.

## Exercise 4: Diagnose const assignment

Attempt `xs[0] = 9` through const vector<int>& in a scratch file.

**Expected:** Compilation fails; remove mutation to repair.

**Reasoning:** The const access path forbids writing an element.

**Verify:** Compile the scratch file with the lesson flags and keep the error that points at the `xs[0] = 9` line; after deleting that write the file must compile without warnings.

## Exercise 5: Identify a lifetime bug

Review a function returning const vector<int>& to its local result.

**Expected:** Reject the reference return; return vector<int> by value.

**Reasoning:** The local owner dies at return, regardless of const.

**Verify:** Trace where the local result is destroyed and confirm the reviewed return type is `const std::vector<int>&`; the repaired signature returns `std::vector<int>` and compiles without warnings.

## Exercise 6: Transfer a safe result

Call doubled with temporary [5] and retain the result.

**Expected:** Stored result remains [10] after the full expression.

**Reasoning:** Owning the returned value extends the useful lifetime safely.

**Verify:** Store `auto kept = doubled(std::vector<int>{5});` and assert `kept == std::vector<int>{10}` on a later line, after the temporary argument is gone.
