# java-019: explanatory solutions

Open after an attempt or an explicit solution reveal. The executable reference runs the six exercise checks together as `Main.java`. The guide contains independent worked examples, while this file explains the choices and failure cases in the complete answer.

## Mechanism review

A data structure is a set of operations with representation and cost tradeoffs. AnArrayList supports constant-time indexed access but shifting elements after a front insertion costs linear work. AHashMap offers expected constant-time lookup under appropriate hashing assumptions,not a promise that every operation always costs one step. ADeque supports queue and stack operations without shifting an array prefix. APriorityQueue keeps the smallest element available but does not expose a fully sorted iteration order. BigO describes how work grows with input size,not a measured wall-clock time or a guarantee about constants.

**BigO:** An asymptotic upper-bound description of growth in work or space.

**Deque:** A double-ended queue supporting insertion and removal at both ends.

**Heap:** A partial ordering that keeps a minimum or maximum at the root.

## Reading the reference

ArrayDeque.addLast/removeFirst implements a queue;push/pop implements a stack. PriorityQueue.add andpoll maintain a heap ordering,and repeatedpoll produces sorted removal order. Iterating the heap is not a sorted traversal. Count comparisons in a simple linear search to connect an algorithmic model to observations. A hash-based membership result must use stable equality and hashing contracts.

## Exercise 1: Use a FIFO queue

Task: Adda,b,c to anArrayDeque and remove from the front.

The queue preserves arrival order. ChoosingremoveLast instead would create a stack-like policy.

```java
Deque<String> queue=new ArrayDeque<>(); queue.addLast("a");queue.addLast("b");queue.addLast("c");
assert List.of(queue.removeFirst(),queue.removeFirst(),queue.removeFirst()).equals(List.of("a","b","c"));
```

**Expected:** a,b,c order.

**Verify:** Compare the program values or named exception with a,b,c order. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 2: Use a LIFO stack

Task: Push1,2,3 onto aDeque andpop all values.

The most recently pushed value is removed first. Stack behavior is useful for nested traversal or undo histories but differs from fair arrival-order processing.

```java
Deque<Integer> stack=new ArrayDeque<>();stack.push(1);stack.push(2);stack.push(3);
assert List.of(stack.pop(),stack.pop(),stack.pop()).equals(List.of(3,2,1));
```

**Expected:** 3,2,1.

**Verify:** Compare the program values or named exception with 3,2,1. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 3: Poll a priority queue

Task: Insert5,1,4,2 and repeatedlypoll.

The heap guarantees the next minimum,not that its backing iteration is sorted. Repeated removal establishes the sorted sequence.

```java
PriorityQueue<Integer> heap=new PriorityQueue<>(List.of(5,1,4,2));List<Integer> removed=new ArrayList<>();
while(!heap.isEmpty())removed.add(heap.remove());
assert removed.equals(List.of(1,2,4,5));
```

**Expected:** 1,2,4,5.

**Verify:** Compare the program values or named exception with 1,2,4,5. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 4: Count linear-search work

Task: Search for the final item in arrays oflength4 and8 using a comparison counter.

Doubling this worst-case input doubles observed comparisons. This supports the linear growth model for this algorithm without making a hardware timing claim.

```java
assert comparisons(new int[]{1,2,3,4},4)==4;
assert comparisons(new int[]{1,2,3,4,5,6,7,8},8)==8;
```

**Expected:** 4 and8 comparisons.

**Verify:** Compare the program values or named exception with 4 and8 comparisons. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 5: Preserve duplicate priorities

Task: Insert tasks with equal priority and a stable sequence tie-breaker.

A priority alone may not define a deterministic order among ties. The explicit sequence field preserves a declared policy.

```java
PriorityQueue<Task> tasks=new PriorityQueue<>(Comparator.comparingInt(Task::priority).thenComparingInt(Task::sequence));
tasks.add(new Task(1,2,"later"));tasks.add(new Task(1,1,"earlier"));
assert tasks.remove().name().equals("earlier");
```

**Expected:** earlier sequence removed first.

**Verify:** Compare the program values or named exception with earlier sequence removed first. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 6: Handle empty removal explicitly

Task: CompareDeque.pollFirst withremoveFirst on an empty queue.

The two APIs express different absence contracts. Choosing one deliberately is clearer than catching an exception that the caller expected as normal control flow.

```java
Deque<Integer> empty=new ArrayDeque<>();assert empty.pollFirst()==null;boolean failed=false;
try{empty.removeFirst();}catch(NoSuchElementException expected){failed=true;}
assert failed;
```

**Expected:** poll returnsnull;remove throwsNoSuchElementException.

**Verify:** Compare the program values or named exception with poll returnsnull;remove throwsNoSuchElementException. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## After comparing the answer

Run the complete reference with assertions enabled, then return to your own implementation. Recreate one check with different values and explain its expected result before execution. A compiler error, an expected domain exception and an assertion failure represent different stages and should be reported separately. Preserve ownership boundaries when adapting file, network or concurrency examples. The reference never authorizes access to a shared service or deletion of learner state. Use a fresh tiny fixture when you need to distinguish two interpretations of an API contract.
