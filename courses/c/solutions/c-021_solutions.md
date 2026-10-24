# c-021: explained solutions

Compare after an attempt or explicit reveal. The complete executable reference implements all six checks in one main.c.

## Mechanism and assumptions

A linked list stores each element in a node that points to the next node. It can insert at the head without moving all existing elements, but each allocation and pointer chase has a cost. The head pointer is part of the mutable structure, so a function changing it often receives a pointer to that pointer. Every node has one release responsibility. When deleting during traversal, save the next pointer before freeing the current node; reading current->next afterward would use an expired object. Lists are useful when their mutation pattern fits the problem, not simply because pointers make them possible.

struct Node contains a value and next pointer. push_front allocates first and changes the head only after success. A Node **head lets the helper update the caller head. Iterative destruction retains next before free and resets the head afterward. Reverse uses previous, current and next pointers, maintaining a processed-prefix invariant without new allocations.

## Exercise 1: Insert at the head

Push 1 and then 2.

```c
struct Node *head = NULL;
CHECK(push_front(&head, 1) && push_front(&head, 2));
CHECK(head->value == 2 && head->next->value == 1);
destroy_list(&head);
```

**Expected:** The list order is 2 then 1.

Head insertion reverses arrival order. If FIFO order is required, a tail pointer or different structure is needed.

## Exercise 2: Count a constructed list

Push three values and count nodes.

```c
struct Node *head = NULL;
for (int i = 0; i < 3; i++)
  CHECK(push_front(&head, i));
CHECK(list_length(head) == 3);
destroy_list(&head);
```

**Expected:** The length is 3.

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

This involution property complements exact order tests. It alone would not reject a no-op implementation, so keep both forms of evidence.

## After comparison

Return to your own source and add a fresh distinguishing input. Explain why every access remains within a live object and why every owned resource is released. A valid expected failure belongs in the test contract; undefined behavior does not. Retain compiler diagnostics and any sanitizer evidence separately from ordinary output. A working fixture demonstrates its stated assumptions, not universal safety for arbitrary inputs.
