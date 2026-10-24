// csharp-023: Exceptions and preserving failure meaning
// Implement the six tasks from the guide. Keep your prediction beside each check.
// Task 1: Identify which failure category each catch handles.
// Task 2: Add a separate negative-count case without classifying it as FormatException.
// Task 3: Define an import API with distinct invalid-input and storage-failure outcomes.
// Task 4: Diagnose catch-all code that returns an empty successful report.
// Task 5: Test success, expected rejection and an unexpected exception separately.
// Task 6: Decide which layer owns user-facing error translation and which details should remain private diagnostics.
using System;

internal static class Program {
  private static void Main() {
    throw new NotImplementedException(
        "Implement your own lesson attempt before running.");
  }
}
