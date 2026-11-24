using System;
using System.Threading.Tasks;

internal static class Program {
  private static void Check(bool condition, string reason) {
    if (!condition)
      throw new InvalidOperationException(reason);
  }

  private static async Task Main() {
    {
      string greeting = "Hello, C#";
      Check(greeting.Length == 9, "greeting length");
      Console.WriteLine(greeting);
    }
    {
      int boxes = 3;
      int itemsPerBox = 4;
      int total = boxes * itemsPerBox;
      Check(total == 12, "computed total");
      Check(total != boxes + itemsPerBox, "multiplication is not addition");
    }
    {
      // Task 2: Guided modification
      string greeting = "Hi there, Ada!";
      Check(greeting.Length == 14, "changed greeting length");
    }
    {
      // Task 3: Independent construction
      int rows = 4;
      int seatsPerRow = 6;
      int seats = rows * seatsPerRow;
      Check(seats == 24, "four rows of six seats");
    }
    {
      // Task 5: Boundary evidence
      int seatsPerRow = 6;
      int noRows = 0 * seatsPerRow;
      int oneRow = 1 * seatsPerRow;
      Check(noRows == 0, "zero rows hold no seats");
      Check(oneRow == seatsPerRow, "one row holds one row of seats");
    }
    Console.WriteLine("csharp-001: passed");
    await Task.CompletedTask;
  }
}
