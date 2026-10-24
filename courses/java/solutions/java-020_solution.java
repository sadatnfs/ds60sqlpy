import java.util.*;

public class Main {

  record Item(String id, int key) {}

  static int lowerBound(int[] values, int target) {
    int low = 0,
      high = values.length;
    while (low < high) {
      int mid = low + (high - low) / 2;
      if (values[mid] < target) low = mid + 1;
      else high = mid;
    }
    return low;
  }

  static int minimumCoins(int amount, int[] coins) {
    if (amount < 0 || amount > 1000) throw new IllegalArgumentException("amount0..1000 required");
    for (int coin : coins)
      if (coin <= 0) throw new IllegalArgumentException("positive coins required");
    int[] dp = new int[amount + 1];
    Arrays.fill(dp, amount + 1);
    dp[0] = 0;
    for (int current = 1; current <= amount; current++) for (int coin : coins)
      if (coin <= current) dp[current] = Math.min(dp[current], dp[current - coin] + 1);
    return dp[amount] > amount ? -1 : dp[amount];
  }

  public static void main(String[] args) throws Exception {
    // Exercise 1: Find the first duplicate boundary
    int[] sorted = { 1, 2, 2, 5 };
    assert lowerBound(sorted, 2) == 1 && lowerBound(sorted, 6) == 4;

    // Exercise 2: Handle empty and outside searches
    assert lowerBound(new int[0], 7) == 0;
    assert lowerBound(sorted, 0) == 0;

    // Exercise 3: Preserve stable ties
    List<Item> items = new ArrayList<>(
      List.of(new Item("a", 2), new Item("b", 1), new Item("c", 2))
    );
    items.sort(Comparator.comparingInt(Item::key));
    assert items.stream().map(Item::id).toList().equals(List.of("b", "a", "c"));

    // Exercise 4: Solve a greedy counterexample
    assert minimumCoins(6, new int[] { 1, 3, 4 }) == 2;

    // Exercise 5: Represent an unreachable amount
    assert minimumCoins(3, new int[] { 2 }) == -1;
    assert minimumCoins(0, new int[] { 2, 5 }) == 0;

    // Exercise 6: Reject invalid recurrence inputs
    boolean negative = false,
      zeroCoin = false;
    try {
      minimumCoins(-1, new int[] { 1 });
    } catch (IllegalArgumentException expected) {
      negative = true;
    }
    try {
      minimumCoins(3, new int[] { 0, 1 });
    } catch (IllegalArgumentException expected) {
      zeroCoin = true;
    }
    assert negative && zeroCoin;
  }
}
