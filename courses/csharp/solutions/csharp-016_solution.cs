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
      var totals = Import(new[] { "pear,2", "apple,3", "pear,4" });
      Check(totals.Rejected == 0, "all accepted");
      Check(totals.Counts["pear"] == 6 && totals.Counts["apple"] == 3,
            "per-item totals");
    }
    {
      var totals = Import(new[] { "pear,2", "pear,no", "apple,-1", "broken" });
      Check(totals.Rejected == 3, "rejections counted");
      Check(totals.Counts.Count == 1 && totals.Counts["pear"] == 2,
            "only valid data contributes");
      Check(Import(Array.Empty<string>()).Counts.Count == 0, "empty input");
    }
    {
      // Task 2: Guided modification
      var totals = Import(new[] { "pear,2", "apple,3", "pear,4", "apple,5" });
      Check(totals.Rejected == 0, "duplicate line accepted");
      Check(totals.Counts["apple"] == 8, "predicted apple total");
      Check(totals.Counts["pear"] == 6, "pear unchanged");
      Check(totals.Counts.Count == 2, "no new key");
    }
    {
      // Task 3: Independent construction
      var result = Import(new[] { "pear,2", "apple,3", "bad", "pear,1" });
      var comparer = StringComparer.Ordinal;
      var names = result.Counts.Keys.OrderBy(key => key, comparer);
      var lines = new List<string>();
      foreach (string name in names) {
        lines.Add($"{name}: {result.Counts[name]}");
      }
      lines.Add($"rejected: {result.Rejected}");
      string report = string.Join("\n", lines);
      Check(report == "apple: 3\npear: 3\nrejected: 1", "sorted report");
    }
    {
      // Task 5: Boundary evidence
      var blank = Import(new[] { ",3", "  ,3" });
      Check(blank.Rejected == 2, "empty and blank names rejected");
      Check(blank.Counts.Count == 0, "no entry for a blank name");
      var extra = Import(new[] { "pear,2,box" });
      Check(extra.Rejected == 1, "extra field rejected");
      var zero = Import(new[] { "pear,0" });
      Check(zero.Rejected == 0 && zero.Counts["pear"] == 0, "zero accepted");
      var none = Import(Array.Empty<string>());
      Check(none.Rejected == 0 && none.Counts.Count == 0, "empty input");
    }
    Console.WriteLine("csharp-016: passed");
    await Task.CompletedTask;
  }

  public static (Dictionary<string, int> Counts, int Rejected)
      Import(IEnumerable<string> lines) {
    var counts = new Dictionary<string, int>(StringComparer.Ordinal);
    int rejected = 0;
    foreach (string line in lines) {
      string[] fields = line.Split(',');
      if (fields.Length != 2 || string.IsNullOrWhiteSpace(fields[0]) ||
          !int.TryParse(fields[1], out int quantity) || quantity < 0) {
        rejected++;
        continue;
      }
      counts.TryGetValue(fields[0], out int before);
      counts[fields[0]] = checked(before + quantity);
    }
    return (counts, rejected);
  }
}
