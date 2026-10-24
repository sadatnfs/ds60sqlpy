import java.util.*;

public class Main {

  record Task(int priority, int sequence, String name) {}

  static int comparisons(int[] values, int target) {
    int count = 0;
    for (int value : values) {
      count++;
      if (value == target) break;
    }
    return count;
  }

  public static void main(String[] args) throws Exception {
    // Exercise 1: Use a FIFO queue
    Deque<String> queue = new ArrayDeque<>();
    queue.addLast("a");
    queue.addLast("b");
    queue.addLast("c");
    assert List.of(queue.removeFirst(), queue.removeFirst(), queue.removeFirst()).equals(
      List.of("a", "b", "c")
    );

    // Exercise 2: Use a LIFO stack
    Deque<Integer> stack = new ArrayDeque<>();
    stack.push(1);
    stack.push(2);
    stack.push(3);
    assert List.of(stack.pop(), stack.pop(), stack.pop()).equals(List.of(3, 2, 1));

    // Exercise 3: Poll a priority queue
    PriorityQueue<Integer> heap = new PriorityQueue<>(List.of(5, 1, 4, 2));
    List<Integer> removed = new ArrayList<>();
    while (!heap.isEmpty()) removed.add(heap.remove());
    assert removed.equals(List.of(1, 2, 4, 5));

    // Exercise 4: Count linear-search work
    assert comparisons(new int[] { 1, 2, 3, 4 }, 4) == 4;
    assert comparisons(new int[] { 1, 2, 3, 4, 5, 6, 7, 8 }, 8) == 8;

    // Exercise 5: Preserve duplicate priorities
    PriorityQueue<Task> tasks = new PriorityQueue<>(
      Comparator.comparingInt(Task::priority).thenComparingInt(Task::sequence)
    );
    tasks.add(new Task(1, 2, "later"));
    tasks.add(new Task(1, 1, "earlier"));
    assert tasks.remove().name().equals("earlier");

    // Exercise 6: Handle empty removal explicitly
    Deque<Integer> empty = new ArrayDeque<>();
    assert empty.pollFirst() == null;
    boolean failed = false;
    try {
      empty.removeFirst();
    } catch (NoSuchElementException expected) {
      failed = true;
    }
    assert failed;
  }
}
