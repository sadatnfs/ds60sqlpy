// csharp-036: Garbage collection, pooling and retained memory
// Implement the six tasks from the guide. Keep your prediction beside each check.
// Task 1: Separate logical length from rented array length.
// Task 2: Use a different requested length while initializing exactly that region.
// Task 3: Write a pooled-buffer helper with finally-based return.
// Task 4: Diagnose reading uninitialized pooled capacity or returning the same buffer twice.
// Task 5: Test cleanup when the computation throws.
// Task 6: Decide whether pooling is justified using allocation measurements and a stated lifetime contract.
using System;

internal static class Program {
  private static void Main() {
    throw new NotImplementedException(
        "Implement your own lesson attempt before running.");
  }
}
