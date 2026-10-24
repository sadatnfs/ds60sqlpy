// csharp-030: Cooperative cancellation and bounded waiting
// Implement the six tasks from the guide. Keep your prediction beside each check.
// Task 1: Identify the request, observation and completion events.
// Task 2: Pass a token through a helper and check it before a state change.
// Task 3: Write an operation that stops cooperatively and preserves already committed work.
// Task 4: Diagnose automatically replaying a write after its waiter times out.
// Task 5: Test cancellation requested before start and after successful completion.
// Task 6: Design an operation receipt distinguishing cancelled waiting, confirmed cancellation and unknown outcome.
using System;

internal static class Program {
  private static void Main() {
    throw new NotImplementedException(
        "Implement your own lesson attempt before running.");
  }
}
