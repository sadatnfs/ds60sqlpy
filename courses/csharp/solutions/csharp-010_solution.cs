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
      var counts = new Dictionary<string, int>(
          StringComparer.OrdinalIgnoreCase) { ["Oak"] = 0 };
      Check(counts.TryGetValue("OAK", out int zero) && zero == 0,
            "present zero");
      Check(!counts.TryGetValue("Pine", out _), "missing key");
    }
    {
      var labels = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
      Check(labels.Add("red"), "first insertion");
      Check(!labels.Add("RED"), "duplicate identity");
      labels.Add("blue");
      Check(labels.Count == 2, "two identities");
    }
    {
      // Task 3: Independent construction
      string[] tags = { "red", "blue", "red" };
      var counts = new Dictionary<string, int>(StringComparer.Ordinal);
      foreach (string tag in tags) {
        counts.TryGetValue(tag, out int before);
        counts[tag] = before + 1;
      }
      Check(counts["red"] == 2 && counts["blue"] == 1, "frequencies");
      Check(counts.Count == 2, "one entry per distinct tag");
    }
    Console.WriteLine("csharp-010: passed");
    await Task.CompletedTask;
  }
}
