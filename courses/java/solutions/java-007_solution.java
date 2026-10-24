import java.util.*;

public class Main {

  static final class Account {

    private int cents;

    Account(int cents) {
      if (cents < 0) throw new IllegalArgumentException("negative balance");
      this.cents = cents;
    }

    int balance() {
      return cents;
    }

    void deposit(int amount) {
      if (amount < 0) throw new IllegalArgumentException("negative deposit");
      cents = Math.addExact(cents, amount);
    }

    void withdraw(int amount) {
      if (amount < 0 || amount > cents) throw new IllegalArgumentException("invalid withdrawal");
      cents -= amount;
    }
  }

  public static void main(String[] args) throws Exception {
    // Exercise 1: Create independent accounts
    Account first = new Account(100);
    Account second = new Account(100);
    first.deposit(50);
    assert first.balance() == 150 && second.balance() == 100;

    // Exercise 2: Withdraw within the contract
    first.withdraw(40);
    assert first.balance() == 110;

    // Exercise 3: Reject overdraft atomically
    boolean overdraft = false;
    try {
      first.withdraw(111);
    } catch (IllegalArgumentException expected) {
      overdraft = true;
    }
    assert overdraft && first.balance() == 110;

    // Exercise 4: Reject negative input
    boolean negative = false;
    try {
      first.deposit(-1);
    } catch (IllegalArgumentException expected) {
      negative = true;
    }
    assert negative && first.balance() == 110;

    // Exercise 5: Reject invalid construction
    boolean invalidStart = false;
    try {
      new Account(-1);
    } catch (IllegalArgumentException expected) {
      invalidStart = true;
    }
    assert invalidStart;

    // Exercise 6: Protect against overflow
    Account full = new Account(Integer.MAX_VALUE);
    boolean overflow = false;
    try {
      full.deposit(1);
    } catch (ArithmeticException expected) {
      overflow = true;
    }
    assert overflow && full.balance() == Integer.MAX_VALUE;
  }
}
