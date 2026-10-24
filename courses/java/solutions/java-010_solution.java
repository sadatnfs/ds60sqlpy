import java.util.*;

public class Main {

  interface Pricing {
    int price(int amount);
  }

  static void requireNonnegative(int amount) {
    if (amount < 0) throw new IllegalArgumentException("negative amount");
  }

  record Fee(Pricing delegate, int cents) implements Pricing {
    Fee {
      Objects.requireNonNull(delegate);
      requireNonnegative(cents);
    }

    public int price(int amount) {
      return Math.addExact(delegate.price(amount), cents);
    }
  }

  public static void main(String[] args) throws Exception {
    // Exercise 1: Call through an interface
    Pricing regular = amount -> {
      requireNonnegative(amount);
      return amount;
    };
    Pricing half = amount -> {
      requireNonnegative(amount);
      return amount / 2;
    };
    assert regular.price(100) == 100 && half.price(100) == 50;

    // Exercise 2: Compose a fee policy
    Pricing withFee = new Fee(half, 10);
    assert withFee.price(100) == 60;

    // Exercise 3: Inspect rounding semantics
    assert half.price(101) == 50;

    // Exercise 4: Validate every implementation
    for (Pricing policy : List.of(regular, half, withFee)) {
      boolean rejected = false;
      try {
        policy.price(-1);
      } catch (IllegalArgumentException expected) {
        rejected = true;
      }
      assert rejected;
    }

    // Exercise 5: Change a collaborator without changing caller code
    List<Integer> prices = new ArrayList<>();
    for (Pricing policy : List.of(regular, half, withFee)) prices.add(policy.price(100));
    assert prices.equals(List.of(100, 50, 60));

    // Exercise 6: Reject an invalid wrapper
    boolean feeRejected = false,
      delegateRejected = false;
    try {
      new Fee(regular, -1);
    } catch (IllegalArgumentException expected) {
      feeRejected = true;
    }
    try {
      new Fee(null, 1);
    } catch (NullPointerException expected) {
      delegateRejected = true;
    }
    assert feeRejected && delegateRejected;
  }
}
