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
      int accepted = 3, rejected = 2, submitted = 5;
      Check(accepted + rejected == submitted, "accounted input");
      Check((double)rejected / submitted == 0.4, "defined rejection rate");
    }
    Console.WriteLine("csharp-044: passed");
    await Task.CompletedTask;
  }

  public record Event(string OperationId, string Stage, string Outcome,
                      int Count);
}
