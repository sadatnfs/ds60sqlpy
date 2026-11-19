using System;
using System.Collections.Generic;
using System.Linq;
using System.IO;
using System.Text;
using System.Text.Json;
using System.Threading;
using System.Threading.Tasks;
using System.Globalization;
using System.Collections.Concurrent;
using System.Threading.Channels;
using System.Net;
using System.Net.Http;
using System.Text.RegularExpressions;
using System.Buffers;

internal static class Program {
  private static void Check(bool condition, string reason) {
    if (!condition)
      throw new InvalidOperationException(reason);
  }

  private static async Task Main() {
    {
      var evt = new Event("fixture-1", "validate", "rejected", 2);
      string json = JsonSerializer.Serialize(evt);
      using var parsed = JsonDocument.Parse(json);
      Check(parsed.RootElement.GetProperty("Outcome").GetString() == "rejected",
            "outcome retained");
    }
    {
      var accepted = new Event("op-7", "save", "accepted", 3);
      var rejected = new Event("op-7", "save", "rejected", 2);
      Event[] events = { accepted, rejected };
      int submitted = 5;
      Check(events.Sum(evt => evt.Count) == submitted, "accounted input");
      Check((double)rejected.Count / submitted == 0.4, "rejection rate");
    }
    {
      // Task 3: Independent construction
      int[] quantities = { 3, -1, 4, -2, 5 };
      int submitted = quantities.Length;
      int accepted = quantities.Count(quantity => quantity >= 0);
      int rejected = quantities.Count(quantity => quantity < 0);
      Check(submitted == 5 && accepted == 3 && rejected == 2, "counts");
      Check(accepted + rejected == submitted, "every record accounted for");
    }
    Console.WriteLine("csharp-044: passed");
    await Task.CompletedTask;
  }

  public record Event(string OperationId, string Stage, string Outcome,
                      int Count);
}
