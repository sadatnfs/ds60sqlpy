# c-021: explained solutions

`c-021_solution.c` assembles the "insert at the head" case through the "transfer double-reversal reasoning" case in one `main.c`.

Compare only after an attempt: [Compare and transfer](../STUDY-GUIDE.md#compare-and-transfer).

## Mechanism and assumptions

A linked list stores each element in a node that points to the next node. It can insert at the head without moving all existing elements, but each allocation and pointer chase has a cost. The head pointer is part of the mutable structure, so a function changing it often receives a pointer to that pointer. Every node has one release responsibility. When deleting during traversal, save the next pointer before freeing the current node; reading current->next afterward would use an expired object. Lists are useful when their mutation pattern fits the problem, not simply because pointers make them possible.

struct Node contains a value and next pointer. push_front allocates first and changes the head only after success. A Node **head lets the helper update the caller head. Iterative destruction retains next before free and resets the head afterward. Reverse uses previous, current and next pointers, maintaining a processed-prefix invariant without new allocations.

## Exercise 1: Insert at the head: predict an edited check

In worked example 1, change `CHECK(push_front(&head, 1) && push_front(&head, 2));` to `CHECK(push_front(&head, 2) && push_front(&head, 2));`. Predict whether the CHECK still holds and why, then run and restore.

The unchanged code is worked example 1:

```c
struct Node *head = NULL;
CHECK(push_front(&head, 1) && push_front(&head, 2));
CHECK(head->value == 2 && head->next->value == 1);
destroy_list(&head);
```

**Expected:** `Check failed`: `CHECK(push_front(&head, 2) && push_front(&head, 2));` is false, although the list order is 2 then 1.

**Verify:** Explain which claim `CHECK(push_front(&head, 2) && push_front(&head, 2));` makes that the state fails; restoring `CHECK(push_front(&head, 1) && push_front(&head, 2));` passes again.

Head insertion reverses arrival order. If FIFO order is required, a tail pointer or different structure is needed.

## Exercise 2: Count a constructed list: debug a regression

Worked example 2 now has a line reading `for (int i = 0; i <= 3; i++)`. Repair it so that the length is 3 again.

The unchanged code is worked example 2:

```c
struct Node *head = NULL;
for (int i = 0; i < 3; i++)
  CHECK(push_front(&head, i));
CHECK(list_length(head) == 3);
destroy_list(&head);
```

**Expected:** `Check failed` at `list_length(head) == 3` until the line reads `for (int i = 0; i < 3; i++)` again.

**Verify:** Explain how `for (int i = 0; i <= 3; i++)` changes the value `list_length(head) == 3` tests, using your failing and repaired runs.

The traversal stops at NULL and does not assume nodes occupy adjacent addresses.

## Exercise 3: Handle an empty list

Measure and destroy a null head.

```c
struct Node *head = NULL;
CHECK(list_length(head) == 0);
destroy_list(&head);
CHECK(head == NULL);
```

**Expected:** Length is zero and head stays NULL.

**Verify:** Keep a CHECK equivalent to `head == NULL`. Control edit: `CHECK(head != NULL);` must fail; then restore it.

An empty structure should have natural operations without a fabricated sentinel payload.

## Exercise 4: Reverse without reallocating

Build 3, 2, 1 and reverse it.

```c
struct Node *head = NULL;
CHECK(push_front(&head, 1) && push_front(&head, 2) && push_front(&head, 3));
reverse_list(&head);
CHECK(head->value == 1 && head->next->value == 2 &&
      head->next->next->value == 3);
destroy_list(&head);
```

**Expected:** The order becomes 1, 2, 3.

**Verify:** Keep a CHECK equivalent to `head->value == 1 && head->next->value == 2 && head->next->next->value == 3`. Control edit: `CHECK(push_front(&head, 2) && push_front(&head, 2) && push_front(&head, 3));` must fail; then restore it.

Saving next before rewiring preserves access to the unprocessed suffix.

## Exercise 5: Reverse a singleton

Reverse a one-node list.

```c
struct Node *head = NULL;
CHECK(push_front(&head, 7));
reverse_list(&head);
CHECK(head->value == 7 && head->next == NULL);
destroy_list(&head);
```

**Expected:** Its value and terminating link are preserved.

**Verify:** Keep a CHECK equivalent to `head->value == 7 && head->next == NULL`. Control edit: `CHECK(push_front(&head, 8));` must fail; then restore it.

The smallest nonempty structure checks the initial and final link conditions.

## Exercise 6: Transfer double-reversal reasoning

Reverse a two-node list twice.

```c
struct Node *head = NULL;
CHECK(push_front(&head, 1) && push_front(&head, 2));
reverse_list(&head);
reverse_list(&head);
CHECK(head->value == 2 && head->next->value == 1);
destroy_list(&head);
```

**Expected:** Its original order is restored.

**Verify:** Keep a CHECK equivalent to `head->value == 2 && head->next->value == 1`. Control edit: `CHECK(push_front(&head, 2) && push_front(&head, 2));` must fail; then restore it.

This involution property complements exact order tests. It alone would not reject a no-op implementation, so keep both forms of evidence.

## After comparison

Build the list 3, 2, 1 with three `push_front` calls, reverse it once and CHECK the exact order 1, 2, 3 node by node, then the NULL after the last node. A double reversal cannot reject a no-op `reverse_list`; a single reversal checked against exact values can. Explain which pointer each step must save before it rewires `next`.
