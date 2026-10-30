// Answer-free learner worksheet. Save your own Main.java before editing.
public class Main {

  public static void main(String[] args) throws Exception {
    // Exercise 1: Use immutable value keys
    // Create two equal Point records and insert one into a map.
    // Expected: lookup with the other returns origin; hashes equal.

    // Exercise 2: Sort with a tie-breaker
    // Sort people(age20,idb),(age20,ida),(age18,idc) by age then ID.
    // Expected: IDs c,a,b.

    // Exercise 3: Expose comparator uniqueness
    // Insert two different people ofage20 into a TreeSet comparingage only.
    // Expected: setsize1 despite unequal records.

    // Exercise 4: Demonstrate mutable-key failure
    // Insert a key withhash1,mutate its hash field to2,and attempt lookup with the same object.
    // Expected: lookup fails in this fixture while mapsize remains1.

    // Exercise 5: Avoid comparator subtraction
    // CompareInteger.MIN_VALUE and 1 usingInteger.compare.
    // Expected: negative result;subtraction overflows positive.

    // Exercise 6: Keep identity and display separate
    // Give twoPoints the same formatted label but different coordinates;compare values.
    // Expected: display labels equal; points unequal.
    System.out.println("Implement and check the six exercises in your saved copy.");
  }
}
